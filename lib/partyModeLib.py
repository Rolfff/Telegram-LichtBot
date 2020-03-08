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

    def regenbogenHorizontal(self):
        Conf.OneThreadSingleton = RaspberryThread(target=runHorizontal, args=(1,2,))
        Conf.OneThreadSingleton.start()
        
    
    def stop(self):
        Conf.OneThreadSingleton.stop()
        
    
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
        


def main():
   
    pm = PartyMode()
    pm.regenbogenHorizontal()
    time.sleep(10)
    
    Conf.OneThreadSingleton.stop()
    

if __name__ == '__main__':
    main()
