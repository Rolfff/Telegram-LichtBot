#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import division
import time
import RPi.GPIO as GPIO
 
# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPIimport

# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

import os, imp
def load_src(name, fpath):
    return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
 
load_src("ledLib", "ledLib.py")
from ledLib import led
load_src("singletonLib", "singletonLib.py")
from singletonLib import OneThreadOnly, OneSpeedOnly
load_src("conf", "../conf.py")
import conf as Conf
#load_src("partyModeLib", "partyModeLib.py")
#from partyModeLib import PartyMode

# Configure the count of pixels:
PIXEL_COUNT = Conf.pin['pixelCount']
ANZSTEGE = Conf.pin['anzalStege']
#Reinfolge der LED-Adressen pro Steg im Uhrzeigersin
PIXEL_MAP = Conf.pin['pixelMap']
BOTTOM_LED = Conf.pin['bottomLed']
# The WS2801 library makes use of the BCM pin numbering scheme. See the README.md for details.

# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = Conf.pin['spiPort']
SPI_DEVICE = Conf.pin['spiDevice']

class light:

    lightmatrix = []
    bottomled = None
    pixels = None
    #Conf.OneSpeedSingleton
    
    def __init__(self):
        
        
        #LED Nr 15 ist die Mitte
        self.pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
        self.bottomled= led(BOTTOM_LED)
        pixelCounter = 0
        for x in range(ANZSTEGE):
            tmp = []
            for y in range(int(PIXEL_COUNT/ANZSTEGE)):
                l = led(PIXEL_MAP[pixelCounter])
                tmp.append(l)
                pixelCounter = pixelCounter + 1
            self.lightmatrix.append(tmp)
        #self.pixels.clear()
        #print(self.lightmatrix)
    
    def setPixel(self,pixel,r = 0,g = 0,b = 0):
        if r > 255:
            r = 255
        if g > 255:
            g = 255
        if b > 255:
            b = 255
        if r < 0:
            r = 0
        if g < 0:
            g = 0
        if b < 0:
            b = 0
        pixel.set(r,g,b)
        self.pixels.set_pixel_rgb(pixel.id, r, g, b)  # Set the RGB color (0-255) of pixel i.
        # Now make sure to call show() to update the pixels with the colors set above!
        self.pixels.show()
    
    def on(self,r=255,g=255,b=255,wait=0.1):
        self.stopThread()
        self.setHorizontal(r,g,b,wait)
        
    def getWait(self, wait=None):
        if wait is None:
            wait = Conf.OneSpeedSingleton
        return wait
    
    def stopThread(self):
        if Conf.OneThreadSingleton is not None:
            if Conf.OneThreadSingleton.isRunning:
                Conf.OneThreadSingleton.stop()
                time.sleep(Conf.OneSpeedSingleton)
        
    def setHorizontal(self,r=255,g=255,b=255,wait=None):
        for y in range(len(self.lightmatrix[1])):
            for x in range(len(self.lightmatrix)):
                self.setPixel(self.lightmatrix[x][y],r,g,b)
            if self.getWait(wait) > 0:
                time.sleep(self.getWait(wait))
        if self.getWait(wait) > 0:
            time.sleep(self.getWait(wait))
        self.setPixel(self.bottomled,r,g,b)
            
    def off(self,r=0,g=0,b=0,wait=0.1):
        self.stopThread()
        self.setPixel(self.bottomled,r,g,b)
        if self.getWait(wait) > 0:
            time.sleep(self.getWait(wait))
        for y in reversed(range(len(self.lightmatrix[1]))):
            for x in range(len(self.lightmatrix)):
                self.setPixel(self.lightmatrix[x][y],r,g,b)
            if self.getWait(wait) > 0:
                time.sleep(self.getWait(wait))
        
                
#    def fadeAllColors(self, wait=0.005):
#        th = RainbowThread()
#        th.start(self.pixels, wait, lightmatrix, self)
#        return th
        
                
    def allOff(self):
        self.stopThread()
        self.pixels.clear()
        
   
    
def main():
    
    l = light() 
    l.on()
    
    
    
    
if __name__ == '__main__':
    main()