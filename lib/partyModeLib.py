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
load_src("singletonLib", "singletonLib.py")
from singletonLib import OneThreadOnly

class PartyMode:

    #th = Conf.OneThreadSingleton
    #speed = Conf.OneSpeedSingleton
    
    #def __init__(self):
        #Conf.OneThreadSingleton = "test"
        
        
    def getSpeed(self):
        return Conf.OneSpeedSingleton
    
    def setSpeed(self,sp):
        Conf.OneSpeedSingleton = sp

    def regenbogen(self):
        if Conf.OneThreadSingleton is not None:
            if Conf.OneThreadSingleton.isRunning:
                Conf.OneThreadSingleton.stop()
        Conf.OneThreadSingleton = RaspberryThread()
        Conf.OneThreadSingleton.start()
        
    
    def stop(self):
        Conf.OneThreadSingleton.stop()
    
class RaspberryThread(threading.Thread):
    running = False
    
    def __init__(self):
        self.running = False
        super(RaspberryThread, self).__init__()

    def start(self):
        self.running = True
        super(RaspberryThread, self).start()

    def run(self):
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
            

    def stop(self):
        self.running = False
        
    def isRunning(self):
        return self.running
    

        
#th = RaspberryThread()
#th.start()
#time.sleep(10)
#th.stop()

def main():
   
    pm = PartyMode()
    pm.regenbogen()
    time.sleep(10)
    
    Conf.OneThreadSingleton.stop()
    

if __name__ == '__main__':
    main()
