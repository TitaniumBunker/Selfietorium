#!/usr/bin/python
# coding=utf-8
import sys
import datetime
try:
    import RPi.GPIO as GPIO
except:
    pass



class Flash :
    """A Class for turning on a flash before taking a photo"""
    gpioImported = True
    modulename = 'RPi.GPIO'
    if modulename in sys.modules:
        channel = 8
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(channel, GPIO.OUT)
    
    
    if modulename not in sys.modules:
        gpioImported = False    

    
    def flash_on(self):
        if (self.gpioImported):
            print "GPIO FLASH ON"
        print "FLASH ON"
        
    def flash_off(self):
        if (self.gpioImported):
            print "GPIO FLASH OFF"
        
        print "FLASH OFF"
        
if __name__ == '__main__':
    # Add sample Code here
    print "This is a flash example"
    c = Flash()
    c.flash_on()
    c.flash_off()
