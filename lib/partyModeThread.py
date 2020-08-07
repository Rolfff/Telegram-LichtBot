#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, imp
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("conf", "../conf.py")
import conf as Conf
load_src("partyMode", "partyMode.py")
import partyMode as Modi
load_src("lampeLib", "lampeLib.py")
from lampeLib import light
import logging
import threading, time


class PartyMode:

    #th = Conf.OneThreadSingleton
    #speed = Conf.OneSpeedSingleton
    
    #def __init__(self):
        #Conf.OneThreadSingleton = "test"
    tastertur = Modi.tastertur
    textbefehl = Modi.textbefehl
    
    def getSpeed(self):
        return Conf.OneSpeedSingleton
    
    def setSpeed(self,sp):
        Conf.OneSpeedSingleton = sp
        
    def stop(self):
        Conf.OneThreadSingleton.stop()
    
    #modi = 'FunktionsName als String'
    def startModi(self, modi, wait = Conf.OneSpeedSingleton, r=255, g=255, b=255):
        method_to_call = getattr(Modi, modi)
        if Conf.OneThreadSingleton is not None:
            if Conf.OneThreadSingleton.isRunning:
                Conf.OneThreadSingleton.stop()
          #      time.sleep(Conf.OneSpeedSingleton)
        Conf.OneThreadSingleton = RaspberryThread(target=method_to_call, args=(wait,r,g,b,))
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
    
    

def main():
    #led = light()
   #led.on()
 #  led.all(255,255,255)
 #  time.sleep(10)
   #led.off()
 #  led.all(0,0,0)
    pm = PartyMode()
    #pm.regenbogenHorizontal()
    #result = method_to_call()
    pm.startModi( 'faideAll', 0.05,0,255,0)
    #pm.laufVertikal(0.05,0,255,0)
    time.sleep(10)
    
    Conf.OneThreadSingleton.stop()
    

if __name__ == '__main__':
    main()
