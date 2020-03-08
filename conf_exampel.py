#!/usr/bin/env python3

# Einstellungen für die Webseite auf der die lnagzeit Wetterdaten gespeichert werden
post = {'url' : 'http://???.de/Temp-Controller.php',
        'tocken' : '???'}

#Schnittstelle zum Deutschen Wetterdiesnst. Einstellung für Messstation Darmstadt am Woog
dwd = {'url' : 'https://opendata.dwd.de/weather/weather_reports/poi/L886_-BEOB.csv',
       #Zeilenname für Temperatur
        'tempKey' : 'temperature_at_5_cm_above_ground',
       #Zeilenname für Luftfeuchtigkeit
        'humidityKey' : 'relative_humidity'}

#Locale Datenbank für kurzfristige Wetteraufzeichnung und Usermanagement
sqlite = {'pathTemp' : '/home/pi/Dokumente/database/tempdata.db',
          #Tabellenname
          'tempTable' : 'temperatur',
          #Zeitraum der Wetteraufzeichung in Wochen
          'deleteAfterWeeks': 2,
          'pathUser' : '/home/pi/Dokumente/database/userdata.db',
          #Tabellenname
          'userTable' : 'user'}

#Pin-Belegung auf dem PI
pin = {'tempSen': 4,
       'spiPort': 0,
       'spiDevice': 0,
       # Configure the count of pixels:
       'pixelCount':31,
       'anzalStege':6,
       #Reinfolge der LED-Adressen pro Steg im Uhrzeigersin
       'pixelMap':[0,1,2,3,4,20,19,18,17,16,21,22,23,24,25,9,8,7,6,5,10,11,12,13,14,30,29,28,27,26],
       'bottomLed':15}

#Telegram-Bot
telegram = {'token' : '???',
            #Telegram _Chat ID des Administrators
            'adminChatID' : '???',
            #Bot Passwort um mit Bot komunizieren zu dürfen.
            'passwort' :'???'}

#Pfad zum Speichern der Temperatur-Charts
tempExport = {'file':'/home/pi/Dokumente/images/lastPic.png',
              #Wieviele Tage geplotet werden sollen
              'days' : 1}

#Not nice, but work ;(
OneSpeedSingleton = 0.1
OneThreadSingleton = None
OneLightmatrix = None
OneLightlist = None

#Quellen:
#https://tutorials-raspberrypi.de/raspberry-pi-ws2801-rgb-led-streifen-anschliessen-steuern/
#https://tutorials-raspberrypi.de/raspberry-pi-luftfeuchtigkeit-temperatur-messen-dht11-dht22/

#Durchgeführte Installationen:
#sudo apt-get update
#sudo apt-get upgrade
#sudo apt-get install sqlite3
#sudo apt-get install sqlitebrowser
#sudo chmod 777 database
#sudo pip3 install Adafruit_WS2801
#sudo pip3 install Adafruit_Python_DHT
#sudo pip3 install matplotlib
#sudo pip3 install -U numpy
#sudo apt-get install libatlas-base-dev

