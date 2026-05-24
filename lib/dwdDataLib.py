#!/usr/bin/python3
# -*- coding: utf-8 -*-
import csv
import requests
import codecs
from lib.config import Config


class DWDData:
    
    def __init__(self):
        self.config = Config()
    
    def getValues(self):
        
        response = requests.get(self.config.get('dwd.url', 'https://opendata.dwd.de/weather/weather_reports/poi/L886_-BEOB.csv'))
        rows = response.content.decode('utf-8').split('\n')
        i = 0
        ret = dict()
        rowHeader = None
        
        for row in rows:
            rowList = row.split(';')
            
            if i == 0:
                rowHeader = rowList
            elif i == 3:
                for x in range(len(rowHeader)):
                    ret[rowHeader[x]] = rowList[x]
                break
            i += 1
        #print(str(ret))
        return ret
        
        
        

#select datetime(timestamp, 'localtime') um richitge zeitzone zu bekommen
def main():
    config = Config()
    db = DWDData()
    row = db.getValues()
    print("temp:"+row[config.get_dwd_temp_key()]+", hum:"+ row[config.get_dwd_humidity_key()])

if __name__ == '__main__':
    main()
