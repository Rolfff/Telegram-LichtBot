#!/usr/bin/python3i
import threading

class RainbowThread(threading.Thread):
    def __init__(self):
        self.running = False
        super(RainbowThread, self).__init__()

    def start(self):
        self.running = True
        super(RaspberryThread, self).start()

    def run(self,pixels, wait=0.005, lightmatrix, lampeLib):
        for j in range(256): # one cycle of all 256 colors in the wheel
            for i in range(len(self.lightmatrix[1])):
                lampeLib.setPixel(i, self.wheel(((i * 256 // pixels.count()) + j) % 256) )
            pixels.show()
            if wait > 0:
                time.sleep(wait)
                
    # Define the wheel function to interpolate between different hues.
    def wheel(pos):
        if pos < 85:
            return Adafruit_WS2801.RGB_to_color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Adafruit_WS2801.RGB_to_color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Adafruit_WS2801.RGB_to_color(0, pos * 3, 255 - pos * 3)

    def stop(self):
        self.running = False 