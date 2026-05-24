#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib.config import LIGHT, MAIN, Config
from lib.lampeLib import light
from lib.telegram_utils import retry_telegram_call

logger = logging.getLogger(__name__)

# Globale Variable für Licht-Instanz
licht = None
config = Config()

def init_light():
    """Initialisiert die globale Licht-Instanz"""
    global licht
    if licht is None:
        licht = light()
    return licht

# Tastatur-Befehle (Button-Texte)
tastertur = {
    'licht_an': 'Licht an',
    'licht_aus': 'Licht aus',
    'logout': 'Logout',
    'back': 'Zurück'
}

# Text-Befehle (für /help)
textbefehl = {
    'licht_an': 'Schaltet das Licht ein',
    'licht_aus': 'Schaltet das Licht aus',
    'logout': 'Loggt den Benutzer aus',
    'back': 'Kehrt zum Hauptmenü zurück'
}

class LichtMode:
    """LichtMode Klasse für die Lichtsteuerung"""
    
    # Klassenvariablen für Kompatibilität
    tastertur = tastertur
    textbefehl = textbefehl
    
    @staticmethod
    def get_callback_handlers():
        """Gibt die Callback-Handler-Konfiguration zurück"""
        return {
            'patterns': [
                r'light_color_.*',  # Für Farb-Auswahl
                r'light_effect_.*'   # Für Effekte
            ],
            'handler': LichtMode.handle_callback
        }
    
    @staticmethod
    async def default(update, context, user_data, markupList):
        """Standard-Funktion für LichtMode"""
        context.user_data['keyboard'] = markupList[LIGHT]
        context.user_data['status'] = LIGHT
        
        await retry_telegram_call(
            update.message.reply_text,
            "💡 **Licht-Modus**\n\n"
            "Verfügbare Funktionen:\n"
            "• Licht an - Schaltet das Licht ein\n"
            "• Licht aus - Schaltet das Licht aus\n\n"
            "💡 Nutze /help für alle Befehle.",
            reply_markup=context.user_data['keyboard']
        )
        return context.user_data['status']
    
    @staticmethod
    async def licht_an(update, context, user_data, markupList):
        """Schaltet das Licht ein"""
        try:
            licht_instance = init_light()
            rgb = config.get_led_default_rgb()
            licht_instance.on(r=rgb['r'], g=rgb['g'], b=rgb['b'])
            
            await retry_telegram_call(
                update.message.reply_text,
                "✅ Licht eingeschaltet!\n"
                "Die LED-Stripe leuchtet jetzt in voller Helligkeit.",
                reply_markup=user_data['keyboard']
            )
        except Exception as e:
            logger.error(f"Fehler beim Einschalten des Lichts: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Einschalten des Lichts. Bitte überprüfe die Hardware.",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    async def licht_aus(update, context, user_data, markupList):
        """Schaltet das Licht aus"""
        try:
            licht_instance = init_light()
            licht_instance.off()
            
            await retry_telegram_call(
                update.message.reply_text,
                "✅ Licht ausgeschaltet!\n"
                "Die LED-Stripe ist jetzt dunkel.",
                reply_markup=user_data['keyboard']
            )
        except Exception as e:
            logger.error(f"Fehler beim Ausschalten des Lichts: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Ausschalten des Lichts. Bitte überprüfe die Hardware.",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    async def logout(update, context, user_data, markupList):
        """Loggt den Benutzer aus"""
        from lib.config import LOGIN
        
        context.user_data['keyboard'] = markupList[LOGIN]
        context.user_data['status'] = LOGIN
        context.user_data['isAuthenticated'] = False
        
        await retry_telegram_call(
            update.message.reply_text,
            "👋 Erfolgreich ausgeloggt!\n"
            "Nutze /start um dich erneut anzumelden.",
            reply_markup=context.user_data['keyboard']
        )
        return LOGIN
    
    @staticmethod
    async def back(update, context, user_data, markupList):
        """Kehrt zum Hauptmenü zurück"""
        context.user_data['keyboard'] = markupList[MAIN]
        context.user_data['status'] = MAIN
        
        await retry_telegram_call(
            update.message.reply_text,
            "🔙 Zurück zum Hauptmenü",
            reply_markup=context.user_data['keyboard']
        )
        return MAIN
    
    @staticmethod
    async def handle_callback(update, context, user_data, markupList):
        """Verarbeitet Callbacks von Inline-Buttons"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith('light_color_'):
            # Farb-Auswahl verarbeiten
            color = callback_data.split('_')[-1]
            await query.edit_message_text(
                f"🎨 Farbe {color} ausgewählt",
                reply_markup=user_data['keyboard']
            )
        
        elif callback_data.startswith('light_effect_'):
            # Effekt-Auswahl verarbeiten
            effect = callback_data.split('_')[-1]
            await query.edit_message_text(
                f"✨ Effekt {effect} aktiviert",
                reply_markup=user_data['keyboard']
            )
        
        else:
            logger.warning(f"Unbekannter Callback: {callback_data}")
            await query.edit_message_text(
                "❌ Unbekannte Aktion",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']

# Globale Funktionen für Kompatibilität mit selectModeFunc
async def default(update, context, user_data, markupList):
    """Default-Funktion - delegiert zur LichtMode.default"""
    return await LichtMode.default(update, context, user_data, markupList)

async def licht_an(update, context, user_data, markupList):
    """Licht an - delegiert zur LichtMode.licht_an"""
    return await LichtMode.licht_an(update, context, user_data, markupList)

async def licht_aus(update, context, user_data, markupList):
    """Licht aus - delegiert zur LichtMode.licht_aus"""
    return await LichtMode.licht_aus(update, context, user_data, markupList)

async def logout(update, context, user_data, markupList):
    """Logout - delegiert zur LichtMode.logout"""
    return await LichtMode.logout(update, context, user_data, markupList)

async def back(update, context, user_data, markupList):
    """Zurück - delegiert zur LichtMode.back"""
    return await LichtMode.back(update, context, user_data, markupList)
