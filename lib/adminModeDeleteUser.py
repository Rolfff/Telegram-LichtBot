#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import importlib.util
def load_src(name, fpath):
    try:
        full_path = os.path.join(os.path.dirname(__file__), fpath)
        spec = importlib.util.spec_from_file_location(name, full_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[name] = module  # Register in sys.modules
            return module
        else:
            print(f"Could not create spec for {name} from {full_path}")
            return None
    except Exception as e:
        print(f"Error loading module {name} from {fpath}: {e}")
        return None
 
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


async def loeschen(update, context, markupList):
    #todo: muss weiteren Workflow schreiben
    text = userList()
    await update.message.reply_text("Noch nicht Implementiert. \n"
                              +text[str(len(text))],
        reply_markup=user_data['keyboard'])
    return user_data['status']

async def quit(update, context, markupList):
    user_data['keyboard'] = markupList[Conf.OneModeListID['ADMIN']]
    await update.message.reply_text("Löschen abgebrochen...",
            reply_markup=user_data['keyboard'])
    user_data['status'] = Conf.OneModeListID['ADMIN']
    return user_data['status']

async def help(update, context, markupList):
    text=''
    for key,value in textbefehl.items():
        text=text+'- /'+key+' '+value+'\n'
            
    await update.message.reply_text(
                'Nutze das Keyboard für Admin-Aktionen: \n'+
                 str(text)+' ',
                reply_markup=user_data['keyboard'])
    return user_data['status']

async def default(update, context, markupList):
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
            
            await update.message.reply_text(
                'Möchtest du '+str(user['firstname'])+' '+str(user['lastname'])+' die Rechte entfernen?',
                reply_markup=user_data['keyboard'])
            
        else:
            raise ValueError('i is not in range')
    except ValueError:
        #Handle the exception
        #print 'Please enter an integer'
        await update.message.reply_text(
                'Bitte gebe eine Zahl von 1 bis '+str(len(text))+' ein, drücke auf "Abbrechen" oder schreibe /quit : \n'+
                 +text[str(len(text))]+' ',
                reply_markup=user_data['keyboard'])
        
    
    return user_data['status']

#TODO: Classenname zu String umwandeln

class Error(Exception):
    """Base class for exceptions in this module."""
    pass