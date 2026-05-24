#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import argparse
# Telegram Importe mit Fallback für Tests
try:
    from telegram import Update, ReplyKeyboardMarkup
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    Update = None
    ReplyKeyboardMarkup = None
    logging.warning("telegram module nicht gefunden - Bot läuft im Test-Modus")

import signal
import sys
import asyncio
# Telegram.ext Import mit Fallback
try:
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
    TELEGRAM_EXT_AVAILABLE = True
except ImportError:
    TELEGRAM_EXT_AVAILABLE = False
    Application = None
    CommandHandler = None
    MessageHandler = None
    filters = None
    ContextTypes = None
    ConversationHandler = None
    CallbackQueryHandler = None
    logging.warning("telegram.ext module nicht gefunden - Bot läuft im Test-Modus")
from lib.config import modeList, markupList, LOGIN, MAIN, ADMIN, SETTINGS, LIGHT, Config, genMarkupList
from lib.user_database import UserDatabase
from lib.telegram_utils import retry_telegram_call

import lib.adminMode as AdminMode
import lib.loginMode as LoginMode
import lib.settingsMode as SettingsMode
import lib.lichtMode as LichtMode

# Konfiguration (wird in main() mit CLI-Argument initialisiert)
config = None
db = None

# Textbefehle für MAIN-Status (da modeList[MAIN] = None)
main_textbefehl = {
    'start': 'Bot starten und Login einleiten',
    'help': 'Diese Hilfe anzeigen',
    'logout': 'Ausloggen',
    'heizung': 'Öffnet den Heizungs-Modus für Heizkörper- und Temperaturverwaltung',
    'automation': 'Öffnet den Automation-Modus für Szenarien und Vorlagen',
    'einstellungen': 'Öffnet die Einstellungen für Sprache und Benachrichtigungen',
    'licht': 'Öffnet den Licht-Modus für LED-Steuerung'
}

# Globale variable for graceful shutdown
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    logging.info("\nBot wird beendet...")
    shutdown_event.set()

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Globale Variablen für Logging
logger = None
debug_logger = None
fritzbox = None

def init_logging():
    """Initialisiert das Logging-System"""
    global logger, debug_logger
    
    # Logging
    logging.basicConfig(**config.get_logging_config())
    logger = logging.getLogger(__name__)
    
    # Zusätzlicher File-Logger für Debug
    debug_logger = logging.getLogger('debug_logger')
    # Level aus Config verwenden, nicht hart auf DEBUG
    debug_logger.setLevel(config.get('logging.level', 'DEBUG'))
    
    # File Handler für Debug-Logs
    file_handler = logging.FileHandler('debug.log', mode='w')
    file_handler.setLevel(config.get('logging.level', 'DEBUG'))
    formatter = logging.Formatter(config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    file_handler.setFormatter(formatter)
    debug_logger.addHandler(file_handler)
    
    # Console Handler für Debug-Logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.get('logging.level', 'DEBUG'))
    console_handler.setFormatter(formatter)
    debug_logger.addHandler(console_handler)



# Nur bei Verfügbarkeit der Telegram-Module initialisieren
if TELEGRAM_AVAILABLE and TELEGRAM_EXT_AVAILABLE:
    pass  # Wird in main() nach config-Initialisierung aufgerufen
    import lib.loginMode as LoginMode  # Modul, keine Klasse
    from lib.settingsMode import SettingsMode

    # Modi Klassennamen zu den Statusen (Index 0=MAIN, 1=LOGIN, 2=ADMIN, usw.)
    # Hinweis: Die Indizes müssen mit den Werten von ConversationHandler.states übereinstimmen
    from lib.config import modeList
    
    # markupList generieren
    from lib.config import genMarkupList
    markupList = genMarkupList()
    
    # modeList initialisieren!
    from lib.config import init_mode_list
    init_mode_list()
else:
    logging.warning("Telegram-Module nicht verfügbar - Bot wird nicht gestartet")
    sys.exit(1)


def initializeChatData(message, user_data):
    """Initialisiert die Chat-Daten"""
    user_data['langCode'] = str(message.from_user.language_code) if message.from_user.language_code else 'de'
    user_data['chatId'] = str(message.chat.id)
    user_data['firstname'] = str(message.from_user.first_name) if message.from_user.first_name else ''
    user_data['lastname'] = str(message.from_user.last_name) if message.from_user.last_name else ''
    user_data['keyboard'] = markupList[LOGIN]
    user_data['status'] = LOGIN
    user_data['userRequest'] = None
    
    # Prüfen ob Admin (immer erlaubt)
    if str(user_data['chatId']) in [str(id) for id in config.get_admin_chat_ids()]:
        user_data['isAuthenticated'] = True
    else:
        # Für andere Benutzer initial auf False setzen, wird in checkAuthentifizierung geprüft
        user_data['isAuthenticated'] = False
    
    logger.info(f'chatID:{user_data["chatId"]} Username: {user_data["firstname"]} {user_data["lastname"]}')

async def checkAuthentifizierung(update, user_data):
    """Überprüft die Authentifizierung"""
    chat_id = user_data['chatId']
    
    # Admin immer erlauben
    if str(chat_id) in [str(id) for id in config.get_admin_chat_ids()]:
        user_data['isAuthenticated'] = True
        # Admin zur Datenbank hinzufügen falls nicht vorhanden
        try:
            if not db.user_exists(int(chat_id)):
                db.add_user(int(chat_id), user_data['firstname'], is_admin=1)
            else:
                # Nur Name aktualisieren falls sich geändert hat
                db.update_user_info(int(chat_id), user_data['firstname'])
        except Exception as e:
            logger.error(f"Fehler beim Admin-Update: {e}")
            pass  # Admin existiert wahrscheinlich schon
    else:
        # Prüfen ob Benutzer in Datenbank und nicht geblockt
        try:
            # Prüfen ob User gerade freigeschaltet wurde (hat Zugriff aber Status ist noch LOGIN)
            was_just_granted = (db.user_exists(int(chat_id)) and 
                              db.is_access_granted(int(chat_id)) and 
                              user_data.get('status') == LOGIN)
            
            if db.user_exists(int(chat_id)) and (db.is_user_allowed(int(chat_id)) or db.is_access_granted(int(chat_id))):
                user_data['isAuthenticated'] = True
                # Wenn User gerade freigeschaltet wurde, automatisch in MAIN wechseln
                if was_just_granted:
                    user_data['keyboard'] = markupList[MAIN]
                    user_data['status'] = MAIN
                    await retry_telegram_call(
                        update.message.reply_text,
                        '🎉 **Willkommen im Licht-Bot!**\n\n'
                        'Dein Zugriff wurde erfolgreich aktiviert.\n'
                        'Du kannst jetzt alle Funktionen nutzen.\n\n'
                        '💡 Nutze /help für eine Übersicht aller Befehle.',
                        reply_markup=markupList[MAIN]
                    )
            else:
                user_data['isAuthenticated'] = False
                if not db.is_user_blocked(int(chat_id)):
                    await retry_telegram_call(
                        update.message.reply_text,
                        'Ohh... Deine Berechtigung ist abgelaufen.',
                        reply_markup=markupList[LOGIN]
                    )
        except:
            user_data['isAuthenticated'] = False
    
    # Status nur anpassen wenn nicht bereits auf MAIN gesetzt (z.B. nach Freischaltung)
    if not user_data['isAuthenticated']:
        user_data['keyboard'] = markupList[LOGIN]
        user_data['status'] = LOGIN
        return LOGIN
    elif user_data['isAuthenticated'] and user_data['status'] == LOGIN:
        # Nur wechseln wenn nicht bereits durch Freischaltung auf MAIN gesetzt
        if 'was_just_granted' not in locals() or not was_just_granted:
            user_data['keyboard'] = markupList[MAIN]
            user_data['status'] = MAIN

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Beendet die Konversation"""
    if 'choice' in context.user_data:
        del context.user_data['choice']

    await update.message.reply_text("bye")
    
    context.user_data.clear()
    return ConversationHandler.END

async def selectModeFunc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wählt die passende Funktion basierend auf dem Modus aus der modeList"""
    logger.debug(f"selectModeFunc aufgerufen - Status: {context.user_data.get('status')}, Text: {update.message.text}")
    
    if modeList[context.user_data['status']] is None:
        await update.message.reply_text(
                'Interner Error: Kein Modul gefunden in modeList an Stelle "'+str(context.user_data['status'])+'".\n',
                reply_markup=ReplyKeyboardMarkup(context.user_data['keyboard'], one_time_keyboard=True))
        return context.user_data['status']
    else:
        module = modeList[context.user_data['status']]
        logger.debug(f"Modul gefunden: {module.__name__ if hasattr(module, '__name__') else module}")
        
        textFromUser = update.message.text
        logger.debug(f"Text vom User: {textFromUser}")
        
        # Authentifizierung prüfen für alle Modi außer LOGIN
        if context.user_data['status'] != LOGIN:
            await checkAuthentifizierung(update, context.user_data)
            # Wenn Status durch checkAuthentifizierung geändert wurde (z.B. nach Freischaltung)
            if context.user_data['status'] == MAIN and context.user_data.get('isAuthenticated'):
                # User wurde gerade freigeschaltet, zeige Hauptmenü
                return MAIN
            elif context.user_data['status'] == LOGIN:
                # User wurde nicht authentifiziert, bleibe im LOGIN
                return LOGIN
        
        # Bei LOGIN-Status immer die Login-Funktion aufrufen
        if context.user_data['status'] == LOGIN:
            # Default Funktion (login) aufrufen
            try:
                func = getattr(module, 'default')
                # Korrekte Parameter-Reihenfolge: (update, context, user_data, markupList)
                funcRet = await func(update, context, context.user_data, markupList)
                context.user_data['status'] = funcRet
                return funcRet
            except AttributeError as e:
                logger.error(f"Default-Funktion nicht gefunden in Modul {module.__name__ if hasattr(module, '__name__') else module}: {e}")
                await update.message.reply_text(
                    'Interner Fehler im Login-Modus.\n',
                    reply_markup=markupList[context.user_data['status']])
                return context.user_data['status']
        if context.user_data['status'] == MAIN:
            # Hauptmenü anzeigen
            await help_command(update, context)
            return context.user_data['status']

        if context.user_data['isAuthenticated'] and context.user_data['status'] != LOGIN:
            funkName=None
            
            # Normale Behandlung für andere Modi (MAIN hat kein Modul)
            # Suche nach FunktionsName ([1:] entfernt / am Anfang der Zeichenkette)
            if hasattr(module, 'tastertur'):
                if textFromUser.startswith('/') and textFromUser[1:] in module.tastertur:
                    funkName=textFromUser[1:]
                    logger.debug(f"Command gefunden: {funkName}")
                # Suche über Button-Beschriftung
                elif textFromUser in module.tastertur.values():
                        for key, value in module.tastertur.items():
                            if value == textFromUser:
                                funkName=key
                                logger.debug(f"Button gefunden: {funkName}")
                                break
            
            if funkName is None:
                logger.debug(f"Keine Funktion gefunden für '{textFromUser}', rufe default auf")
                # Default Funktion versuchen (nur für Nicht-MAIN Modi)
                try:
                    func = getattr(module, 'default')
                    logger.debug(f"Default-Funktion gefunden: {func}")
                    # Korrekte Parameter-Reihenfolge: (update, context, user_data, markupList)
                    funcRet = await func(update, context, context.user_data, markupList)
                    logger.debug(f"Default-Funktion zurückgegeben: {funcRet}")
                    context.user_data['status'] = funcRet
                except AttributeError as e:
                    logger.error(f"Default-Funktion nicht gefunden in Modul {module.__name__ if hasattr(module, '__name__') else module}: {e}")
                    await update.message.reply_text(
                        'Modus: "'+textFromUser+'" wurde leider nicht gefunden.\n'+
                        'Versuche es mal mit /help.\n',
                        reply_markup=markupList[context.user_data['status']])
            else:
                logger.debug(f"Funktion {funkName} wird aufgerufen")
                # Normale Funktionsausführung für andere Modi
                if str(context.user_data['chatId']) not in [str(id) for id in config.get_admin_chat_ids()]:
                    admin_ids = config.get_admin_chat_ids()
                    for admin_id in admin_ids:
                        try:
                            await retry_telegram_call(
                                context.bot.send_message,
                                admin_id,
                                text=context.user_data['firstname']+" hat Funktion "+str(module.__name__ if hasattr(module, '__name__') else module)+"."+funkName+" aufgerufen."
                            )
                        except Exception as e:
                            logger.warning(f"Konnte Admin-Benachrichtigung nicht senden an {admin_id}: {e}")
                
                logger.debug(f"Suche Methode {funkName} in Modul {module}")
                logger.debug(f"Modul hat {funkName}: {hasattr(module, funkName)}")
                func = getattr(module, str(funkName))
                logger.debug(f"Funktion {funkName} gefunden: {func}")
                # Korrekte Parameter-Reihenfolge: (update, context, user_data, markupList)
                funcRet = await func(update, context, context.user_data, markupList)
                logger.debug(f"Funktion {funkName} zurückgegeben: {funcRet}")
                context.user_data['status'] = funcRet
    return context.user_data['status']

async def send_admin_notifications(context, notifications):
    """Sendet Benachrichtigungen an alle Admins"""
    from lib.config import Config
    config = Config()
    admin_ids = config.get_admin_chat_ids()
    
    if not admin_ids:
        logger.warning("Keine Admin-Chat-IDs konfiguriert")
        return
    
    for notification in notifications:
        message = notification['message']
        for admin_id in admin_ids:
            try:
                await retry_telegram_call(
                    context.bot.send_message,
                    chat_id=admin_id,
                    text=message,
                    parse_mode='Markdown'
                )
                logger.info(f"Admin-Benachrichtigung gesendet an {admin_id}: {notification['type']}")
            except Exception as e:
                logger.error(f"Fehler beim Senden der Admin-Benachrichtigung an {admin_id}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Startfunktion"""
    # Chat-Daten initialisieren
    initializeChatData(update.message, context.user_data)
    
    await update.message.reply_text(
        f"Hi {update.message.from_user.first_name}! "
    )
    
    # Authentifizierung prüfen
    await checkAuthentifizierung(update, context.user_data)
    
    if context.user_data['isAuthenticated']:
        await update.message.reply_text("Willkommen zurück ;P",
            reply_markup=markupList[context.user_data['status']])
        return context.user_data['status']
    else:
        await update.message.reply_text(
            "Bitte melde dich mit dem Passwort an um fortzufahren:",
            reply_markup=markupList[LOGIN]
        )
        return LOGIN

async def switchToAdminModus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wechsel zum Admin-Modus"""
    admin_ids = config.get_admin_chat_ids()
    logger.debug(f"switchToAdminModus aufgerufen - chatId: {context.user_data.get('chatId')}, admin_chat_ids: {admin_ids}")
    
    if str(context.user_data['chatId']) in [str(id) for id in admin_ids]:
        # Admin-Tastatur aus config.py verwenden
        from lib.config import getMarkupList
        
        context.user_data['keyboard'] = getMarkupList(ADMIN)
        context.user_data['status'] = ADMIN
        logger.debug(f"Status gesetzt auf ADMIN ({ADMIN})")
        await update.message.reply_text("-->ADMINMODE<--",
                                  reply_markup=context.user_data['keyboard'])
        logger.debug(f"Rückgabe Status: {context.user_data['status']}")
        return context.user_data['status']
    else:
        await update.message.reply_text('Sorry, du hast leider keine Admin-Rechte.')
        return context.user_data.get('status', MAIN)

async def switchToLichtModus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wechsel zum Licht-Modus"""
    from lib.config import getMarkupList
    
    context.user_data['keyboard'] = getMarkupList(LIGHT)
    context.user_data['status'] = LIGHT
    logger.debug(f"Status gesetzt auf LIGHT ({LIGHT})")
    await retry_telegram_call(
        update.message.reply_text,
        "💡 -->LICHTMODE<--",
        reply_markup=context.user_data['keyboard']
    )
    logger.debug(f"Rückgabe Status: {context.user_data['status']}")
    return context.user_data['status']

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zeigt Hilfe mit allen verfügbaren Befehlen"""
    # Debug: Logge den Aufruf
    logger.info(f"help_command aufgerufen für Status: {context.user_data.get('status', MAIN)}")
    
    help_text = """Nutze das Keyboard für Standard-Aktionen.
Weitere Funktionen:"""
    help_text += "\n- /help zeigt diesen Text an"
    if str(context.user_data['chatId']) in [str(id) for id in config.get_admin_chat_ids()]:
        help_text += "\n- /admin aktiviert den Admin-Modus"
    
    # Textbefehle für aktuellen Status anzeigen
    current_status = context.user_data.get('status', MAIN)
    
    if current_status == MAIN:
        # MAIN-Status hat keine Klasse, aber unsere main_textbefehl Map
        for key, value in main_textbefehl.items():
            help_text += f'\n- /{key} {value}'
    else:
        # Andere Modi haben Klassen mit textbefehl Maps
        try:
            if modeList[current_status] is not None:
                logger.debug(f"Suche textbefehl in modeList[{current_status}]")
                for key, value in modeList[current_status].textbefehl.items():
                    help_text += f'\n- /{key} {value}'
                    logger.debug(f"Gefunden: {key} = {value}")
        except (KeyError, AttributeError, IndexError) as e:
            # Fallback falls etwas schief geht
            logger.error(f"Fehler in help_command: {e}")
            help_text += f'\n- Status {current_status}: Keine Hilfe verfügbar'
    
    help_text += "\n \nInvalide Angaben führen zu dieser Ausgabe. Wande dich bei weitern Fragen an den Administrator."
    
    logger.debug(f"Sende Hilfe-Text: {help_text[:100]}...")
    await update.message.reply_text(help_text)

async def async_main():
    """Asynchronous main function"""
    # Prüfen ob Telegram-Module verfügbar sind
    if not TELEGRAM_AVAILABLE or not TELEGRAM_EXT_AVAILABLE:
        logging.error("Telegram-Module nicht verfügbar - Bot kann nicht gestartet werden")
        return
    
    token = config.get_telegram_token()
    if not token:
        logging.error("Bot-Token nicht in config.json gefunden!")
        return
    
    application = Application.builder().token(token).build()
    
    autoStatesHandler={
            MAIN: [
                MessageHandler(filters.Regex('^(Temp\\.-Verlauf)$'), lambda update, context: StatistikModeOptimized.temp_history(update, context, context.user_data, markupList)),
                CommandHandler('temp_history', lambda update, context: StatistikModeOptimized.temp_history(update, context, context.user_data, markupList)),
                MessageHandler(filters.Regex('^(Einstellungen)$'), lambda update, context: SettingsMode.default(update, context, context.user_data, markupList)),
                CommandHandler('einstellungen',  lambda update, context: SettingsMode.default(update, context, context.user_data, markupList)),
                MessageHandler(filters.Regex('^(Licht)$'), lambda update, context: switchToLichtModus(update, context)),
                CommandHandler('licht', lambda update, context: switchToLichtModus(update, context)),
                MessageHandler(filters.Regex('^(Logout)$'), done),
                CommandHandler('logout', done),
            ] if TELEGRAM_AVAILABLE and TELEGRAM_EXT_AVAILABLE else []
        }
    
    
    for x in range(len(modeList)):
        
        #Gegen none testen
        if modeList[x] is not None:
            autoStates=[]
            module = modeList[x]
            if hasattr(module, 'tastertur'):
                for value in module.tastertur.values():
                    regex_pattern = '^'+str(value)+'$'
                    autoStates.extend([MessageHandler(filters.Regex(regex_pattern),
                                        selectModeFunc)])
            if hasattr(module, 'textbefehl'):
                for key in module.textbefehl.keys():
                    autoStates.extend([CommandHandler(str(key),
                                        selectModeFunc)])
            # Admin-Command auch zu Admin-States hinzufügen
            if x == ADMIN:
                autoStates.extend([CommandHandler("admin", switchToAdminModus)])
            #selectModeFunc nur für Modi mit Modulen registrieren (nicht für MAIN)
            autoStates.extend([MessageHandler(filters.TEXT & ~filters.COMMAND, selectModeFunc)])
            autoStatesHandler[x]=autoStates

    
    # ConversationHandler für die Zustandsverwaltung
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start),MessageHandler(filters.TEXT, start)],
        states=autoStatesHandler,
        fallbacks=[CommandHandler("admin", switchToAdminModus), CommandHandler("logout", done)],  # admin zu fallbacks hinzugefügt
    )
    
    application.add_handler(conv_handler)
    
    # Status command handler
    application.add_handler(CommandHandler("status", lambda update, context: StatistikModeOptimized.default(update, context, context.user_data, markupList)))
    
    # Help command handler
    application.add_handler(CommandHandler("help", help_command))
    
    # Help command als Fallback für unbekannte Befehle (nach Admin-Handler)
    # NUR für Commands, nicht für Button-Texte
    application.add_handler(MessageHandler(filters.COMMAND & ~filters.Regex(r'^(start|help|admin|logout|heizung|automation|einstellungen|status|licht)$'), help_command))
    
    # Callback handler für Inline-Keyboards
    logger.debug("Registriere Callback-Handler...")
    
    # Dynamische Callback-Handler registrieren
    callback_configs = [
        (SETTINGS, SettingsMode),
        (ADMIN, AdminMode),
        (LIGHT, LichtMode)
    ]
    
    for mode, module in callback_configs:
        if hasattr(module, 'get_callback_handlers'):
            callback_config = module.get_callback_handlers()
            handler = callback_config['handler']
            patterns = callback_config['patterns']
            logger.info(f"Registriere Callback-Handler für {module.__name__}: {patterns}")
            for pattern in patterns:
                application.add_handler(CallbackQueryHandler(
                    lambda update, context, h=handler: h(update, context, context.user_data, markupList), 
                    pattern=pattern
                ))
                logger.debug(f"Callback-Handler registriert für Pattern: {pattern}")
        else:
            logger.info(f"Keine Callback-Handler für {module.__name__} gefunden")
    
    logging.info("Bot wird gestartet...")
    
    # Timer für expire-Benachrichtigungen
    async def expire_notification_timer():
        """Timer für regelmäßige expire-Benachrichtigungen"""
        import asyncio
        while True:
            try:
                # Alle 6 Stunden prüfen
                await asyncio.sleep(6 * 3600)
                
                # Benachrichtigungen prüfen und senden
                notifications = db.check_expire_notifications()
                if notifications:
                    await send_admin_notifications(application, notifications)
                    
            except Exception as e:
                logger.error(f"Fehler im expire-notification timer: {e}")
    
    # Start the bot with shutdown handling
    async with application:
        await application.initialize()
        await application.start()
        
        # Timer starten
        import asyncio
        timer_task = asyncio.create_task(expire_notification_timer())
        
        await application.updater.start_polling()
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
        logging.info("Bot wird heruntergefahren...")
        timer_task.cancel()
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def main():
    """Hauptfunktion"""
    # CLI-Argumente parsen
    parser = argparse.ArgumentParser(description='Telegram FritzDECT Bot')
    parser.add_argument('-c', '--config', 
                       default='config.json',
                       help='Pfad zur Konfigurationsdatei (Standard: config.json)')
    args = parser.parse_args()
    
    # Konfiguration mit übergebenem Pfad initialisieren
    global config, db
    config = Config(args.config)
    
    # UserDatabase nach config-Initialisierung erstellen
    db = UserDatabase()
    
    # LoginMode die globale Datenbank-Instanz setzen
    LoginMode.set_database(db)
    # AdminMode die globale Datenbank- und Config-Instanz setzen
    AdminMode.set_database(db)
    AdminMode.set_config(config)
    # SettingsMode die globale Datenbank-Instanz setzen
    from lib.settingsMode import set_database as settings_set_database
    settings_set_database(db)
    
    # Logging und FritzBox nach config-Initialisierung
    if TELEGRAM_AVAILABLE and TELEGRAM_EXT_AVAILABLE:
        init_logging()
        
        logger.info("=== Bot gestartet - Logging aktiviert ===")
        logger.info(f"Logging-Level: {config.get('logging.level')}")
        debug_logger.info("=== DEBUG LOG START ===")
        debug_logger.debug("TEST DEBUG MESSAGE")
        logging.info("DEBUG LOGGER AKTIVIERT - debug.log wird geschrieben")
        logging.debug("TEST DEBUG MESSAGE GESCHRIEBEN")
    
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logging.warning("Bot beendet.")
    except Exception as e:
        logging.error(f"Fehler: {e}")

if __name__ == '__main__':
    main()