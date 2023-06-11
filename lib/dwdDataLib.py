#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, imp, sys
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("conf", "../conf.py")
import conf as Conf
import csv
import requests
import codecs


class DWDData:
    
    def getValues(self):
        
        response = requests.get(Conf.dwd['url'])
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
    db = DWDData()
    row = db.getValues()
    print("temp:"+row[Conf.dwd['tempKey']]+", hum:"+ row[Conf.dwd['humidityKey']])

if __name__ == '__main__':
    main()
