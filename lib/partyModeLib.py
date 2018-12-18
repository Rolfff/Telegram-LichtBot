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
from singletonLib import OneThreadOnly, OneSpeedOnly

class PartyMode:

    th = None
    speed = None
    
    def __init__(self):
        self.speed = OneSpeedOnly()

    def regenbogen(self):
        self.th = RaspberryThread()
        self.th.start(self.speed)
        return OneThreadOnly(self.th)
    
        
    
class RaspberryThread(threading.Thread):
    def __init__(self):
        self.running = False
        self.wait = 0.1
        super(RaspberryThread, self).__init__()

    def start(self,wait):
        self.running = True
        self.wait = wait
        super(RaspberryThread, self).start()

    def run(self):
        led = light()
        #255^3 = 16581375 Farben?
        while self.running:
            led.setHorizontal(255,0,0,self.wait.getSpeed())
            time.sleep(self.wait.getSpeed())
            if self.running:
                led.setHorizontal(127,127,0,self.wait.getSpeed())
                time.sleep(self.wait.getSpeed())
            if self.running:
                led.setHorizontal(0,255,0,self.wait.getSpeed())
                time.sleep(self.wait.getSpeed())
            if self.running:
                led.setHorizontal(0,127,127,self.wait.getSpeed())
                time.sleep(self.wait.getSpeed())
            if self.running:
                led.setHorizontal(0,0,255,self.wait.getSpeed())
                time.sleep(self.wait.getSpeed())
            if self.running:
                led.setHorizontal(127,0,127,self.wait.getSpeed())
                time.sleep(self.wait.getSpeed())
            

    def stop(self):
        self.running = False
        
    def isRunning(self):
        return self.running
    

        
#th = RaspberryThread()
#th.start()
#time.sleep(10)
#th.stop()

def main():
    sp = OneSpeedOnly()
    pm = PartyMode()
    th2 = pm.regenbogen()
    time.sleep(5)
    th=OneThreadOnly()
    th.stop()
    th2.stop()

if __name__ == '__main__':
    main()
