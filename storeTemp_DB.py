#!/usr/bin/env python3
import pymysql
import requests
import board
import adafruit_dht
import argparse
from lib.config import Config
from lib.tempDatabaseLib import TempDatabase
from lib.user_database import UserDatabase
from lib.dwdDataLib import DWDData
from lib.telegram_utils import send_telegram_message_sync
import sys

# CLI-Argumente parsen
parser = argparse.ArgumentParser(description='Temperatur-Messung und Speicherung')
parser.add_argument('-c', '--config', default='config.json',
                   help='Pfad zur Konfigurationsdatei (Standard: config.json)')
args = parser.parse_args()

config = Config(args.config)

# GPIO Pin für Temperatursensor - Standardwert falls nicht in config
temp_sensor_pin = config.get('sensor.temp_pin', 4)

# Pin-Mapping für adafruit-circuitpython-dht
# GPIO 4 entspricht board.D4
pin_mapping = {
    4: board.D4,
    17: board.D17,
    18: board.D18,
    27: board.D27,
    22: board.D22,
}
dht_pin = pin_mapping.get(temp_sensor_pin, board.D4)

# DHT11-Sensor initialisieren
dht = adafruit_dht.DHT11(dht_pin)

try:
    humidity = dht.humidity
    temperature = dht.temperature
except RuntimeError as error:
    # Fehler beim Lesen des Sensors
    print(f"Fehler beim Lesen des DHT-Sensors: {error.args[0]}")
    humidity, temperature = None, None

db = DWDData()
row = db.getValues()
dwdHum = row[config.get_dwd_humidity_key()]
dwdTem = row[config.get_dwd_temp_key()]

print ("Tempratur: " + str(temperature) + "; Luftfeuchtigkeit: " + str(humidity) +"; DWD Tempratur:"+str(dwdTem)+"; DWD Luftfeuchtigkeit:"+ str(dwdHum))

db = TempDatabase()
userDB = UserDatabase()
altwerte = db.getValue()

if altwerte is None:
    print ("Keine vorherigen Werte vorhanden")
    altwerte = {'temp': 0, 'dwdtemp': 0}
else:
    print ("Vorher Tempratur: " + str(altwerte['temp']) + "; Vorher DWD Tempratur:"+str(altwerte['dwdtemp']))

db.insertValues(temperature,humidity,dwdTem,dwdHum)

if float(temperature) > float(dwdTem.replace(',','.')) and float(altwerte['temp']) <= float(altwerte['dwdtemp']):
    token = config.get_telegram_token()
    users = userDB.getAllWetterAboUsers()
    for user in users:
        chat_id = user['chatID']
        mode_type = user.get('mode_type', 'push')
        
        # Benachrichtigung basierend auf Modus senden
        if mode_type == 'silent':
            disable_notification = True  # Silent Notification
        elif mode_type == 'push':
            disable_notification = False  # Normale Push-Nachricht
        else:
            disable_notification = False  # Fallback: push
        
        send_telegram_message_sync(token, chat_id,
            f'In deinem Zimmer ist es mit {temperature} Grad wärmer als {dwdTem} Grad draußen.',
            disable_notification=disable_notification)

if float(temperature) < float(dwdTem.replace(',','.')) and float(altwerte['temp']) >= float(altwerte['dwdtemp']):
    token = config.get_telegram_token()
    users = userDB.getAllWetterAboUsers()
    for user in users:
        chat_id = user['chatID']
        mode_type = user.get('mode_type', 'push')
        
        # Benachrichtigung basierend auf Modus senden
        if mode_type == 'silent':
            disable_notification = True  # Silent Notification
        elif mode_type == 'push':
            disable_notification = False  # Normale Push-Nachricht
        else:
            disable_notification = False  # Fallback: push
        
        send_telegram_message_sync(token, chat_id,
            f'In deinem Zimmer ist es mit {temperature} Grad kälter als {dwdTem} Grad draußen.',
            disable_notification=disable_notification)

#Send to Server
try:
    mysql_config = config.get('mysql', {})
    connection = pymysql.connect(
        host=mysql_config.get('host', 'localhost'),
        user=mysql_config.get('user', ''),
        password=mysql_config.get('password', ''),
        db=mysql_config.get('database', '')
    )
except:
    print ("Keine Verbindung zum Server ")
    print("Unexpected error:", sys.exc_info()[0])
    exit(0)

print ("Verbindung zum Server hergestellt")
#Datensatz einfuegen
cursor = connection.cursor()
dbTable = config.get('mysql.table', 'temperatur')
try:
    cursor.execute("INSERT INTO %s (temp,humidity,dwdtemp,dwdhumi) VALUES (%s,%s,%s,%s)",(dbTable,temperature,humidity,dwdTem,dwdHum))
    print ("Abfrage","INSERT INTO ",dbTable," (temp,humidity,dwdtemp,dwdhumi) VALUES (",temperature,",",humidity,",",str(dwdTem),",",str(dwdHum),")", "ausgefuert")
    connection.commit()
except:
    print ("Abfrage","INSERT INTO ",dbTable," (temp,humidity,dwdtemp,dwdhumi) VALUES (",temperature,",",humidity,",",str(dwdTem),",",str(dwdHum),")", "fehlgeschlagen")
    connection.rollback()
connection.close()
print ("Verbindung zum Server geschlossen")