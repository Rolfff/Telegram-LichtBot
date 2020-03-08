#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, imp, sys, sqlite3
import datetime as DT
from sqlite3 import Error
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("conf", "../conf.py")
import conf as Conf



class UserDatabase:

    def __init__(self):
        # Existenz der Datenbank überprüfen und ggf. diese anlegen
        if not os.path.exists(Conf.sqlite['pathUser']):
            print ("Datenbank "+Conf.sqlite['pathUser']+" nicht vorhanden - Datenbank wird anglegt.")
            self.createDatabase()
            
    def execute(self, sql):
        connection = sqlite3.connect(Conf.sqlite['pathUser'])
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
            connection.commit()
            #print("29: exit: "+sql)
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        finally:
            connection.close()
            
    def createDatabase(self):
        # Tabelle erzeugen
        sql = "CREATE TABLE "+Conf.sqlite['userTable']+" ( "\
            "chatID	INTEGER NOT NULL,"\
            "firstname	TEXT DEFAULT NULL,"\
            "lastname	TEXT DEFAULT NULL,"\
            "isAdmin	INTEGER NOT NULL DEFAULT 0,"\
            "alowToDatetime DATE NOT NULL,"\
            "wetterAbbo	INTEGER NOT NULL DEFAULT 0,"\
            "PRIMARY KEY(chatID)"\
            ");"
        self.execute(sql)
        sql = "CREATE INDEX index_"+Conf.sqlite['userTable']+" ON "+Conf.sqlite['userTable']+" (chatID);"
        self.execute(sql)
        self.execute("PRAGMA auto_vacuum = FULL;")
            
    def insertNewUser(self,user_data,days_=0):
        today = DT.date.today()
        futureDay = today + DT.timedelta(days=days_)
        #User ist noch nicht freigeschaltet
        isAdmin = -1
        if user_data['chatId'] == Conf.telegram['adminChatID']:
            isAdmin = 1
        sql = "INSERT INTO "+Conf.sqlite['userTable']+" (chatID,firstname,lastname,isAdmin,alowToDatetime,wetterAbbo) VALUES ("+str(user_data['chatId'])+",'"+str(user_data['firstname'])+"','"+str(user_data['lastname'])+"',"+str(isAdmin)+",datetime('now','start of day','"+str(days_)+" days'),0)"
        self.execute(sql)
    
    def updateUserDays(self,chatID,days_=0):
        today = DT.date.today()
        futureDay = today + DT.timedelta(days=days_)
        isAdmin = 0
        if str(chatID) == Conf.telegram['adminChatID']:
            isAdmin = 1
        sql =  "UPDATE "+Conf.sqlite['userTable']+" SET isAdmin = "+str(isAdmin)+", alowToDatetime = datetime('now','start of day','"+str(days_)+" days') WHERE chatID = '"+str(chatID)+"'"
        self.execute(sql)
    
    def updateWetterAbo(self,chatID,wert=0):
        sql =  "UPDATE "+Conf.sqlite['userTable']+" SET wetterAbbo = "+str(wert)+" WHERE chatID = '"+str(chatID)+"'"
        self.execute(sql)
        
    def getWetterAbo(self,chatID):
        bool = 0
        connection = sqlite3.connect(Conf.sqlite['pathUser'])
        cursor = connection.cursor()
        sql = "SELECT wetterAbbo FROM "+Conf.sqlite['userTable']+" WHERE chatID='"+str(chatID)+"'"
        try:
            cursor.execute(sql)
            bool = cursor.fetchone()[0]
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        finally:
            connection.close()
        return bool
        
    def getAllWetterAboUsers(self):
        connection = sqlite3.connect(Conf.sqlite['pathUser'])
        cursor = connection.cursor()
        users = []
        try:
            cursor.execute("SELECT chatID FROM "+Conf.sqlite['userTable']+" WHERE wetterAbbo = '1' ")
            rows = cursor.fetchall()
            for row in rows:
                print('chatID'+str(row[0]))
                user = {'chatID':row[0]}
                users.append(user)
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        except Exception as e:
            print(str(e))  
        finally:
            connection.close()
            return users
    
    def deleteUser(self,chatID):
        sql = "DELETE FROM "+Conf.sqlite['userTable']+" WHERE chatID = '"+str(chatID)+"'"
        #print (sql)
        self.execute(sql)
    
    def existUser(self,chatID):
        bool = 0
        connection = sqlite3.connect(Conf.sqlite['pathUser'])
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM "+Conf.sqlite['userTable']+" WHERE chatID='"+str(chatID)+"')")
            bool = cursor.fetchone()[0]
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        finally:
            connection.close()
        return bool
    
    def isAlowed(self,chatID):
        if chatID == Conf.telegram['adminChatID']:
            return 1
        bool = 0
        if self.existUser(chatID) == 0:
            return -1
        connection = sqlite3.connect(Conf.sqlite['pathUser'])
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT Date(alowToDatetime), isAdmin FROM "+Conf.sqlite['userTable']+" WHERE chatID = '"+str(chatID)+"'")
            tub = cursor.fetchone()
            date = tub[0]
            isAdmin = tub[1]
            print('date:'+str(date)+'isAdmin:'+str(isAdmin))
            if isAdmin ==  -1:
                bool = -1
            else:
                if date < str(DT.date.today()):
                    self.deleteUser(chatID)
                else:
                    bool = 1
                
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        finally:
            connection.close()
        return bool
    
    def getNextRequest(self):
        connection = sqlite3.connect(Conf.sqlite['pathUser'])
        cursor = connection.cursor()
        nextRequest = {'chatID':None,'firstname':None,'lastname':None}
        
        try:
            cursor.execute("SELECT chatID,firstname,lastname FROM "+Conf.sqlite['userTable']+" WHERE isAdmin = '-1'")
            tub = cursor.fetchone()
            nextRequest['chatID'] = tub[0]
            nextRequest['firstname'] = tub[1]
            nextRequest['lastname'] = tub[2]
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        finally:
            connection.close()
            return nextRequest
    
    def getAllUsers(self):
        connection = sqlite3.connect(Conf.sqlite['pathUser'])
        cursor = connection.cursor()
        users = []
        try:
            cursor.execute("SELECT chatID,firstname,lastname,alowToDatetime FROM "+Conf.sqlite['userTable']+" WHERE isAdmin = '1' or isAdmin = '0'")
            rows = cursor.fetchall()
            for row in rows:
                print('chatID'+str(row[0])+'firstname'+str(row[1])+'lastname'+str(row[2])+ 'alowToDatetime'+str(row[3]))
                user = {'chatID':row[0],'firstname':row[1],'lastname':row[2], 'alowToDatetime':row[3]}
                if self.isAlowed(user['chatID']) == 1:
                    print('hallo')
                    users.append(user)
        except Error as e:
            print(str(e)+" SQL-Query:"+str(sql))
        except Exception as e:
            print(str(e))  
        finally:
            connection.close()
            return users
        
        
        
    
def main():
    user_data = {}
    user_data['chatId'] = str(10010110)
    user_data['firstname'] = 'rolf1'
    user_data['lastname'] = 'tulpe'
    
    user_data2 = {}
    user_data2['chatId'] = str(10011111)
    user_data2['firstname'] = 'rolf2'
    user_data2['lastname'] = 'kolf'
    db = UserDatabase()
    db.insertNewUser(user_data,0)
    db.insertNewUser(user_data2,2)
    print('isAlowed:'+str(db.isAlowed(user_data['chatId'])))
    print('isAlowed:'+str(db.isAlowed(user_data2['chatId'])))
    print('isAlowed:'+str(db.isAlowed(str(1))))
    print('existUser:'+str(db.existUser(user_data['chatId'])))
    print('existUser:'+str(db.existUser(user_data2['chatId'])))
    
    users = db.getAllUsers()
    print('users:'+str(len(users)))
    for y in range(len(users)):
        print("Request "+str(users[y]['chatID'])+": "+str(users[y]['firstname'])+" "+str(users[y]['lastname']))
        

if __name__ == '__main__':
    main()