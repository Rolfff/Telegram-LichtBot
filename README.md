# Telegram-LichtBot

Master-Repo sollte eigentlich laufen.

## Hardware
### Licht 
siehe auch Quelle [1]: 
- LED RGB Stripe mit WS2801 Chipsatz: https://www.amazon.de/gp/product/B01FPXCUK4/
- Netzteil Spannung: 5V / Strom: 3A https://www.amazon.de/Schaltnetzteil-Netzteil-15W-MeanWell-RS-15-5/dp/B00MWQD43U/
- Raspberry Pi 3 Model B (EU Produktion) 
- SanDisk Ultra 16GB microSDHC Speicherkarte
- Raspberry Pi 3 Gehäuse
### Für Temperatursensor 
siehe auch Quelle [2]:
- Widerstand 10k Ohm 
- DHT11 oder DHT22 Luftfeuchtigkeits-Sensor
### Sonstiges:
- Micro-USB zu Netzteil: https://www.amazon.de/Delock-82697-Stecker-Kabelenden-schwarz/dp/B01A9GLG6Q/
- jumper wire cable Kabel: https://www.amazon.de/gp/product/B00OK74ABO/

## Todo:
- 3D Model hinzufügen
- Temperatur-Controler und SQL-DB von Webseite hinzufügen
- BootBot.py erklären, Fals stromausfällt PI bot bootet
- Kronjob Temeratur aufziechnen dokumentieren
- Fehler in TEmeraturgraph fixen oder ander Lib nutzen
- Partymodus feritg progrmmieren Thread-Problem lösen
- Repositorys aufräumen, bzw struckur reinbringen. 


## Quellen:
[1]: https://tutorials-raspberrypi.de/raspberry-pi-ws2801-rgb-led-streifen-anschliessen-steuern/ "RGB-LED mit PI"
1. RGB-LED mit PI: https://tutorials-raspberrypi.de/raspberry-pi-ws2801-rgb-led-streifen-anschliessen-steuern/

[2]: https://tutorials-raspberrypi.de/raspberry-pi-luftfeuchtigkeit-temperatur-messen-dht11-dht22/ "Temperatur mit PI"
2. Temperatur mit PI: https://tutorials-raspberrypi.de/raspberry-pi-luftfeuchtigkeit-temperatur-messen-dht11-dht22/

## Durchgeführte Installationen:
> sudo apt-get update

> sudo apt-get upgrade

> sudo apt-get install sqlite3

> sudo apt-get install sqlitebrowser

> sudo chmod 777 database

> sudo pip3 install Adafruit_WS2801

> sudo pip3 install Adafruit_Python_DHT

> sudo pip3 install matplotlib

> sudo pip3 install -U numpy

> sudo apt-get install libatlas-base-dev
