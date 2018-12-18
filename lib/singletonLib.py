#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

class OneThreadOnly:  
    singleton = None
    thread = None
   
    def __new__(cls, *args, **kwargs):  
        if not cls.singleton:
            print("init Singelton")
            cls.singleton = object.__new__(OneThreadOnly)  
        return cls.singleton  
   
    def __init__(self, th):
        print("Singelton überschreiben ")
        self.stop()
        time.sleep(0.1)
        self.thread = th
        
    def running(self):
        if self.thread is None:
            return False
        else:
            #return self.thread.isRunning()
            return True
        #Warum falakert das Licht beim überschreiben des threads?
        
    def stop(self):
        if self.running():
            self.thread.stop()

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