#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import threading
import time
from lib.config import LIGHT, MAIN, Config
from lib.lampeLib import light
from lib.telegram_utils import retry_telegram_call

logger = logging.getLogger(__name__)

# Globale Variable für Licht-Instanz
licht = None
config = Config()

# Global flag for stopping effects
effect_running = False
effect_thread = None

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
    'set_color': 'Farbe setzen',
    'set_brightness': 'Helligkeit',
    'rainbow': 'Regenbogen',
    'rainbow_successive': 'Regenbogen (sukzessiv)',
    'rainbow_colors': 'Regenbogen-Farben',
    'brightness_decrease': 'Helligkeit abnehmen',
    'appear_from_back': 'Erscheinen von hinten',
    'party_mode': 'Party-Modus',
    'stop_effect': 'Effekt stoppen',
    'back': 'Zurück'
}

# Text-Befehle (für /help)
textbefehl = {
    'licht_an': 'Schaltet das Licht ein',
    'licht_aus': 'Schaltet das Licht aus',
    'set_color': 'Setzt eine bestimmte Farbe (über Auswahl oder RGB)',
    'set_brightness': 'Passt die Helligkeit an',
    'rainbow': 'Startet einen Regenbogen-Effekt',
    'rainbow_successive': 'Regenbogen-Effekt Pixel für Pixel',
    'rainbow_colors': 'Regenbogen-Farben durchlaufen',
    'brightness_decrease': 'Helligkeit langsam abnehmen',
    'appear_from_back': 'Licht erscheint von hinten',
    'party_mode': 'Startet den Party-Modus mit verschiedenen Effekten',
    'stop_effect': 'Stoppt den aktuell laufenden Effekt',
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
                r'color_.*',  # Für Farb-Auswahl
                r'light_color_.*',  # Für Farb-Auswahl (legacy)
                r'light_effect_.*',  # Für Effekte
                r'party_effect_.*',  # Für Party-Effekte (direct start)
                r'party_select_.*',  # Für Party-Effekt-Auswahl mit Farbauswahl
                r'party_color_.*'   # Für Party-Farben-Auswahl
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
            "• Licht aus - Schaltet das Licht aus\n"
            "• Farbe setzen - Wähle eine Farbe aus oder gib RGB ein\n"
            "• Helligkeit - Passt die Helligkeit an\n"
            "• Regenbogen - Startet einen Regenbogen-Effekt\n"
            "• Regenbogen (sukzessiv) - Pixel für Pixel\n"
            "• Regenbogen-Farben - Farben durchlaufen\n"
            "• Helligkeit abnehmen - Langsam dimmen\n"
            "• Erscheinen von hinten - Aufbau-Effekt\n"
            "• Party-Modus - Verschiedene Party-Effekte\n"
            "• Effekt stoppen - Stoppt laufende Effekte\n\n"
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
        
        if callback_data.startswith('color_'):
            # Farb-Auswahl verarbeiten
            parts = callback_data.split('_')
            r, g, b = int(parts[1]), int(parts[2]), int(parts[3])
            
            try:
                licht_instance = init_light()
                licht_instance.on(r=r, g=g, b=b)
                await query.edit_message_text(
                    f"✅ Farbe gesetzt!\nR: {r}, G: {g}, B: {b}",
                    reply_markup=user_data['keyboard']
                )
            except Exception as e:
                logger.error(f"Fehler beim Setzen der Farbe: {e}")
                await query.edit_message_text(
                    "❌ Fehler beim Setzen der Farbe.",
                    reply_markup=user_data['keyboard']
                )
        
        elif callback_data.startswith('light_color_'):
            # Farb-Auswahl verarbeiten (legacy)
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
        
        elif callback_data.startswith('party_select_'):
            # Party-Effekt-Auswahl mit Farbauswahl
            effect = callback_data.split('_')[-1]
            
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            # Show color selection inline keyboard
            color_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔴 Rot", callback_data=f"party_color_{effect}_255_0_0"),
                    InlineKeyboardButton("🟢 Grün", callback_data=f"party_color_{effect}_0_255_0"),
                    InlineKeyboardButton("🔵 Blau", callback_data=f"party_color_{effect}_0_0_255")
                ],
                [
                    InlineKeyboardButton("🟡 Gelb", callback_data=f"party_color_{effect}_255_255_0"),
                    InlineKeyboardButton("🟣 Lila", callback_data=f"party_color_{effect}_255_0_255"),
                    InlineKeyboardButton("🟠 Orange", callback_data=f"party_color_{effect}_255_165_0")
                ],
                [
                    InlineKeyboardButton("⚪ Weiß", callback_data=f"party_color_{effect}_255_255_255"),
                    InlineKeyboardButton("🩷 Pink", callback_data=f"party_color_{effect}_255_192_203"),
                    InlineKeyboardButton("🔵 Cyan", callback_data=f"party_color_{effect}_0_255_255")
                ]
            ])
            
            await query.edit_message_text(
                f"🎨 **Farbe für {effect} auswählen**\n\n"
                f"Wähle eine Farbe für den Effekt:",
                reply_markup=color_keyboard
            )
        
        elif callback_data.startswith('party_effect_'):
            # Party-Effekt-Auswahl verarbeiten (direct start with default color)
            effect = callback_data.split('_')[-1]
            await LichtMode._start_party_effect(effect)
            await query.edit_message_text(
                f"🎉 Party-Effekt {effect} gestartet!\n"
                f"Nutze 'Effekt stoppen' um ihn zu beenden.",
                reply_markup=user_data['keyboard']
            )
        
        elif callback_data.startswith('party_color_'):
            # Party-Farben-Auswahl verarbeiten
            parts = callback_data.split('_')
            r, g, b = int(parts[2]), int(parts[3]), int(parts[4])
            effect = parts[1]
            await LichtMode._start_party_effect(effect, r, g, b)
            await query.edit_message_text(
                f"🎉 Party-Effekt {effect} mit Farbe R:{r} G:{g} B:{b} gestartet!\n"
                f"Nutze 'Effekt stoppen' um ihn zu beenden.",
                reply_markup=user_data['keyboard']
            )
        
        else:
            logger.warning(f"Unbekannter Callback: {callback_data}")
            await query.edit_message_text(
                "❌ Unbekannte Aktion",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    async def set_color(update, context, user_data, markupList):
        """Setzt eine bestimmte Farbe (RGB) mit Farbauswahl"""
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            # Check if RGB values provided via command
            args = context.args if context.args else []
            if len(args) >= 3:
                r = int(args[0])
                g = int(args[1])
                b = int(args[2])
                licht_instance = init_light()
                licht_instance.on(r=r, g=g, b=b)
                
                await retry_telegram_call(
                    update.message.reply_text,
                    f"✅ Farbe gesetzt!\n"
                    f"R: {r}, G: {g}, B: {b}",
                    reply_markup=user_data['keyboard']
                )
            else:
                # Show color selection inline keyboard
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("🔴 Rot", callback_data="color_255_0_0"),
                        InlineKeyboardButton("🟢 Grün", callback_data="color_0_255_0"),
                        InlineKeyboardButton("🔵 Blau", callback_data="color_0_0_255")
                    ],
                    [
                        InlineKeyboardButton("🟡 Gelb", callback_data="color_255_255_0"),
                        InlineKeyboardButton("🟣 Lila", callback_data="color_255_0_255"),
                        InlineKeyboardButton("🟠 Orange", callback_data="color_255_165_0")
                    ],
                    [
                        InlineKeyboardButton("⚪ Weiß", callback_data="color_255_255_255"),
                        InlineKeyboardButton("⚫ Schwarz/Aus", callback_data="color_0_0_0"),
                        InlineKeyboardButton("🩷 Pink", callback_data="color_255_192_203")
                    ],
                    [
                        InlineKeyboardButton("🔵 Cyan", callback_data="color_0_255_255"),
                        InlineKeyboardButton("🟤 Braun", callback_data="color_165_42_42"),
                        InlineKeyboardButton("🩵 Hellblau", callback_data="color_173_216_230")
                    ]
                ])
                
                await retry_telegram_call(
                    update.message.reply_text,
                    "🎨 **Farbe auswählen**\n\n"
                    "Wähle eine Farbe aus der Liste:\n"
                    "Oder verwende: /set_color R G B (z.B. /set_color 255 0 0)",
                    reply_markup=keyboard
                )
        except Exception as e:
            logger.error(f"Fehler beim Setzen der Farbe: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Setzen der Farbe.",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    async def set_brightness(update, context, user_data, markupList):
        """Passt die Helligkeit an"""
        try:
            args = context.args if context.args else []
            if len(args) >= 1:
                brightness = int(args[0])
                brightness = max(0, min(255, brightness))  # Clamp to 0-255
            else:
                brightness = 128  # Default to 50%
            
            # Scale current color by brightness
            licht_instance = init_light()
            rgb = config.get_led_default_rgb()
            r = int(rgb['r'] * brightness / 255)
            g = int(rgb['g'] * brightness / 255)
            b = int(rgb['b'] * brightness / 255)
            
            licht_instance.on(r=r, g=g, b=b)
            
            await retry_telegram_call(
                update.message.reply_text,
                f"✅ Helligkeit gesetzt auf {brightness}/255",
                reply_markup=user_data['keyboard']
            )
        except Exception as e:
            logger.error(f"Fehler beim Setzen der Helligkeit: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Setzen der Helligkeit.\n"
                "Verwende: /set_brightness 0-255",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    async def rainbow(update, context, user_data, markupList):
        """Startet einen Regenbogen-Effekt"""
        global effect_running, effect_thread
        
        try:
            # Stop any running effect first
            if effect_running:
                await LichtMode.stop_effect(update, context, user_data, markupList)
            
            # Start rainbow effect in thread
            effect_running = True
            effect_thread = threading.Thread(
                target=LichtMode._rainbow_effect,
                daemon=True
            )
            effect_thread.start()
            
            await retry_telegram_call(
                update.message.reply_text,
                "🌈 Regenbogen-Effekt gestartet!\n"
                "Nutze 'Effekt stoppen' um ihn zu beenden.",
                reply_markup=user_data['keyboard']
            )
        except Exception as e:
            logger.error(f"Fehler beim Starten des Regenbogen-Effekts: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Starten des Regenbogen-Effekts.",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    def _rainbow_effect():
        """Rainbow effect running in background thread"""
        global effect_running
        try:
            licht_instance = init_light()
            speed = config.get_led_default_speed()
            
            while effect_running:
                for j in range(256):
                    if not effect_running:
                        break
                    for i in range(licht_instance.pixels.count()):
                        color = licht_instance.wheel(((i * 256 // licht_instance.pixels.count()) + j) % 256)
                        licht_instance.pixels.set_pixel(i, color)
                    licht_instance.pixels.show()
                    time.sleep(speed)
        except Exception as e:
            logger.error(f"Fehler im Regenbogen-Effekt: {e}")
        finally:
            effect_running = False
    
    @staticmethod
    async def rainbow_successive(update, context, user_data, markupList):
        """Regenbogen-Effekt Pixel für Pixel"""
        global effect_running, effect_thread
        
        try:
            if effect_running:
                await LichtMode.stop_effect(update, context, user_data, markupList)
            
            effect_running = True
            effect_thread = threading.Thread(
                target=LichtMode._rainbow_successive_effect,
                daemon=True
            )
            effect_thread.start()
            
            await retry_telegram_call(
                update.message.reply_text,
                "🌈 Regenbogen (sukzessiv) gestartet!\n"
                "Nutze 'Effekt stoppen' um ihn zu beenden.",
                reply_markup=user_data['keyboard']
            )
        except Exception as e:
            logger.error(f"Fehler beim Starten des Regenbogen-Effekts: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Starten des Regenbogen-Effekts.",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    def _rainbow_successive_effect():
        """Rainbow successive effect running in background thread"""
        global effect_running
        try:
            licht_instance = init_light()
            speed = config.get_led_default_speed()
            
            while effect_running:
                for i in range(licht_instance.pixels.count()):
                    if not effect_running:
                        break
                    color = licht_instance.wheel(((i * 256 // licht_instance.pixels.count())) % 256)
                    licht_instance.pixels.set_pixel(i, color)
                    licht_instance.pixels.show()
                    time.sleep(speed)
        except Exception as e:
            logger.error(f"Fehler im Regenbogen-Sukzessiv-Effekt: {e}")
        finally:
            effect_running = False
    
    @staticmethod
    async def rainbow_colors(update, context, user_data, markupList):
        """Regenbogen-Farben durchlaufen"""
        global effect_running, effect_thread
        
        try:
            if effect_running:
                await LichtMode.stop_effect(update, context, user_data, markupList)
            
            effect_running = True
            effect_thread = threading.Thread(
                target=LichtMode._rainbow_colors_effect,
                daemon=True
            )
            effect_thread.start()
            
            await retry_telegram_call(
                update.message.reply_text,
                "🌈 Regenbogen-Farben gestartet!\n"
                "Nutze 'Effekt stoppen' um ihn zu beenden.",
                reply_markup=user_data['keyboard']
            )
        except Exception as e:
            logger.error(f"Fehler beim Starten der Regenbogen-Farben: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Starten der Regenbogen-Farben.",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    def _rainbow_colors_effect():
        """Rainbow colors effect running in background thread"""
        global effect_running
        try:
            licht_instance = init_light()
            speed = config.get_led_default_speed()
            
            while effect_running:
                for j in range(256):
                    if not effect_running:
                        break
                    for i in range(licht_instance.pixels.count()):
                        color = licht_instance.wheel(((256 // licht_instance.pixels.count() + j)) % 256)
                        licht_instance.pixels.set_pixel(i, color)
                    licht_instance.pixels.show()
                    time.sleep(speed)
        except Exception as e:
            logger.error(f"Fehler im Regenbogen-Farben-Effekt: {e}")
        finally:
            effect_running = False
    
    @staticmethod
    async def brightness_decrease(update, context, user_data, markupList):
        """Helligkeit langsam abnehmen"""
        global effect_running, effect_thread
        
        try:
            if effect_running:
                await LichtMode.stop_effect(update, context, user_data, markupList)
            
            # First turn on lights with default color
            licht_instance = init_light()
            rgb = config.get_led_default_rgb()
            licht_instance.on(r=rgb['r'], g=rgb['g'], b=rgb['b'])
            
            effect_running = True
            effect_thread = threading.Thread(
                target=LichtMode._brightness_decrease_effect,
                daemon=True
            )
            effect_thread.start()
            
            await retry_telegram_call(
                update.message.reply_text,
                "📉 Helligkeit abnehmen gestartet!\n"
                "Nutze 'Effekt stoppen' um ihn zu beenden.",
                reply_markup=user_data['keyboard']
            )
        except Exception as e:
            logger.error(f"Fehler beim Starten der Helligkeitsabnahme: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Starten der Helligkeitsabnahme.",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    def _brightness_decrease_effect():
        """Brightness decrease effect running in background thread"""
        global effect_running
        try:
            licht_instance = init_light()
            speed = config.get_led_default_speed()
            step = 1
            
            for j in range(int(256 // step)):
                if not effect_running:
                    break
                for i in range(licht_instance.pixels.count()):
                    r, g, b = licht_instance.pixels.get_pixel_rgb(i)
                    r = int(max(0, r - step))
                    g = int(max(0, g - step))
                    b = int(max(0, b - step))
                    licht_instance.pixels.set_pixel(i, (r, g, b))
                licht_instance.pixels.show()
                time.sleep(speed)
        except Exception as e:
            logger.error(f"Fehler im Helligkeitsabnahme-Effekt: {e}")
        finally:
            effect_running = False
    
    @staticmethod
    async def appear_from_back(update, context, user_data, markupList):
        """Licht erscheint von hinten"""
        global effect_running, effect_thread
        
        try:
            if effect_running:
                await LichtMode.stop_effect(update, context, user_data, markupList)
            
            # Parse color from args
            args = context.args if context.args else []
            if len(args) >= 3:
                r, g, b = int(args[0]), int(args[1]), int(args[2])
            else:
                rgb = config.get_led_default_rgb()
                r, g, b = rgb['r'], rgb['g'], rgb['b']
            
            effect_running = True
            effect_thread = threading.Thread(
                target=LichtMode._appear_from_back_effect,
                args=(r, g, b),
                daemon=True
            )
            effect_thread.start()
            
            await retry_telegram_call(
                update.message.reply_text,
                "✨ Erscheinen von hinten gestartet!\n"
                "Nutze 'Effekt stoppen' um ihn zu beenden.",
                reply_markup=user_data['keyboard']
            )
        except Exception as e:
            logger.error(f"Fehler beim Starten des Erscheinens von hinten: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Starten des Erscheinens von hinten.",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    def _appear_from_back_effect(r, g, b):
        """Appear from back effect running in background thread"""
        global effect_running
        try:
            licht_instance = init_light()
            speed = config.get_led_default_speed()
            
            for i in range(licht_instance.pixels.count()):
                if not effect_running:
                    break
                for j in reversed(range(i, licht_instance.pixels.count())):
                    if not effect_running:
                        break
                    licht_instance.pixels.clear()
                    # Set all pixels at the beginning
                    for k in range(i):
                        licht_instance.pixels.set_pixel(k, (r, g, b))
                    # Set the pixel at position j
                    licht_instance.pixels.set_pixel(j, (r, g, b))
                    licht_instance.pixels.show()
                    time.sleep(speed)
        except Exception as e:
            logger.error(f"Fehler im Erscheinen-von-hinten-Effekt: {e}")
        finally:
            effect_running = False
    
    @staticmethod
    async def party_mode(update, context, user_data, markupList):
        """Startet den Party-Modus mit verschiedenen Effekten"""
        try:
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🌈 Fade Horizontal", callback_data="party_select_faidHorizontal"),
                    InlineKeyboardButton("⭐ Disco-Kugel", callback_data="party_select_stars")
                ],
                [
                    InlineKeyboardButton("⚡ Strobo", callback_data="party_select_strobo"),
                    InlineKeyboardButton("➡️ Lauflicht Horizontal", callback_data="party_select_laufHorizontal")
                ],
                [
                    InlineKeyboardButton("⬆️ Lauflicht Vertikal", callback_data="party_select_laufVertikal"),
                    InlineKeyboardButton("🎨 Fade Alle", callback_data="party_select_faideAll")
                ]
            ])
            
            await retry_telegram_call(
                update.message.reply_text,
                "🎉 **Party-Modus**\n\n"
                "Wähle einen Effekt:",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Fehler im Party-Modus: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Öffnen des Party-Modus.",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    @staticmethod
    def _start_party_effect(effect_name, r=None, g=None, b=None):
        """Startet einen Party-Effekt im Hintergrund"""
        global effect_running, effect_thread
        
        # Stop any running effect first
        effect_running = False
        if effect_thread and effect_thread.is_alive():
            effect_thread.join(timeout=1.0)
        
        # Use default color if not provided
        if r is None or g is None or b is None:
            rgb = config.get_led_default_rgb()
            r, g, b = rgb['r'], rgb['g'], rgb['b']
        
        # Start new effect
        effect_running = True
        effect_thread = threading.Thread(
            target=LichtMode._run_party_effect,
            args=(effect_name, r, g, b),
            daemon=True
        )
        effect_thread.start()
    
    @staticmethod
    def _run_party_effect(effect_name, r, g, b):
        """Führt einen Party-Effekt aus"""
        global effect_running
        try:
            licht_instance = init_light()
            speed = config.get_led_default_speed()
            lightmatrix = licht_instance.OneLightmatrix
            lightlist = licht_instance.OneLightlist
            
            if effect_name == 'faidHorizontal':
                while effect_running:
                    licht_instance.setHorizontal(r, g, b)
                    time.sleep(speed)
                    if not effect_running: break
                    # Create color variations
                    licht_instance.setHorizontal(int(r*0.5), int(g*0.5), int(b*0.5))
                    time.sleep(speed)
                    if not effect_running: break
                    licht_instance.setHorizontal(int(r*0.3), int(g*0.3), int(b*0.3))
                    time.sleep(speed)
            
            elif effect_name == 'stars':
                import random
                ledAnzahl = 2
                while effect_running:
                    temp = []
                    for i in range(ledAnzahl):
                        pixel = lightlist[random.randrange(len(lightlist))]
                        temp.append(pixel)
                        licht_instance.setPixel(pixel, r, g, b)
                    time.sleep(random.uniform(0.000001, 0.1))
                    for i in range(len(temp)):
                        licht_instance.setPixel(temp[i], 0, 0, 0)
            
            elif effect_name == 'strobo':
                while effect_running:
                    licht_instance.all(r, g, b)
                    time.sleep(speed)
                    if not effect_running: break
                    licht_instance.all(0, 0, 0)
                    time.sleep(speed)
            
            elif effect_name == 'laufHorizontal':
                while effect_running:
                    for y in range(1 + len(lightmatrix[1])):
                        if not effect_running: break
                        if y == len(lightmatrix[1]):
                            licht_instance.setBottomLed(r, g, b)
                        else:
                            licht_instance.setZeile(y, r, g, b)
                        time.sleep(speed)
                        if y - 1 == -1:
                            licht_instance.setBottomLed(0, 0, 0)
                        else:
                            licht_instance.setZeile(y - 1, 0, 0, 0)
            
            elif effect_name == 'laufVertikal':
                while effect_running:
                    for x in range(len(lightmatrix)):
                        if not effect_running: break
                        licht_instance.setSpalte(x, r, g, b)
                        time.sleep(speed)
                        if x - 1 == -1:
                            licht_instance.setSpalte(len(lightmatrix) - 1, 0, 0, 0)
                        else:
                            licht_instance.setSpalte(x - 1, 0, 0, 0)
            
            elif effect_name == 'faideAll':
                while effect_running:
                    for j in range(256):
                        if not effect_running: break
                        for i in range(licht_instance.pixels.count()):
                            color = licht_instance.wheel(((256 // licht_instance.pixels.count() + j)) % 256)
                            licht_instance.pixels.set_pixel(i, color)
                        licht_instance.pixels.show()
                        time.sleep(speed)
        
        except Exception as e:
            logger.error(f"Fehler im Party-Effekt {effect_name}: {e}")
        finally:
            effect_running = False
    
    @staticmethod
    async def stop_effect(update, context, user_data, markupList):
        """Stoppt den aktuell laufenden Effekt"""
        global effect_running, effect_thread
        
        try:
            effect_running = False
            
            if effect_thread and effect_thread.is_alive():
                effect_thread.join(timeout=2.0)
            
            # Turn off lights
            licht_instance = init_light()
            licht_instance.all(0, 0, 0)
            
            await retry_telegram_call(
                update.message.reply_text,
                "🛑 Effekt gestoppt!",
                reply_markup=user_data['keyboard']
            )
        except Exception as e:
            logger.error(f"Fehler beim Stoppen des Effekts: {e}")
            await retry_telegram_call(
                update.message.reply_text,
                "❌ Fehler beim Stoppen des Effekts.",
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

async def set_color(update, context, user_data, markupList):
    """Farbe setzen - delegiert zur LichtMode.set_color"""
    return await LichtMode.set_color(update, context, user_data, markupList)

async def set_brightness(update, context, user_data, markupList):
    """Helligkeit - delegiert zur LichtMode.set_brightness"""
    return await LichtMode.set_brightness(update, context, user_data, markupList)

async def rainbow(update, context, user_data, markupList):
    """Regenbogen - delegiert zur LichtMode.rainbow"""
    return await LichtMode.rainbow(update, context, user_data, markupList)

async def rainbow_successive(update, context, user_data, markupList):
    """Regenbogen (sukzessiv) - delegiert zur LichtMode.rainbow_successive"""
    return await LichtMode.rainbow_successive(update, context, user_data, markupList)

async def rainbow_colors(update, context, user_data, markupList):
    """Regenbogen-Farben - delegiert zur LichtMode.rainbow_colors"""
    return await LichtMode.rainbow_colors(update, context, user_data, markupList)

async def brightness_decrease(update, context, user_data, markupList):
    """Helligkeit abnehmen - delegiert zur LichtMode.brightness_decrease"""
    return await LichtMode.brightness_decrease(update, context, user_data, markupList)

async def appear_from_back(update, context, user_data, markupList):
    """Erscheinen von hinten - delegiert zur LichtMode.appear_from_back"""
    return await LichtMode.appear_from_back(update, context, user_data, markupList)

async def party_mode(update, context, user_data, markupList):
    """Party-Modus - delegiert zur LichtMode.party_mode"""
    return await LichtMode.party_mode(update, context, user_data, markupList)

async def stop_effect(update, context, user_data, markupList):
    """Effekt stoppen - delegiert zur LichtMode.stop_effect"""
    return await LichtMode.stop_effect(update, context, user_data, markupList)

async def back(update, context, user_data, markupList):
    """Zurück - delegiert zur LichtMode.back"""
    return await LichtMode.back(update, context, user_data, markupList)
