#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

class OneThreadOnly:  
    singleton = None
    thread = None
   
    def __new__(cls, *args, **kwargs):
        #Wird einmal erstellt
        if not cls.singleton:
            cls.singleton = object.__new__(OneThreadOnly)  
        return cls.singleton  
   
    def __init__(self, th):
        if th is not None:
            if self.thread is not None:
                print ('19: thread ist not None')
                self.thread.stop()
            print ('21: th ist not None')
            self.thread = th
        
    def running(self):
        if self.thread is None:
            print ('th ist None')
            return False
        else:
            print ('th ist not None')
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
        print("Singelton überschreiben: "+name)
        self.name = name  
   
    def print_name(self):  
        print(self.name) 
   
def main(): 
    test1 = OneOnly("Willock")  
   
     
   # test2 = OneOnly.singleton  
      
    test2 = OneOnly("NONONO")  
    #assert test1 == test2  
    print("test1.name: ", test1.name)  
    print("test2.name: ", test2.name)  
    test1.print_name()
   
if __name__ == '__main__':
    main()