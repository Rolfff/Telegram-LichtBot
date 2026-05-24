#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Telegram Importe mit Fallback für Tests
try:
    from telegram import Update
    from telegram.ext import ConversationHandler
    TELEGRAM_AVAILABLE = True
except ImportError:
    Update = None
    ConversationHandler = None
    TELEGRAM_AVAILABLE = False
    logging.warning("telegram module nicht gefunden - LoginMode läuft im Test-Modus")

try:
    import os
except ImportError:
    logging.warning("os module nicht gefunden")
    os = None

try:
    import importlib.util
except ImportError:
    logging.warning("importlib.util module nicht gefunden")
    importlib = None

try:
    import sys
except ImportError:
    logging.warning("sys module nicht gefunden")
    sys = None

try:
    import logging
    logger = logging.getLogger(__name__)
except ImportError:
    logging.warning("logging module nicht gefunden")
    logging = None

def load_module(name, filepath):
    """Load a module from file path using importlib"""
    if importlib is not None and os is not None and sys is not None:
        spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), filepath))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    else:
        logging.warning("load_module nicht möglich - benötigte Module nicht gefunden")
        return None

# Load configuration and database modules
config_module = load_module("config", "config.py")
config = config_module.Config()
user_database_module = load_module("user_database", "user_database.py")

# Import Konstanten aus config
LOGIN, MAIN, ADMIN = config_module.LOGIN, config_module.MAIN, config_module.ADMIN

# Globale Variable für Datenbank - wird von fritzdect_bot.py gesetzt
db = None

def set_database(database_instance):
    """Setzt die globale Datenbank-Instanz"""
    global db
    db = database_instance


# Funktionen hier registrieren für Admin-Mode
# Funktionen Map{ Funk-Name: Tastertur beschriftung}
tastertur = {'login': 'Login',
         'bye': 'Bye'}

# Funktionen Map{Funk-Name, Beschreiung in Help}
textbefehl = {'login': 'Um alle Funktionen zu nutzen, musst du dich einloggen',
         'bye': 'Schließt die aktuelle Sitzung'}

async def default(update, context, user_data, markupList):
    return await login(update, context, user_data, markupList)

async def login(update, context, user_data, markupList):
    """Login-Verarbeitung"""
    global db
    if db is None:
        await update.message.reply_text("❌ Datenbank nicht verfügbar. Bitte kontaktiere den Admin.")
        return LOGIN
    
    # User-Informationen initialisieren falls noch nicht vorhanden
    if 'firstname' not in user_data:
        user_data['firstname'] = update.effective_user.first_name if hasattr(update.effective_user, 'first_name') else ''
    if 'lastname' not in user_data:
        user_data['lastname'] = update.effective_user.last_name if hasattr(update.effective_user, 'last_name') else ''
    
    password = update.message.text
    chat_id = update.effective_chat.id
    
    # Prüfen ob Benutzer geblockt ist
    if db.is_user_blocked(chat_id):
        block_days = config.get_block_duration_days()
        await update.message.reply_text(
            f"Du bist für {block_days} Tage geblockt wegen zu vieler fehlgeschlagener Login-Versuche."
        )
        await bye(update, user_data, markupList)
        return LOGIN

    if password == "Login" or password == "/login":
        # Keyboard setzen falls noch nicht vorhanden
        if 'keyboard' not in user_data:
            user_data['keyboard'] = markupList[LOGIN]
        await update.message.reply_text(
            "Bitte gib dein Passwort ein",
            reply_markup=user_data['keyboard']
        )
        return user_data['status']  # Bleibt im LOGIN-Status
    
    if password == config.get_telegram_password():
        # Erfolgreicher Login - fehlgeschlagene Versuche zurücksetzen
        db.reset_failed_attempts(chat_id)
        
        # User-Informationen aus Update extrahieren
        firstname = update.effective_user.first_name if hasattr(update.effective_user, 'first_name') else ''
        lastname = update.effective_user.last_name if hasattr(update.effective_user, 'last_name') else ''
        
        # user_data aktualisieren
        user_data['firstname'] = firstname
        user_data['lastname'] = lastname
        
        if str(chat_id) in [str(id) for id in config.get_admin_chat_ids()]:
            # Sprache des Users ermitteln
            user_language = update.effective_user.language_code if hasattr(update.effective_user, 'language_code') else 'en'
            db.add_user(chat_id, firstname, lastname, is_admin=1, language_code=user_language)
            await update.message.reply_text(
                "Admin-Login erfolgreich!",
                reply_markup= markupList[MAIN]
            )
            # Wichtig: Status auf MAIN setzen bei Admin-Login
            user_data['status'] = MAIN
            return MAIN
        else:
            # Sprache des Users ermitteln
            user_language = update.effective_user.language_code if hasattr(update.effective_user, 'language_code') else 'en'
            db.add_user(chat_id, firstname, lastname, language_code=user_language)
            await update.message.reply_text(
                "Login erfolgreich! Warte auf Admin-Freigabe...",
                reply_markup= markupList[LOGIN]
            )
            try:
                admin_ids = config.get_admin_chat_ids()
                for admin_id in admin_ids:
                    try:
                        await context.bot.send_message(
                            admin_id,
                            text=f'🔐 Zugriffsanfrage: {user_data["firstname"]} {user_data["lastname"]} (ID: {chat_id}) möchte den Bot nutzen.\n\n'
                            f'Antworte mit /admin um den Zugriff zu gewähren.'
                        )
                    except Exception as e:
                        logging.error(f"Failed to notify admin {admin_id}: {e}")
                await context.bot.send_message(chat_id,
                    text='✅ Anfrage an Admin gesendet. Du wirst benachrichtigt, sobald der Zugriff freigegeben wurde.')
            except Exception as e:
                logging.error(f"Failed to notify admin: {e}")
                await context.bot.send_message(chat_id,
                    text='❌ Der Admin konnte nicht benachrichtigt werden. Bitte versuche es später erneut.')
        
        # Wichtig: Status auf LOGIN setzen bei erfolgreichem Login (nicht-Admin)
        user_data['status'] = LOGIN
        return LOGIN 
    else:
        # Fehlgeschlagener Login-Versuch aufzeichnen und erneut nach Passwort fragen
        logging.debug(f"Fehlgeschlagener Login-Versuch für Chat-ID {chat_id}")
        is_blocked = db.record_failed_attempt(chat_id)
        max_attempts = config.get_max_failed_attempts()
        remaining_attempts = max_attempts - db.get_failed_attempts(chat_id)
        
        logging.debug(f"is_blocked={is_blocked}, remaining_attempts={remaining_attempts}")
        
        if is_blocked:
            block_days = config.get_block_duration_days()
            await update.message.reply_text(
                f"Zu viele fehlgeschlagene Login-Versuche! Du bist für {block_days} Tage geblockt."
            )
        else:
            await update.message.reply_text(
                f"❌ Falsches Passwort!\n"
                f"🔢 Verbleibende Versuche: {remaining_attempts}\n"
                f"🔑 Bitte gib dein Passwort erneut ein:"
            )
        
        # Wichtig: Status auf LOGIN setzen um Modus-Suche zu vermeiden
        user_data['status'] = LOGIN
        return LOGIN

async def bye(update, user_data, markupList):
    """Beendet die Konversation"""
    if 'isAuthenticated' in user_data:
        del user_data['isAuthenticated']
        del user_data['status']
        del user_data['keyboard'] 

    await update.message.reply_text("bye")
    
    user_data.clear()
    return ConversationHandler.END

