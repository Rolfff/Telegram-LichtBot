# Telegram Importe mit Fallback für Tests
try:
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    TELEGRAM_AVAILABLE = True
except ImportError:
    InlineKeyboardButton = None
    InlineKeyboardMarkup = None
    TELEGRAM_AVAILABLE = False
    print("WARNING: telegram module nicht gefunden - SettingsMode läuft im Test-Modus")

import os
import importlib.util
import sys
import datetime as DT


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

# Importiere Konstanten
from lib.config import SETTINGS, MAIN

# Globale Datenbank-Instanz
db = None

def set_database(database_instance):
    """Setzt die globale Datenbank-Instanz"""
    global db
    db = database_instance


def get_callback_handlers():
    """Gibt die Callback-Handler-Konfiguration für SettingsMode zurück"""
    return {
        'handler': handle_settings_callback,
        'patterns': [
            r'set_language_.*',
            r'select_vacation_.*',
            r'select_power_.*',
            r'select_door_.*',
            r'select_temperature_.*',
            r'select_burglar_.*',
            r'set_notifyVacationMode_.*',
            r'set_notifyDoorPowerMeter_.*',
            r'set_notifyDoorFrontDoor_.*',
            r'set_notifyTemperatureWarning_.*',
            r'set_notifyBurglarAlarm_.*',
            r'set_battery_info_.*',
            r'back_to_notifications_.*',
            r'cancel_language_.*',
            r'back_settings_.*'
        ]
    }


# Funktionen hier registrieren für Settings-Mode
# Funktionen Map{ Funk-Name: Tastertur beschriftung}
tastertur = {
    'language': 'Sprache ändern',
    'notifications': 'Benachrichtigungen',
    'back': 'Zurück'
}

# Funktionen Map{Funk-Name, Beschreiung in Help}
textbefehl = {
    'language': 'Ändert die Sprache des Bots',
    'notifications': 'Konfiguriert Benachrichtigungseinstellungen',
    'back': 'Wechselt zurück ins Main-Menu'
}


async def default(update, context, user_data, markupList):
    """Default-Funktion für Settings-Mode"""
    """Wechselt in den Settings-Modus"""
    context.user_data['keyboard'] = markupList[SETTINGS]
    context.user_data['status'] = SETTINGS
    await update.message.reply_text("-->SETTINGSMODE<--\n\n⚙️ Verfügbare Funktionen:\n"
                                  "• Sprache ändern (🇩🇪🇬🇧🇷🇺🇫🇷🇪🇸)\n"
                                  "• Benachrichtigungen konfigurieren\n"
                                  "• Zurück zum Hauptmenü", reply_markup=markupList[SETTINGS])
    return context.user_data['status']


async def language(update, context, user_data, markupList):
    """Zeigt Sprachauswahl mit Inline-Buttons"""
    global db
    if db is None:
        await update.message.reply_text("❌ Datenbank nicht verfügbar. Bitte kontaktiere den Admin.")
        return user_data['status']
    
    try:
        chat_id = int(user_data['chatId'])  # Sicherstellen, dass es ein Integer ist
        current_language = db.get_user_language(chat_id)
        
        # Sprach-Optionen mit Flag-Emojis
        keyboard = [
            [InlineKeyboardButton("🇩🇪 Deutsch", callback_data=f'set_language_de_{chat_id}')],
            [InlineKeyboardButton("🇬🇧 English", callback_data=f'set_language_en_{chat_id}')],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data=f'set_language_ru_{chat_id}')],
            [InlineKeyboardButton("🇫🇷 Français", callback_data=f'set_language_fr_{chat_id}')],
            [InlineKeyboardButton("🇪🇸 Español", callback_data=f'set_language_es_{chat_id}')],
            [InlineKeyboardButton("❌ Abbrechen", callback_data=f'cancel_language_{chat_id}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Aktuelle Sprache anzeigen
        language_names = {
            'de': '🇩🇪 Deutsch',
            'en': '🇬🇧 English', 
            'ru': '🇷🇺 Русский',
            'fr': '🇫🇷 Français',
            'es': '🇪🇸 Español'
        }
        
        current_display = language_names.get(current_language, f"🌐 {current_language.upper()}")
        
        await update.message.reply_text(
            f"🌐 Spracheinstellungen\n\n"
            f"Aktuelle Sprache: {current_display}\n\n"
            f"Wähle eine neue Sprache:",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Fehler: {str(e)}", reply_markup=user_data['keyboard'])
    
    return user_data['status']


async def show_mode_selection(update, context, user_data, notification_type, chat_id):
    """Zeigt die Modus-Auswahl für einen bestimmten Benachrichtigungstyp"""
    global db
    if db is None:
        await update.callback_query.edit_message_text("❌ Datenbank nicht verfügbar.")
        return user_data['status']
    
    try:
        # Aktuelle Einstellung holen
        notification_settings = db.get_notification_settings(chat_id)
        current_mode = notification_settings.get(notification_type, 'push')
        
        # Verfügbare Modi
        available_modes = db.get_notification_modes()
        
        # Keyboard für Modus-Auswahl
        keyboard = []
        
        # Typ-Header
        type_names = {
            'notifyVacationMode': '🏖️ Urlaubsschaltung',
            'notifyDoorPowerMeter': '⚡ Tür-Stromzähler',
            'notifyDoorFrontDoor': '🚪 Haustür',
            'notifyTemperatureWarning': '🌡️ Temperaturwarnung',
            'notifyBurglarAlarm': '🚨 Einbruchalarm'
        }
        
        header_text = type_names.get(notification_type, notification_type)
        keyboard.append([InlineKeyboardButton(header_text, callback_data=f"header_{notification_type}")])
        
        # Modi-Buttons
        for mode_name, mode_info in available_modes.items():
            if mode_name != 'default_mode':
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode_name)
                current_icon = '✅' if mode_name == current_mode else ''
                keyboard.append([InlineKeyboardButton(
                    f"{current_icon} {icon} {desc}", 
                    callback_data=f'set_{notification_type}_{chat_id}_{mode_name}'
                )])
        
        # Zurück-Button
        keyboard.append([InlineKeyboardButton("🔙 Zurück zur Übersicht", callback_data=f'back_to_notifications_{chat_id}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            f"{header_text}\n\n"
            "Wähle deinen gewünschten Benachrichtigungs-Modus:\n\n"
            "✅ = Aktuell eingestellt",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        await update.callback_query.edit_message_text(f"❌ Fehler: {str(e)}")
    
    return user_data['status']


async def notifications(update, context, user_data, markupList):
    """Zeigt Benachrichtigungseinstellungen"""
    global db
    if db is None:
        await update.message.reply_text("❌ Datenbank nicht verfügbar. Bitte kontaktiere den Admin.")
        return user_data['status']
    
    try:
        chat_id = int(user_data['chatId'])  # Sicherstellen, dass es ein Integer ist
        
        # Aktuelle Benachrichtigungseinstellungen holen
        notification_settings = db.get_notification_settings(chat_id)
        
        # Verfügbare Modi aus Config holen
        available_modes = db.get_notification_modes()
        
        if notification_settings:
            vacation_mode = notification_settings.get('notifyVacationMode', 'push')
            door_power_meter = notification_settings.get('notifyDoorPowerMeter', 'push')
            door_front_door = notification_settings.get('notifyDoorFrontDoor', 'push')
            temperature_warning = notification_settings.get('notifyTemperatureWarning', 'push')
            burglar_alarm = notification_settings.get('notifyBurglarAlarm', 'push')
        else:
            # Standardwerte wenn nicht gefunden
            default_mode = db.get_notification_modes().get('default_mode', 'push')
            vacation_mode = door_power_meter = door_front_door = temperature_warning = burglar_alarm = default_mode
        
        
        # Inline-Keyboard für Benachrichtigungstypen-Auswahl
        keyboard = []
        
        # Benachrichtigungstypen mit aktuellen Modi anzeigen
        vacation_icon = available_modes.get(vacation_mode, {}).get('icon', '📱')
        vacation_desc = available_modes.get(vacation_mode, {}).get('description', vacation_mode)
        keyboard.append([InlineKeyboardButton(
            f"🏖️ Urlaubsschaltung: {vacation_icon} {vacation_desc}", 
            callback_data=f'select_vacation_{chat_id}'
        )])
        
        power_icon = available_modes.get(door_power_meter, {}).get('icon', '📱')
        power_desc = available_modes.get(door_power_meter, {}).get('description', door_power_meter)
        keyboard.append([InlineKeyboardButton(
            f"⚡ Tür-Stromzähler: {power_icon} {power_desc}", 
            callback_data=f'select_power_{chat_id}'
        )])
        
        door_icon = available_modes.get(door_front_door, {}).get('icon', '📱')
        door_desc = available_modes.get(door_front_door, {}).get('description', door_front_door)
        keyboard.append([InlineKeyboardButton(
            f"🚪 Haustür: {door_icon} {door_desc}", 
            callback_data=f'select_door_{chat_id}'
        )])
        
        temp_icon = available_modes.get(temperature_warning, {}).get('icon', '📱')
        temp_desc = available_modes.get(temperature_warning, {}).get('description', temperature_warning)
        keyboard.append([InlineKeyboardButton(
            f"🌡️ Temperaturwarnung: {temp_icon} {temp_desc}", 
            callback_data=f'select_temperature_{chat_id}'
        )])
        
        burglar_icon = available_modes.get(burglar_alarm, {}).get('icon', '📱')
        burglar_desc = available_modes.get(burglar_alarm, {}).get('description', burglar_alarm)
        keyboard.append([InlineKeyboardButton(
            f"🚨 Einbruchalarm: {burglar_icon} {burglar_desc}", 
            callback_data=f'select_burglar_{chat_id}'
        )])
        
        # Batterie-Info-Einstellung
        battery_setting = db.get_battery_info_setting(chat_id)
        battery_status = "✅ Immer" if battery_setting else "🔕 Nur bei niedrigem Stand"
        keyboard.append([InlineKeyboardButton(
            f"🔋 Batterie-Info: {battery_status}", 
            callback_data=f'set_battery_info_{chat_id}'
        )])
        
        # Zurück-Button
        keyboard.append([InlineKeyboardButton("🔙 Zurück", callback_data=f'back_settings_{chat_id}')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔔 **Benachrichtigungseinstellungen**\n\n"
            "Wähle für jeden Benachrichtigungstyp deinen gewünschten Modus:\n\n"
            "✅ = Aktuell eingestellt\n"
            "🔕 Keine Benachrichtigung\n"
            "🔔 Stille Benachrichtigung\n"
            "📱 Push-Nachricht\n",
            reply_markup=reply_markup
        )
        
    except Exception as e:
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





async def handle_settings_callback(update, context, user_data, markupList):
    """Verarbeitet Callbacks von Inline-Buttons im Settings-Mode"""
    global db
    if db is None:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("❌ Datenbank nicht verfügbar")
        return user_data['status']
    
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    user_id = update.effective_user.id
    
    try:
        # Aktuelle Benachrichtigungseinstellungen holen
        notification_settings = db.get_notification_settings(user_id)
        # Verfügbare Modi aus Config holen
        available_modes = db.get_notification_modes()
        
        if callback_data.startswith('select_vacation_'):
            # Urlaubsschaltung-Modus-Auswahl
            await show_mode_selection(update, context, user_data, 'notifyVacationMode', user_id)
            
        elif callback_data.startswith('select_power_'):
            # Stromausfall-Modus-Auswahl
            await show_mode_selection(update, context, user_data, 'notifyDoorPowerMeter', user_id)
            
        elif callback_data.startswith('select_door_'):
            # Tür-Öffnungs-Modus-Auswahl
            await show_mode_selection(update, context, user_data, 'notifyDoorFrontDoor', user_id)
            
        elif callback_data.startswith('select_temperature_'):
            # Temperatur-Modus-Auswahl
            await show_mode_selection(update, context, user_data, 'notifyTemperatureWarning', user_id)
            
        elif callback_data.startswith('select_burglar_'):
            # Einbruch-Modus-Auswahl
            await show_mode_selection(update, context, user_data, 'notifyBurglarAlarm', user_id)
            
        elif callback_data.startswith('set_notifyVacationMode_'):
            # Urlaub-Benachrichtigungen setzen
            mode = callback_data.replace(f'set_notifyVacationMode_{user_id}_', '')
            
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_notification_setting(user_id, 'notifyVacationMode', mode)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                mode_info = available_modes.get(mode, {})
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode)
                await query.edit_message_text(f"✅ Urlaub-Benachrichtigung: {icon} {desc}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data.startswith('set_notifyDoorPowerMeter_'):
            # Stromausfall-Benachrichtigungen setzen
            mode = callback_data.replace(f'set_notifyDoorPowerMeter_{user_id}_', '')
            
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_notification_setting(user_id, 'notifyDoorPowerMeter', mode)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                mode_info = available_modes.get(mode, {})
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode)
                await query.edit_message_text(f"✅ Stromausfall-Benachrichtigung: {icon} {desc}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data.startswith('set_notifyDoorFrontDoor_'):
            # Tür-Öffnungs-Benachrichtigungen setzen
            mode = callback_data.replace(f'set_notifyDoorFrontDoor_{user_id}_', '')
            
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_notification_setting(user_id, 'notifyDoorFrontDoor', mode)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                mode_info = available_modes.get(mode, {})
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode)
                await query.edit_message_text(f"✅ Tür-Öffnungs-Benachrichtigung: {icon} {desc}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data.startswith('set_notifyTemperatureWarning_'):
            # Temperatur-Benachrichtigungen setzen
            mode = callback_data.replace(f'set_notifyTemperatureWarning_{user_id}_', '')
                        
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_notification_setting(user_id, 'notifyTemperatureWarning', mode)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                mode_info = available_modes.get(mode, {})
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode)
                await query.edit_message_text(f"✅ Temperatur-Benachrichtigung: {icon} {desc}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data.startswith('set_notifyBurglarAlarm_'):
            # Einbruch-Benachrichtigungen setzen
            mode = callback_data.replace(f'set_notifyBurglarAlarm_{user_id}_', '')
                        
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_notification_setting(user_id, 'notifyBurglarAlarm', mode)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                mode_info = available_modes.get(mode, {})
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode)
                await query.edit_message_text(f"✅ Einbruch-Benachrichtigung: {icon} {desc}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data.startswith('set_battery_info_'):
            # Batterie-Info-Einstellung umschalten
            current_setting = db.get_battery_info_setting(user_id)
            new_setting = not current_setting
            
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_battery_info_setting(user_id, new_setting)
            
            if success:
                status_text = "✅ Immer anzeigen" if new_setting else "🔕 Nur bei niedrigem Stand"
                await query.edit_message_text(f"🔋 Batterie-Info: {status_text}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data.startswith('back_to_notifications_'):
            # Zurück zur Benachrichtigungs-Übersicht
            await notifications(update, context, user_data, markupList)
                
        elif callback_data.startswith('set_language_'):
            # Sprache setzen
            lang = callback_data.replace('set_language_', '')
                                    
            # Stelle sicher, dass nur der Sprachcode verwendet wird (falls zusätzliche Daten anhängen)
            lang = lang.split('_')[0]  # Nur den Teil vor dem ersten Unterstrich verwenden
                                                
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_user_language(user_id, lang)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                lang_names = {'de': 'Deutsch', 'en': 'English', 'fr': 'Français', 'es': 'Español'}
                display_name = lang_names.get(lang, lang.upper())
                await query.edit_message_text(
                    f"✅ Sprache geändert zu {display_name}"
                )
            else:
                await query.edit_message_text("❌ Sprachänderung fehlgeschlagen")
                
        elif callback_data.startswith('set_vacation_'):
            # Urlaub-Benachrichtigungen setzen
            mode = callback_data.replace(f'set_vacation_{user_id}_', '')
                                    
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_notification_setting(user_id, 'notifyVacationMode', mode)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                mode_info = available_modes.get(mode, {})
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode)
                await query.edit_message_text(f"✅ Urlaub-Benachrichtigung: {icon} {desc}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data.startswith('set_power_'):
            # Stromausfall-Benachrichtigungen setzen
            mode = callback_data.replace(f'set_power_{user_id}_', '')
                                    
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_notification_setting(user_id, 'notifyDoorPowerMeter', mode)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                mode_info = available_modes.get(mode, {})
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode)
                await query.edit_message_text(f"✅ Stromausfall-Benachrichtigung: {icon} {desc}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data.startswith('set_door_'):
            # Tür-Öffnungs-Benachrichtigungen setzen
            mode = callback_data.replace(f'set_door_{user_id}_', '')
                                    
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_notification_setting(user_id, 'notifyDoorFrontDoor', mode)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                mode_info = available_modes.get(mode, {})
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode)
                await query.edit_message_text(f"✅ Tür-Öffnungs-Benachrichtigung: {icon} {desc}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data.startswith('set_temperature_'):
            # Temperatur-Benachrichtigungen setzen
            mode = callback_data.replace(f'set_temperature_{user_id}_', '')
                                    
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_notification_setting(user_id, 'notifyTemperatureWarning', mode)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                mode_info = available_modes.get(mode, {})
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode)
                await query.edit_message_text(f"✅ Temperatur-Benachrichtigung: {icon} {desc}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data.startswith('set_burglar_'):
            # Einbruch-Benachrichtigungen setzen
            mode = callback_data.replace(f'set_burglar_{user_id}_', '')
                                    
            if db is None:
                print("ERROR: Database instance is None!")
                await query.edit_message_text("❌ Datenbank nicht verfügbar")
                return user_data['status']
            
            success = db.update_notification_setting(user_id, 'notifyBurglarAlarm', mode)
                        
            # Debug: Überprüfen ob die Änderung in der DB ankam
            db.debug_user_settings(user_id)
            
            if success:
                mode_info = available_modes.get(mode, {})
                icon = mode_info.get('icon', '')
                desc = mode_info.get('description', mode)
                await query.edit_message_text(f"✅ Einbruch-Benachrichtigung: {icon} {desc}")
            else:
                await query.edit_message_text("❌ Einstellung konnte nicht gespeichert werden")
                
        elif callback_data == 'vacation_header':
            await query.answer("Urlaubsschaltung - Wähle einen Modus")
            
        elif callback_data == 'power_header':
            await query.answer("Tür-Stromzähler - Wähle einen Modus")
            
        elif callback_data == 'door_header':
            await query.answer("Haustür - Wähle einen Modus")
            
        elif callback_data == 'temp_header':
            await query.answer("Temperaturwarnung - Wähle einen Modus")
            
        elif callback_data == 'burglar_header':
            await query.answer("Einbruchalarm - Wähle einen Modus")
                
        elif callback_data.startswith('cancel_language_'):
            await query.edit_message_text("❌ Sprachänderung abgebrochen")
                
        elif callback_data.startswith('back_settings_'):
            # Zurück zu den Einstellungen
            await query.edit_message_text("🔙 Zurück zu den Einstellungen")
               
    except Exception as e:
        await query.edit_message_text(f"❌ Fehler: {str(e)}")
                        
    return user_data['status']

# Klasse für Kompatibilität mit fritzdect_bot.py
class SettingsMode:
    """Wrapper-Klasse für Kompatibilität mit dem Bot-Framework"""
    
    # Tastatur-Befehle und Textbefehle für Kompatibilität
    tastertur = tastertur
    textbefehl = textbefehl
    
    @staticmethod
    async def default(update, context, user_data, markupList):
        """Default-Funktion - delegiert zur globalen Funktion"""
        return await default(update, context, user_data, markupList)
    
    @staticmethod
    async def language(update, context, user_data, markupList):
        """Sprache ändern - delegiert zur globalen Funktion"""
        return await language(update, context, user_data, markupList)
    
    @staticmethod
    async def notifications(update, context, user_data, markupList):
        """Benachrichtigungen - delegiert zur globalen Funktion"""
        return await notifications(update, context, user_data, markupList)
    
    @staticmethod
    async def back(update, context, user_data, markupList):
        """Zurück - delegiert zur globalen Funktion"""
        return await back(update, context, user_data, markupList)
    
    @staticmethod
    def get_callback_handlers():
        """Gibt Callback-Handler für Inline-Keyboards zurück"""
        return get_callback_handlers()
    
    @staticmethod
    async def handle_settings_callback(update, context, user_data, markupList):
        """Handler für Settings-Callbacks - delegiert zur globalen Funktion"""
        return await handle_settings_callback(update, context, user_data, markupList)
