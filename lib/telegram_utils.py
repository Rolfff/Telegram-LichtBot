#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Zentrale Telegram-Utility-Funktionen für den FritzDECTBot
"""
import asyncio
import logging

logger = logging.getLogger(__name__)

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
    import telegram.error
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except telegram.error.NetworkError as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Telegram NetworkError (Versuch {attempt + 1}/{max_retries}): {str(e)}. Wiederhole in {delay:.1f}s...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"Telegram NetworkError: Alle {max_retries} Versuche fehlgeschlagen. {str(e)}")
                raise
        except Exception as e:
            # Andere Fehler nicht retryen
            raise

def send_telegram_message_sync(token, chat_id, text, max_retries=3, base_delay=1):
    """
    Sendet eine Telegram-Nachricht synchron mit Retry-Logik.
    Verwendet requests.post direkt mit Retry-Logik für NetworkErrors.
    
    Args:
        token: Telegram Bot Token
        chat_id: Chat ID des Empfängers
        text: Nachrichtentext
        max_retries: Maximale Anzahl an Wiederholungsversuchen (Standard: 3)
        base_delay: Basis-Verzögerung in Sekunden für exponential backoff (Standard: 1)
    
    Returns:
        True bei Erfolg, False bei Fehler
    """
    import requests
    import time
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json={
                'chat_id': chat_id,
                'text': text
            }, timeout=10)
            response.raise_for_status()
            return True
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Telegram Request Error (Versuch {attempt + 1}/{max_retries}): {str(e)}. Wiederhole in {delay:.1f}s...")
                time.sleep(delay)
            else:
                logger.error(f"Telegram Request Error: Alle {max_retries} Versuche fehlgeschlagen. {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Unerwarteter Fehler beim Senden der Telegram-Nachricht: {str(e)}")
            return False
