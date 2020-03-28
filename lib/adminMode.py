#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, imp
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("conf", "../conf.py")
import conf as Conf
load_src("userDatabaseLib", "userDatabaseLib.py")
from userDatabaseLib import UserDatabase

#Funktionen hier registrieren für Partymode
# Funktionen Map{ Funk-Name: Tastertur beschriftung}
tastertur = {'nextRequest': 'nächster Request',
         'displayUsers': 'Zeige alle User',
         'deleteUsers': 'Lösche User',
         'quit': 'Verlasse AdminMode'}
#Funktionen Map{Funk-Name, Beschreiung in Help}
textbefehl = {'nextRequest': 'Zeigt nächsten Request',
         'displayUsers': 'Zeigt alle User',
         'deleteUsers': 'Lösche User',
         'quit': 'Verlasse AdminMode'}

def displayUsers(bot, update, user_data, markupList):
    userDB = UserDatabase()
    userList = userDB.getAllUsers()
    text = 'Nr. - Name bis Zugriff \n'
    x = 1
    #print(userList)
    for user in userList:
        text = text +''+str(x)+' - '+str(user['firstname'])+' '+str(user['lastname']) +' bis '+str(user['alowToDatetime'])[0:10]+' \n'
        x = x+1
        
    update.message.reply_text("Hier die Liste aller aktiven User \n \n"
                              +text,
        reply_markup=user_data['keyboard'])
    return user_data['status']

def deleteUsers(bot, update, user_data,markupList):
    #todo: muss user auflisten zum auswählen
    update.message.reply_text("Nicht implementiert",
        reply_markup=user_data['keyboard'])
    return user_data['status']

def quit(bot, update, user_data, markupList):
    user_data['keyboard'] = markupList[Conf.OneModeListID['LIGHT']]
    update.message.reply_text("EXIT --ADMINMODE--",
            reply_markup=user_data['keyboard'])
    user_data['status'] = Conf.OneModeListID['LIGHT']
    return user_data['status']

def nextRequest(bot, update, user_data, markupList):
    userDB = UserDatabase()
    nextRequest = userDB.getNextRequest()
    if nextRequest['chatID'] is not None:
        user_data['keyboard'] = markupList[Conf.OneModeListID['ADMINREQUEST']]
        user_data['status'] = Conf.OneModeListID['ADMINREQUEST']
        user_data['userRequest'] = nextRequest
        update.message.reply_text("Request "+str(nextRequest['chatID'])+": "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname']),
            reply_markup=user_data['keyboard'])
    else:
        user_data['keyboard'] = markupList[Conf.OneModeListID['ADMIN']]
        user_data['status'] = Conf.OneModeListID['ADMIN']
        user_data['userRequest'] = nextRequest
        update.message.reply_text("No request.",
            reply_markup=user_data['keyboard'])
    return user_data['status']

#TODO: Classenname zu String umwandeln