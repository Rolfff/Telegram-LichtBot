# Simple demo of of WS2801/SPI-like addressable RGB LED lights.
import time
import RPi.GPIO as GPIO
 
# Configure the count of pixels:
PIXEL_COUNT = 31

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
    
    def set_pixel(self, index, color):
        self.pixels[index] = color
    
    def get_pixel_rgb(self, index):
        return self.pixels[index]
    
    def count(self):
        return self.num_pixels

pixels = WS2801(CLK_PIN, DATA_PIN, PIXEL_COUNT)
 
 
# Define wheel function to interpolate between different hues.
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
    for i in range(pixels.count()):
        # tricky math! we use each pixel as a fraction of the full 96-color wheel
        # (thats the i / strip.numPixels() part)
        # Then add in j which makes the colors go around per pixel
        # the % 96 is to make the wheel cycle around
        pixels.set_pixel(i, wheel(((i * 256 // pixels.count())) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def rainbow_cycle(pixels, wait=0.005):
    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(pixels.count()):
            pixels.set_pixel(i, wheel(((i * 256 // pixels.count()) + j) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def rainbow_colors(pixels, wait=0.05):
    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(pixels.count()):
            pixels.set_pixel(i, wheel(((256 // pixels.count() + j)) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def brightness_decrease(pixels, wait=0.01, step=1):
    for j in range(int(256 // step)):
        for i in range(pixels.count()):
            r, g, b = pixels.get_pixel_rgb(i)
            r = int(max(0, r - step))
            g = int(max(0, g - step))
            b = int(max(0, b - step))
            pixels.set_pixel(i, (r, g, b))
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def blink_color(pixels, blink_times=5, wait=0.5, color=(255,0,0)):
    for i in range(blink_times):
        # blink two times, then wait
        pixels.clear()
        for j in range(2):
            for k in range(pixels.count()):
                pixels.set_pixel(k, (color[0], color[1], color[2]))
            pixels.show()
            time.sleep(0.08)
            pixels.clear()
            pixels.show()
            time.sleep(0.08)
        time.sleep(wait)
 
def appear_from_back(pixels, color=(255, 0, 0)):
    pos = 0
    for i in range(pixels.count()):
        for j in reversed(range(i, pixels.count())):
            pixels.clear()
            # first set all pixels at the begin
            for k in range(i):
                pixels.set_pixel(k, (color[0], color[1], color[2]))
            # set then the pixel at position j
            pixels.set_pixel(j, (color[0], color[1], color[2]))
            pixels.show()
            time.sleep(0.02)
            
 
if __name__ == "__main__":
    # Clear all the pixels to turn them off.
    pixels.clear()
    pixels.show()  # Make sure to call show() after changing any pixels!
 
    rainbow_cycle_successive(pixels, wait=0.1)
    rainbow_cycle(pixels, wait=0.01)
 
    brightness_decrease(pixels)
    
    appear_from_back(pixels)
    
    for i in range(3):
        blink_color(pixels, blink_times = 1, color=(255, 0, 0))
        blink_color(pixels, blink_times = 1, color=(0, 255, 0))
        blink_color(pixels, blink_times = 1, color=(0, 0, 255))
 
    
    
    rainbow_colors(pixels)
    
    brightness_decrease(pixels)