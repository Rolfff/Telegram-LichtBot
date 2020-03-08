#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from lib.lampeLib import light
import logging
import conf as Conf
from lib.tempDatabaseLib import TempDatabase
from lib.userDatabaseLib import UserDatabase
from lib.tempPlot import TempPlot
import datetime as DT
from lib.partyModeLib import PartyMode

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LOGIN, LIGHT, ADMIN, ADMINREQUEST, GETDAYS, PARTY = range(6)

reply_keyboard_login = [['Login', 'Bye',],
                        ['Sensor']]
reply_keyboard_light_Abo = [['Licht an', 'Licht aus'],
                        ['Sensor','Abo','Logout']]
reply_keyboard_light_quitAbo = [['Licht an', 'Licht aus'],
                        ['Sensor','quit Abo','Logout']]
reply_keyboard_admin = [['Nächster Request', 'Zeige alle User'],
                        ['Lösche User','Verlasse AdminMode']]
reply_keyboard_adminRequest = [['Ja', 'Löschen']]
reply_keyboard_quit = [['Abbrechen']]
reply_keyboard_party = [['Farbwechsel horizontal','Verlasse PartyMode']]

markup_login = ReplyKeyboardMarkup(reply_keyboard_login, one_time_keyboard=True)
markup_light = ReplyKeyboardMarkup(reply_keyboard_light_Abo, one_time_keyboard=True)
markup_admin = ReplyKeyboardMarkup(reply_keyboard_admin, one_time_keyboard=True)
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
        user_data['keyboard'] = markup_login
        user_data['status'] = LOGIN
        update.message.reply_text(
            'Ohh... Deine Berechtigung ist abgelaufen.',
            reply_markup=markup_login)
        return LOGIN
    else:
        if ret == 1 and user_data['status'] == LOGIN:
            user_data['keyboard'] = markup_light
            if user_data['wetterAbo'] == 1:
                user_data['keyboard'] = ReplyKeyboardMarkup(reply_keyboard_light_quitAbo, one_time_keyboard=True)

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
        if user_data['wetterAbo'] == 1:
            user_data['keyboard'] = ReplyKeyboardMarkup(reply_keyboard_light_quitAbo, one_time_keyboard=True)

    else :
        user_data['wetterAbo'] = 0
    print('chatID:'+user_data['chatId']+' Username: '+user_data['firstname']+' '+user_data['lastname']);
    
def switchWetterAbo(bot, update, user_data):
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        userDB = UserDatabase()
        if user_data['wetterAbo'] == 1:
            userDB.updateWetterAbo(user_data['chatId'],0)
            user_data['wetterAbo'] = 0
            user_data['keyboard'] = ReplyKeyboardMarkup(reply_keyboard_light_Abo, one_time_keyboard=True)
            text='OK. Du bekommst keine Meldungen mehr, wenn sich die Temperaturen unterscheiden.'
        else:
            userDB.updateWetterAbo(user_data['chatId'],1)
            user_data['wetterAbo'] = 1
            user_data['keyboard'] = ReplyKeyboardMarkup(reply_keyboard_light_quitAbo, one_time_keyboard=True)
            text='Ich melde mich bei dir sobald es draußen wärmer oder kälter ist als im Zimmer.'
    else:
        text='Du hast leider keine Berechtiungen für diese Funktion.'
    update.message.reply_text(
        text,
        reply_markup=user_data['keyboard'])
    return user_data['status']
    
def getSensor(bot,update,user_data):
    checkAthentifizierung(update,user_data)
    tmpDB = TempDatabase()
    werte = tmpDB.getValue()
    try:
        plot = TempPlot()
        plot.plot(tmpDB,Conf.tempExport['days'])
    
        bot.send_photo(chat_id=user_data['chatId'], photo=open(Conf.tempExport['file'], 'rb'))
    except Exception as e:
        bot.send_message(chat_id=user_data['chatId'], 
                  text='Error: '+str(e) 
                  )
    finally:
        update.message.reply_text(
            'Werte: Time:'+str(werte['datetime'])+' Temp:'+str(werte['temp'])+' Hum:'+str(werte['hum']) +' DWD_Temp:'+str(werte['dwdtemp'])+' DWD_Hum:'+str(werte['dwdhum']),
            reply_markup=user_data['keyboard'])
    return user_data['status']

def start(bot, update, user_data):
    inilasizeChatData(update.message, user_data)
    update.message.reply_text(
        "Hi "+update.message.from_user.first_name+"! ")
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        update.message.reply_text("Willkommen zurück ;P",
            reply_markup=user_data['keyboard'])
        return user_data['status']
    else:
        return getPasswort(bot, update, user_data)

def getPasswort(bot, update, user_data):
    update.message.reply_text(
        "Bitte gib dein Passwort ein",
            reply_markup=markup_login)
    return LOGIN

def checkPasswort(bot, update, user_data):
    passwort = update.message.text
    print('m'+passwort)
    if passwort == Conf.telegram['passwort']:
        if user_data['chatId'] == Conf.telegram['adminChatID']:
            userDB = UserDatabase()
            userDB.insertNewUser(user_data,0)
            user_data['keyboard'] = markup_light
            user_data['status'] = LIGHT
            update.message.reply_text(
                'Du kannst jetzt das Licht steuern.',
                reply_markup=markup_light)
            return LIGHT
        else:
            #kein Admin
            userDB = UserDatabase()
            userDB.insertNewUser(user_data,0)
            bot.send_message(Conf.telegram['adminChatID'],text='Request: '+user_data['firstname']+' '+user_data['lastname']+' möchte auf dein Licht im Zimmer zugreifen. Möchtest du in den Admin-Modus wechseln?')
            bot.send_message(Conf.telegram['adminChatID'],text='Antworte: /admin')
            bot.send_message(user_data['chatId'],text='Der Admin wurde benachrichtigt.')
            update.message.reply_text(
                'Falls der Admin nicht schnell genug reagiert, gib das Passwort bitte noch einmal ein um den Admin an die Freigebe zu erinnern.',
                reply_markup=markup_login)
            return LOGIN
    else:
        update.message.reply_text(
            'Das Passwort ist falsch.',
            reply_markup=markup_login)
        return LOGIN
    
def checkRechte(bot, update, user_data):
    checkAthentifizierung(update, user_data)
    update.message.reply_text("Viel spaß!",
            reply_markup=user_data['keyboard'])
    return user_data['status']

def switchToAdminModus(bot, update, user_data):
    if user_data['chatId'] == Conf.telegram['adminChatID']:
        user_data['keyboard'] = markup_admin
        user_data['status'] = ADMIN
        update.message.reply_text("-->ADMINMODE<--",
                                  reply_markup=user_data['keyboard'])
        return user_data['status']
    else:
        update.message.reply_text('Sorry, du hast leider keine Admin-Rechte.')

def nextRequest(bot, update, user_data):
    userDB = UserDatabase()
    nextRequest = userDB.getNextRequest()
    if nextRequest['chatID'] is not None:
        user_data['keyboard'] = markup_adminRequest
        user_data['status'] = ADMINREQUEST
        user_data['userRequest'] = nextRequest
        update.message.reply_text("Request "+str(nextRequest['chatID'])+": "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname']),
            reply_markup=user_data['keyboard'])
    else:
        user_data['keyboard'] = markup_admin
        user_data['status'] = ADMIN
        user_data['userRequest'] = nextRequest
        update.message.reply_text("No request.",
            reply_markup=user_data['keyboard'])
    return user_data['status']

def allowUser(bot, update, user_data):
    user_data['keyboard'] = markup_quit
    user_data['status'] = GETDAYS
    nextRequest = user_data['userRequest']
    update.message.reply_text("Wieviel Tage soll "+str(nextRequest['firstname'])+" zugriff auf die Lampe haben? Bitte gebe eine natürliche Zahl ein oder /quit .",
        reply_markup=user_data['keyboard'])
    return user_data['status']

def updateUser(bot, update, user_data):
    text = update.message.text
    print(str(text))
    user_data['keyboard'] = markup_admin
    user_data['status'] = ADMIN
    nextRequest = user_data['userRequest']
    try:
        days_ = int(text)
        userDB = UserDatabase()
        userDB.updateUserDays(nextRequest['chatID'],days_)
        today = DT.date.today()
        futureDay = today + DT.timedelta(days=days_)
        update.message.reply_text("User: "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname'])+ " erlaubt bis "+str(futureDay)+".",
            reply_markup=user_data['keyboard'])
        bot.send_message(nextRequest['chatID'],text="Der Admin hat dir bis zum "+str(futureDay)+" eingeräumt die Lampe zu steuern. Bitte schreibe mir /letsgo !")
    except ValueError as e:
        update.message.reply_text("Error "+str(e)+" User: "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname'])+ " nicht freigegeben. Bitte versuche es nochmal.",
            reply_markup=user_data['keyboard'])
    except Exception as e:
        update.message.reply_text("Error "+str(e)+" User: "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname'])+ " nicht freigegeben. Bitte versuche es nochmal.",
            reply_markup=user_data['keyboard'])
    finally:
        user_data['userRequest'] = None
        return user_data['status']

def deletUser(bot, update, user_data):
    user_data['keyboard'] = markup_admin
    user_data['status'] = ADMIN
    nextRequest = user_data['userRequest']
    userDB = UserDatabase()
    userDB.deleteUser(nextRequest['chatID'])
    user_data['userRequest'] = None
    update.message.reply_text("User "+str(nextRequest['chatID'])+": "+str(nextRequest['firstname'])+" "+str(nextRequest['lastname'])+" wurde gelöscht.",
        reply_markup=user_data['keyboard'])
    return user_data['status']

def exitAdminRequest(bot, update, user_data):
    user_data['userRequest'] = None
    user_data['keyboard'] = markup_admin
    user_data['status'] = ADMIN
    update.message.reply_text("Request abgebrochen",
        reply_markup=user_data['keyboard'])
    return user_data['status']
    
def displayUsers(bot, update, user_data):
    #todo
    update.message.reply_text("Nicht implementiert",
        reply_markup=user_data['keyboard'])
    return user_data['status']

def deleteUsers(bot, update, user_data):
    #todo: muss user auflisten zum auswählen
    update.message.reply_text("Nicht implementiert",
        reply_markup=user_data['keyboard'])
    return user_data['status']
    
def quitSpecialMode(bot, update, user_data):
    user_data['keyboard'] = markup_light
    if user_data['status'] == PARTY:
        update.message.reply_text("EXIT --PARTYMODE--",
            reply_markup=user_data['keyboard'])
    if user_data['status'] == ADMIN:
        update.message.reply_text("EXIT --ADMINMODE--",
            reply_markup=user_data['keyboard'])
    user_data['status'] = LIGHT
    return user_data['status']

def switchToPartyModus(bot, update, user_data):
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        user_data['keyboard'] = markup_party
        user_data['status'] = PARTY
        update.message.reply_text("-->PARTYMODE<--",
                                  reply_markup=user_data['keyboard'])
        return user_data['status']
    else:
        update.message.reply_text('Sorry, du hast leider keine Rechte.')

def changeColorHorizontal(bot, update, user_data):
 #   update.message.reply_text(
 #               'Hat leider noch eine bug.\n ',
 #               reply_markup=user_data['keyboard'])
 #   return user_data['status']

    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        if user_data['chatId'] != Conf.telegram['adminChatID']:
                bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat das ChangeColorHorizontal an geschaltet.")
        
        
        update.message.reply_text(
                'Party... wooob!!!,\n '+
                'Mit /speed [duble] in Sekunden kannst du die geschwindigkeit regulieren.\n'+
                'Aktuelle Geschwindigkeit: '+str(Conf.OneSpeedSingleton),
                reply_markup=user_data['keyboard'])
        pm = PartyMode()
        pm.regenbogenHorizontal()
        
        return user_data['status']

def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("bye")
    
    user_data.clear()
    return ConversationHandler.END

def lightOn(bot, update, user_data):
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        if user_data['chatId'] != Conf.telegram['adminChatID']:
            bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat das Licht an geschaltet.")
        update.message.reply_text(
            'Es werde Licht...',
            reply_markup=user_data['keyboard'])
        licht.on()
        return user_data['status']
    
def setSpeed(bot, update, user_data, args):
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        try:
            sp = float(args[0])
            Conf.OneSpeedSingleton = sp
            if user_data['chatId'] != Conf.telegram['adminChatID']:
                bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat speed auf "+args[0]+" geändert.")
            update.message.reply_text(
                'Die Geschwindigkeit wurde auf '+args[0]+' geändert.',
                reply_markup=user_data['keyboard'])
            
        except ValueError as e:
            update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
                reply_markup=user_data['keyboard'])
        except Exception as e:
            update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
                reply_markup=user_data['keyboard'])
        finally:
            return user_data['status']
        
def rgb(bot, update, user_data, args):
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        try:
            rot = int(args[0])
            grün = int(args[1])
            blau = int(args[2])
            if user_data['chatId'] != Conf.telegram['adminChatID']:
                bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat das Licht Rot:"+args[0]+" Grün:"+args[1]+" Blau:"+args[2]+" geschaltet.")
            update.message.reply_text(
                'Es werde Rot:'+args[0]+' Grün:'+args[1]+' Blau:'+args[2]+' ...',
                reply_markup=user_data['keyboard'])
            licht.on(rot,grün,blau)
        except ValueError as e:
            update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
                reply_markup=user_data['keyboard'])
        except Exception as e:
            update.message.reply_text("Error "+str(e)+" Bitte versuche es nochmal.",
                reply_markup=user_data['keyboard'])
        finally:
            return user_data['status']
    
def lightOff(bot, update, user_data):
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        if user_data['chatId'] != Conf.telegram['adminChatID']:
            bot.send_message(Conf.telegram['adminChatID'],text=user_data['firstname']+" hat das Licht aus geschaltet.") 
        update.message.reply_text(
            'Licht aus.',
            reply_markup=user_data['keyboard'])
        licht.off()
        return user_data['status']
    
def help(bot,update, user_data):
    checkAthentifizierung(update,user_data)
    if user_data['isAlowed'] == 1:
        if user_data['status'] == LIGHT:
            update.message.reply_text(
                'Nutze das Keyboard für Standard-Aktionen. \n\n'+
                'Weitere Funktionen: \n'+
                '- /help zeigt diesen Text an \n'+
                '- /rgb 0-255 0-255 0-255 färbt Licht buntisch \n'+
                '- /admin wechselt in die Userverwaltung \n' +
                '- /party wechselt in den Partymodus ',
                reply_markup=user_data['keyboard'])
        if user_data['status'] == PARTY:
            
            update.message.reply_text(
                'Nutze das Keyboard für Standard-Aktionen. \n\n'+
                'Weitere Funktionen: \n'+
                '- /help zeigt diesen Text an \n'+
                '- /speed [duble] in Sekunden kannst du die geschwindigkeit regulieren.'+
                'Aktuelle Geschwindigkeit: '+str(Conf.OneSpeedSingleton),
                '- /admin wechselt in die Userverwaltung \n' +
                '- /exit verläst den Partymodus ',
                reply_markup=user_data['keyboard'])
    return user_data['status']
    
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)
    

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(Conf.telegram['token'])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start',
                                     start,
                                     pass_user_data=True),
                      MessageHandler(Filters.text,
                                    start,
                                    pass_user_data=True)
                      ],
        states={
            LOGIN: [RegexHandler('^Login$',
                                 getPasswort,
                                 pass_user_data=True),
                    RegexHandler('^Bye$',
                                 done,
                                 pass_user_data=True),
                    RegexHandler('^Sensor$',
                                 getSensor,
                                 pass_user_data=True),
                    CommandHandler('letsgo',
                                   checkRechte,
                                   pass_user_data=True),
                    MessageHandler(Filters.text,
                                   checkPasswort,
                                   pass_user_data=True),
                    ],
            LIGHT: [RegexHandler('^Logout$',
                                 done,
                                 pass_user_data=True),
                    RegexHandler('^Sensor$',
                                 getSensor,
                                 pass_user_data=True),
                    RegexHandler('^Licht an$',
                                 lightOn,
                                 pass_user_data=True),
                    RegexHandler('^Licht aus$',
                                 lightOff,
                                 pass_user_data=True),
                    RegexHandler('^Abo$',
                                 switchWetterAbo,
                                 pass_user_data=True),
                    RegexHandler('^quit Abo$',
                                 switchWetterAbo,
                                 pass_user_data=True),
                    CommandHandler('rgb',
                                   rgb,
                                   pass_user_data=True,
                                   pass_args=True),
                    CommandHandler('admin',
                                   switchToAdminModus,
                                   pass_user_data=True),
                    CommandHandler('help',
                                   help,
                                   pass_user_data=True),
                    CommandHandler('party',
                                   switchToPartyModus,
                                   pass_user_data=True),
                    MessageHandler(Filters.text,
                                    help,
                                    pass_user_data=True)
                    ],
            PARTY:[ RegexHandler('^Farbwechsel horizontal$',
                                 changeColorHorizontal,
                                 pass_user_data=True),
                    RegexHandler('^Verlasse PartyMode$',
                                 quitSpecialMode,
                                 pass_user_data=True),
                    CommandHandler('speed',
                                   setSpeed,
                                   pass_user_data=True,
                                   pass_args=True),
                    CommandHandler('admin',
                                   switchToAdminModus,
                                   pass_user_data=True),
                    CommandHandler('exit',
                                   quitSpecialMode,
                                   pass_user_data=True),
                    CommandHandler('help',
                                   help,
                                   pass_user_data=True),
                    CommandHandler('rgb',
                                   rgb,
                                   pass_user_data=True,
                                   pass_args=True),
                    MessageHandler(Filters.text,
                                    help,
                                    pass_user_data=True)
                ],
            GETDAYS:[RegexHandler('^Abbrechen$$',
                                 exitAdminRequest,
                                 pass_user_data=True),
                    CommandHandler('quit',
                                exitAdminRequest,
                                pass_user_data=True),
                    MessageHandler(Filters.text,
                                updateUser,
                                pass_user_data=True)
                    ],
            ADMINREQUEST: [RegexHandler('^Ja$',
                                 allowUser,
                                 pass_user_data=True),
                    RegexHandler('^Löschen$',
                                 deletUser,
                                 pass_user_data=True),
                    RegexHandler('^Abbrechen$',
                                 exitAdminRequest,
                                 pass_user_data=True)
                    ],
            ADMIN: [RegexHandler('^Nächster Request$',
                                 nextRequest,
                                 pass_user_data=True),
                    RegexHandler('^Zeige alle User$',
                                 displayUsers,
                                 pass_user_data=True),
                    RegexHandler('^Lösche User$',
                                 deleteUsers,
                                 pass_user_data=True),
                    RegexHandler('^Verlasse AdminMode$',
                                 quitSpecialMode,
                                 pass_user_data=True)
                           ],
        },
        fallbacks=[RegexHandler('^Logout$', done, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    
    if Conf.OneThreadSingleton is not None:
        if Conf.OneThreadSingleton.isRunning:
            Conf.OneThreadSingleton.stop()



if __name__ == '__main__':
    main()