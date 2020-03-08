#!/usr/bin/python3
# -*- coding: utf-8 -*-

class led:
    
    id = None
    r = 0
    g = 0
    b = 0
    lr = 0
    lg = 0
    lb = 0
    
    def __init__(self,id):
        self.id = id
        self.r = 0
        self.g = 0
        self.b = 0
        
    def set(self,r,g,b):
        self.r = r
        self.g = g
        self.b = b
    
    def __str__(self):
        return "id = %f, r = %f , g = %f , b = %f" % (self.id, self.r, self.g, self.b)