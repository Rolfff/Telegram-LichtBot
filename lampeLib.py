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

from ledLib import led
#from lib.rainbowLib import RainbowThread

# Configure the count of pixels:
PIXEL_COUNT = 31
ANZSTEGE = 6
#Reinfolge der LED-Adressen pro Steg im Uhrzeigersin
PIXEL_MAP = [0,1,2,3,4,20,19,18,17,16,21,22,23,24,25,9,8,7,6,5,10,11,12,13,14,30,29,28,27,26] 
BOTTOM_LED = 15
# The WS2801 library makes use of the BCM pin numbering scheme. See the README.md for details.

# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0

class light:

    lightmatrix = []
    bottomled = None
    pixels = None

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
        self.pixels.clear()
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
    
    def on(self,r=255,g=255,b=255,wait=0.1,):
        for y in range(len(self.lightmatrix[1])):
            for x in range(len(self.lightmatrix)):
                self.setPixel(self.lightmatrix[x][y],r,g,b)
            if wait > 0:
                time.sleep(wait)
        if wait > 0:
            time.sleep(wait)
        self.setPixel(self.bottomled,r,g,b)
            
    def off(self,r=0,g=0,b=0,wait=0.1):
        self.setPixel(self.bottomled,r,g,b)
        if wait > 0:
            time.sleep(wait)
        for y in reversed(range(len(self.lightmatrix[1]))):
            for x in range(len(self.lightmatrix)):
                self.setPixel(self.lightmatrix[x][y],r,g,b)
            if wait > 0:
                time.sleep(wait)
        
                
#    def fadeAllColors(self, wait=0.005):
#        th = RainbowThread()
#        th.start(self.pixels, wait, lightmatrix, self)
#        return th
        
                
    def allOff(self):
        self.pixels.clear()
        
   
    
def main():
    
    l = light() 
    l.on()
    
    
    
    
if __name__ == '__main__':
    main()