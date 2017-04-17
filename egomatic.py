#!/usr/bin/python
import os
import time
import math
import logging
import sys
import RPi.GPIO as GPIO
from flowmeter import *
from data_sender import *
from configreader import *

# read configuration settings
confReader = ConfigReader()
_GPIO_pin_list = confReader.get_GPIO_pins()

print ('Listening flowmeters on pins ' + str(_GPIO_pin_list).strip('[]'))

GPIO.setmode(GPIO.BCM)  # use real GPIO numbering
GPIO.setup(_GPIO_pin_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# set up the flow meters
_GPIO_flowmeters = {}


def tick_once(channel):
    _GPIO_flowmeters[channel].tick()


i = 0
for pin in _GPIO_pin_list:
    _flowmeter = FlowMeter(confReader.get_pulses_per_liter())
    _GPIO_flowmeters[pin] = _flowmeter
    GPIO.add_event_detect(pin, GPIO.RISING, callback=tick_once, bouncetime=20)

sender = DataSender()

# main loop
while True:
    currentTime = int(time.time() * FlowMeter.MS_IN_A_SECOND)

    for pin in _GPIO_pin_list:
        flowmeter = _GPIO_flowmeters[pin]

        if flowmeter.thisPour > 0.001 and currentTime - flowmeter.lastClick > 1000:
            # message = "Poured " + flowmeter.getFormattedThisPour() + " of " + str(pin)
            # print(message)
            sender.send_flow(pin, flowmeter.thisPour)
            flowmeter.thisPour = 0.0
