#!/usr/bin/python3
# -*- coding: utf-8 -*-
import socket
from lib.lampeLib import light

UDP_IP_ADDRESS = "192.168.0.2"
UDP_PORT_NO = 21324
secTimeout = 1

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def main():
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
    serverSock.settimeout(secTimeout)
    licht = light()
    partyTime = False

    while True:
        try:
            data, addr = serverSock.recvfrom(1024)
            partyTime = True
            #hex Data    
            ledList = [data[i:i + 3].hex() for i in range(0, len(data), 3)]
            
            for i in range(len(ledList)):
                rgbTuple = hex_to_rgb(ledList[i])
                if i == len(ledList)-1:
                    licht.setBottomLed(rgbTuple[0],rgbTuple[1],rgbTuple[2])
                else:
                    licht.setZeile(i,rgbTuple[0],rgbTuple[1],rgbTuple[2])
            #print (ledList)
            
        except socket.timeout:
            if partyTime:
                print("Timeout!!! Try again...")
                partyTime = False
        
    #    red        red
    #b'\xff\x00\x00\xff\x00\x00'
    #           blue        blue
    #b'\x00\x00\xff\x00\x00\xff'
    #Wenn mehr als eine Sekunde keine Daten kommen partymodus off



    
    
    
    
if __name__ == '__main__':
    main()

