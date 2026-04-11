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


    
async def displayUsers(update, context, markupList):
    userDB = UserDatabase()
    text = userDB.userList()
    await update.message.reply_text("Hier die Liste aller aktiven User \n \n"
                              +text[str(len(text))],
        reply_markup=user_data['keyboard'])
    return user_data['status']

async def deleteUsers(update, context, markupList):
    #todo: muss weiteren Workflow schreiben
    userDB = UserDatabase()
    text = userDB.userList()
    user_data['keyboard'] = markupList[Conf.OneModeListID['ADMINDELETE']]
    user_data['status'] = Conf.OneModeListID['ADMINDELETE']
    await update.message.reply_text("Bitte wähle den zu löschenden User aus in dem du einen dessen Nummer schickst: \n \n"
                              +text[str(len(text))],
        reply_markup=user_data['keyboard'])
    return user_data['status']

async def quit(update, context, markupList):
    user_data['keyboard'] = markupList[Conf.OneModeListID['LIGHT']]
    await update.message.reply_text("EXIT --ADMINMODE--",
            reply_markup=user_data['keyboard'])
    user_data['status'] = Conf.OneModeListID['LIGHT']
    return user_data['status']

async def nextRequest(update, context, markupList):
    userDB = UserDatabase()
    nextRequest = userDB.getNextRequest()
    if nextRequest['chatID'] is not None:
        user_data['keyboard'] = markupList[Conf.OneModeListID['ADMINREQUEST']]
        user_data['status'] = Conf.OneModeListID['ADMINREQUEST']
        user_data['userRequest'] = nextRequest
        await update.message.reply_text("Request "+str(nextRequest['chatID'])+": "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname']),
            reply_markup=user_data['keyboard'])
    else:
        user_data['keyboard'] = markupList[Conf.OneModeListID['ADMIN']]
        user_data['status'] = Conf.OneModeListID['ADMIN']
        user_data['userRequest'] = nextRequest
        await update.message.reply_text("No request.",
            reply_markup=user_data['keyboard'])
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
    return await help(update, context, markupList)

#TODO: Classenname zu String umwandeln