#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import division
import time
import sys

# Try to import RPi.GPIO, fallback to mock if not on Raspberry Pi
try:
    import RPi.GPIO as GPIO
except (ImportError, RuntimeError):
    print("Warning: RPi.GPIO not available - using mock GPIO")
    # Create a simple mock GPIO class for non-Raspberry Pi systems
    class MockGPIO:
        BCM = 'BCM'
        OUT = 'OUT'
        HIGH = 1
        LOW = 0
        
        @staticmethod
        def setmode(mode):
            print(f"Mock GPIO setmode: {mode}")
            
        @staticmethod
        def setup(pin, direction, initial=None):
            print(f"Mock GPIO setup: pin {pin}, direction {direction}")
            
        @staticmethod
        def output(pin, value):
            print(f"Mock GPIO output: pin {pin}, value {value}")
            
        @staticmethod
        def setwarnings(state):
            print(f"Mock GPIO setwarnings: {state}")
            
        @staticmethod
        def cleanup():
            print("Mock GPIO cleanup")
    
    GPIO = MockGPIO
 
# WS2801 GPIO pins
CLK_PIN = 11  # GPIO 11 (Pin 23)
DATA_PIN = 10  # GPIO 10 (Pin 19)

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(CLK_PIN, GPIO.OUT)
GPIO.setup(DATA_PIN, GPIO.OUT)

class WS2801:
    def __init__(self, clk_pin, data_pin, num_pixels):
        self.clk_pin = clk_pin
        self.data_pin = data_pin
        self.num_pixels = num_pixels
        self.pixels = [(0, 0, 0)] * num_pixels
        
    def __setitem__(self, index, color):
        if isinstance(index, slice):
            start, stop, step = index.indices(self.num_pixels)
            for i in range(start, stop, step):
                self.pixels[i] = color
        else:
            self.pixels[index] = color
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            start, stop, step = index.indices(self.num_pixels)
            return [self.pixels[i] for i in range(start, stop, step)]
        else:
            return self.pixels[index]
    
    def __len__(self):
        return self.num_pixels
    
    def clear(self):
        self.pixels = [(0, 0, 0)] * self.num_pixels
        
    def show(self):
        # Send all pixel data
        for r, g, b in self.pixels:
            self._send_byte(r)
            self._send_byte(g)
            self._send_byte(b)
        
        # Send latch signal (clock pulse with no data)
        GPIO.output(DATA_PIN, GPIO.LOW)
        for _ in range(36):  # Latch for WS2801
            GPIO.output(CLK_PIN, GPIO.HIGH)
            GPIO.output(CLK_PIN, GPIO.LOW)
    
    def _send_byte(self, byte):
        for bit in range(7, -1, -1):
            GPIO.output(DATA_PIN, (byte >> bit) & 1)
            GPIO.output(CLK_PIN, GPIO.HIGH)
            GPIO.output(CLK_PIN, GPIO.LOW)
    
    def set_pixel_rgb(self, index, r, g, b):
        self.pixels[index] = (r, g, b)
    
    def get_pixel_rgb(self, index):
        return self.pixels[index]
    
    def set_pixel(self, index, color):
        self.pixels[index] = color
    
    def count(self):
        return self.num_pixels

import os
import sys
import importlib.util
def load_src(name, fpath):
    try:
        full_path = os.path.join(os.path.dirname(__file__), fpath)
        spec = importlib.util.spec_from_file_location(name, full_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[name] = module  # Register in sys.modules
            return module
        else:
            print(f"Could not create spec for {name} from {full_path}")
            return None
    except Exception as e:
        print(f"Error loading module {name} from {fpath}: {e}")
        return None
 
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


class light:

    lightmatrix = []
    lightlist = []
    bottomled = None
    pixels = None
    #Conf.OneSpeedSingleton
    
    def __init__(self):
        
        #LED Nr 15 ist die Mitte
        self.pixels = WS2801(CLK_PIN, DATA_PIN, PIXEL_COUNT)
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
            return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return (255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return (0, pos * 3, 255 - pos * 3)
            
    def betrwRGB(self,rgbWert):
        if rgbWert > 255:
            rgbWert = 255
        if rgbWert < 0:
            rgbWert = 0
        return int(rgbWert)
    
    def setBottomLed(self,r = 0,g = 0,b = 0):
        self.setPixel(self.bottomled,r,g,b)
    
    def setPixel(self,pixel,r = 0,g = 0,b = 0):
        
        pixel.set(self.betrwRGB(r),self.betrwRGB(b),self.betrwRGB(g))
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
#TODO: BottemLED ist ein Wait zu lange
        if self.getWait(wait) > 0:
            time.sleep(self.getWait(wait))
        self.setPixel(self.bottomled,r,g,b)
        
    def setZeile(self,zeilenNr,r=255,g=255,b=255):
        for x in range(len(self.lightmatrix)):
            pixel = self.lightmatrix[x][zeilenNr]
            pixel.set(self.betrwRGB(r),self.betrwRGB(b),self.betrwRGB(g))
            #print(pixel)
            self.pixels.set_pixel_rgb(int(pixel.id), self.betrwRGB(r),self.betrwRGB(g),self.betrwRGB(b))  # Set the RGB color (0-255) of pixel i.
        # Now make sure to call show() to update the pixels with the colors set above!
        self.pixels.show()
        
    def setSpalte(self,spaltenNr,r=255,g=255,b=255):
        for y in range(len(self.lightmatrix[spaltenNr])):
            pixel = self.lightmatrix[spaltenNr][y]
            pixel.set(self.betrwRGB(r),self.betrwRGB(b),self.betrwRGB(g))
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
            pixel.set(self.betrwRGB(r),self.betrwRGB(b),self.betrwRGB(g))
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