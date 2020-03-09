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
    lightlist = []
    bottomled = None
    pixels = None
    #Conf.OneSpeedSingleton
    
    def __init__(self):
        
        #LED Nr 15 ist die Mitte
        self.pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
        self.bottomled= led(BOTTOM_LED)
        
        if Conf.OneLightmatrix is None or Conf.OneLightlist is None:
            self.lightlist.append(self.bottomled)
            tmp = []
            for x in range(len(PIXEL_MAP)):
                l = led(PIXEL_MAP[x])
                tmp.append(l)
                self.lightlist.append(l)
                if int(len(PIXEL_MAP)/ANZSTEGE) == len(tmp):
                    self.lightmatrix.append(tmp)
                    tmp = []
            Conf.OneLightmatrix = self.lightmatrix
            Conf.OneLightlist = self.lightlist
            
        else:
            self.lightmatrix = Conf.OneLightmatrix
            self.lightlist = Conf.OneLightlist
        #self.pixels.clear()
        #print(self.lightmatrix)
                
    # Define the wheel function to interpolate between different hues.
    def wheel(self,pos):
        if pos < 85:
            return Adafruit_WS2801.RGB_to_color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Adafruit_WS2801.RGB_to_color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Adafruit_WS2801.RGB_to_color(0, pos * 3, 255 - pos * 3)
            
    def betrwRGB(self,rgbWert):
        if rgbWert > 255:
            rgbWert = 255
        if rgbWert < 0:
            rgbWert = 0
        return int(rgbWert)
    
    def setBottomLed(self,r = 0,g = 0,b = 0):
        self.setPixel(self.bottomled,r,g,b)
    
    def setPixel(self,pixel,r = 0,g = 0,b = 0):
        
        pixel.set(self.betrwRGB(r),self.betrwRGB(g),self.betrwRGB(b))
        self.pixels.set_pixel_rgb(pixel.id, self.betrwRGB(r),self.betrwRGB(g),self.betrwRGB(b))  # Set the RGB color (0-255) of pixel i.
        # Now make sure to call show() to update the pixels with the colors set above!
        self.pixels.show()
    
    def on(self,r=255,g=255,b=255,wait=0.1,stopThread=True):
        if stopThread:
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
            self.setZeile(y,r,g,b)
            if self.getWait(wait) > 0:
                time.sleep(self.getWait(wait))
        if self.getWait(wait) > 0:
            time.sleep(self.getWait(wait))
        self.setPixel(self.bottomled,r,g,b)
        
    def setZeile(self,zeilenNr,r=255,g=255,b=255):
        for x in range(len(self.lightmatrix)):
            pixel = self.lightmatrix[x][zeilenNr]
            pixel.set(self.betrwRGB(r),self.betrwRGB(g),self.betrwRGB(b))
            #print(pixel)
            self.pixels.set_pixel_rgb(int(pixel.id), self.betrwRGB(r),self.betrwRGB(g),self.betrwRGB(b))  # Set the RGB color (0-255) of pixel i.
        # Now make sure to call show() to update the pixels with the colors set above!
        self.pixels.show()
        
    def setSpalte(self,spaltenNr,r=255,g=255,b=255):
        for y in range(len(self.lightmatrix[spaltenNr])):
            pixel = self.lightmatrix[spaltenNr][y]
            pixel.set(self.betrwRGB(r),self.betrwRGB(g),self.betrwRGB(b))
            self.pixels.set_pixel_rgb(pixel.id, self.betrwRGB(r),self.betrwRGB(g),self.betrwRGB(b))  # Set the RGB color (0-255) of pixel i.
        # Now make sure to call show() to update the pixels with the colors set above!
        self.pixels.show()
            
    def off(self,r=0,g=0,b=0,wait=0.1,stopThread=True):
        if stopThread:
            self.stopThread()
        self.setPixel(self.bottomled,r,g,b)
        if self.getWait(wait) > 0:
            time.sleep(self.getWait(wait))
        for y in reversed(range(len(self.lightmatrix[1]))):
            self.setZeile(y,r,g,b)
            if self.getWait(wait) > 0:
                time.sleep(self.getWait(wait))
        
                
#    def fadeAllColors(self, wait=0.005):
#        th = RainbowThread()
#        th.start(self.pixels, wait, lightmatrix, self)
#        return th
    def all(self,r=255,g=255,b=255):
        
        self.pixels.clear()
        for z in range(len(self.lightlist)):
            
            pixel = self.lightlist[z]
            #print(pixel.id)
            pixel.set(self.betrwRGB(r),self.betrwRGB(g),self.betrwRGB(b))
            self.pixels.set_pixel_rgb(pixel.id, self.betrwRGB(r),self.betrwRGB(g),self.betrwRGB(b))  # Set the RGB color (0-255) of pixel i.
        # Now make sure to call show() to update the pixels with the colors set above!
        self.pixels.show()
        
                
    def allOff(self,stopThread=True):
        if stopThread:
            self.stopThread()
        self.pixels.clear()
        
   
    
def main():
    
    l = light() 
    l.on()
    
    
    
    
if __name__ == '__main__':
    main()