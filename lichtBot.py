#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, filters, PrefixHandler,
                          ConversationHandler, Application, ApplicationBuilder)
from lib.lampeLib import light
import logging
import conf as Conf
from lib.tempDatabaseLib import TempDatabase
from lib.userDatabaseLib import UserDatabase
from lib.tempPlotLib import TempPlot
import datetime as DT
from lib.partyModeThread import PartyMode
import lib.partyMode as ModiLib
import lib.adminMode as AdminMode
import lib.adminModeDeleteUser as AdminModeDeleteUser
import wledpy.wled as wled


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.ERROR)

logger = logging.getLogger(__name__)

#LOGIN = 0 , LIGHT = 1, ...
LOGIN, LIGHT, ADMIN, ADMINREQUEST, GETDAYS, PARTY, ADMINDELETE = range(7)
Conf.OneModeListID = {'LOGIN':LOGIN,
                'LIGHT':LIGHT,
                'ADMIN':ADMIN,
                'ADMINREQUEST':ADMINREQUEST,
                'GETDAYS':GETDAYS,
                'PARTY':PARTY,
                'ADMINDELETE':ADMINDELETE}
#Modi Klassennamen zu den Statusen
modeList = [None,None,AdminMode,None,None,PartyMode,AdminModeDeleteUser]

reply_keyboard_login = [['Login', 'Bye',],
                        ['Sensor']]
reply_keyboard_light_Abo = [['Licht an', 'Licht aus'],
                        ['Sensor','Abo','Logout']]
reply_keyboard_light_quitAbo = [['Licht an', 'Licht aus'],
                        ['Sensor','quit Abo','Logout']]
reply_keyboard_adminRequest = [['Ja', 'Löschen']]
reply_keyboard_quit = [['Abbrechen']]

#TODO umkofigurierem zu einer Liste mit IPs
#schreibtisch = wled.Wled(Conf.wled.get('ip', None))


def buildKeyboard(classs):
    temp=[]
    reply_keyboard=[]
    i=0
    for v in classs.tastertur.values():
        temp.append(v)
        i=i+1
        if i % 3 == 0:
            reply_keyboard.append(temp)
            temp=[]
    reply_keyboard.append(temp)
    return reply_keyboard

def getMarkup(user_data):
    if modeList[user_data['status']] is None:
        print("Keine Klasse an Stelle "+ str(user_data['status']) +"gefunden")
        return None
    else:
        reply_keyboard = buildKeyboard(modeList[user_data['status']])
        return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

#TODO in Partymode auslagern
reply_keyboard_party = buildKeyboard(ModiLib)
temp=['Verlasse PartyMode']
reply_keyboard_party.append(temp)

def getMarkupList(user_data):
    if user_data['wetterAbo'] == 1:
        reply_keyboard_light = reply_keyboard_light_quitAbo
    else:
        reply_keyboard_light = reply_keyboard_light_Abo
        
    markup = {LOGIN:ReplyKeyboardMarkup(reply_keyboard_login, one_time_keyboard=True),
            LIGHT:ReplyKeyboardMarkup(reply_keyboard_light, one_time_keyboard=True),
            ADMIN:ReplyKeyboardMarkup(buildKeyboard(AdminMode), one_time_keyboard=True),
            ADMINREQUEST:ReplyKeyboardMarkup(reply_keyboard_adminRequest, one_time_keyboard=True),
            GETDAYS:ReplyKeyboardMarkup(reply_keyboard_quit, one_time_keyboard=True),
            PARTY:ReplyKeyboardMarkup(reply_keyboard_party, one_time_keyboard=True)}
    #GEgen none testen
    for x in range(len(modeList)):
        if modeList[x] is not None:
            markup[x] = ReplyKeyboardMarkup(buildKeyboard(modeList[x]), one_time_keyboard=True)
    return markup

#TODO: Nach einander in neue Funktionen umschreiben
markup_login = ReplyKeyboardMarkup(reply_keyboard_login, one_time_keyboard=True)
markup_light = ReplyKeyboardMarkup(reply_keyboard_light_Abo, one_time_keyboard=True)
markup_admin = ReplyKeyboardMarkup(buildKeyboard(AdminMode), one_time_keyboard=True)
markup_adminRequest = ReplyKeyboardMarkup(reply_keyboard_adminRequest, one_time_keyboard=True)
markup_quit = ReplyKeyboardMarkup(reply_keyboard_quit, one_time_keyboard=True)
markup_party = ReplyKeyboardMarkup(reply_keyboard_party, one_time_keyboard=True)

licht = light()

def checkAthentifizierung(update,user_data):
    userDB = UserDatabase()
    if user_data['chatId'] != Conf.telegram['adminChatID']:
        ret = userDB.isAlowed(user_data['chatId'])
    else:
        ret = 1
        if userDB.existUser(user_data['chatId']) == 0:
            userDB.insertNewUser(user_data,0)
    user_data['isAlowed'] = ret
    #print('ret'+str(ret))
    if ret == 0:
        user_data['keyboard'] = getMarkupList(user_data)[LOGIN]
        user_data['status'] = LOGIN
        return LOGIN
    else:
        if ret == 1 and user_data['status'] == LOGIN:
            user_data['keyboard'] = getMarkupList(user_data)[LIGHT]
            user_data['status'] = LIGHT
        #else:
            #nichts
    

def inilasizeChatData(message,user_data):
    userDB = UserDatabase()
    #userDB.deleteUser(str(message.chat.id))
    user_data['langCode'] = str(message.from_user.language_code)
    user_data['chatId'] = str(message.chat.id)
    user_data['firstname'] = str(message.from_user.first_name)
    user_data['lastname'] = str(message.from_user.last_name)
    user_data['keyboard'] = markup_login
    user_data['status'] = LOGIN
    user_data['userRequest'] = None
    if userDB.existUser(user_data['chatId']):
        user_data['wetterAbo'] = userDB.getWetterAbo(user_data['chatId'])
        getMarkupList(user_data)[LIGHT]
    else :
        user_data['wetterAbo'] = 0
    print('chatID:'+user_data['chatId']+' Username: '+user_data['firstname']+' '+user_data['lastname']);
    
async def switchWetterAbo(update, context):
    user_data = context.user_data
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        userDB = UserDatabase()
        if user_data['wetterAbo'] == 1:
            userDB.updateWetterAbo(user_data['chatId'],0)
            user_data['wetterAbo'] = 0
            text='OK. Du bekommst keine Meldungen mehr, wenn sich die Temperaturen unterscheiden.'
        else:
            userDB.updateWetterAbo(user_data['chatId'],1)
            user_data['wetterAbo'] = 1
            text='Ich melde mich bei dir sobald es draußen wärmer oder kälter ist als im Zimmer.'
        user_data['keyboard'] = getMarkupList(user_data)[LIGHT]
    else:
        text='Du hast leider keine Berechtiungen für diese Funktion.'
    await update.message.reply_text(
        text,
        reply_markup=user_data['keyboard'])
    return user_data['status']

async def getSensorDays(update, context, args):
    user_data = context.user_data
    text = update.message.text
    
    try:
        days = int(args[0])
        await getSensor(update, context, days)
        
    except ValueError as e:
        await update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
            reply_markup=user_data['keyboard'])
        return user_data['status']
    except Exception as e:
        await update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
            reply_markup=user_data['keyboard'])
        return user_data['status']
   
    
async def getSensor(update, context, days=Conf.tempExport['days']):
    user_data = context.user_data
    checkAthentifizierung(update,user_data)
    tmpDB = TempDatabase()
    werte = tmpDB.getValue()
    maxSavedDaysInDB = Conf.sqlite['deleteAfterWeeks']*7
    if(days > maxSavedDaysInDB):
        context.bot.send_message(chat_id=user_data['chatId'], 
                  text='In der Datenbank sind nur '+str(maxSavedDaysInDB)+' Tage verfügbar.'
                  )
        days = maxSavedDaysInDB
    if(days <= 0):
        days = Conf.tempExport['days']
        context.bot.send_message(chat_id=user_data['chatId'], 
                  text='Weniger als einen Tag geht leider nicht.\n Ich bin großzügig und gebe dir '+str(days)+' Tage.'
                  )
        
    
    try:
        plot = TempPlot()
        plot.plot(tmpDB,days)
    
        context.bot.send_photo(chat_id=user_data['chatId'], photo=open(Conf.tempExport['file'], 'rb'))
    except Exception as e:
        context.bot.send_message(chat_id=user_data['chatId'], 
                  text='Error: '+str(e) 
                  )
    finally:
        if werte == None:
            await update.message.reply_text(
                'Keine Werte in der Datenbank gefunden. Bitte überprüfe den "storeTemp_POST.py" cron-job.',
                reply_markup=user_data['keyboard'])
        else:
            await update.message.reply_text(
                'Werte: \n Time:'+str(werte['datetime'])+'\n Temperatur (blau):'+str(werte['temp'])+' Grad \n rel. Luftfeuchtigkeit (Orange):'+str(werte['hum']) +'%\n Außentemperatur (Grün):'+str(werte['dwdtemp'])+' Grad \n rel. Luftfeuchtigkeit außen (Rot):'+str(werte['dwdhum'])+'%',
                reply_markup=user_data['keyboard'])
    return user_data['status']

async def start(update, context):
    user_data = context.user_data
    inilasizeChatData(update.message, user_data)
    await update.message.reply_text(
        "Hi "+update.message.from_user.first_name+"! ")
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        await update.message.reply_text("Willkommen zurück ;P",
            reply_markup=user_data['keyboard'])
        return user_data['status']
    else:
        return await getPasswort(update, context)

async def getPasswort(update, context):
    user_data = context.user_data
    await update.message.reply_text(
        "Bitte gib dein Passwort ein",
            reply_markup=getMarkupList(user_data)[LOGIN])
    return LOGIN

async def checkPasswort(update, context):
    user_data = context.user_data
    passwort = update.message.text
    print('m'+passwort)
    if passwort == Conf.telegram['passwort']:
        if user_data['chatId'] == Conf.telegram['adminChatID']:
            userDB = UserDatabase()
            userDB.insertNewUser(user_data,0)
            user_data['keyboard'] = getMarkupList(user_data)[LIGHT]
            user_data['status'] = LIGHT
            await update.message.reply_text(
                'Du kannst jetzt das Licht steuern.',
                reply_markup=user_data['keyboard'])
            return LIGHT
        else:
            #kein Admin
            userDB = UserDatabase()
            userDB.insertNewUser(user_data,0)
            context.bot.send_message(Conf.telegram['adminChatID'],text='Request: '+user_data['firstname']+' '+user_data['lastname']+' möchte auf dein Licht im Zimmer zugreifen. Möchtest du in den Admin-Modus wechseln?')
            context.bot.send_message(Conf.telegram['adminChatID'],text='Antworte: /admin')
            context.bot.send_message(user_data['chatId'],text='Der Admin wurde benachrichtigt.')
            await update.message.reply_text(
                'Falls der Admin nicht schnell genug reagiert, gib das Passwort bitte noch einmal ein um den Admin an die Freigebe zu erinnern.',
                reply_markup=getMarkupList(user_data)[LOGIN])
            return LOGIN
    else:
        await update.message.reply_text(
            'Das Passwort ist falsch.',
            reply_markup=getMarkupList(user_data)[LOGIN])
        return LOGIN
    
async def checkRechte(update, context):
    user_data = context.user_data
    checkAthentifizierung(update, user_data)
    await update.message.reply_text("Viel spaß!",
            reply_markup=user_data['keyboard'])
    return user_data['status']

async def switchToAdminModus(update, context):
    user_data = context.user_data
    if user_data['chatId'] == Conf.telegram['adminChatID']:
        user_data['keyboard'] = getMarkupList(user_data)[ADMIN]
        user_data['status'] = ADMIN
        await update.message.reply_text("-->ADMINMODE<--",
                                  reply_markup=user_data['keyboard'])
        return user_data['status']
    else:
        await update.message.reply_text('Sorry, du hast leider keine Admin-Rechte.')

#TODO  Alle Bot-Stati in solche Funktionen umschreiben/auslagern
async def selectModeFunc(update, context):
    user_data = context.user_data
    if modeList[user_data['status']] is None:
        await update.message.reply_text(
                'Interner Error: Keine Klasse gefunden in modeList an Stelle "'+str(user_data['status'])+'".\n',
                reply_markup=user_data['keyboard'])
    else:
        classs = modeList[user_data['status']]
        
        textFromUser = update.message.text
        checkAthentifizierung(update,user_data)
        if user_data['isAlowed'] == 1:
            funkName=None
            #Suche nach FunktionsName ([1:] entfernt / am Anfang der Zeichenkette)
            if textFromUser[1:] in classs.tastertur or textFromUser[1:] in classs.textbefehl:
                funkName=textFromUser[1:]
            #Suche über Button-Beschriftung
            elif textFromUser in classs.tastertur.values():
                for key, value in classs.tastertur.items():
                    if value == textFromUser:
                        funkName=key
            if funkName is None:
                #if exist Fuction defoult?
                try:
                    funcRet = getattr(classs, 'default')(context.bot, update, user_data,getMarkupList(user_data))
                    user_data['status'] = funcRet
                except Error as e:
                    print(str(e)+" Keine Funktion 'default' in "+str(classs)+" gefunden.")    
                    await update.message.reply_text(
                        'Modus: "'+textFromUser+'" wurde leider nicht gefunden.\n'+
                        'Versuche es mal mit /help.\n',
                        reply_markup=user_data['keyboard'])
            else:
                if user_data['chatId'] != Conf.telegram['adminChatID']:
                    context.bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat Funktion "+str(classs)+"."+funkName+" an geschaltet.")
                
                funcRet = getattr(classs, str(funkName))(context.bot, update, user_data,getMarkupList(user_data))
                user_data['status'] = funcRet
                
    return user_data['status']
    
async def quitSpecialMode(update, context):
    user_data = context.user_data
    user_data['keyboard'] = getMarkupList(user_data)[LIGHT]
    if user_data['status'] == PARTY:
        await update.message.reply_text("EXIT --PARTYMODE--",
            reply_markup=user_data['keyboard'])
    if user_data['status'] == ADMIN:
        await update.message.reply_text("EXIT --ADMINMODE--",
            reply_markup=user_data['keyboard'])
    user_data['status'] = LIGHT
    return user_data['status']

async def switchToPartyModus(update, context):
    user_data = context.user_data
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        user_data['keyboard'] = getMarkupList(user_data)[PARTY]
        user_data['status'] = PARTY
        await update.message.reply_text("-->PARTYMODE<--",
                                  reply_markup=user_data['keyboard'])
        return user_data['status']
    else:
        await update.message.reply_text('Sorry, du hast leider keine Rechte.')

async def allowUser(update, context):
    user_data = context.user_data
    user_data['keyboard'] = getMarkupList(user_data)[GETDAYS]
    user_data['status'] = GETDAYS
    nextRequest = user_data['userRequest']
    await update.message.reply_text("Wieviel Tage soll "+str(nextRequest['firstname'])+" zugriff auf die Lampe haben? Bitte gebe eine natürliche Zahl ein oder /quit .",
        reply_markup=user_data['keyboard'])
    return user_data['status']

async def updateUser(update, context):
    user_data = context.user_data
    text = update.message.text
    print(str(text))
    user_data['keyboard'] = getMarkupList(user_data)[ADMIN]
    user_data['status'] = ADMIN
    nextRequest = user_data['userRequest']
    try:
        days_ = int(text)
        userDB = UserDatabase()
        userDB.updateUserDays(nextRequest['chatID'],days_)
        today = DT.date.today()
        futureDay = today + DT.timedelta(days=days_)
        await update.message.reply_text("User: "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname'])+ " erlaubt bis "+str(futureDay)+".",
            reply_markup=user_data['keyboard'])
        await context.bot.send_message(nextRequest['chatID'],text="Der Admin hat dir bis zum "+str(futureDay)+" eingeräumt die Lampe zu steuern. Bitte schreibe mir /letsgo !")
    except ValueError as e:
        await update.message.reply_text("Error "+str(e)+" User: "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname'])+ " nicht freigegeben. Bitte versuche es nochmal.",
            reply_markup=user_data['keyboard'])
    except Exception as e:
        await update.message.reply_text("Error "+str(e)+" User: "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname'])+ " nicht freigegeben. Bitte versuche es nochmal.",
            reply_markup=user_data['keyboard'])
    finally:
        user_data['userRequest'] = None
        return user_data['status']

async def deletUser(update, context):
    user_data = context.user_data
    user_data['keyboard'] = getMarkupList(user_data)[ADMIN]
    user_data['status'] = ADMIN
    nextRequest = user_data['userRequest']
    userDB = UserDatabase()
    userDB.deleteUser(nextRequest['chatID'])
    user_data['userRequest'] = None
    await update.message.reply_text("User "+str(nextRequest['chatID'])+": "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname'])+" wurde gelöscht.",
        reply_markup=user_data['keyboard'])
    return user_data['status']

async def exitAdminRequest(update, context):
    user_data = context.user_data
    user_data['userRequest'] = None
    user_data['keyboard'] = getMarkupList(user_data)[ADMIN]
    user_data['status'] = ADMIN
    await update.message.reply_text("Request abgebrochen",
        reply_markup=user_data['keyboard'])
    return user_data['status']

#TODO  Alle Bot-Stati in solche Funktionen umschreiben/auslagern
async def selectPartyModi(update, context):
    user_data = context.user_data
    textFromUser = update.message.text
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        funkName=None
        #Suche nach FunktionsName ([1:] entfernt / am Anfang der Zeichenkette)
        if textFromUser[1:] in ModiLib.tastertur or textFromUser[1:] in ModiLib.textbefehl:
            funkName=textFromUser[1:]
        #Suche über Button-Beschriftung
        elif textFromUser in ModiLib.tastertur.values():
            for key, value in ModiLib.tastertur.items():
                if value == textFromUser:
                    funkName=key
        if funkName is None:
            await update.message.reply_text(
                'Modus: "'+textFromUser+'" wurde leider nicht gefunden.\n'+
                'Versuche es mal mit /help.\n',
                reply_markup=user_data['keyboard'])
        else:
            if user_data['chatId'] != Conf.telegram['adminChatID']:
                context.bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat das "+funkName+" an geschaltet.")
            textOfSpeeds=''
            #Suche Speedempfehlungen raus
            if funkName in ModiLib.speedEmpfehlungen:
                listOfSpeeds = ModiLib.speedEmpfehlungen.get(funkName)
                if listOfSpeeds is not None:
                    textOfSpeeds=('Mit /speed [duble] in Sekunden kannst du die Geschwindigkeit regulieren.\n'+
                        'Aktuelle Geschwindigkeit: '+str(Conf.OneSpeedSingleton)+'\n'+
                        'Folgende Geschwindigkeiten werden empfohlen:\n')
                    for speed in listOfSpeeds:
                        textOfSpeeds=textOfSpeeds+'- /speed '+str(speed)+'\n'
            pm = PartyMode()
            #pm.startModi( 'funkName', wait=0.05,r=0,g=255,b=255)
            pm.startModi(str(funkName), Conf.OneSpeedSingleton,Conf.OneRGB.get('r'),Conf.OneRGB.get('g'),Conf.OneRGB.get('b'))
            await update.message.reply_text(
                'Modus: "'+funkName+'"\n'+
                'Party... wooob!!!,\n '+
                textOfSpeeds,
                reply_markup=user_data['keyboard'])
            
        return user_data['status']
    
async def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    await update.message.reply_text("bye")
    
    user_data.clear()
    return ConversationHandler.END

async def lightOn(update, context):
    user_data = context.user_data
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        if user_data['chatId'] != Conf.telegram['adminChatID']:
            context.bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat das Licht an geschaltet.")
        await update.message.reply_text(
            'Es werde Licht...',
            reply_markup=user_data['keyboard'])
#        if Conf.wled['ip'] != None:
#            schreibtisch.turn_on()
#            schreibtisch.set_color((255,255,255))
        licht.on()
        return user_data['status']
    
async def setSpeed(update, context, args):
    user_data = context.user_data
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        try:
            sp = float(args[0])
            Conf.OneSpeedSingleton = sp
            if user_data['chatId'] != Conf.telegram['adminChatID']:
                context.bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat speed auf "+args[0]+" geändert.")
            await update.message.reply_text(
                'Die Geschwindigkeit wurde auf '+args[0]+' geändert.',
                reply_markup=user_data['keyboard'])
            
        except ValueError as e:
            await update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
                reply_markup=user_data['keyboard'])
        except Exception as e:
            await update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
                reply_markup=user_data['keyboard'])
        finally:
            return user_data['status']
        
async def setRGB(update, context, args):
    user_data = context.user_data
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        try:
            Conf.OneRGB['r'] = int(args[0])
            Conf.OneRGB['g'] = int(args[1])
            Conf.OneRGB['b'] = int(args[2])
            if user_data['chatId'] != Conf.telegram['adminChatID']:
                context.bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat das Licht Rot:"+args[0]+" Grün:"+args[1]+" Blau:"+args[2]+" geschaltet.")
            await update.message.reply_text(
                'Es werde Rot:'+args[0]+' Grün:'+args[1]+' Blau:'+args[2]+' ...',
                reply_markup=user_data['keyboard'])
            
        except ValueError as e:
            await update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
                reply_markup=user_data['keyboard'])
        except Exception as e:
            await update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
                reply_markup=user_data['keyboard'])
        finally:
            return user_data['status']


        
async def rgb(update, context, args):
    user_data = context.user_data
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        try:
            rot = int(args[0])
            grün = int(args[1])
            blau = int(args[2])
            if user_data['chatId'] != Conf.telegram['adminChatID']:
                context.bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat das Licht Rot:"+args[0]+" Grün:"+args[1]+" Blau:"+args[2]+" geschaltet.")
            await update.message.reply_text(
                'Es werde Rot:'+args[0]+' Grün:'+args[1]+' Blau:'+args[2]+' ...',
                reply_markup=user_data['keyboard'])
#            if Conf.wled['ip'] != None:
#                schreibtisch.set_color((rot,grün,blau))
            licht.on(rot,grün,blau)
        except ValueError as e:
            await update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
                reply_markup=user_data['keyboard'])
        except Exception as e:
            await update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
                reply_markup=user_data['keyboard'])
        finally:
            return user_data['status']
    
async def lightOff(update, context):
    user_data = context.user_data
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        if user_data['chatId'] != Conf.telegram['adminChatID']:
            context.bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat das Licht aus geschaltet.") 
        await update.message.reply_text(
            'Licht aus.',
            reply_markup=user_data['keyboard'])
#        if Conf.wled['ip'] != None:
#            schreibtisch.turn_off()
        licht.off()
        return user_data['status']
    
async def help(update, context):
    user_data = context.user_data
    #TODo: In einzelne Modis auslagern
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        if user_data['status'] == LIGHT:
            await update.message.reply_text(
                'Nutze das Keyboard für Standard-Aktionen. \n\n'+
                'Weitere Funktionen: \n'+
                '- /help zeigt diesen Text an \n'+
                '- /rgb 0-255 0-255 0-255 färbt Licht buntisch \n'+
                '- /sensor 1-'+str(Conf.sqlite['deleteAfterWeeks']*7)+' Zeigt Sensordaten für x Tage an \n'+
                '- /admin wechselt in die Userverwaltung \n' +
                '- /party wechselt in den Partymodus ',
                reply_markup=user_data['keyboard'])
        if user_data['status'] == PARTY:
            text='\n Jetzt wird es erst spannend...\n'
            for key,value in ModiLib.textbefehl.items():
                text=text+'- /'+key+' '+value+'\n'
            
            await update.message.reply_text(
                'Nutze das Keyboard für Standard-Aktionen. \n\n'+
                'Weitere Funktionen: \n'+
                '- /help zeigt diesen Text an \n'+
                '- /speed [duble] in Sekunden kannst du die geschwindigkeit regulieren. '+
                'Aktuelle Geschwindigkeit: '+str(Conf.OneSpeedSingleton)+'\n'+
                '- /admin wechselt in die Userverwaltung \n' +
                '- /exit verläst den Partymodus \n' +
                 str(text)+' ',
                reply_markup=user_data['keyboard'])
    return user_data['status']
    
async def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    

def main():
    # Create the Application using ApplicationBuilder
    application = Application.builder().token(Conf.telegram['token']).build()

    # Get the dispatcher to register handlers
    dp = application
    
    #TODO: ModiLib.tastertur in conv_handler intigrieren
    #for key,value in ModiLib.textbefehl.items():
    #            text=text+'- /'+key+' '+value+'\n'
    
    partyList=[     MessageHandler(filters.Regex('^Verlasse PartyMode$'),
                                 quitSpecialMode
                                 ),
                    CommandHandler('speed',
                                   setSpeed,
                                   has_args=True),
                    CommandHandler('admin',
                                   switchToAdminModus
                                   ),
                    CommandHandler('exit',
                                   quitSpecialMode
                                   ),
                    CommandHandler('help',
                                   help
                                   ),
                    CommandHandler('rgb',
                                   setRGB,
                                   has_args=True)   
                ]
    for value in ModiLib.tastertur.values():
               partyList.extend([MessageHandler(filters.Regex('^'+str(value)+'$'),
                                   selectPartyModi,
                                   )])
    for key in ModiLib.textbefehl.keys():
               partyList.extend([CommandHandler(str(key),
                                   selectPartyModi,
                                   )])
    partyList.extend([MessageHandler(filters.TEXT,
                                    help,
                                    )])
    autoStatesHandler={}
    for x in range(len(modeList)):
        
        #GEgen none und Partymode testen
        if modeList[x] is not None and x != PARTY:
            #print(str(x)+"="+str(modeList[x]))
            tempList=[]
            for value in modeList[x].tastertur.values():
               tempList.extend([MessageHandler(filters.Regex('^'+str(value)+'$'),
                                   selectModeFunc,
                                   )])
            for key in modeList[x].textbefehl.keys():
               tempList.extend([CommandHandler(str(key),
                                   selectModeFunc,
                                   )])
            tempList.extend([MessageHandler(filters.TEXT,
                                    selectModeFunc,
                                    )])
            autoStatesHandler[x]=tempList
    
    statess={
            LOGIN: [MessageHandler(filters.Regex('^Login$'),
                                 getPasswort,
                                 ),
                    MessageHandler(filters.Regex('^Bye$'),
                                 done,
                                 ),
                    MessageHandler(filters.Regex('^Sensor$'),
                                 getSensor,
                                 ),
                    CommandHandler('letsgo',
                                   checkRechte,
                                   ),
                    MessageHandler(filters.TEXT,
                                   checkPasswort,
                                   ),
                    ],
            LIGHT: [MessageHandler(filters.Regex('^Logout$'),
                                 done,
                                 ),
                    MessageHandler(filters.Regex('^Sensor$'),
                                 getSensor,
                                 ),
                    MessageHandler(filters.Regex('^Licht an$'),
                                 lightOn,
                                 ),
                    MessageHandler(filters.Regex('^Licht aus$'),
                                 lightOff,
                                 ),
                    MessageHandler(filters.Regex('^Abo$'),
                                 switchWetterAbo,
                                 ),
                    MessageHandler(filters.Regex('^quit Abo$'),
                                 switchWetterAbo,
                                 ),
                    CommandHandler('rgb',
                                   rgb,
                                   has_args=True),
                    CommandHandler('admin',
                                   switchToAdminModus,
                                   ),
                    CommandHandler('help',
                                   help,
                                   ),
                    CommandHandler('party',
                                   switchToPartyModus,
                                   ),
                    CommandHandler('sensor',
                                   getSensorDays,
                                   has_args=True),
                    MessageHandler(filters.TEXT,
                                    help,
                                    )
                    ],
            PARTY:partyList,
            GETDAYS:[MessageHandler(filters.Regex('^Abbrechen$'),
                                 exitAdminRequest,
                                 ),
                    CommandHandler('quit',
                                exitAdminRequest,
                                ),
                    MessageHandler(filters.TEXT,
                                updateUser,
                                )
                    ],
            ADMINREQUEST: [MessageHandler(filters.Regex('^Ja$'),
                                 allowUser,
                                 ),
                    MessageHandler(filters.Regex('^Löschen$'),
                                 deletUser,
                                 ),
                    MessageHandler(filters.Regex('^Abbrechen$'),
                                 exitAdminRequest,
                                 )
                    ],
        }
    #print(autoStatesHandler)
    statess.update(autoStatesHandler)
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',
                                     start,
                                     ),
                      MessageHandler(filters.TEXT,
                                    start,
                                    )
                      ],
        states = statess,
        fallbacks=[MessageHandler(filters.Regex('^Logout$'), done)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    application.run_polling()
    
    if Conf.OneThreadSingleton is not None:
        if Conf.OneThreadSingleton.isRunning:
            Conf.OneThreadSingleton.stop()



if __name__ == '__main__':
    main()