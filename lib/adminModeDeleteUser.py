#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, imp
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("conf", "../conf.py")
import conf as Conf
load_src("userDatabaseLib", "userDatabaseLib.py")
from userDatabaseLib import UserDatabase

#Funktionen hier registrieren 
# Funktionen Map{ Funk-Name: Tastertur beschriftung}
tastertur = {
         'quit': 'Abbrechen'}
#Funktionen Map{Funk-Name, Beschreiung in Help}
textbefehl = {'help': 'Zeigt diesen Text an',
         'quit': 'Abbrechen'}


def loeschen(bot, update, user_data,markupList):
    #todo: muss weiteren Workflow schreiben
    text = userList()
    update.message.reply_text("Noch nicht Implementiert. \n"
                              +text[str(len(text))],
        reply_markup=user_data['keyboard'])
    return user_data['status']

def quit(bot, update, user_data, markupList):
    user_data['keyboard'] = markupList[Conf.OneModeListID['ADMIN']]
    update.message.reply_text("Löschen abgebrochen...",
            reply_markup=user_data['keyboard'])
    user_data['status'] = Conf.OneModeListID['ADMIN']
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
    textFromUser = update.message.text
    
    userDB = UserDatabase()
    text = userDB.userList()
    #TODO: ExceptionHandlich funktioniert leider noch nicht richtig!!!!
    try:
        i = int(textFromUser)
        if i > 0 and i <= len(text):
            #User i löschen?
            print("chatID? = "+str(text[i]))
            user = userDB.getAllUsers(text[i])
            
            update.message.reply_text(
                'Möchtest du '+str(user['firstname'])+' '+str(user['lastname'])+' die Rechte entfernen?',
                reply_markup=user_data['keyboard'])
            
        else:
            raise ValueError('i is not in range')
    except ValueError:
        #Handle the exception
        #print 'Please enter an integer'
        update.message.reply_text(
                'Bitte gebe eine Zahl von 1 bis '+str(len(text))+' ein, drücke auf "Abbrechen" oder schreibe /quit : \n'+
                 +text[str(len(text))]+' ',
                reply_markup=user_data['keyboard'])
        
    
    return user_data['status']

#TODO: Classenname zu String umwandeln

class Error(Exception):
    """Base class for exceptions in this module."""
    pass