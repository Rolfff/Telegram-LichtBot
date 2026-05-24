#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import time

# Try to import RPi.GPIO, use MockGPIO if not available
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("RPi.GPIO nicht verfügbar - verwende MockGPIO (Test-Modus)")
    
    class MockGPIO:
        BCM = 'BCM'
        OUT = 'OUT'
        HIGH = 1
        LOW = 0
        
        @staticmethod
        def setwarnings(warnings):
            pass
            
        @staticmethod
        def setmode(mode):
            pass
            
        @staticmethod
        def setup(pin, direction):
            pass
            
        @staticmethod
        def output(pin, value):
            pass
            
        @staticmethod
        def cleanup():
            pass
    
    GPIO = MockGPIO()
 
# Configure the count of pixels:
PIXEL_COUNT = 32

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

# Create WS2801 instance
pixels = WS2801(CLK_PIN, DATA_PIN, PIXEL_COUNT)
 
 
# Define the wheel function to interpolate between different hues.
def wheel(pos):
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)
 
# Define rainbow cycle function to do a cycle of all hues.
def rainbow_cycle_successive(pixels, wait=0.1):
    for i in range(len(pixels)):
        # tricky math! we use each pixel as a fraction of the full 96-color wheel
        # (thats the i / strip.numPixels() part)
        # Then add in j which makes the colors go around per pixel
        # the % 96 is to make the wheel cycle around
        pixels[i] = wheel(((i * 256 // len(pixels))) % 256)
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def rainbow_cycle(pixels, wait=0.005):
    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(len(pixels)):
            pixels[i] = wheel(((i * 256 // len(pixels)) + j) % 256)
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def rainbow_colors(pixels, wait=0.05):
    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(len(pixels)):
            pixels[i] = wheel(((256 // len(pixels) + j)) % 256)
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def brightness_decrease(pixels, wait=0.01, step=1):
    for j in range(int(256 // step)):
        for i in range(len(pixels)):
            r, g, b = pixels[i]
            r = int(max(0, r - step))
            g = int(max(0, g - step))
            b = int(max(0, b - step))
            pixels[i] = (r, g, b)
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def blink_color(pixels, blink_times=5, wait=0.5, color=(255,0,0)):
    for i in range(blink_times):
        # blink two times, then wait
        pixels.clear()
        for j in range(2):
            for k in range(len(pixels)):
                pixels[k] = color
            pixels.show()
            time.sleep(0.08)
            pixels.clear()
            pixels.show()
            time.sleep(0.08)
        time.sleep(wait)
 
def appear_from_back(pixels, color=(255, 0, 0)):
    pos = 0
    for i in range(len(pixels)):
        for j in reversed(range(i, len(pixels))):
            pixels.clear()
            # first set all pixels at the begin
            for k in range(i):
                pixels[k] = color
            # set then the pixel at position j
            pixels[j] = color
            pixels.show()
            time.sleep(0.02)
            
def allOneCollor(pixels, color=(255, 255, 255)):
    for i in range(len(pixels)):
        pixels[i] = color
    pixels.show() 

def test():
    # Set the first third of the pixels red.
    for i in range(PIXEL_COUNT//3):
        pixels[i] = (255, 0, 0)

    # Set the next third of pixels green.
    for i in range(PIXEL_COUNT//3, PIXEL_COUNT//3*2):
        pixels[i] = (0, 255, 0)

    # Set the last third of pixels blue.
    for i in range(PIXEL_COUNT//3*2, PIXEL_COUNT):
        pixels[i] = (0, 0, 255)

    # Now make sure to call show() to update the pixels with the colors set above!
    pixels.show()
    

if __name__ == "__main__":
    try:
        # Clear all the pixels to turn them off.
        pixels.clear()
        pixels.show()  # Make sure to call show() after changing any pixels!
    
  #  allOneCollor(pixels, color=(255, 255, 255))
    
    
    
    # Clear all the pixels to turn them off.
#    pixels.clear()
#    pixels.show()  # Make sure to call show() after changing any pixels!
 
        rainbow_cycle_successive(pixels, wait=0.1)
        while (5 < 9):
            rainbow_cycle(pixels, wait=0.01)
    except KeyboardInterrupt:
        print("\nProgramm beendet")
        # Turn off all LEDs before exit
        pixels.clear()
        pixels.show()
    finally:
        GPIO.cleanup()
 
#    brightness_decrease(pixels)
    
#    appear_from_back(pixels)
    
#    for i in range(3):
#        blink_color(pixels, blink_times = 1, color=(255, 0, 0))
#        blink_color(pixels, blink_times = 1, color=(0, 255, 0))
 #       blink_color(pixels, blink_times = 1, color=(0, 0, 255))
 
    
    
#    rainbow_colors(pixels)
    
#    brightness_decrease(pixels)
