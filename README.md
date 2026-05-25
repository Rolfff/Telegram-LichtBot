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
- ca 50cm 3x1,5mm NYM-Leitung
- 1 Schelle + M3 Schraube zur befestigung des Nezteils an der NYM-Leitung
- 1 M3 Schraube zur befestigung des PI-Gehäuses mit dem Netzteil
- 3D-Model der Lampe drucken. -> ./Dokumentation/3Dmodel_lampe.stl

## Todo:
- Temperatur-Controler und SQL-DB von Webseite hinzufügen
- BootBot.py erklären, Fals stromausfällt PI bot bootet
- Partymodus feritg progrmmieren Thread-Problem lösen
  - Lieber in [LedFx](https://ledfx.readthedocs.io/en/master/) intigrieren
- Repositorys aufräumen, bzw struckur reinbringen.
- ledLib.py und lampeLib.py in Lib-Ornder verschieben
- Integration von [WLED](https://kno.wled.ge/)

## Installation

### Voraussetzungen
- Raspberry Pi 3 oder höher
- Python 3.8 oder höher
- pip3

### Schritte

1. Repository klonen oder herunterladen
```bash
cd /home/pi
git clone <repository-url> Telegram-LichtBot_v2
cd Telegram-LichtBot_v2
```

2. Virtuelle Umgebung erstellen und aktivieren
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Abhängigkeiten installieren
```bash
pip3 install -r requirements.txt
```

4. Konfiguration erstellen
```bash
cp config.example.json config.json
nano config.json
```
Passe die Konfiguration an (Telegram-Token, Admin-Chat-ID, etc.)

5. System-User und Gruppe für den Bot erstellen
```bash
sudo useradd -r -s /bin/false lichtbot
sudo groupadd lichtbot
sudo usermod -a -G lichtbot lichtbot
```

6. Bot-Verzeichnis nach /opt/licht-bot verschieben
```bash
sudo mkdir -p /opt/licht-bot
sudo cp -r /home/pi/Telegram-LichtBot_v2/* /opt/licht-bot/
sudo chown -R lichtbot:lichtbot /opt/licht-bot
```

7. Datenbank-Verzeichnis erstellen
```bash
mkdir -p /home/pi/Data_LichtBot
chmod 777 /home/pi/Data_LichtBot
```

8. Bot testen
```bash
python3 licht_bot.py
```

### Systemd Service Installation

1. Service-Datei kopieren
```bash
sudo cp licht-bot.service /etc/systemd/system/
```

2. Service aktivieren und starten
```bash
sudo systemctl daemon-reload
sudo systemctl enable licht-bot.service
sudo systemctl start licht-bot.service
```

3. Status prüfen
```bash
sudo systemctl status licht-bot.service
```

4. Logs anzeigen
```bash
sudo journalctl -u licht-bot.service -f
```

### Cron-Job Konfiguration

### Temperatur-Messung
Ermittelt alle 10 Minuten Raum- und DWD-Werte und speichert diese in der Datenbank:

```bash
# Crontab-Eintrag (mit virtueller Umgebung und Konfiguration)
*/10 * * * * cd /opt/licht-bot && /opt/licht-bot/venv/bin/python /opt/licht-bot/storeTemp_DB.py -c /opt/licht-bot/config.json
```

Beispiel für Installation:
```bash
# Crontab öffnen
crontab -e

# Zeile hinzufügen (Pfade anpassen)
*/10 * * * * cd /opt/licht-bot && /opt/licht-bot/venv/bin/python /opt/licht-bot/storeTemp_DB.py -c /opt/licht-bot/config.json
```

### Cron-Job testen
```bash
# Manuelles Testen des Scripts
cd /opt/licht-bot
./venv/bin/python storeTemp_DB.py -c config.json
```


## Quellen:
[1]: https://tutorials-raspberrypi.de/raspberry-pi-ws2801-rgb-led-streifen-anschliessen-steuern/ "RGB-LED mit PI"
1. RGB-LED mit PI: https://tutorials-raspberrypi.de/raspberry-pi-ws2801-rgb-led-streifen-anschliessen-steuern/

[2]: https://tutorials-raspberrypi.de/raspberry-pi-luftfeuchtigkeit-temperatur-messen-dht11-dht22/ "Temperatur mit PI"
2. Temperatur mit PI: https://tutorials-raspberrypi.de/raspberry-pi-luftfeuchtigkeit-temperatur-messen-dht11-dht22/


