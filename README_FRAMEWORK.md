# FritzDECT Bot Framework

Ein modulares Telegram Bot Framework für die Verwaltung von Fritz!DECT Geräten mit erweiterbarer Architektur.

## Inhaltsverzeichnis

1. [Bot Funktionsweise](#bot-funktionsweise)
2. [Framework Architektur](#framework-architektur)
3. [Modul Entwicklung](#modul-entwicklung)
4. [Handler System](#handler-system)
5. [Beispiel: Neues Modul erstellen](#beispiel-neues-modul-erstellen)
6. [Best Practices](#best-practices)

## Bot Funktionsweise

Der FritzDECT Bot ist ein Telegram Bot, der die Verwaltung von Fritz!DECT Geräten ermöglicht. Der Bot verwendet ein modulares System, bei dem jeder Funktionsbereich als eigener "Mode" implementiert ist.

### Hauptfunktionen

- **Geräte-Management**: Heizkörper steuern, Temperaturen setzen, Verläufe anzeigen
- **Automatisierung**: Szenarien und Vorlagen für automatische Aktionen
- **Einstellungen**: Sprache, Benachrichtigungen und persönliche Präferenzen
- **Administration**: Benutzer- und Zugriffsverwaltung
- **Statistik**: Energieverbrauch und Temperaturdaten analysieren

### Modi-System

Der Bot arbeitet mit verschiedenen Modi, die der Benutzer durchlaufen kann:

```
START → LOGIN → MAIN → {STATISTICS | AUTOMATION | SETTINGS | ADMIN}
```

- **MAIN**: Hauptmenü mit allen verfügbaren Optionen
- **STATISTICS**: Geräte- und Temperaturverwaltung
- **AUTOMATION**: Szenarien und Vorlagen
- **SETTINGS**: Persönliche Einstellungen
- **ADMIN**: Administrationsfunktionen

## Framework Architektur

### Kernkomponenten

#### 1. Mode-System

Jeder Mode ist eine eigene Klasse mit standardisierten Schnittstellen:

```python
class ExampleMode:
    # Tastatur-Befehle (Button-Texte)
    tastertur = {
        'function1': 'Button Text 1',
        'function2': 'Button Text 2'
    }
    
    # Text-Befehle (für /help)
    textbefehl = {
        'function1': 'Beschreibung von function1',
        'function2': 'Beschreibung von function2'
    }
    
    # Callback-Handler Konfiguration
    def get_callback_handlers():
        return {
            'patterns': [r'pattern_.*', r'other_pattern'],
            'handler': ExampleMode.handle_callback
        }
    
    # Standard-Funktion (wenn Modus aktiviert wird)
    async def default(update, context, user_data, markupList):
        # Modus-Initialisierung
        pass
```

#### 2. Handler-System

Das Framework verwendet drei Arten von Handlern:

##### a) `tastertur` - Button-Handler
```python
tastertur = {
    'function_name': 'Button-Text',
    'another_function': 'Anderer Button-Text'
}
```

**Wirkungsweise:**
- Benutzer klickt auf "Button-Text"
- Bot ruft `function_name()` auf
- Automatische Weiterleitung an die entsprechende Funktion

##### b) `textbefehl` - Command-Handler
```python
textbefehl = {
    'function_name': 'Beschreibung für /help',
    'another_function': 'Beschreibung für /help'
}
```

**Wirkungsweise:**
- Benutzer gibt `/function_name` ein
- Bot ruft `function_name()` auf
- Beschreibung wird in `/help` angezeigt

##### c) `get_callback_handlers()` - Inline-Button-Handler
```python
def get_callback_handlers():
    return {
        'patterns': [r'callback_pattern_.*', r'other_callback'],
        'handler': ExampleMode.handle_callback
    }
```

**Wirkungsweise:**
- Benutzer klickt auf Inline-Button mit Callback-Daten
- Bot prüft Pattern-Matching
- Ruft entsprechende Handler-Funktion auf

#### 3. `default()` Funktion

Jeder Mode muss eine `default()` Funktion implementieren:

```python
async def default(update, context, user_data, markupList):
    """Wird aufgerufen, wenn der Modus aktiviert wird"""
    context.user_data['keyboard'] = markupList[MODE_CONSTANT]
    context.user_data['status'] = MODE_CONSTANT
    
    await update.message.reply_text(
        "Willkommen im Example-Modus!\n\n"
        "Verfügbare Funktionen:\n"
        "• Funktion 1\n"
        "• Funktion 2\n\n"
        "💡 Nutze /help für alle Befehle",
        reply_markup=context.user_data['keyboard']
    )
    return context.user_data['status']
```

**Aufgaben der `default()` Funktion:**
1. **Modus aktivieren**: `context.user_data['status']` setzen
2. **Keyboard setzen**: `context.user_data['keyboard']` zuweisen
3. **Begrüßungsnachricht**: Informationen über verfügbare Funktionen
4. **Rückgabe**: Neuer Status

### Dynamische Registrierung

Das Framework registriert alle Handler automatisch:

```python
# In fritzdect_bot.py
callback_configs = [
    (STATISTICS, StatistikModeOptimized),
    (AUTOMATION, AutomationModeOptimized),
    (SETTINGS, SettingsMode),
    (ADMIN, AdminMode)
]

for mode, module in callback_configs:
    if hasattr(module, 'get_callback_handlers'):
        config = module.get_callback_handlers()
        handler = config['handler']
        for pattern in config['patterns']:
            application.add_handler(CallbackQueryHandler(
                lambda update, context, h=handler: h(update, context, context.user_data, markupList), 
                pattern=pattern
            ))
```

## Modul Entwicklung

### Schritt 1: Modul-Struktur erstellen

Erstelle eine neue Python-Datei im `lib/` Verzeichnis:

```python
# lib/exampleMode.py

import logging
from lib.config import EXAMPLE_MODE  # Neue Konstante in config.py

logger = logging.getLogger(__name__)

# Tastatur-Befehle (Button-Texte)
tastertur = {
    'show_data': 'Daten anzeigen',
    'process_data': 'Daten verarbeiten',
    'back': 'Zurück'
}

# Funktionen Map{Funk-Name, Beschreiung in Help}
textbefehl = {
    'show_data': 'Zeigt aktuelle Daten an',
    'process_data': 'Verarbeitet die Daten',
    'back': 'Wechselt zurück ins Main-Menu'
}

def get_callback_handlers():
    """Gibt die Callback-Handler-Konfiguration zurück"""
    return {
        'patterns': [
            r'detail_.*',  # Für Detail-Ansichten
            r'confirm_.*'  # Für Bestätigungen
        ],
        'handler': ExampleMode.handle_callback
    }

class ExampleMode:
    async def default(update, context, user_data, markupList):
        """Standard-Funktion für Example-Mode"""
        context.user_data['keyboard'] = markupList[EXAMPLE_MODE]
        context.user_data['status'] = EXAMPLE_MODE
        
        await update.message.reply_text(
            "-->EXAMPLEMODE<--\n\n"
            "🔧 Verfügbare Funktionen:\n"
            "• Daten anzeigen und verarbeiten\n"
            "• Detail-Ansichten öffnen\n\n"
            "💡 Nutze /help für alle Befehle",
            reply_markup=context.user_data['keyboard']
        )
        return context.user_data['status']
    
    async def show_data(update, context, user_data, markupList):
        """Zeigt aktuelle Daten an"""
        await update.message.reply_text(
            "📊 Aktuelle Daten:\n"
            "• Wert 1: 123\n"
            "• Wert 2: 456\n"
            "• Wert 3: 789",
            reply_markup=user_data['keyboard']
        )
        return user_data['status']
    
    async def process_data(update, context, user_data, markupList):
        """Verarbeitet die Daten"""
        await update.message.reply_text(
            "⚙️ Daten werden verarbeitet...\n"
            "✅ Verarbeitung abgeschlossen!",
            reply_markup=user_data['keyboard']
        )
        return user_data['status']
    
    async def back(update, context, user_data, markupList):
        """Wechselt zurück ins Main-Menu"""
        from lib.config import MAIN
        context.user_data['keyboard'] = markupList[MAIN]
        context.user_data['status'] = MAIN
        
        await update.message.reply_text(
            "🔙 Zurück zum Hauptmenü",
            reply_markup=user_data['keyboard']
        )
        return MAIN
    
    async def handle_callback(update, context, user_data, markupList):
        """Verarbeitet Callbacks von Inline-Buttons"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith('detail_'):
            # Detail-Ansicht
            item_id = callback_data.split('_')[1]
            await query.edit_message_text(
                f"📋 Details für Item {item_id}\n"
                f"• Status: Aktiv\n"
                f"• Wert: {item_id * 10}\n"
                f"• Zuletzt aktualisiert: Jetzt",
                reply_markup=user_data['keyboard']
            )
        
        elif callback_data.startswith('confirm_'):
            # Bestätigung verarbeiten
            action = callback_data.split('_')[1]
            await query.edit_message_text(
                f"✅ Aktion '{action}' wurde bestätigt und ausgeführt!",
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
```

### Schritt 2: Konfiguration erweitern

Füge die neue Konstante zu `lib/config.py` hinzu:

```python
# In lib/config.py
# Bot-Zustände
MAIN = 0
LOGIN = 1
ADMIN = 2
STATISTICS = 3
AUTOMATION = 4
SETTINGS = 5
EXAMPLE_MODE = 6  # NEU

# Modi-Liste
modeList = [None] * 7  # Größe anpassen
modeList[ADMIN] = AdminMode
modeList[STATISTICS] = StatistikModeOptimized
modeList[AUTOMATION] = AutomationModeOptimized
modeList[SETTINGS] = SettingsMode
modeList[EXAMPLE_MODE] = ExampleMode  # NEU
```

### Schritt 3: Keyboard hinzufügen

Erweitere das Keyboard in `lib/config.py`:

```python
def genMarkupList():
    """Generiert die Keyboard-Layouts für alle Modi"""
    markupList = [None] * 7  # Größe anpassen
    
    # ... bestehende Keyboards ...
    
    # Example-Mode Keyboard
    markupList[EXAMPLE_MODE] = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Daten anzeigen"), KeyboardButton("Daten verarbeiten")],
            [KeyboardButton("Zurück")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    return markupList
```

### Schritt 4: Bot registrieren

Importiere und registriere das neue Modul in `fritzdect_bot.py`:

```python
# In fritzdect_bot.py
import lib.exampleMode as ExampleMode

# In callback_configs hinzufügen
callback_configs = [
    (STATISTICS, StatistikModeOptimized),
    (AUTOMATION, AutomationModeOptimized),
    (SETTINGS, SettingsMode),
    (ADMIN, AdminMode),
    (EXAMPLE_MODE, ExampleMode)  # NEU
]
```

## Handler System

### Handler-Typen und ihre Verwendung

#### 1. Button-Handler (`tastertur`)

**Zweck:** Handler für normale Keyboard-Buttons

**Implementierung:**
```python
tastertur = {
    'function_name': 'Button-Text'
}

async def function_name(update, context, user_data, markupList):
    # Handler-Logik
    pass
```

**Automatische Registrierung:**
```python
# In fritzdect_bot.py
for key in modeList[x].textbefehl.keys():
    autoStates.extend([CommandHandler(str(key), selectModeFunc)])
```

#### 2. Command-Handler (`textbefehl`)

**Zweck:** Handler für Slash-Commands und Help-System

**Implementierung:**
```python
textbefehl = {
    'function_name': 'Beschreibung für /help'
}

async def function_name(update, context, user_data, markupList):
    # Handler-Logik
    pass
```

**Help-Integration:**
```python
# help_command() verwendet textbefehl automatisch
for key, value in modeList[current_status].textbefehl.items():
    help_text += f'\n- /{key} {value}'
```

#### 3. Callback-Handler (`get_callback_handlers`)

**Zweck:** Handler für Inline-Buttons mit Callback-Daten

**Implementierung:**
```python
def get_callback_handlers():
    return {
        'patterns': [r'pattern_.*', r'other_pattern'],
        'handler': ExampleMode.handle_callback
    }

async def handle_callback(update, context, user_data, markupList):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    # Pattern-Matching und Verarbeitung
```

**Dynamische Registrierung:**
```python
# Automatische Registrierung in fritzdect_bot.py
for mode, module in callback_configs:
    config = module.get_callback_handlers()
    for pattern in config['patterns']:
        application.add_handler(CallbackQueryHandler(...))
```

## Beispiel: Neues Modul erstellen

### Complete Example: WeatherMode

Hier ist ein vollständiges Beispiel für ein Wetter-Modul:

#### 1. Modul-Datei erstellen

```python
# lib/weatherMode.py

import logging
from lib.config import WEATHER_MODE

logger = logging.getLogger(__name__)

# Tastatur-Befehle
tastertur = {
    'current_weather': 'Aktuelles Wetter',
    'forecast': 'Vorhersage',
    'alerts': 'Warnungen',
    'back': 'Zurück'
}

# Text-Befehle
textbefehl = {
    'current_weather': 'Zeigt das aktuelle Wetter an',
    'forecast': 'Zeigt die Wettervorhersage',
    'alerts': 'Zeigt Wetterwarnungen',
    'back': 'Wechselt zurück ins Main-Menu'
}

def get_callback_handlers():
    """Gibt die Callback-Handler-Konfiguration zurück"""
    return {
        'patterns': [
            r'weather_detail_.*',  # Wetter-Details
            r'forecast_day_.*'      # Tages-Vorhersage
        ],
        'handler': WeatherMode.handle_callback
    }

class WeatherMode:
    async def default(update, context, user_data, markupList):
        """Standard-Funktion für Weather-Mode"""
        context.user_data['keyboard'] = markupList[WEATHER_MODE]
        context.user_data['status'] = WEATHER_MODE
        
        await update.message.reply_text(
            "🌤️ **Wetter-Modus**\n\n"
            "Verfügbare Funktionen:\n"
            "• Aktuelles Wetter anzeigen\n"
            "• Wettervorhersage einsehen\n"
            "• Wetterwarnungen prüfen\n\n"
            "💡 Nutze /help für alle Befehle",
            reply_markup=context.user_data['keyboard']
        )
        return context.user_data['status']
    
    async def current_weather(update, context, user_data, markupList):
        """Zeigt aktuelles Wetter an"""
        # Wetter-API Aufruf (Beispiel)
        weather_data = await self._get_weather_data()
        
        # Inline-Buttons für Details
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🌡️ Temperatur", callback_data="weather_detail_temp"),
                InlineKeyboardButton("💧 Luftfeuchte", callback_data="weather_detail_humidity")
            ],
            [
                InlineKeyboardButton("🌬️ Wind", callback_data="weather_detail_wind"),
                InlineKeyboardButton("👁️ Sicht", callback_data="weather_detail_visibility")
            ]
        ])
        
        await update.message.reply_text(
            f"🌤️ **Aktuelles Wetter**\n\n"
            f"📍 Standort: Berlin\n"
            f"🌡️ Temperatur: {weather_data['temp']}°C\n"
            f"☁️ Zustand: {weather_data['condition']}\n"
            f"💧 Luftfeuchte: {weather_data['humidity']}%\n"
            f"🌬️ Wind: {weather_data['wind']} km/h",
            reply_markup=keyboard
        )
        return user_data['status']
    
    async def forecast(update, context, user_data, markupList):
        """Zeigt Wettervorhersage"""
        forecast_data = await self._get_forecast_data()
        
        # Inline-Buttons für Tages-Auswahl
        keyboard_rows = []
        for day in forecast_data['days']:
            keyboard_rows.append([
                InlineKeyboardButton(
                    f"{day['date']}: {day['temp']}°C", 
                    callback_data=f"forecast_day_{day['date']}"
                )
            ])
        
        keyboard = InlineKeyboardMarkup(keyboard_rows)
        
        await update.message.reply_text(
            "📅 **Wettervorhersage**\n\n"
            "Wähle einen Tag für Details:",
            reply_markup=keyboard
        )
        return user_data['status']
    
    async def alerts(update, context, user_data, markupList):
        """Zeigt Wetterwarnungen"""
        alerts = await self._get_weather_alerts()
        
        if not alerts:
            await update.message.reply_text(
                "✅ **Keine Wetterwarnungen**\n\n"
                "Aktuell keine Warnungen für Ihren Standort.",
                reply_markup=user_data['keyboard']
            )
        else:
            alert_text = "⚠️ **Wetterwarnungen**\n\n"
            for alert in alerts:
                alert_text += f"🔴 {alert['level']}: {alert['description']}\n"
                alert_text += f"🕐 Gültig bis: {alert['expires']}\n\n"
            
            await update.message.reply_text(
                alert_text,
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    async def back(update, context, user_data, markupList):
        """Wechselt zurück ins Main-Menu"""
        from lib.config import MAIN
        context.user_data['keyboard'] = markupList[MAIN]
        context.user_data['status'] = MAIN
        
        await update.message.reply_text(
            "🔙 Zurück zum Hauptmenü",
            reply_markup=context.user_data['keyboard']
        )
        return MAIN
    
    async def handle_callback(update, context, user_data, markupList):
        """Verarbeitet Callbacks von Inline-Buttons"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data.startswith('weather_detail_'):
            detail_type = callback_data.split('_')[-1]
            detail_info = await self._get_weather_detail(detail_type)
            
            await query.edit_message_text(
                f"📊 **Wetter-Details: {detail_type.title()}**\n\n"
                f"{detail_info['description']}\n"
                f"Wert: {detail_info['value']}\n"
                f"Einheit: {detail_info['unit']}",
                reply_markup=user_data['keyboard']
            )
        
        elif callback_data.startswith('forecast_day_'):
            day_date = callback_data.split('_')[-1]
            day_forecast = await self._get_day_forecast(day_date)
            
            forecast_text = f"📅 **Vorhersage für {day_date}**\n\n"
            forecast_text += f"🌡️ Temperatur: {day_forecast['temp_min']}°C - {day_forecast['temp_max']}°C\n"
            forecast_text += f"☁️ Zustand: {day_forecast['condition']}\n"
            forecast_text += f"💧 Regenwahrscheinlichkeit: {day_forecast['rain_chance']}%\n"
            forecast_text += f"🌬️ Wind: {day_forecast['wind']} km/h"
            
            await query.edit_message_text(
                forecast_text,
                reply_markup=user_data['keyboard']
            )
        
        return user_data['status']
    
    # Hilfsfunktionen
    async def _get_weather_data(self):
        """Holt aktuelle Wetterdaten"""
        # API-Aufruf implementieren
        return {
            'temp': 22,
            'condition': 'Teilweise bewölkt',
            'humidity': 65,
            'wind': 12
        }
    
    async def _get_forecast_data(self):
        """Holt Wettervorhersage"""
        # API-Aufruf implementieren
        return {
            'days': [
                {'date': '2024-01-15', 'temp': 20},
                {'date': '2024-01-16', 'temp': 18},
                {'date': '2024-01-17', 'temp': 16}
            ]
        }
    
    async def _get_weather_alerts(self):
        """Holt Wetterwarnungen"""
        # API-Aufruf implementieren
        return []
    
    async def _get_weather_detail(self, detail_type):
        """Holt detaillierte Wetterinformationen"""
        # API-Aufruf implementieren
        return {
            'description': f'Details für {detail_type}',
            'value': '123',
            'unit': 'Einheit'
        }
    
    async def _get_day_forecast(self, day_date):
        """Holt Tages-Vorhersage"""
        # API-Aufruf implementieren
        return {
            'temp_min': 15,
            'temp_max': 25,
            'condition': 'Sonnig',
            'rain_chance': 10,
            'wind': 8
        }
```

#### 2. Konfiguration erweitern

```python
# lib/config.py
WEATHER_MODE = 6  # Neue Konstante

modeList = [None] * 7
modeList[WEATHER_MODE] = WeatherMode

def genMarkupList():
    markupList = [None] * 7
    
    # Weather-Mode Keyboard
    markupList[WEATHER_MODE] = ReplyKeyboardMarkup(
        [
            [KeyboardButton("Aktuelles Wetter"), KeyboardButton("Vorhersage")],
            [KeyboardButton("Warnungen"), KeyboardButton("Zurück")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    return markupList
```

#### 3. Bot registrieren

```python
# fritzdect_bot.py
import lib.weatherMode as WeatherMode

callback_configs = [
    # ... bestehende Modi ...
    (WEATHER_MODE, WeatherMode)
]
```

## Telegram Retry-Funktionalität

### Übersicht

Der Bot verfügt über eine zentrale Retry-Funktion für Telegram-Nachrichten, um Netzwerkfehler automatisch zu behandeln. Diese Funktion ist in `lib/telegram_utils.py` implementiert und wird in allen wichtigen Modulen verwendet.

### retry_telegram_call Funktion

**Datei:** `lib/telegram_utils.py`

```python
async def retry_telegram_call(func, *args, max_retries=10, base_delay=1, **kwargs):
    """
    Führt einen Telegram-Aufruf mit Retry-Logik aus.
    Bei NetworkError wird der Aufruf bis zu max_retries Mal wiederholt.
    
    Args:
        func: Die async-Funktion, die ausgeführt werden soll
        *args: Positionale Argumente für die Funktion
        max_retries: Maximale Anzahl an Wiederholungsversuchen (Standard: 10)
        base_delay: Basis-Verzögerung in Sekunden für exponential backoff (Standard: 1)
        **kwargs: Keyword-Argumente für die Funktion
    
    Returns:
        Das Ergebnis der Funktion
    
    Raises:
        Exception: Die ursprüngliche Exception, wenn alle Retrys fehlschlagen
    """
```

### Funktionsweise

1. **Exponential Backoff:** Die Verzögerung zwischen den Retrys verdoppelt sich bei jedem Versuch (1s, 2s, 4s, 8s, ...)
2. **Maximale Retrys:** Standardmäßig 10 Versuche
3. **NetworkError-Behandlung:** Nur bei `telegram.error.NetworkError` wird retryt
4. **Logging:** Jeder Retry wird geloggt mit Versuchsnummer und Verzögerung
5. **Error-Log:** Nach 10 fehlgeschlagenen Versuchen wird ein Error geloggt

### Verwendung

#### Import

```python
from lib.telegram_utils import retry_telegram_call
```

#### Beispiel: reply_text mit Retry

```python
# Ohne Retry
await update.message.reply_text("Nachricht", reply_markup=keyboard)

# Mit Retry
await retry_telegram_call(
    update.message.reply_text,
    "Nachricht",
    reply_markup=keyboard
)
```

#### Beispiel: send_message mit Retry

```python
# Ohne Retry
await bot.send_message(chat_id=123, text="Nachricht")

# Mit Retry
await retry_telegram_call(
    bot.send_message,
    chat_id=123,
    text="Nachricht"
)
```

#### Beispiel: edit_message_text mit Retry

```python
# Ohne Retry
await query.edit_message_text("Neuer Text")

# Mit Retry
await retry_telegram_call(
    query.edit_message_text,
    "Neuer Text"
)
```

### Integration in Modulen

Die Retry-Funktion ist bereits in folgenden Modulen integriert:

- **fritzdect_bot.py:** Haupt-Bot-Datei mit Admin-Benachrichtigungen
- **lib/statistikMode_optimized.py:** Statistik-Modul mit Graphik- und Status-Nachrichten
- **lib/adminMode.py:** Admin-Modul mit Benutzer-Verwaltung
- **lib/automationMode_optimized.py:** Automatisierungs-Modul
- **notification_api.py:** Notification-API für externe Benachrichtigungen

### Best Practices

1. **Immer verwenden für kritische Nachrichten:** Alle wichtigen Telegram-Aufrufe sollten mit retry_telegram_call umhüllt werden
2. **Nicht für interne Debug-Nachrichten:** Für reine Debug-Logs kann auf Retry verzichtet werden
3. **Parameter beachten:** Die Funktion muss als erstes Argument übergeben werden, danach die Parameter
4. **Fehlerbehandlung:** Die Retry-Funktion wirft die Exception nach allen Retrys, daher sollte try-except weiterhin verwendet werden

### Beispiel für neue Module

Wenn Sie ein neues Modul erstellen, sollten Sie die Retry-Funktion verwenden:

```python
# lib/newMode.py
from lib.telegram_utils import retry_telegram_call

async def new_function(update, context, user_data, markupList):
    try:
        # Telegram-Aufruf mit Retry
        await retry_telegram_call(
            update.message.reply_text,
            "Wichtige Nachricht",
            reply_markup=user_data['keyboard']
        )
        
        # Weitere Logik...
        
    except Exception as e:
        logger.error(f"Fehler: {e}")
        # Fehlerbehandlung
    
    return user_data['status']
```

## Best Practices

### 1. Namenskonventionen

- **Modul-Dateien:** `camelCase.py` (z.B. `weatherMode.py`)
- **Klassen:** `PascalCase` (z.B. `WeatherMode`)
- **Funktionen:** `snake_case` (z.B. `handle_callback`)
- **Konstanten:** `UPPER_CASE` (z.B. `WEATHER_MODE`)

### 2. Modul-Struktur

```python
# 1. Imports
import logging
from lib.config import MODE_CONSTANT

# 2. Logger
logger = logging.getLogger(__name__)

# 3. Konfiguration (tastertur, textbefehl, get_callback_handlers)
tastertur = {...}
textbefehl = {...}

def get_callback_handlers():
    return {...}

# 4. Haupt-Klasse
class ModeClass:
    async def default(update, context, user_data, markupList):
        # Standard-Implementierung
        pass
    
    async def function1(update, context, user_data, markupList):
        # Handler-Implementierung
        pass
    
    async def handle_callback(update, context, user_data, markupList):
        # Callback-Handler
        pass
```

### 3. Fehlerbehandlung

```python
async def function_name(update, context, user_data, markupList):
    try:
        # Hauptlogik
        result = await api_call()
        
        await update.message.reply_text(
            f"✅ Erfolg: {result}",
            reply_markup=user_data['keyboard']
        )
        
    except Exception as e:
        logger.error(f"Fehler in function_name: {e}")
        
        await update.message.reply_text(
            "❌ Leider ist ein Fehler aufgetreten. Bitte versuche es später erneut.",
            reply_markup=user_data['keyboard']
        )
    
    return user_data['status']
```

### 4. Callback-Handler

```python
async def handle_callback(update, context, user_data, markupList):
    try:
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        # Pattern-Matching mit Regex
        if callback_data.startswith('detail_'):
            item_id = callback_data.split('_')[1]
            # Detail-Logik
        
        elif callback_data.startswith('action_'):
            action = callback_data.split('_')[1]
            # Action-Logik
        
        else:
            logger.warning(f"Unbekannter Callback: {callback_data}")
            await query.edit_message_text(
                "❌ Unbekannte Aktion",
                reply_markup=user_data['keyboard']
            )
    
    except Exception as e:
        logger.error(f"Fehler in Callback-Handler: {e}")
        await query.answer("❌ Fehler bei der Aktion", show_alert=True)
    
    return user_data['status']
```

### 5. Help-Integration

```python
# textbefehl automatisch in /help integrieren
textbefehl = {
    'function1': 'Klare Beschreibung was die Funktion tut',
    'function2': 'Noch eine klare Beschreibung',
    'back': 'Wechselt zurück ins Main-Menu'
}
```

### 6. Status-Management

```python
async def function_name(update, context, user_data, markupList):
    # Status bei Bedarf ändern
    context.user_data['status'] = NEW_STATUS
    context.user_data['keyboard'] = markupList[NEW_STATUS]
    
    # Immer den aktuellen Status zurückgeben
    return context.user_data['status']
```

### 7. Logging

```python
import logging

logger = logging.getLogger(__name__)

# Debug-Informationen
logger.debug(f"Function called with data: {data}")

# Fehler loggen
logger.error(f"Error in function: {e}")

# Info-Loggen
logger.info(f"User {user_id} performed action: {action}")
```

### 8. Testing

```python
# Einfache Tests für Handler-Funktionen
async def test_function():
    # Mock-Update und Context erstellen
    update = Mock()
    context = Mock()
    user_data = {'status': MODE_CONSTANT}
    markupList = {MODE_CONSTANT: Mock()}
    
    # Funktion testen
    result = await function_name(update, context, user_data, markupList)
    
    # Ergebnis prüfen
    assert result == MODE_CONSTANT
```

Dieses Framework ermöglicht es externen Entwicklern, einfach neue Funktionen zum Bot hinzuzufügen, ohne die Kernarchitektur ändern zu müssen.
