#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import os
import logging

# Globale Config-Instanz
_global_config = None

class Config:
    def __init__(self, config_file='config.json'):
        # Globale Config-Instanz deaktiviert - immer neue Instanz erstellen
        
        # Konfigurationsdatei-Pfad auflösen
        if not os.path.isabs(config_file):
            # Pfad relativ zum Verzeichnis dieser Datei (lib/config.py)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(script_dir, '..', config_file)
            config_file = os.path.abspath(config_file)
        
        # Erste Instanz - Konfiguration laden mit Fallback
        config_data = self._try_load_config(config_file)
        
        # Wenn das fehlschlägt, Fallback-Konfiguration aus Home-Verzeichnis laden
        if config_data is None:
            fallback_config = os.path.expanduser('~/.fritzdect_config')
            if os.path.exists(fallback_config):
                try:
                    with open(fallback_config, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    self.config_file = fallback_config
                    logging.info(f"Konfiguration aus Fallback-Datei geladen: {fallback_config}")
                except (json.JSONDecodeError, FileNotFoundError):
                    config_data = {}
                    self.config_file = config_file
            else:
                config_data = {}
                self.config_file = config_file
        else:
            self.config_file = config_file
        
        # Config setzen
        self.config = config_data
    
    def _try_load_config(self, config_file):
        """Versucht, eine Konfigurationsdatei zu laden"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def load_config(self):
        try:
            # Absoluten Pfad für bessere Fehlermeldungen
            abs_path = os.path.abspath(self.config_file)
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            abs_path = os.path.abspath(self.config_file)
            logging.warning(f"Konfigurationsdatei nicht gefunden: {abs_path}")
            return {}
        except json.JSONDecodeError as e:
            abs_path = os.path.abspath(self.config_file)
            logging.error(f"Fehler beim Lesen der Konfigurationsdatei {abs_path}: {e}")
            return {}
    
    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_telegram_token(self):
        return self.get('telegram.token')
    
    def get_admin_chat_id(self):
        return self.get('telegram.admin_chat_id')
    
    def get_admin_chat_ids(self):
        """Gibt eine Liste von Admin-Chat-IDs zurück"""
        admin_id = self.get('telegram.admin_chat_id')
        if isinstance(admin_id, list):
            return admin_id
        elif admin_id:
            return [admin_id]
        return []
    
    def get_expire_notification_config(self):
        """Gibt die Konfiguration für Ablauf-Benachrichtigungen zurück"""
        return self.get('expire_notifications', {
            'enabled': True,
            'warning_days': [7, 3, 1],  # Tage vor Ablauf warnen
            'weekly_summary': True,
            'summary_day': 1,  # Wochentag (1=Montag)
            'summary_time': '09:00'  # Uhrzeit
        })
    
    def get_telegram_password(self):
        return self.get('telegram.password')
    
    def get_fritzbox_config(self):
        return self.get('fritzbox', {})
    
    def get_database_config(self):
        return self.get('database', {})
    
    def get_database_type(self):
        """Gibt den Datenbank-Typ zurück"""
        return self.get('database.type', 'sqlite')
    
    def get_temp_database_path(self):
        """Gibt den Pfad zur Temperatur-Datenbank zurück"""
        return self.get('database.pathTemp', '/home/pi/Data_LichtBot/tempdata.db')
    
    def get_temp_table_name(self):
        """Gibt den Namen der Temperatur-Tabelle zurück"""
        return self.get('database.tempTable', 'temperatur')
    
    def get_delete_after_weeks(self):
        """Gibt die Anzahl der Wochen zurück, nach der Daten gelöscht werden"""
        return self.get('database.deleteAfterWeeks', 4)
    
    def get_user_database_path(self):
        """Gibt den Pfad zur Benutzer-Datenbank zurück"""
        return self.get('database.pathUser', '/home/pi/Data_LichtBot/userdata.db')
    
    def get_user_table_name(self):
        """Gibt den Namen der Benutzer-Tabelle zurück"""
        return self.get('database.userTable', 'user')
    
    def get_logging_config(self):
        return self.get('logging', {'level': 'INFO', 'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'})
    
    def get_security_config(self):
        return self.get('security', {'max_failed_attempts': 5, 'block_duration_days': 2})
    
    def get_max_failed_attempts(self):
        return self.get('security.max_failed_attempts', 5)
    
    def get_block_duration_days(self):
        return self.get('security.block_duration_days', 2)
    
    def get_telegram_token(self):
        """Gibt den Telegram-Token zurück"""
        return self.get('telegram.token')
    
    def get_dwd_temp_key(self):
        """Gibt den DWD-Temperatur-Schlüssel zurück"""
        return self.get('dwd.tempKey', 'dry_bulb_temperature_at_2_meter_above_ground')
    
    def get_dwd_humidity_key(self):
        """Gibt den DWD-Luftfeuchtigkeits-Schlüssel zurück"""
        return self.get('dwd.humidityKey', 'relative_humidity')
    

    
    def get_notification_modes(self):
        """Gibt die konfigurierten Benachrichtigungs-Modi zurück"""
        return {
            'none': {'value': 0, 'description': 'Keine Benachrichtigung', 'icon': '🔕'},
            'silent': {'value': 1, 'description': 'Silent Notification', 'icon': '🔔'},
            'push': {'value': 2, 'description': 'Push-Nachricht', 'icon': '📱'},
            'default_mode': 'none'
        }
    
    def get_default_notification_mode(self):
        """Gibt den Standard-Benachrichtigungsmodus zurück"""
        modes = self.get_notification_modes()
        return modes.get('default_mode', 'none')
    
    def get_led_config(self):
        """Gibt die LED-Konfiguration zurück"""
        return self.get('led', {
            'clk_pin': 11,
            'data_pin': 10,
            'pixel_count': 31,
            'num_segments': 6,
            'pixel_map': [0,1,2,3,4,20,19,18,17,16,21,22,23,24,25,9,8,7,6,5,10,11,12,13,14,30,29,28,27,26],
            'bottom_led': 15,
            'default_speed': 0.1,
            'default_rgb': {'r': 255, 'g': 255, 'b': 255}
        })
    
    def get_led_clk_pin(self):
        """Gibt den CLK-Pin für LEDs zurück"""
        return self.get('led.clk_pin', 11)
    
    def get_led_data_pin(self):
        """Gibt den DATA-Pin für LEDs zurück"""
        return self.get('led.data_pin', 10)
    
    def get_led_pixel_count(self):
        """Gibt die Anzahl der Pixel zurück"""
        return self.get('led.pixel_count', 31)
    
    def get_led_num_segments(self):
        """Gibt die Anzahl der Segmente zurück"""
        return self.get('led.num_segments', 6)
    
    def get_led_pixel_map(self):
        """Gibt die Pixel-Map zurück"""
        return self.get('led.pixel_map', [0,1,2,3,4,20,19,18,17,16,21,22,23,24,25,9,8,7,6,5,10,11,12,13,14,30,29,28,27,26])
    
    def get_led_bottom_led(self):
        """Gibt die Bottom-LED-Nummer zurück"""
        return self.get('led.bottom_led', 15)
    
    def get_led_default_speed(self):
        """Gibt die Standard-Geschwindigkeit zurück"""
        return self.get('led.default_speed', 0.1)
    
    def get_led_default_rgb(self):
        """Gibt die Standard-Farben zurück"""
        return self.get('led.default_rgb', {'r': 255, 'g': 255, 'b': 255})

# Konstanten für Bot-Zustände
MAIN, LOGIN, ADMIN, SETTINGS, LIGHT, TEMPERATUR = range(6)

# Modi werden in fritzdect_bot.py gesetzt (um zirkuläre Imports zu vermeiden)
modeList = [None, None, None, None, None, None]

# Import hier am Ende der Datei, um zirkuläre Imports zu vermeiden
def init_mode_list():
    """Initialisiert die modeList mit den Klassen"""
    global modeList
    try:
        import lib.loginMode as LoginMode
        import lib.adminMode as AdminMode  
        import lib.settingsMode as SettingsMode
        import lib.lichtMode as LichtMode
        import lib.temperaturMode as TemperaturMode
        
        # Globale modeList aktualisieren (nicht lokale Variable!)
        modeList[0] = None  # MAIN
        modeList[1] = LoginMode
        modeList[2] = AdminMode
        modeList[3] = SettingsMode
        modeList[4] = LichtMode
        modeList[5] = TemperaturMode  # TEMPERATUR
    except ImportError as e:
        # Fallback für Tests ohne vollständige Installation
        logging.warning(f"ImportError in init_mode_list: {e}")
        pass

# Tastatur-Layouts
reply_keyboard_main = [['Licht', 'Temp.-Verlauf'],['Einstellungen','Logout']]

def genMarkupList():
    """Generiert die MarkupList für alle Modi"""
    # Stelle sicher, dass die modeList initialisiert ist
    init_mode_list()
    
    try:
        from telegram import ReplyKeyboardMarkup
    except ImportError:
        # Fallback für Tests ohne Telegram
        ReplyKeyboardMarkup = None
    
    markupList = {}
    for i in range(len(modeList)):
        if modeList[i] != None:
            if ReplyKeyboardMarkup:
                markupList[i] = ReplyKeyboardMarkup(buildKeyboard(modeList[i]), one_time_keyboard=False, resize_keyboard=True)
            else:
                # Fallback: Leere Liste
                markupList[i] = []
        else:
            if ReplyKeyboardMarkup:
                markupList[i] = ReplyKeyboardMarkup(reply_keyboard_main, one_time_keyboard=False, resize_keyboard=True)
            else:
                markupList[i] = []
    return markupList

def getMarkupList(status):
    """Gibt die MarkupList für einen bestimmten Status zurück"""
    try:
        from telegram import ReplyKeyboardMarkup
    except ImportError:
        # Fallback für Tests ohne Telegram
        ReplyKeyboardMarkup = None
    
    if modeList[status] != None:
        if ReplyKeyboardMarkup:
            return ReplyKeyboardMarkup(buildKeyboard(modeList[status]), one_time_keyboard=False, resize_keyboard=True)
        else:
            return []
    return []

def buildKeyboard(classs):
    """Erstellt eine Tastatur aus den Variablen 'tastertur' einer Klasse"""
    temp=[]
    reply_keyboard=[]
    i=0
    
    # Fallback für tastertur Attribut
    if hasattr(classs, 'tastertur'):
        tastertur_values = classs.tastertur.values()
    else:
        # Standard-Tastatur wenn tastertur nicht vorhanden
        tastertur_values = ['Hilfe', 'Zurück']
    
    for v in tastertur_values:
        temp.append(v)
        i=i+1
        if i % 3 == 0:
            reply_keyboard.append(temp)
            temp=[]
    reply_keyboard.append(temp)
    return reply_keyboard

# markupList wird in lichtbot.py generiert
markupList = None

