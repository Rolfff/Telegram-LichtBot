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
 
from lib.config import Config
load_src("lampeLib", "lampeLib.py")
from lampeLib import light
import time
import random 

# Get config
config = Config()

#Funktionen hier registrieren für Partymode
# Funktionen Map{ Funk-Name: Tastertur beschriftung}
tastertur = {'faidHorizontal': 'faid Hori.',
         'stars': 'Disco-Kugel',
         'strobo': 'Strobo Licht',
         'laufHorizontal': 'Hori. Lauflicht',
         'laufVertikal': 'Verti. Lauflicht',
         'faideAll': 'faide'}
#Funktionen Map{Funk-Name, Beschreiung in Help}
textbefehl = {'faidHorizontal': 'faid Horizontal',
         'stars': 'Imitiert eine Disco-Kugel',
         'strobo': 'Strobo Licht',
         'laufHorizontal': 'Horizontales Lauflicht',
         'laufVertikal': 'Vertikales Lauflicht',
         'faideAll': 'faide'}
#Funktionen Map{Funk-Name, Speed-Empfehlung in Double als Liste von schnell nach langsam}
speedEmpfehlungen = {'faidHorizontal': [0.01,0.05,0.1],
         'stars': None,
         'strobo': [0.05,0.1,0.5],
         'laufHorizontal': [0.01,0.05,0.1],
         'laufVertikal': [0.01,0.05,0.1],
         'faideAll': [0.01,0.05,0.1,0.5]}


def faidHorizontal(self,wait, r,g,b):
        print("runHorizontal was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
        #Todo: Hier könnet man noch Parameter zum dynamischen einstellen mitgeben
        #ZB: Anzahl der Farb-Stufen und so weiter...
        led = light()
        speed = config.get_led_default_speed()
        #255^3 = 16581375 Farben?
        while self.running:
            led.setHorizontal(255,0,0)
            time.sleep(speed)
            if self.running:
                led.setHorizontal(127,127,0)
                time.sleep(speed)
            if self.running:
                led.setHorizontal(0,255,0)
                time.sleep(speed)
            if self.running:
                led.setHorizontal(0,127,127)
                time.sleep(speed)
            if self.running:
                led.setHorizontal(0,0,255)
                time.sleep(speed)
            if self.running:
                led.setHorizontal(127,0,127)
                time.sleep(speed)   

def stars(self,wait, r,g,b):
    print("stars was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    ledAnzahl = 2
    led = light()
    rgb = config.get_led_default_rgb()
    lightlist = light.OneLightlist
    while self.running:
        temp=[]
        for i in range(ledAnzahl):
            pixel = lightlist[random.randrange(len(lightlist))]
            temp.append(pixel)
            led.setPixel(pixel,rgb.get('r'),rgb.get('g'),rgb.get('b'))
        time.sleep(random.uniform(0.000001, 0.1))
        for i in range(len(temp)):
            led.setPixel(temp[i],0,0,0)

def strobo(self,wait, r,g,b):
    print("strobo was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    rgb = config.get_led_default_rgb()
    speed = config.get_led_default_speed()
    while self.running:
        led.all(rgb.get('r'),rgb.get('g'),rgb.get('b'))
        time.sleep(speed)
        led.all(0,0,0)
        #led.allOff(False)
        time.sleep(speed)

#in Smooshig bestimmt auch seht schön
def laufHorizontal(self,wait, r,g,b):
    print("laufHorizontal was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    rgb = config.get_led_default_rgb()
    speed = config.get_led_default_speed()
    lightmatrix = light.OneLightmatrix
    while self.running:
        for y in range(1+len(lightmatrix[1])):
            if y == len(lightmatrix[1]):
                led.setBottomLed(rgb.get('r'),rgb.get('g'),rgb.get('b'))
            else:
                led.setZeile(y,r,g,b)
            time.sleep(speed)
            if y-1 == -1:
                led.setBottomLed(0,0,0)
            else:
                led.setZeile(y-1,0,0,0)
  

def laufVertikal(self,wait, r,g,b):
    print("laufVertikal was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    rgb = config.get_led_default_rgb()
    speed = config.get_led_default_speed()
    lightmatrix = light.OneLightmatrix
    while self.running:
        for x in range(len(lightmatrix)):
            led.setSpalte(x,rgb.get('r'),rgb.get('g'),rgb.get('b'))
            time.sleep(speed)
            if x-1 == -1:
                led.setSpalte(len(lightmatrix)-1,0,0,0)
            else:
                led.setSpalte(x-1,0,0,0)
                
def faideAll(self, wait, r,g,b):
    print("faideAll was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    speed = config.get_led_default_speed()
    while self.running:
        for j in range(256): # one cycle of all 256 colors in the wheel
            for i in range(led.pixels.count()):
                led.pixels.set_pixel(i, led.wheel(((256 // led.pixels.count() + j)) % 256) )
            led.pixels.show()
            if speed > 0:
                time.sleep(speed)