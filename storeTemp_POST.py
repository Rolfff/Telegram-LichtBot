#!/usr/bin/env python3
import requests
import Adafruit_DHT
import conf as Conf
from lib.tempDatabaseLib import TempDatabase
from lib.userDatabaseLib import UserDatabase
from lib.dwdDataLib import DWDData
import telegram

sensor = Adafruit_DHT.DHT11
humidity, temperature = Adafruit_DHT.read_retry(sensor, Conf.pin['tempSen'])

db = DWDData()
row = db.getValues()
dwdHum = row[Conf.dwd['humidityKey']]
dwdTem = row[Conf.dwd['tempKey']]

print ("Tempratur: " + str(temperature) + "; Luftfeuchtigkeit: " + str(humidity) +"; DWD Tempratur:"+str(dwdTem)+"; DWD Luftfeuchtigkeit:"+ str(dwdHum))

db = TempDatabase()
userDB = UserDatabase()
altwerte = db.getValue()

print ("Vorher Tempratur: " + str(altwerte['temp']) + "; Vorher DWD Tempratur:"+str(altwerte['dwdtemp']))

db.insertValues(temperature,humidity,dwdTem,dwdHum)

if float(temperature) > float(dwdTem.replace(',','.')) and float(altwerte['temp']) <= float(altwerte['dwdtemp']):
    bot = telegram.Bot(token=Conf.telegram['token'])
    users = userDB.getAllWetterAboUsers()
    for user in users:
        bot.send_message(chat_id=user['chatID'], 
                  text='In deinem Zimmer ist es mit '+str(temperature)+' Grad wärmer als '+str(dwdTem)+' Grad draußen.',
                    )
    
if float(temperature) < float(dwdTem.replace(',','.')) and float(altwerte['temp']) >= float(altwerte['dwdtemp']):
    bot = telegram.Bot(token=Conf.telegram['token'])
    users = userDB.getAllWetterAboUsers()
    for user in users:
        bot.send_message(chat_id=user['chatID'], 
                  text='In deinem Zimmer ist es mit '+str(temperature)+' Grad kälter als '+str(dwdTem)+' Grad draußen.',
                    )

r = requests.post(Conf.post['url'], data={'temp': temperature, 'humi': humidity, 'token': Conf.post['tocken'], 'dwdtemp': dwdTem, 'dwdhumi': dwdHum,})
print(r.status_code, r.reason)