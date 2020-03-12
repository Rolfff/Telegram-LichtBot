#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, imp
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("conf", "../conf.py")
import conf as Conf
load_src("lampeLib", "lampeLib.py")
from lampeLib import light
import time
import random 

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
        #255^3 = 16581375 Farben?
        while self.running:
            led.setHorizontal(255,0,0)
            time.sleep(Conf.OneSpeedSingleton)
            if self.running:
                led.setHorizontal(127,127,0)
                time.sleep(Conf.OneSpeedSingleton)
            if self.running:
                led.setHorizontal(0,255,0)
                time.sleep(Conf.OneSpeedSingleton)
            if self.running:
                led.setHorizontal(0,127,127)
                time.sleep(Conf.OneSpeedSingleton)
            if self.running:
                led.setHorizontal(0,0,255)
                time.sleep(Conf.OneSpeedSingleton)
            if self.running:
                led.setHorizontal(127,0,127)
                time.sleep(Conf.OneSpeedSingleton)   

def stars(self,wait, r,g,b):
    print("stars was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    ledAnzahl = 2
    led = light()
    while self.running:
        temp=[]
        for i in range(ledAnzahl):
            pixel = Conf.OneLightlist[random.randrange(len(Conf.OneLightlist))]
            temp.append(pixel)
            led.setPixel(pixel,Conf.OneRGB.get('r'),Conf.OneRGB.get('g'),Conf.OneRGB.get('b'))
        time.sleep(random.uniform(0.000001, 0.1))
        for i in range(len(temp)):
            led.setPixel(temp[i],0,0,0)

def strobo(self,wait, r,g,b):
    print("strobo was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    while self.running:
        led.all(Conf.OneRGB.get('r'),Conf.OneRGB.get('g'),Conf.OneRGB.get('b'))
        time.sleep(Conf.OneSpeedSingleton)
        led.all(0,0,0)
        #led.allOff(False)
        time.sleep(Conf.OneSpeedSingleton)

#in Smooshig bestimmt auch seht schön
def laufHorizontal(self,wait, r,g,b):
    print("laufHorizontal was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    while self.running:
        for y in range(1+len(Conf.OneLightmatrix[1])):
            if y == len(Conf.OneLightmatrix[1]):
                led.setBottomLed(Conf.OneRGB.get('r'),Conf.OneRGB.get('g'),Conf.OneRGB.get('b'))
            else:
                led.setZeile(y,r,g,b)
            time.sleep(Conf.OneSpeedSingleton)
            if y-1 == -1:
                led.setBottomLed(0,0,0)
            else:
                led.setZeile(y-1,0,0,0)
  

def laufVertikal(self,wait, r,g,b):
    print("laufVertikal was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    while self.running:
        for x in range(len(Conf.OneLightmatrix)):
            led.setSpalte(x,Conf.OneRGB.get('r'),Conf.OneRGB.get('g'),Conf.OneRGB.get('b'))
            time.sleep(Conf.OneSpeedSingleton)
            if x-1 == -1:
                led.setSpalte(len(Conf.OneLightmatrix)-1,0,0,0)
            else:
                led.setSpalte(x-1,0,0,0)
                
def faideAll(self, wait, r,g,b):
    print("faideAll was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    while self.running:
        for j in range(256): # one cycle of all 256 colors in the wheel
            for i in range(led.pixels.count()):
                led.pixels.set_pixel(i, led.wheel(((256 // led.pixels.count() + j)) % 256) )
            led.pixels.show()
            if Conf.OneSpeedSingleton > 0:
                time.sleep(Conf.OneSpeedSingleton)