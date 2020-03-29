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
textbefehl = {'nextRequest': 'Zeigt den nächsten User-Request an',
         'displayUsers': 'Zeigt alle User',
         'deleteUsers': 'Lösche User',
         'help': 'Zeigt diesen Text an',
         'quit': 'Verlasse AdminMode'}
#def default fungiert als Funktion die bei freien Texteingaben ausgeführt wird


    
def displayUsers(bot, update, user_data, markupList):
    userDB = UserDatabase()
    text = userDB.userList()
    update.message.reply_text("Hier die Liste aller aktiven User \n \n"
                              +text[str(len(text))],
        reply_markup=user_data['keyboard'])
    return user_data['status']

def deleteUsers(bot, update, user_data,markupList):
    #todo: muss weiteren Workflow schreiben
    userDB = UserDatabase()
    text = userDB.userList()
    user_data['keyboard'] = markupList[Conf.OneModeListID['ADMINDELETE']]
    user_data['status'] = Conf.OneModeListID['ADMINDELETE']
    update.message.reply_text("Bitte wähle den zu löschenden User aus in dem du einen dessen Nummer schickst: \n \n"
                              +text[str(len(text))],
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

def help(bot, update, user_data, markupList):
    text=''
    for key,value in textbefehl.items():
        text=text+'- /'+key+' '+value+'\n'
            
    update.message.reply_text(
                'Nutze das Keyboard für Admin-Aktionen: \n'+
                 str(text)+' ',
                reply_markup=user_data['keyboard'])
    return user_data['status']
    

def default(bot, update, user_data, markupList):
    return help(bot, update, user_data, markupList)

#TODO: Classenname zu String umwandeln