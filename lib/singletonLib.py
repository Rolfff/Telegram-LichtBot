#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

class OneThreadOnly:  
    singleton = None
    thread = None
   
    def __new__(cls, *args, **kwargs):  
        if not cls.singleton:
            cls.singleton = object.__new__(OneThreadOnly)  
        return cls.singleton  
   
    def __init__(self, th=None):
        if th is not None:
            self.stop()
            self.thread = th
        
    def running(self):
        if self.thread is None:
            print ('th ist None')
            return False
        else:
            return self.thread.isRunning()
    
    def stop(self):
        if self.running():
            self.thread.stop()
            
class OneSpeedOnly:  
    singleton = None
    speed = None
   
    def __new__(cls, *args, **kwargs):  
        if not cls.singleton:
            cls.singleton = object.__new__(OneSpeedOnly)  
        return cls.singleton  
   
    def __init__(self, sp=0.1):
        if self.speed is None:
            self.speed = sp 
            #print("New Speed: "+str(self.speed))
    
    def getSpeed(self):  
        return self.speed
    
    def setSpeed(self,sp=0.1):  
        self.speed = sp
        
class OneOnly:  
    singleton = None  
   
    def __new__(cls, *args, **kwargs):  
        if not cls.singleton:
            print("init Singelton")
            cls.singleton = object.__new__(OneOnly)  
        return cls.singleton  
   
    def __init__(self, name):
        print("Singelton überschreiben ")
        self.name = name  
   
    def print_name(self):  
        print(self.name) 
   
def main(): 
    test1 = OneOnly("Willock")  
   
    if OneOnly.singleton:  
        test2 = OneOnly.singleton  
    #else:  
    test2 = OneOnly("NONONO")  
    assert test1 == test2  
    print("test1.name: ", test1.name)  
    print("test2.name: ", test2.name)  
    test1.print_name()
   
if __name__ == '__main__':
    main()