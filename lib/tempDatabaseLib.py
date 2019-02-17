#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, imp, sys, sqlite3
import datetime as DT
from sqlite3 import Error
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("conf", "../conf.py")
import conf as Conf



class TempDatabase:

    def __init__(self):
        # Existenz der Datenbank überprüfen und ggf. diese anlegen
        if not os.path.exists(Conf.sqlite['pathTemp']):
            print ("Datenbank "+Conf.sqlite['pathTemp']+" nicht vorhanden - Datenbank wird anglegt.")
            self.createDatabase()
            
    def execute(self, sql):
        connection = sqlite3.connect(Conf.sqlite['pathTemp'])
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            connection.commit()
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        finally:
            connection.close()
            
    def createDatabase(self):
        # Tabelle erzeugen
        sql = "CREATE TABLE "+Conf.sqlite['tempTable']+" ( "\
            "datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"\
            "temp double DEFAULT 0,"\
            "humidity double DEFAULT 0"\
            "DWDtemp double DEFAULT 0,"\
            "DWDhumidity double DEFAULT 0"\
            ") ;"
        self.execute(sql)
        sql = "CREATE INDEX index_"+Conf.sqlite['tempTable']+" ON "+Conf.sqlite['tempTable']+" (datetime);"
        self.execute(sql)
        self.execute("PRAGMA auto_vacuum = FULL;")
            
    def insertValues(self,temperature,humidity,dwdTemperature,dwdHumidity):
        if humidity < 101:
            sql = "INSERT INTO "+Conf.sqlite['tempTable']+" (temp,humidity,DWDtemp,DWDhumidity) VALUES ("+str(temperature)+","+str(humidity)+","+str(dwdTemperature).replace(',','.')+","+str(dwdHumidity).replace(',','.')+")"
        else:
            tmp = self.getValue()
            sql = "INSERT INTO "+Conf.sqlite['tempTable']+" (temp,humidity,DWDtemp,DWDhumidity) VALUES ("+str(tmp['temp'])+","+str(tmp['hum'])+","+str(dwdTemperature).replace(',','.')+","+str(dwdHumidity).replace(',','.')+")"
        self.execute(sql)
    
    def deleteToOldValues(self,overWeeks):
        today = DT.date.today()
        week_ago = today - DT.timedelta(weeks=overWeeks)
        sql = "DELETE FROM "+Conf.sqlite['tempTable']+" WHERE datetime <= '"+str(week_ago)+"'"
        print (sql)
        self.execute(sql)
        
    def getValue(self):
        connection = sqlite3.connect(Conf.sqlite['pathTemp'])
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM "+Conf.sqlite['tempTable']+" ORDER BY datetime DESC LIMIT 1;")
            rows = cursor.fetchall()
            for row in rows:
                date = row[0]
                tem = row[1]
                hum = row[2]
                dwdtem = row[3]
                dwdhum = row[4]
                
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        finally:
            connection.close()
        return {"datetime":date,"temp":tem,"hum":hum,"dwdtemp":dwdtem,"dwdhum":dwdhum}
    
    def getValues(self,overDays):
        values = []
        today = DT.date.today()
        day_ago = today - DT.timedelta(days=overDays)
        connection = sqlite3.connect(Conf.sqlite['pathTemp'])
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM "+Conf.sqlite['tempTable']+" WHERE datetime > '"+str(day_ago)+"' ORDER BY datetime ASC ;")
            rows = cursor.fetchall()
            for row in rows:
                values.append({"datetime":row[0],"temp":row[1],"hum":row[2],"dwdtemp":row[3],"dwdhum":row[4]})
                
                
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        finally:
            connection.close()
        return values

#select datetime(timestamp, 'localtime') um richitge zeitzone zu bekommen
def main():
    print("Delete all Data older than "+str(Conf.sqlite['deleteAfterWeeks'])+" Weeks.")
    db = TempDatabase()
    db.deleteToOldValues(Conf.sqlite['deleteAfterWeeks'])
    

if __name__ == '__main__':
    main()