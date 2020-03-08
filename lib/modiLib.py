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

#Funktionen hier registrieren für Partymode
# Funktionen Map{ Funk-Name: 
tastertur = {'runHorizontal': 'faidHori',
         'stars': 'DicoKugel',
         'strobo': 'Strobo Licht',
         'laufHorizontal': 'Hori. Lauflicht',
         'laufVertikal': 'Verti. Lauflicht'}

textbefehl = {'runHorizontal': 'faidHori',
         'stars': 'DicoKugel',
         'strobo': 'StroboLicht',
         'laufHorizontal': 'HoriLauflicht',
         'laufVertikal': 'VertiLauflicht'}


def runHorizontal(self,wait, r,g,b):
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
    led = light()
    #setPixel(self.lightmatrix[x][y],r,g,b)

def strobo(self,wait, r,g,b):
    print("strobo was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    while self.running:
        led.all(r,g,b)
        time.sleep(wait)
        led.all(0,0,0)
        #led.allOff(False)
        time.sleep(wait)

#in Smooshig bestimmt auch seht schön
def laufHorizontal(self,wait, r,g,b):
    print("laufHorizontal was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    while self.running:
        for y in range(1+len(Conf.OneLightmatrix[1])):
            if y == len(Conf.OneLightmatrix[1]):
                led.setBottomLed(r,g,b)
            else:
                led.setZeile(y,r,g,b)
            time.sleep(wait)
            if y-1 == -1:
                led.setBottomLed(0,0,0)
            else:
                led.setZeile(y-1,0,0,0)
  

def laufVertikal(self,wait, r,g,b):
    print("laufVertikal was called : wait=%s; r=%s; g=%s; b=%s" % (str(wait), str(r), str(g), str(b)))
    led = light()
    while self.running:
        for x in range(len(Conf.OneLightmatrix)):
            led.setSpalte(x,r,g,b)
            time.sleep(wait)
            if x-1 == -1:
                led.setSpalte(len(Conf.OneLightmatrix)-1,0,0,0)
            else:
                led.setSpalte(x-1,0,0,0)