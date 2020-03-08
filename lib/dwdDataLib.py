#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, imp, sys
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("conf", "../conf.py")
import conf as Conf
import csv
from urllib.request import urlopen
import codecs


class DWDData:
    
    def getValues(self):
        response = urlopen(Conf.dwd['url'])
        reader = csv.DictReader(codecs.iterdecode(response, 'utf-8'),delimiter=';')
        next(reader)
        next(reader)
        return next(reader)
        
        

#select datetime(timestamp, 'localtime') um richitge zeitzone zu bekommen
def main():
    db = DWDData()
    row = db.getValues()
    print("temp:"+row[Conf.dwd['tempKey']]+", hum:"+ row[Conf.dwd['humidityKey']])

if __name__ == '__main__':
    main()
