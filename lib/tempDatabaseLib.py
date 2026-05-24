#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys, sqlite3
import datetime as DT
from sqlite3 import Error
from lib.config import Config

class TempDatabase:

    def __init__(self):
        self.config = Config()
        self.db_path = self.config.get_temp_database_path()
        self.table_name = self.config.get_temp_table_name()
        self.delete_after_weeks = self.config.get_delete_after_weeks()
        
        # Existenz der Datenbank überprüfen und ggf. diese anlegen
        if not os.path.exists(self.db_path):
            print ("Datenbank "+self.db_path+" nicht vorhanden - Datenbank wird anglegt.")
            self.createDatabase()
            
    def execute(self, sql):
        connection = sqlite3.connect(self.db_path)
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
        sql = "CREATE TABLE "+self.table_name+" ( "\
            "datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"\
            "temp double DEFAULT 0,"\
            "humidity double DEFAULT 0,"\
            "DWDtemp double DEFAULT 0,"\
            "DWDhumidity double DEFAULT 0"\
            ") ;"
        self.execute(sql)
        sql = "CREATE INDEX index_"+self.table_name+" ON "+self.table_name+" (datetime);"
        self.execute(sql)
        self.execute("PRAGMA auto_vacuum = FULL;")
            
    def insertValues(self,temperature,humidity,dwdTemperature,dwdHumidity):
        if humidity < 101:
            sql = "INSERT INTO "+self.table_name+" (temp,humidity,DWDtemp,DWDhumidity) VALUES ("+str(temperature)+","+str(humidity)+","+str(dwdTemperature).replace(',','.')+","+str(dwdHumidity).replace(',','.')+")"
        else:
            tmp = self.getValue()
            sql = "INSERT INTO "+self.table_name+" (temp,humidity,DWDtemp,DWDhumidity) VALUES ("+str(tmp['temp'])+","+str(tmp['hum'])+","+str(dwdTemperature).replace(',','.')+","+str(dwdHumidity).replace(',','.')+")"
        self.execute(sql)
    
    def deleteToOldValues(self,overWeeks):
        today = DT.date.today()
        week_ago = today - DT.timedelta(weeks=overWeeks)
        sql = "DELETE FROM "+self.table_name+" WHERE datetime <= '"+str(week_ago)+"'"
        print (sql)
        self.execute(sql)
        
    def getValue(self):
        ret = None
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM "+self.table_name+" ORDER BY datetime DESC LIMIT 1;")
            rows = cursor.fetchall()
            for row in rows:
                date = row[0]
                tem = row[1]
                hum = row[2]
                dwdtem = row[3]
                dwdhum = row[4]
                ret = {"datetime":date,"temp":tem,"hum":hum,"dwdtemp":dwdtem,"dwdhum":dwdhum}
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
            
        finally:
            connection.close()
        return ret
    
    def getValues(self,overDays):
        values = []
        today = DT.date.today()
        day_ago = today - DT.timedelta(days=overDays)
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM "+self.table_name+" WHERE datetime > '"+str(day_ago)+"' ORDER BY datetime ASC ;")
            rows = cursor.fetchall()
            for row in rows:
                values.append({"datetime":row[0],"temp":row[1],"hum":row[2],"dwdtemp":row[3],"dwdhum":row[4]})
                
#            print(str(len(rows))+" SQL-Query:"+str("SELECT * FROM "+self.table_name+" WHERE datetime > '"+str(day_ago)+"' ORDER BY datetime ASC ;"))
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        finally:
            connection.close()
        return values

#select datetime(timestamp, 'localtime') um richitge zeitzone zu bekommen
def main():
    config = Config()
    print("Delete all Data older than "+str(config.get_delete_after_weeks())+" Weeks.")
    db = TempDatabase()
    db.deleteToOldValues(config.get_delete_after_weeks())
    

if __name__ == '__main__':
    main()