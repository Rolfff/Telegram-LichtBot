#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lampeLib import light
import logging
import conf as Conf
import threading, time
import os

class bootBot:

    l = None
    th = None

    def __init__(self):
        self.l = light() 
        self.l.allOff()
    
        self.th = RaspberryThread()
        self.th.start()
        while True:
            a = os.system ("ping -c 1 tomatenjoe.com")
            print('a:'+str(a))
            if a == 0:
                break
            time.sleep(3)
        self.th.stop()
        self.l.setPixel(self.l.bottomled,0,0,255)
        time.sleep(1)
        self.l.setPixel(self.l.bottomled,0,0,0)
    
class RaspberryThread(threading.Thread):
    def __init__(self):
        self.running = False
        super(RaspberryThread, self).__init__()

    def start(self):
        self.running = True
        super(RaspberryThread, self).start()

    def run(self):
        led = light() 
        while self.running:
            led.setPixel(led.bottomled,255,0,0)
            time.sleep(1)
            led.setPixel(led.bottomled,0,0,0)
            time.sleep(1)

    def stop(self):
        self.running = False
    

        
#th = RaspberryThread()
#th.start()
#time.sleep(10)
#th.stop()

def main():
    
    bootBot() 

if __name__ == '__main__':
    main()