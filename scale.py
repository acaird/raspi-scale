#!/usr/bin/env python
import yaml
import shelve
import logging
import scaleConfig
import argparse

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

configFile = './scaleConfig.yaml'

parser = argparse.ArgumentParser()
parser.add_argument ("-d", "--debug", type=int, choices=[0,1],
		     nargs='?', const=1,
		     help="turn debugging on (1) or off (0); this overrides"+
		     "the value in the configuration file ")
parser.add_argument("-c","--config", action="store", dest="configFile",
		    help="specify a configuration file")
args = parser.parse_args()

if args.configFile:
	configFile = args.configFile

cfg = scaleConfig.readConfig(configFile)

try:
        f = open(cfg['raspberryPiConfig']['plotlyCredsFile'])
except:
        print "=========================== ERROR ==========================="
        print "I couldn't open the file '{0}'".format(cfg['raspberryPiConfig']['plotlyCredsFile'])
        print "to read the plot.ly settings, so I can't make a plot and"
        print "am giving up."
        print "(I am:", os.path.abspath(os.path.dirname(sys.argv[0]))+"/"+sys.argv[0],")"
        print "=========================== ERROR ==========================="
        exit (1)

plotlyConfig = yaml.safe_load(f)
f.close()

if args.debug == None:
	DEBUG = cfg['raspberryPiConfig']['debug']
else:
	DEBUG = args.debug

if DEBUG:
	print "Initializing."

if not cfg['raspberryPiConfig']['alertChannels']:
	cfg['raspberryPiConfig']['alertChannels'] = ''
if not cfg['raspberryPiConfig']['updateChannels']:
	cfg['raspberryPiConfig']['updateChannels'] = ''


import time
import datetime
import os
import RPi.GPIO as GPIO
import scalePlotly
import scaleTwitter
import scaleEmail
import scaleAlerts

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) # to stop the "This channel is already in use" warning

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
# ADCPort    Cobbler
# -------- ----------
SPICLK    =    cfg['raspberryPiConfig']['ADCtoCobbler']['SPICLK']
SPIMISO   =    cfg['raspberryPiConfig']['ADCtoCobbler']['SPIMISO']
SPIMOSI   =    cfg['raspberryPiConfig']['ADCtoCobbler']['SPIMOSI']
SPICS     =    cfg['raspberryPiConfig']['ADCtoCobbler']['SPICS']
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
fsr_adc = cfg['raspberryPiConfig']['adcPortWithFSR']

# this keeps track of the last FSR value
last_read = 0

# to keep from being jittery we'll only change when the FSR has moved
# more than this many 'counts'
tolerance = cfg['raspberryPiConfig']['tolerance']

# not ideal, but at least it's just in one place now
logString = '{0} {1}\tfsr: {2:4d}\tlast_value: {3:4d}\tchange: {4:4d}\tbeans: {5}'


#
# If we will need Twitter credentials, read them now
#
if 'twitter' in cfg['raspberryPiConfig']['alertChannels'] or 'twitter' in cfg['raspberryPiConfig']['updateChannels']:
	if DEBUG:
		print "Reading Twitter credentials from ",cfg['twitterConfiguration']['twitterCredsFile']

        try:
                f = open(cfg['twitterConfiguration']['twitterCredsFile'])
                twitterCredentials = yaml.safe_load(f)
                f.close()
        except:
                if DEBUG:
                        print "=========================== ERROR ==========================="
                        print "I couldn't open the file '{0}'".format(cfg['twitterConfiguration']['twitterCredsFile'])
                        print "to read the twitter credentials, so I can't tweet."
                        print "(I am:", os.path.abspath(os.path.dirname(sys.argv[0]))+"/"+sys.argv[0],")"
                        print "=========================== ERROR ==========================="

			cfg['raspberryPiConfig']['alertChannels'].remove('twitter')
			cfg['raspberryPiConfig']['updateChannels'].remove('twitter')

oTime = cfg['raspberryPiConfig']['updateTime']

while cfg['raspberryPiConfig']['updateTime'] % cfg['raspberryPiConfig']['checkTime']:
        cfg['raspberryPiConfig']['updateTime'] += 1

if oTime != cfg['raspberryPiConfig']['updateTime'] and DEBUG:
        print "\"updateTime\" changed from {0} to {1} so it would divide evenly by \"checkTime\".".format(oTime, cfg['raspberryPiConfig']['updateTime'])

# This totally isn't a clock, it's a counter.  But we use it sort of
# like a clock.
scaleClock = 0

# Python shelves let us keep some state between runs; in this case, we
# are keeping the state of the alerts we have generated, so we don't
# re-send emails or tweets if one has already been sent for a given
# state
alertState = shelve.open("scaleState.db", writeback=True)
for alert in cfg['raspberryPiConfig']['alertChannels']:
        if alert not in alertState:
                alertState[alert] = 0

if DEBUG:
	print "Ready."

while True:

        # read the analog pin
        fsr = readadc(fsr_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # how much has it changed since the last read?
        fsr_change = (fsr - last_read)

	currentTime = str(datetime.datetime.now()).split('.')[0]

        if fsr_change > cfg['raspberryPiConfig']['maxChange'] and ( abs(fsr_change) > tolerance ):
                last_read = fsr
                beans = int((fsr/1024.)*100)
                if DEBUG:
                        print logString.format(currentTime, "CHANGE",
                                               fsr, last_read,
                                               fsr_change, beans)
                scalePlotly.updatePlot (currentTime,
                                        beans,
                                        plotlyConfig['username'],
                                        plotlyConfig['apikey'])

                # I think we only need to check the alert status after
                # changes, within tolerance and maxChange
                scaleAlerts.processLowBeanAlerts (fsr, alertState, cfg, currentTime)


        if scaleClock % cfg['raspberryPiConfig']['updateTime'] == 0:
                last_read = fsr
                beans = int((fsr/1024.)*100)
                if DEBUG:
                        print logString.format(currentTime, "UPDATE",
                                               fsr, last_read,
                                               fsr_change, beans)
                if 'plotly' in cfg['raspberryPiConfig']['updateChannels']:
                        scalePlotly.updatePlot (currentTime,
                                                beans,
                                                plotlyConfig['username'],
                                                plotlyConfig['apikey'])
                if 'twitter' in cfg['raspberryPiConfig']['updateChannels']:
                        hashTags=" ".join(["#"+m for m in cfg['twitterConfiguration']['twitterUpdateHashtags']])
                        tweet   = cfg['twitterConfiguration']['twitterUpdateMessage']+" "+ hashTags
			tweet = tweet.format(beans,currentTime)

                        scaleTwitter.tweetStatus(cfg['twitterConfiguration']['twitterCredsFile'],
                                                 tweet)
                if 'email' in cfg['raspberryPiConfig']['updateChannels']:
                        subject = cfg['emailConfiguration']['emailUpdateSubject']
                        body    = cfg['emailConfiguration']['emailUpdateMessage'].format(beans)

                        scaleEmail.sendEmail (cfg['emailConfiguration']['smtpServer'],
                                              cfg['emailConfiguration']['gmailCredsFile'],
                                              cfg['emailConfiguration']['fromAddr'],
                                              cfg['emailConfiguration']['toAddr'],
                                              subject, body)


        scaleClock += cfg['raspberryPiConfig']['checkTime']

        time.sleep(cfg['raspberryPiConfig']['checkTime'])
