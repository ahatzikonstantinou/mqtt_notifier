#!/usr/bin/env python
import paho.mqtt.client as mqtt  #import the client1
import signal   #to detect CTRL C
import sys

import json #to generate payloads for mqtt publishing
import os.path # to check if configuration file exists


#from https://www.connectedcities.com.ph/blogs/tutorial/sim800l-and-raspberry-pi-3-b-controlled-3-led-tutorial
import RPi.GPIO as GPIO
import serial
import time, sys
import datetime

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

SERIAL_PORT = "/dev/ttyS0"    # Rasp 3 UART Port

ser = serial.Serial(SERIAL_PORT, baudrate = 115200, timeout = 5)
setup()
ser.write("AT+CMGF=1\r") # set to text mode
time.sleep(1)
ser.write('AT+CMGDA="DEL ALL"\r') # delete all SMS
time.sleep(1)
reply = ser.read(ser.inWaiting()) # Clean buf
print "Listening for incomming SMS..."
while True:
    reply = ser.read(ser.inWaiting())
    if reply != "":
        ser.write("AT+CMGR=1\r") 
        time.sleep(1)
        reply = ser.read(ser.inWaiting())
        print "SMS received. Content:"
        print reply
 	if "ON" in reply.upper():
	    if "LED1" in reply.upper():
                print "LED 1 ON"
                GPIO.output(23,GPIO.HIGH)
	    if "LED2" in reply.upper():
                print "LED 2 ON"
                GPIO.output(24,GPIO.HIGH)
            if "LED3" in reply.upper():
                print "LED 3 ON"
                GPIO.output(25,GPIO.HIGH)
            if "ALL" in reply.upper():
		print ("ALL LED ON")
                GPIO.output(23,GPIO.HIGH)
                GPIO.output(24,GPIO.HIGH)
                GPIO.output(25,GPIO.HIGH)
	if "OFF" in reply.upper():
	    if "LED1" in reply.upper():
                print "LED 1 OFF"
                GPIO.output(23,GPIO.LOW)
	    if "LED2" in reply.upper():
                print "LED 2 OFF"
                GPIO.output(24,GPIO.LOW)
            if "LED3" in reply.upper():
                print "LED 3 OFF"
                GPIO.output(25,GPIO.LOW)
            if "ALL" in reply.upper():
                print "ALL LED OFF"
                GPIO.output(23,GPIO.LOW)
                GPIO.output(24,GPIO.LOW)
                GPIO.output(25,GPIO.LOW)
        time.sleep(.500)
        ser.write('AT+CMGDA="DEL ALL"\r') # delete all
        time.sleep(.500)
        ser.read(ser.inWaiting()) # Clear buffer
        time.sleep(.500)  


if( __name__ == '__main__' ):
    configurationFile = 'notifier.conf'
    if( not os.path.isfile( configurationFile ) ):
        print( 'Configuration file "{}" not found, exiting.'.format( configurationFile ) )
        sys.exit()

    with open( configurationFile ) as json_file:
        configuration = json.load( json_file )
        print( 'Configuration: ' )
        pprint( configuration )