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

    th = None

    def regenbogen(self,wait):
        self.th = RaspberryThread()
        self.th.start(wait)
        return self.th
        
    
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
            led.on(255,0,0,self.wait)
            time.sleep(self.wait)
            led.on(127,127,0,self.wait)
            time.sleep(self.wait)
            led.on(0,255,0,self.wait)
            time.sleep(self.wait)
            led.on(0,127,127,self.wait)
            time.sleep(self.wait)
            led.on(0,0,255,self.wait)
            time.sleep(self.wait)
            led.on(127,0,127,self.wait)
            time.sleep(self.wait)
            

    def stop(self):
        self.running = False
    

        
#th = RaspberryThread()
#th.start()
#time.sleep(10)
#th.stop()

def main():
    
    pm = PartyMode()
    th = pm.regenbogen(0.1)
    time.sleep(10)
    th.stop()

if __name__ == '__main__':
    main()
