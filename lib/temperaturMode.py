# Telegram Importe mit Fallback für Tests
try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    TELEGRAM_AVAILABLE = True
except ImportError:
    InlineKeyboardButton = None
    InlineKeyboardMarkup = None
    TELEGRAM_AVAILABLE = False
    print("WARNING: telegram module nicht gefunden - TemperaturMode läuft im Test-Modus")

import os
import importlib.util
import sys
import datetime as DT
import logging

logger = logging.getLogger(__name__)

def load_module(name, filepath):
    """Load a module from file path using importlib"""
    spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(__file__), filepath))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load configuration and database modules
config_module = load_module("config", "config.py")
user_database_module = load_module("user_database", "user_database.py")
temp_database_module = load_module("tempDatabaseLib", "tempDatabaseLib.py")
dwd_data_module = load_module("dwdDataLib", "dwdDataLib.py")

# Importiere Konstanten
from lib.config import TEMPERATUR, MAIN

# Globale Datenbank-Instanzen
db = None
temp_db = None

def set_database(database_instance):
    """Setzt die globale Datenbank-Instanz"""
    global db
    db = database_instance

def set_temp_database(database_instance):
    """Setzt die globale Temperatur-Datenbank-Instanz"""
    global temp_db
    temp_db = database_instance


def get_callback_handlers():
    """Gibt die Callback-Handler-Konfiguration für TemperaturMode zurück"""
    return {
        'handler': handle_temperatur_callback,
        'patterns': [
            r'temp_plot_.*',
            r'temp_days_.*',
            r'mold_mode_.*',
            r'mold_info',
            r'weather_forecast_.*',
            r'back_to_temperatur_.*'
        ]
    }


# Funktionen hier registrieren für Temperatur-Mode
# Funktionen Map{ Funk-Name: Tastertur beschriftung}
tastertur = {
    'show_plot': 'Temperatur-Verlauf',
    'weather_forecast': 'Wetter-Vorhersage',
    'mold_warning': 'Schimmel-Warnung',
    'back': 'Zurück'
}

# Funktionen Map{Funk-Name, Beschreiung in Help}
textbefehl = {
    'show_plot': 'Zeigt den Temperatur-Verlauf als Graph',
    'weather_forecast': 'Zeigt die Wetter-Vorhersage für die nächsten 7 Tage',
    'mold_warning': 'Aktiviert/Deaktiviert Schimmel-Warnungen',
    'back': 'Wechselt zurück ins Main-Menu'
}


async def default(update, context, user_data, markupList):
    """Default-Funktion für Temperatur-Mode"""
    context.user_data['keyboard'] = markupList[TEMPERATUR]
    context.user_data['status'] = TEMPERATUR
    
    await update.message.reply_text(
        "-->TEMPERATURMODE<--\n\n"
        "🌡️ Verfügbare Funktionen:\n"
        "• Temperatur-Verlauf als Graph anzeigen\n"
        "• Wetter-Vorhersage für die nächsten 7 Tage\n"
        "• Schimmel-Warnung konfigurieren\n"
        "• Zurück zum Hauptmenü\n\n"
        "💡 Nutze /help für alle Befehle",
        reply_markup=markupList[TEMPERATUR]
    )
    return context.user_data['status']


async def show_plot(update, context, user_data, markupList):
    """Zeigt Temperatur-Verlauf mit verschiedenen Zeiträumen"""
    global temp_db
    if temp_db is None:
        await update.message.reply_text("❌ Temperatur-Datenbank nicht verfügbar. Bitte kontaktiere den Admin.")
        return user_data['status']
    
    try:
        # Inline-Keyboard für Zeiträume
        keyboard = [
            [InlineKeyboardButton("📊 Letzte 24 Stunden", callback_data='temp_days_1'),
             InlineKeyboardButton("📈 Letzte 3 Tage", callback_data='temp_days_3')],
            [InlineKeyboardButton("📉 Letzte 7 Tage", callback_data='temp_days_7'),
             InlineKeyboardButton("📅 Letzte 14 Tage", callback_data='temp_days_14')],
            [InlineKeyboardButton("🔙 Zurück", callback_data='back_to_temperatur_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📊 **Temperatur-Verlauf**\n\n"
            "Wähle den Zeitraum für den Graph:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Fehler in show_plot: {e}")
        await update.message.reply_text(f"❌ Fehler: {str(e)}", reply_markup=user_data['keyboard'])
    
    return user_data['status']


async def generate_temp_plot(days, show_mold_warning=False):
    """Generiert den Temperatur-Plot für die angegebenen Tage"""
    global temp_db
    if temp_db is None:
        return None
    
    try:
        import matplotlib.pyplot as plt
        
        werte = temp_db.getValues(days)
        
        if not werte:
            return None
        
        # Daten extrahieren
        s = []
        h = []
        dwds = []
        dwdh = []
        dates = []
        
        for y in range(len(werte)):
            s.append(werte[y]['temp'])
            h.append(werte[y]['hum'])
            dwds.append(werte[y]['dwdtemp'])
            dwdh.append(werte[y]['dwdhum'])
            dates.append(DT.datetime.strptime(werte[y]['datetime'], "%Y-%m-%d %H:%M:%S"))
        
        # Plot erstellen
        plt.clf()
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Temperatur-Linien
        ax.plot_date(dates, s, linestyle='-', label='Raumtemperatur (°C)', linewidth=2, color='red')
        ax.plot_date(dates, dwds, linestyle='--', label='DWD Temperatur (°C)', linewidth=2, color='blue')
        
        # Luftfeuchtigkeit-Linien
        ax2 = ax.twinx()
        ax2.plot_date(dates, h, linestyle=':', label='Raumfeuchte (%)', linewidth=2, color='green')
        ax2.plot_date(dates, dwdh, linestyle='-.', label='DWD Feuchte (%)', linewidth=2, color='orange')
        
        # Schimmel-Warnung anzeigen
        if show_mold_warning:
            mold_risk_periods = []
            in_risk = False
            risk_start = None
            
            for i in range(len(s)):
                temp = s[i]
                hum = h[i]
                
                # Schimmelrisiko prüfen
                if (temp > 20 and hum > 55) or (temp > 16 and hum > 60):
                    if not in_risk:
                        in_risk = True
                        risk_start = dates[i]
                else:
                    if in_risk:
                        in_risk = False
                        mold_risk_periods.append((risk_start, dates[i]))
            
            # Letzten Risikobereich hinzufügen
            if in_risk:
                mold_risk_periods.append((risk_start, dates[-1]))
            
            # Schimmelrisiko-Bereiche markieren
            for start, end in mold_risk_periods:
                ax.axvspan(start, end, alpha=0.3, color='red', label='Schimmelrisiko')
        
        # Achsen beschriften
        ax.set_xlabel('Zeit')
        ax.set_ylabel('Temperatur (°C)', color='red')
        ax2.set_ylabel('Luftfeuchtigkeit (%)', color='green')
        
        # Tick-Farben
        ax.tick_params(axis='y', labelcolor='red')
        ax2.tick_params(axis='y', labelcolor='green')
        
        # Datum-Formatierung
        from matplotlib.dates import DateFormatter
        formatter = DateFormatter('%Y-%m-%d %H:%M')
        ax.xaxis.set_major_formatter(formatter)
        fig.autofmt_xdate(rotation=45)
        
        # Legende
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        # Titel
        title = f'Temperatur- und Luftfeuchtigkeitsverlauf ({days} Tage)'
        if show_mold_warning:
            title += ' - Mit Schimmelrisiko-Anzeige'
        ax.set_title(title)
        
        # Grid
        ax.grid(True, alpha=0.3)
        
        # Speichern
        plot_file = '/tmp/temp_plot.png'
        fig.savefig(plot_file, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        return plot_file
        
    except Exception as e:
        logger.error(f"Fehler beim Generieren des Plots: {e}")
        return None


async def weather_forecast(update, context, user_data, markupList):
    """Zeigt Wetter-Vorhersage für die nächsten 7 Tage und heute"""
    try:
        from lib.dwdDataLib import DWDData
        
        dwd = DWDData()
        current_data = dwd.getValues()
        
        if not current_data:
            await update.message.reply_text(
                "❌ Konnte keine Wetterdaten abrufen.",
                reply_markup=user_data['keyboard']
            )
            return user_data['status']
        
        from lib.config import Config
        config = Config()
        temp_key = config.get_dwd_temp_key()
        hum_key = config.get_dwd_humidity_key()
        
        current_temp = current_data.get(temp_key, 'N/A')
        current_hum = current_data.get(hum_key, 'N/A')
        
        # Inline-Keyboard für Vorhersage-Optionen
        keyboard = [
            [InlineKeyboardButton("🌡️ Aktuelles Wetter", callback_data='weather_forecast_current'),
             InlineKeyboardButton("📅 7-Tage Vorhersage", callback_data='weather_forecast_7days')],
            [InlineKeyboardButton("🔙 Zurück", callback_data='back_to_temperatur_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🌤️ **Wetter-Übersicht**\n\n"
            f"📍 Aktuelle Werte:\n"
            f"🌡️ Temperatur: {current_temp}°C\n"
            f"💧 Luftfeuchtigkeit: {current_hum}%\n\n"
            f"Wähle eine Option für mehr Details:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Fehler in weather_forecast: {e}")
        await update.message.reply_text(f"❌ Fehler: {str(e)}", reply_markup=user_data['keyboard'])
    
    return user_data['status']


async def mold_warning(update, context, user_data, markupList):
    """Zeigt und konfiguriert Schimmel-Warnung-Einstellungen"""
    global db
    if db is None:
        await update.message.reply_text("❌ Datenbank nicht verfügbar. Bitte kontaktiere den Admin.")
        return user_data['status']
    
    try:
        chat_id = int(user_data['chatId'])
        current_mode = db.get_mold_warning_notification_mode(chat_id)
        
        # Inline-Keyboard für Schimmel-Warnung
        mode_text = {'none': '🔕 Aus', 'silent': '🔔 Leise', 'push': '📱 Push'}.get(current_mode, '🔕 Aus')
        
        keyboard = [
            [InlineKeyboardButton(f"📢 Benachrichtigung: {mode_text}", 
                                callback_data=f'mold_mode_{chat_id}')],
            [InlineKeyboardButton("ℹ️ Info zu Schimmelrisiko", callback_data='mold_info')],
            [InlineKeyboardButton("🔙 Zurück", callback_data='back_to_temperatur_main')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🦠 **Schimmel-Warnung**\n\n"
            f"Benachrichtigung: {mode_text}\n\n"
            "Die Schimmel-Warnung warnt dich, wenn:\n"
            "• Temperatur > 20°C und Luftfeuchtigkeit > 55%\n"
            "• Temperatur > 16°C und Luftfeuchtigkeit > 60%\n\n"
            "Diese Bedingungen begünstigen Schimmelbildung.",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Fehler in mold_warning: {e}")
        await update.message.reply_text(f"❌ Fehler: {str(e)}", reply_markup=user_data['keyboard'])
    
    return user_data['status']


async def back(update, context, user_data, markupList):
    """Wechselt zurück ins Main-Menu"""
    user_data['keyboard'] = markupList[MAIN]
    user_data['status'] = MAIN
    await update.message.reply_text(
        "🔙 Zurück zum Hauptmenü",
        reply_markup=markupList[MAIN]
    )
    return MAIN


async def handle_temperatur_callback(update, context, user_data, markupList):
    """Verarbeitet Callbacks von Inline-Buttons im Temperatur-Mode"""
    global db, temp_db
    if db is None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("❌ Datenbank nicht verfügbar")
        return user_data['status']
    
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = update.effective_user.id
    
    try:
        if callback_data.startswith('temp_days_'):
            # Temperatur-Plot für bestimmte Anzahl Tage
            days = int(callback_data.split('_')[-1])
            
            # Schimmel-Warnung-Einstellung prüfen (aktiv wenn nicht 'none')
            try:
                mold_mode = db.get_mold_warning_notification_mode(user_id)
                show_mold = mold_mode != 'none'
            except Exception as e:
                logger.error(f"Fehler beim Abrufen der Schimmel-Warnung-Einstellung: {e}")
                show_mold = False
            
            # Plot generieren
            plot_file = await generate_temp_plot(days, show_mold)
            
            if plot_file and os.path.exists(plot_file):
                await query.edit_message_text(
                    f"📊 Temperatur-Verlauf der letzten {days} Tage\n"
                    f"{'🦠 Schimmelrisiko-Anzeige aktiv' if show_mold else ''}"
                )
                # Foto senden
                if query.message:
                    await query.message.reply_photo(photo=open(plot_file, 'rb'))
            else:
                await query.edit_message_text(
                    "❌ Konnte keinen Plot generieren. Keine Daten verfügbar."
                )
        
        elif callback_data.startswith('mold_mode_'):
            # Schimmel-Warnung Benachrichtigungsmodus umschalten
            try:
                current_mode = db.get_mold_warning_notification_mode(user_id)
            except Exception as e:
                logger.error(f"Fehler beim Abrufen des aktuellen Modus: {e}")
                current_mode = 'none'
            
            modes = ['none', 'silent', 'push']
            current_index = modes.index(current_mode) if current_mode in modes else 0
            new_mode = modes[(current_index + 1) % len(modes)]
            success = db.update_mold_warning_notification_mode(user_id, new_mode)
            
            if success:
                mode_text = {'none': '🔕 Aus', 'silent': '🔔 Leise', 'push': '📱 Push'}.get(new_mode, '🔕 Aus')
                await query.edit_message_text(
                    f"📢 Benachrichtigung: {mode_text}"
                )
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
        
        elif callback_data == 'mold_info':
            await query.edit_message_text(
                "ℹ️ **Info zu Schimmelrisiko**\n\n"
                "Schimmel entsteht bei:\n"
                "• Hoher Luftfeuchtigkeit (>60%)\n"
                "• Milden Temperaturen (>16°C)\n\n"
                "Vorbeugung:\n"
                "• Regelmäßiges Lüften\n"
                "• Heizung nicht ganz abdrehen\n"
                "• Feuchtequellen vermeiden"
            )
        
        elif callback_data == 'weather_forecast_current':
            # Aktuelles Wetter anzeigen
            from lib.dwdDataLib import DWDData
            from lib.config import Config
            
            dwd = DWDData()
            current_data = dwd.getValues()
            config = Config()
            temp_key = config.get_dwd_temp_key()
            hum_key = config.get_dwd_humidity_key()
            
            await query.edit_message_text(
                f"🌤️ **Aktuelles Wetter**\n\n"
                f"🌡️ Temperatur: {current_data.get(temp_key, 'N/A')}°C\n"
                f"💧 Luftfeuchtigkeit: {current_data.get(hum_key, 'N/A')}%\n"
                f"📍 Quelle: DWD (Deutscher Wetterdienst)"
            )
        
        elif callback_data == 'weather_forecast_7days':
            # 7-Tage Vorhersage (Platzhalter - DWD API erweitern für Vorhersage)
            await query.edit_message_text(
                "📅 **7-Tage Vorhersage**\n\n"
                "⚠️ Diese Funktion erfordert eine Erweiterung der DWD-API.\n"
                "Aktuell werden nur Echtzeit-Daten vom DWD abgerufen.\n\n"
                "Für eine 7-Tage Vorhersage müsste die DWD-Vorhersage-API "
                "integriert werden (z.B. MOSMIX oder ICON-Modell)."
            )
        
        elif callback_data == 'back_to_temperatur_main':
            # Zurück zum Hauptmenü
            from lib.config import reply_keyboard_main
            user_data['keyboard'] = reply_keyboard_main
            user_data['status'] = MAIN
            await query.edit_message_text("🔙 Zurück zum Hauptmenü")
        
    except Exception as e:
        logger.error(f"Fehler in Callback-Handler: {e}")
        await query.edit_message_text(f"❌ Fehler: {str(e)}")
    
    return user_data['status']


# Klasse für Kompatibilität mit fritzdect_bot.py
class TemperaturMode:
    """Wrapper-Klasse für Kompatibilität mit dem Bot-Framework"""
    
    # Tastatur-Befehle und Textbefehle für Kompatibilität
    tastertur = tastertur
    textbefehl = textbefehl
    
    @staticmethod
    async def default(update, context, user_data, markupList):
        """Default-Funktion - delegiert zur globalen Funktion"""
        return await default(update, context, user_data, markupList)
    
    @staticmethod
    async def show_plot(update, context, user_data, markupList):
        """Temperatur-Verlauf - delegiert zur globalen Funktion"""
        return await show_plot(update, context, user_data, markupList)
    
    @staticmethod
    async def weather_forecast(update, context, user_data, markupList):
        """Wetter-Vorhersage - delegiert zur globalen Funktion"""
        return await weather_forecast(update, context, user_data, markupList)
    
    @staticmethod
    async def mold_warning(update, context, user_data, markupList):
        """Schimmel-Warnung - delegiert zur globalen Funktion"""
        return await mold_warning(update, context, user_data, markupList)
    
    @staticmethod
    async def back(update, context, user_data, markupList):
        """Zurück - delegiert zur globalen Funktion"""
        return await back(update, context, user_data, markupList)
    
    @staticmethod
    def get_callback_handlers():
        """Gibt Callback-Handler für Inline-Keyboards zurück"""
        return get_callback_handlers()
    
    @staticmethod
    async def handle_temperatur_callback(update, context, user_data, markupList):
        """Handler für Temperatur-Callbacks - delegiert zur globalen Funktion"""
        return await handle_temperatur_callback(update, context, user_data, markupList)
