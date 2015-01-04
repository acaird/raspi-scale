#!/usr/bin/env python
import time
import datetime
import os
import RPi.GPIO as GPIO
'''
This is mostly from:
https://learn.adafruit.com/
   reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/
   script

(git://gist.github.com/3151375.git)

With some modifications by me that should have been other
commits, but weren't, so sorry, you'll have to diff it yourself
if you want to see what changed.

I have no idea what the license is on the original, so I have no
idea what the license on this is.  Personally, I don't care, but
Adafruit might.
'''
 
GPIO.setmode(GPIO.BCM)
DEBUG = 1
 
# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)
 
        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low
 
        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
 
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
 
        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout
 
# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
# ADCPort    Cobbler
# -------- ----------
SPICLK    =    18
SPIMISO   =    23
SPIMOSI   =    24
SPICS     =    25
# Diagram of ADC (MCP3008) is at:
#   https://learn.adafruit.com/
#     reading-a-analog-in-and-controlling-audio-volume-with-the-raspberry-pi/
#     connecting-the-cobbler-to-a-mcp3008
 
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
 
# FSR connected to adc #0
fsr_adc = 0;
 
last_read = 0       # this keeps track of the last FSR value
tolerance = 4.5     # to keep from being jittery we'll only change 
                    # when the FSR has moved more than this many 'counts'
 
while True:
        # we'll assume that the fsr reading didn't change
        fsr_changed = False
 
        # read the analog pin
        fsr = readadc(fsr_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # how much has it changed since the last read?
        fsr_change = (fsr - last_read)
 
 
        if ( abs(fsr_change) > tolerance ):
                fsr_changed = True
        	if DEBUG:
			print '{0}\tfsr: {1:4d}\tlast_value: {2:4d}\tchange: {3:4d}'.format(datetime.datetime.now(),
												fsr,
												last_read,
												fsr_change)
		last_read = fsr
 
        time.sleep(2)
