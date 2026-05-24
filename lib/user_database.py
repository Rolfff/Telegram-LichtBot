#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import datetime as DT
import logging
from sqlite3 import Error
from lib.config import Config

class UserDatabase:
    def __init__(self):
        self.config = Config()
        self.db_path = self.config.get_user_database_path()
        self.table_name = self.config.get_user_table_name()
        
        # Datenbankpfad auflösen
        if not os.path.isabs(self.db_path):
            # Pfad relativ zum Verzeichnis dieser Datei (lib/user_database.py)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(script_dir, '..', self.db_path)
            self.db_path = os.path.abspath(self.db_path)
        
        # Existenz der Datenbank überprüfen und ggf. diese anlegen
        if not os.path.exists(self.db_path):
            logging.info(f"Datenbank {self.db_path} nicht vorhanden - Datenbank wird angelegt.")
            self.create_database()
    
    def execute(self, sql, params=None):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            connection.commit()
            return True  # Erfolg zurückgeben
        except Error as e:
            logging.error(f"SQL Error: {str(e)} SQL-Query: {sql} Params: {params}")
            return False  # Fehler zurückgeben
        finally:
            connection.close()
    
    def fetch_one(self, sql, params=None):
        """Führt eine SQL-Abfrage aus und gibt einen Datensatz zurück"""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchone()
            return result
        except Error as e:
            logging.error(f"Fehler bei fetch_one: {e} SQL-Query: {sql}")
            return None
        finally:
            connection.close()
    
    def create_database(self):
        # Verzeichnis erstellen falls nicht vorhanden
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Tabelle für Benutzer erzeugen
        sql = f"""CREATE TABLE {self.table_name} (
            chatID INTEGER NOT NULL,
            firstname TEXT DEFAULT NULL,
            lastname TEXT DEFAULT NULL,
            isAdmin INTEGER NOT NULL DEFAULT 0,
            allowedToDatetime DATE DEFAULT NULL,
            failedAttempts INTEGER NOT NULL DEFAULT 0,
            blockedUntil DATE DEFAULT NULL,
            notifyWetterAbboMode INTEGER NOT NULL DEFAULT 1,
            language_code TEXT DEFAULT 'en',
            PRIMARY KEY(chatID)
        );"""
        self.execute(sql)
        
        # Tabelle für expire_notifications erzeugen
        sql = """CREATE TABLE expire_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notification_type TEXT NOT NULL,  -- 'weekly_summary' oder 'warning'
            sent_at DATETIME NOT NULL,
            chat_ids TEXT NOT NULL  -- Komma-separierte Liste von Chat-IDs
        );"""
        self.execute(sql)
        
        sql = f"CREATE INDEX index_{self.table_name} ON {self.table_name} (chatID);"
        self.execute(sql)
        self.execute("PRAGMA auto_vacuum = FULL;")
    
    def migrate_database(self):
        """Prüft und migriert die Datenbank auf die aktuelle Schema-Version"""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        
        try:
            # Prüfen welche Spalten existieren
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            # Prüfen ob expire_notifications Tabelle existiert
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expire_notifications'")
            expire_table_exists = cursor.fetchone() is not None
            
            if not expire_table_exists:
                logging.info("Erstelle expire_notifications Tabelle...")
                sql = """CREATE TABLE expire_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notification_type TEXT NOT NULL,  -- 'weekly_summary' oder 'warning'
                    sent_at DATETIME NOT NULL,
                    chat_ids TEXT NOT NULL  -- Komma-separierte Liste von Chat-IDs
                );"""
                cursor.execute(sql)
                connection.commit()
            
            # Fehlende Standard-Spalten hinzufügen
            if 'failedAttempts' not in existing_columns:
                logging.info("Füge Spalte 'failedAttempts' hinzu...")
                cursor.execute(f"ALTER TABLE {self.table_name} ADD COLUMN failedAttempts INTEGER NOT NULL DEFAULT 0")
                connection.commit()
            
            if 'blockedUntil' not in existing_columns:
                logging.info("Füge Spalte 'blockedUntil' hinzu...")
                cursor.execute(f"ALTER TABLE {self.table_name} ADD COLUMN blockedUntil DATE DEFAULT NULL")
                connection.commit()
            
            # Spracheinstellung hinzufügen
            if 'language_code' not in existing_columns:
                logging.info("Füge Spalte 'language_code' hinzu...")
                cursor.execute(f"ALTER TABLE {self.table_name} ADD COLUMN language_code TEXT DEFAULT 'en'")
                connection.commit()
            
            # Batterie-Info-Einstellung hinzufügen
            if 'showBatteryInfo' not in existing_columns:
                logging.info("Füge Spalte 'showBatteryInfo' hinzu...")
                cursor.execute(f"ALTER TABLE {self.table_name} ADD COLUMN showBatteryInfo INTEGER NOT NULL DEFAULT 0")
                connection.commit()
            
            # Dynamisch Benachrichtigungs-Spalten aus der Config hinzufügen
            config = Config()
            notifications = config.get_notifications()
            default_mode_value = self._get_default_mode_value()
            
            for config_key in notifications.keys():
                db_column = f"notify{config_key.title().replace('_', '')}"
                
                if db_column not in existing_columns:
                    logging.info(f"Füge Spalte '{db_column}' hinzu...")
                    cursor.execute(f"ALTER TABLE {self.table_name} ADD COLUMN {db_column} INTEGER NOT NULL DEFAULT {default_mode_value}")
                    connection.commit()
                
        except Error as e:
            logging.error(f"Fehler bei Datenbank-Migration: {e}")
        finally:
            connection.close()

    def updateWetterAbo(self,chatID,wert=0):
        sql =  "UPDATE "+self.table_name+" SET notifyWetterAbboMode = "+str(wert)+" WHERE chatID = '"+str(chatID)+"'"
        self.execute(sql)
        
    def getWetterAbo(self,chatID):
        bool = 0
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        sql = "SELECT notifyWetterAbboMode FROM "+self.table_name+" WHERE chatID='"+str(chatID)+"'"
        try:
            cursor.execute(sql)
            bool = cursor.fetchone()[0]
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        finally:
            connection.close()
        return bool
        
    def getAllWetterAboUsers(self):
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        users = []
        try:
            cursor.execute("SELECT chatID FROM "+self.table_name+" WHERE notifyWetterAbboMode = '1' ")
            rows = cursor.fetchall()
            for row in rows:
                print('chatID'+str(row[0]))
                user = {'chatID':row[0]}
                users.append(user)
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        except Exception as e:
            print(str(e))  
        finally:
            connection.close()
            return users
    
    def add_user(self, chat_id, firstname=None, lastname=None, is_admin=0, language_code='en'):
        """Fügt einen neuen Benutzer hinzu (überschreibt keine existierenden Benutzer)"""
        # Prüfen ob Benutzer bereits existiert
        if self.user_exists(chat_id):
            logging.info(f"User {chat_id} already exists, not adding/updating")
            return False
            
        # allowedToDatetime auf NULL setzen, erst bei Admin-Freigabe wird ein Datum gesetzt
        sql = f"""INSERT INTO {self.table_name} 
                 (chatID, firstname, lastname, isAdmin, allowedToDatetime, failedAttempts, blockedUntil, language_code) 
                 VALUES (?, ?, ?, ?, NULL, 0, NULL, ?)"""
        return self.execute(sql, (chat_id, firstname, lastname, is_admin, language_code))
    
    def update_user_info(self, chat_id, firstname=None, lastname=None):
        """Aktualisiert Benutzer-Info ohne Einstellungen zu überschreiben"""
        if firstname is None and lastname is None:
            return True
            
        updates = []
        params = []
        
        if firstname is not None:
            updates.append("firstname = ?")
            params.append(firstname)
        if lastname is not None:
            updates.append("lastname = ?")
            params.append(lastname)
        
        if not updates:
            return True
            
        params.append(chat_id)
        sql = f"UPDATE {self.table_name} SET {', '.join(updates)} WHERE chatID = ?"
        return self.execute(sql, params)
    
    def update_user_language(self, chat_id, language_code):
        """Aktualisiert die Spracheinstellung eines Benutzers"""
        sql = f"UPDATE {self.table_name} SET language_code = ? WHERE chatID = ?"
        return self.execute(sql, (language_code, chat_id))
    
    def get_user_language(self, chat_id):
        """Gibt die Spracheinstellung eines Benutzers zurück"""
        sql = f"SELECT language_code FROM {self.table_name} WHERE chatID = ?"
        result = self.fetch_one(sql, (chat_id,))
        return result[0] if result else 'en'
    
    def is_user_blocked(self, chat_id):
        """Prüft ob Benutzer geblockt ist"""
        sql = f"SELECT blockedUntil FROM {self.table_name} WHERE chatID = ?"
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            if result and result[0]:
                blocked_until = DT.datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
                check_blocked = DT.datetime.now() < blocked_until
                if check_blocked == False:
                    # Versuche reset
                    update_sql = f"UPDATE {self.table_name} SET failedAttempts = ?, blockedUntil = ? WHERE chatID = ?"
                    cursor.execute(update_sql, (0,None, chat_id))
                    connection.commit()
                return check_blocked
            return False
        except Error as e:
            logging.error(f"Fehler bei Block-Prüfung: {e}")
            return False
        finally:
            connection.close()
    
    def record_failed_attempt(self, chat_id):
        """Zeichnet einen fehlgeschlagenen Login-Versuch auf"""
        max_attempts = self.config.get_max_failed_attempts()
        block_days = self.config.get_block_duration_days()
        
        # Zuerst prüfen ob Benutzer existiert
        if not self.user_exists(chat_id):
            self.add_user(chat_id)
            return False
        
        # Aktuelle Versuche holen
        sql = f"SELECT failedAttempts FROM {self.table_name} WHERE chatID = ?"
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            if result:
                new_attempts = result[0] + 1
                
                if new_attempts >= max_attempts:
                    # Benutzer blockieren
                    blocked_until = DT.datetime.now() + DT.timedelta(days=block_days)
                    update_sql = f"""UPDATE {self.table_name} 
                                   SET failedAttempts = ?, blockedUntil = ? 
                                   WHERE chatID = ?"""
                    cursor.execute(update_sql, (new_attempts, blocked_until, chat_id))
                    connection.commit()
                    return True
                else:
                    # Versuche erhöhen
                    update_sql = f"UPDATE {self.table_name} SET failedAttempts = ? WHERE chatID = ?"
                    cursor.execute(update_sql, (new_attempts, chat_id))
                    connection.commit()
        except Error as e:
            logging.error(f"Fehler bei Aufzeichnung fehlgeschlagener Versuche: {e}")
        finally:
            connection.close()
        
        return False
    
    def reset_failed_attempts(self, chat_id):
        """Setzt fehlgeschlagene Versuche zurück"""
        sql = f"UPDATE {self.table_name} SET failedAttempts = 0, blockedUntil = NULL WHERE chatID = ?"
        self.execute(sql, (chat_id,))
    
    def user_exists(self, chat_id):
        """Prüft ob Benutzer existiert"""
        # Zuerst abgelaufene Benutzer aufräumen
        self.cleanup_expired_users()
        
        sql = f"SELECT EXISTS(SELECT 1 FROM {self.table_name} WHERE chatID = ?)"
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (chat_id,))
            return cursor.fetchone()[0] == 1
        except Error as e:
            logging.error(f"Fehler bei Existenz-Prüfung: {e}")
            return False
        finally:
            connection.close()
    
    def get_failed_attempts(self, chat_id):
        """Gibt Anzahl fehlgeschlagener Versuche zurück"""
        sql = f"SELECT failedAttempts FROM {self.table_name} WHERE chatID = ?"
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Error as e:
            logging.error(f"Fehler bei Abfrage fehlgeschlagener Versuche: {e}")
            return 0
        finally:
            connection.close()
    
    def cleanup_expired_users(self):
        """Löscht automatisch Benutzer mit abgelaufenem Zugriff (nicht-Admins)"""
        # Dann Benutzer löschen (Benachrichtigungen werden separat gehandhabt)
        sql = f"""DELETE FROM {self.table_name} 
                 WHERE isAdmin = 0 
                 AND allowedToDatetime IS NOT NULL 
                 AND allowedToDatetime < ?"""
        return self.execute(sql, (DT.datetime.now(),))
    
    def check_expire_notifications(self):
        """Prüft und sammelt expire-Benachrichtigungen ohne Benutzer zu löschen"""
        return self.send_expire_notifications()
    
    def delete_user(self, chat_id):
        """Löscht einen Benutzer aus der Datenbank"""
        sql = f"DELETE FROM {self.table_name} WHERE chatID = ?"
        return self.execute(sql, (chat_id,))
    
    def delete_request(self, chat_id):
        """Löscht eine Benutzeranfrage (Benutzer ohne Freigabe)"""
        sql = f"DELETE FROM {self.table_name} WHERE chatID = ? AND allowedToDatetime IS NULL"
        return self.execute(sql, (chat_id,))
    
    def is_user_allowed(self, chat_id):
        """Prüft ob Benutzer Zugriff hat"""
        # Zuerst abgelaufene Benutzer aufräumen
        self.cleanup_expired_users()
        
        # Zuerst prüfen ob Benutzer geblockt ist
        if self.is_user_blocked(chat_id):
            return False
        
        sql = f"SELECT allowedToDatetime FROM {self.table_name} WHERE chatID = ?"
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            if result and result[0] is not None:
                # Nur prüfen wenn ein Datum gesetzt ist (NULL bedeutet keine Freigabe)
                allowed_until = DT.datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
                return DT.datetime.now() < allowed_until
            return False  # NULL oder kein Ergebnis = keine Freigabe
        except Error as e:
            logging.error(f"Fehler bei Prüfung Benutzerzugriff: {e}")
            return False
        finally:
            connection.close()
    
    def is_admin(self, chat_id):
        """Prüft ob Benutzer Admin ist"""
        sql = f"SELECT isAdmin FROM {self.table_name} WHERE chatID = ?"
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            return result and result[0] == 1
        except Error as e:
            logging.error(f"Fehler bei Admin-Prüfung: {e}")
            return False
        finally:
            connection.close()
    
    def get_notification_settings(self, chat_id):
        """Gibt die Benachrichtigungseinstellungen für einen Benutzer zurück"""
        # Dynamisch alle Benachrichtigungstypen aus der Config laden
        config = Config()
        notifications = config.get_notifications()
        
        # Config-Keys zu Datenbank-Spalten-Namen konvertieren
        db_columns = []
        for config_key in notifications.keys():
            db_column = f"notify{config_key.title().replace('_', '')}"
            db_columns.append(db_column)
        
        if not db_columns:
            # Fallback auf Standard-Spalten wenn keine Konfiguration gefunden
            db_columns = ['notifyVacationMode', 'notifyDoorPowerMeter', 'notifyDoorFrontDoor']
        
        sql = f"SELECT {', '.join(db_columns)} FROM {self.table_name} WHERE chatID = ?"
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            
            settings = {}
            if result:
                for i, db_column in enumerate(db_columns):
                    value = result[i] if i < len(result) else self._get_default_mode_value()
                    settings[db_column] = self._convert_notification_mode(value)
            else:
                # Standardwerte zurückgeben wenn Benutzer nicht gefunden
                for db_column in db_columns:
                    settings[db_column] = config.get_default_notification_mode()
            
            return settings
            
        except Error as e:
            logging.error(f"Fehler bei Abfrage Benachrichtigungseinstellungen: {e}")
            # Fallback: Standardwerte zurückgeben
            settings = {}
            for db_column in db_columns:
                settings[db_column] = config.get_default_notification_mode()
            return settings
        finally:
            connection.close()
    
    def _get_default_mode_value(self):
        """Gibt den Standard-Datenbank-Wert für Benachrichtigungsmodus zurück"""
        modes = self.get_notification_modes()
        default_mode = modes.get('default_mode', 'none')
        return modes.get(default_mode, {}).get('value', 0)
    
    def _convert_notification_mode(self, value):
        """Konvertiert Datenbank-Wert in Benachrichtigungs-Modus"""
        if isinstance(value, str):
            return value.lower()
        
        # Zuerst versuchen, über die konfigurierten Modi zu mappen
        config = Config()
        modes = config.get_notification_modes()
        
        for mode_name, mode_info in modes.items():
            if mode_info.get('value') == value:
                return mode_name
        
        # Fallback auf numerische Werte
        if value == 0:
            return 'none'
        elif value == 1:
            return 'silent'
        elif value == 2:
            return 'push'
        else:
            return config.get_default_notification_mode()  # Standard aus Config
    
    def update_notification_setting(self, chat_id, setting, value):
        """Aktualisiert eine einzelne Benachrichtigungseinstellung"""
        # Dynamisch alle Benachrichtigungstypen aus der Config laden
        config = Config()
        notifications = config.get_notifications()
        
        # Config-Keys zu Datenbank-Spalten-Namen konvertieren
        valid_settings = []
        for config_key in notifications.keys():
            db_column = f"notify{config_key.title().replace('_', '')}"
            valid_settings.append(db_column)
        
        if not valid_settings:
            # Fallback auf Standard-Spalten wenn keine Konfiguration gefunden
            valid_settings = ['notifyVacationMode', 'notifyDoorPowerMeter', 'notifyDoorFrontDoor']
        
        if setting not in valid_settings:
            raise ValueError(f"Ungültige Einstellung: {setting}. Erlaubt: {valid_settings}")
        
        # Wert in numerischen Modus konvertieren
        if isinstance(value, str):
            value = value.lower()
            modes = config.get_notification_modes()
            if value in modes:
                db_value = modes[value].get('value')
            else:
                raise ValueError(f"Ungültiger Modus: {value}. Erlaubt: {list(modes.keys())}")
        else:
            # Numerische Werte direkt übernehmen
            db_value = value
        
        sql = f"UPDATE {self.table_name} SET {setting} = ? WHERE chatID = ?"
        return self.execute(sql, (db_value, chat_id))
    
    def get_notification_modes(self):
        """Gibt die verfügbaren Benachrichtigungs-Modi zurück"""
        config = Config()
        return config.get_notification_modes()
    
    def update_all_notification_settings(self, chat_id, vacation_mode, door_power_meter, door_front_door):
        """Aktualisiert alle Benachrichtigungseinstellungen"""
        sql = f"""UPDATE {self.table_name} 
                 SET notifyVacationMode = ?, notifyDoorPowerMeter = ?, notifyDoorFrontDoor = ? 
                 WHERE chatID = ?"""
        return self.execute(sql, (int(vacation_mode), int(door_power_meter), int(door_front_door), chat_id))
    
    def debug_user_settings(self, chat_id):
        """Debug-Methode: Zeigt alle Einstellungen eines Benutzers"""
        sql = f"""SELECT chatID, firstname, language_code, notifyVacationMode, notifyDoorPowerMeter, notifyDoorFrontDoor 
                 FROM {self.table_name} WHERE chatID = ?"""
        result = self.fetch_one(sql, (chat_id,))
        if result:
            logging.debug(f"User {chat_id} settings: Name={result[1]}, Language={result[2]}, Vacation={result[3]}, Power={result[4]}, Door={result[5]}")
            return {
                'chatID': result[0],
                'firstname': result[1],
                'language_code': result[2],
                'notifyVacationMode': bool(result[3]),
                'notifyDoorPowerMeter': bool(result[4]),
                'notifyDoorFrontDoor': bool(result[5])
            }
        else:
            logging.warning(f"User {chat_id} not found in database")
            return None
    
    def grant_access(self, chat_id, days=30):
        """Gewährt einem Benutzer Zugriff für eine bestimmte Anzahl von Tagen"""
        allowed_until = DT.datetime.now() + DT.timedelta(days=days)
        sql = f"UPDATE {self.table_name} SET allowedToDatetime = ? WHERE chatID = ?"
        self.execute(sql, (allowed_until, chat_id))
        return allowed_until
    
    def is_access_granted(self, chat_id):
        """Prüft ob einem Benutzer Zugriff gewährt wurde (nach Admin-Freigabe)"""
        sql = f"SELECT allowedToDatetime FROM {self.table_name} WHERE chatID = ?"
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (chat_id,))
            result = cursor.fetchone()
            if result and result[0] is not None:
                # Nur prüfen wenn ein Datum gesetzt ist (NULL bedeutet keine Freigabe)
                allowed_until = DT.datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
                return DT.datetime.now() < allowed_until
            return False  # NULL oder kein Ergebnis = keine Freigabe
        except Error as e:
            logging.error(f"Fehler bei Prüfung Zugriffsgewährung: {e}")
            return False
        finally:
            connection.close()
    
    def extend_access(self, chat_id, d=0):
        """Verlängert den Zugriff eines Benutzers"""
        allowed_until = DT.datetime.now() + DT.timedelta(days=d)
        sql = f"UPDATE {self.table_name} SET allowedToDatetime = ? WHERE chatID = ?"
        self.execute(sql, (allowed_until, chat_id))
    
    def get_pending_requests(self):
        """Gibt alle User zurück, die auf Freigabe warten"""
        # Zuerst abgelaufene Benutzer aufräumen
        self.cleanup_expired_users()
        
        sql = f"""SELECT chatID, firstname, lastname FROM {self.table_name} 
                 WHERE allowedToDatetime IS NULL AND isAdmin = 0 
                 ORDER BY chatID"""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Fehler beim Abrufen der wartenden Anfragen: {e}")
            return []
        finally:
            connection.close()
    
    def get_all_users(self):
        """Gibt alle Benutzer zurück"""
        # Zuerst abgelaufene Benutzer aufräumen
        self.cleanup_expired_users()
        
        sql = f"SELECT * FROM {self.table_name}"
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            return cursor.fetchall()
        except Error as e:
            logging.error(f"Fehler beim Abrufen aller Benutzer: {e}")
            return []
        finally:
            connection.close()
    
    def send_expire_notifications(self):
        """Sendet Benachrichtigungen über ablaufende Benutzerrechte"""
        from lib.config import Config
        config = Config()
        expire_config = config.get_expire_notification_config()
        
        if not expire_config.get('enabled', False):
            return []
        
        now = DT.datetime.now()
        notifications = []
        
        # Wöchentliche Zusammenfassung senden
        if expire_config.get('weekly_summary', True):
            weekly = self._send_weekly_summary(now, expire_config)
            if weekly:
                notifications.append(weekly)
        
        # Einzelne Warnungen senden
        for days in expire_config.get('warning_days', [7, 3, 1]):
            warning = self._send_warning_notifications(now, expire_config, days)
            if warning:
                notifications.append(warning)
        
        return notifications
    
    def _send_weekly_summary(self, now, expire_config):
        """Sendet wöchentliche Zusammenfassung der ablaufenden Benutzerrechte"""
        # Prüfen ob heute der konfigurierte Tag ist
        summary_day = expire_config.get('summary_day', 1)  # 1 = Montag
        if now.weekday() != summary_day:
            return None
        
        # Prüfen ob heute schon eine Zusammenfassung gesendet wurde
        if self._was_notification_sent_today('weekly_summary', now):
            return None
        
        # Benutzer finden, die in den nächsten 7 Tagen ablaufen
        seven_days_from_now = now + DT.timedelta(days=7)
        sql = f"""SELECT chatID, firstname, lastname, allowedToDatetime 
                 FROM {self.table_name} 
                 WHERE isAdmin = 0 
                 AND allowedToDatetime IS NOT NULL 
                 AND allowedToDatetime <= ?
                 AND allowedToDatetime > ?
                 ORDER BY allowedToDatetime ASC"""
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (seven_days_from_now, now))
            expiring_users = cursor.fetchall()
            
            if expiring_users:
                # Benachrichtigungstext erstellen
                message = "📅 **Wöchentliche Zusammenfassung - Ablaufende Benutzerrechte:**\n\n"
                
                for user in expiring_users:
                    chat_id, firstname, lastname, allowed_until = user
                    days_until = (allowed_until - now).days
                    name = f"{firstname or 'Unbekannt'} {lastname or ''}".strip()
                    
                    status_emoji = "🔴" if days_until <= 1 else "🟡" if days_until <= 3 else "🟢"
                    message += f"{status_emoji} **{name}** (ID: {chat_id}) - "
                    message += f"Recht läuft in {days_until} Tagen ab ({allowed_until.strftime('%d.%m.%Y %H:%M')})\n"
                
                # Letzte Benachrichtigung speichern
                self._save_notification_sent('weekly_summary', now, [str(user[0]) for user in expiring_users])
                
                # Nachricht an Admins senden (wird vom Bot aufgerufen)
                return {
                    'type': 'weekly_summary',
                    'message': message,
                    'users': expiring_users
                }
            
            return None
            
        except Error as e:
            logging.error(f"Fehler bei wöchentlicher Zusammenfassung: {e}")
            return None
        finally:
            connection.close()
    
    def _send_warning_notifications(self, now, expire_config, days):
        """Sendet Warnungen für Benutzer, deren Rechte bald ablaufen"""
        # Prüfen ob für diesen Zeitraum heute schon eine Warnung gesendet wurde
        if self._was_notification_sent_today(f'warning_{days}', now):
            return None
        
        target_date = now + DT.timedelta(days=days)
        
        # Benutzer finden, deren Rechte in genau X Tagen ablaufen
        sql = f"""SELECT chatID, firstname, lastname, allowedToDatetime 
                 FROM {self.table_name} 
                 WHERE isAdmin = 0 
                 AND allowedToDatetime IS NOT NULL 
                 AND DATE(allowedToDatetime) = DATE(?)
                 ORDER BY allowedToDatetime ASC"""
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (target_date,))
            warning_users = cursor.fetchall()
            
            if warning_users:
                # Benachrichtigungstext erstellen
                urgency = "🔴 KRITISCH" if days <= 1 else "🟡 WARNUNG" if days <= 3 else "🟢 HINWEIS"
                message = f"{urgency} - Benutzerrechte laufen in {days} Tag(en) ab:\n\n"
                
                for user in warning_users:
                    chat_id, firstname, lastname, allowed_until = user
                    name = f"{firstname or 'Unbekannt'} {lastname or ''}".strip()
                    message += f"• **{name}** (ID: {chat_id}) - "
                    message += f"ablaufend am {allowed_until.strftime('%d.%m.%Y %H:%M')}\n"
                
                # Letzte Benachrichtigung speichern
                self._save_notification_sent(f'warning_{days}', now, [str(user[0]) for user in warning_users])
                
                # Nachricht an Admins senden (wird vom Bot aufgerufen)
                return {
                    'type': f'warning_{days}',
                    'message': message,
                    'users': warning_users
                }
            
            return None
            
        except Error as e:
            logging.error(f"Fehler bei Warnungs-Benachrichtigung: {e}")
            return None
        finally:
            connection.close()
    
    def _was_notification_sent_today(self, notification_type, now):
        """Prüft ob heute schon eine Benachrichtigung dieses Typs gesendet wurde"""
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        sql = """SELECT COUNT(*) FROM expire_notifications 
                 WHERE notification_type = ? 
                 AND sent_at >= ? AND sent_at <= ?"""
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (notification_type, today_start, today_end))
            result = cursor.fetchone()
            return result[0] > 0
        except Error as e:
            logging.error(f"Fehler bei Prüfung gesendeter Benachrichtigungen: {e}")
            return False
        finally:
            connection.close()
    
    def update_battery_info_setting(self, chat_id, show_battery_info):
        """Aktualisiert die Batterie-Info-Einstellung eines Benutzers"""
        sql = f"UPDATE {self.table_name} SET showBatteryInfo = ? WHERE chatID = ?"
        return self.execute(sql, (1 if show_battery_info else 0, chat_id))
    
    def get_battery_info_setting(self, chat_id):
        """Gibt die Batterie-Info-Einstellung eines Benutzers zurück"""
        sql = f"SELECT showBatteryInfo FROM {self.table_name} WHERE chatID = ?"
        result = self.fetch_one(sql, (chat_id,))
        return bool(result[0]) if result else False
    
    def _save_notification_sent(self, notification_type, now, chat_ids):
        """Speichert, dass eine Benachrichtigung gesendet wurde"""
        sql = """INSERT INTO expire_notifications (notification_type, sent_at, chat_ids) 
                 VALUES (?, ?, ?)"""
        
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (notification_type, now, ','.join(chat_ids)))
            connection.commit()
            return True
        except Error as e:
            logging.error(f"Fehler beim Speichern der Benachrichtigung: {e}")
            return False
        finally:
            connection.close()
