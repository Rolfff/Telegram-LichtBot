#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, imp
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("conf", "../conf.py")
import conf as Conf
load_src("lampeLib", "lampeLib.py")
from lampeLib import light
import logging
import threading, time


class PartyMode:

    #th = Conf.OneThreadSingleton
    #speed = Conf.OneSpeedSingleton
    
    #def __init__(self):
        #Conf.OneThreadSingleton = "test"
        
        
    def getSpeed(self):
        return Conf.OneSpeedSingleton
    
    def setSpeed(self,sp):
        Conf.OneSpeedSingleton = sp
        
    def stop(self):
        Conf.OneThreadSingleton.stop()

    def regenbogenHorizontal(self):
        Conf.OneThreadSingleton = RaspberryThread(target=runHorizontal, args=(1,2,))
        Conf.OneThreadSingleton.start()
        
        #wait = 0.05 ist geil
    def strobo(self, wait = Conf.OneSpeedSingleton, r=255, g=255, b=255):
        Conf.OneThreadSingleton = RaspberryThread(target=strobo, args=(wait,r,g,b,))
        Conf.OneThreadSingleton.start()   
    
    def laufHorizontal(self, wait = Conf.OneSpeedSingleton, r=255, g=255, b=255):
        Conf.OneThreadSingleton = RaspberryThread(target=laufHorizontal, args=(wait,r,g,b,))
        Conf.OneThreadSingleton.start()
        
    def laufVertikal(self, wait = Conf.OneSpeedSingleton, r=255, g=255, b=255):
        Conf.OneThreadSingleton = RaspberryThread(target=laufVertikal, args=(wait,r,g,b,))
        Conf.OneThreadSingleton.start()
        
    
class RaspberryThread(threading.Thread):
    running = False
    
    def __init__(self,target,args):
        self.running = False
        self.__target = target
        self.__args = args
        threading.Thread.__init__(self)
        #super(RaspberryThread, self).__init__()
        

    def start(self):
        led = light()
        led.stopThread()
        self.running = True
        super(RaspberryThread, self).start()

    def run(self):
        try:
            if self.__target:
                self.__target(self,*self.__args)#, **self.__kwargs)
        finally:
        # Avoid a refcycle if the thread is running a function with
        # an argument that has a member that points to the thread.
            del self.__target, self.__args#, self.__kwargs

    def stop(self):
        self.running = False
        
    def isRunning(self):
        return self.running
    
    
def runHorizontal(self,data, key):
        print("runHorizontal was called : data=%s; key=%s" % (str(data), str(key)))
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

def stars(self,data, key):
    print("stars was called : data=%s; key=%s" % (str(data), str(key)))
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
            

def main():
    #led = light()
   #led.on()
 #  led.all(255,255,255)
 #  time.sleep(10)
   #led.off()
 #  led.all(0,0,0)
    pm = PartyMode()
    #pm.regenbogenHorizontal()
    pm.laufVertikal(0.05,0,255,0)
    time.sleep(10)
    
    Conf.OneThreadSingleton.stop()
    

if __name__ == '__main__':
    main()
