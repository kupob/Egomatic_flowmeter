# -*- coding: utf-8 -*-
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
config = ConfigReader()
_GPIO_pin_list = config.get_GPIO_pins()

print ('Listening flowmeters on pins ' + str(_GPIO_pin_list).strip('[]'))

GPIO.setmode(GPIO.BCM)  # use real GPIO numbering
GPIO.setup(_GPIO_pin_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# set up the flow meters
_GPIO_flowmeters = {}


def tick_once(channel):
    _GPIO_flowmeters[channel].tick()

i = 0
for pin in _GPIO_pin_list:
    _flowmeter = FlowMeter(config.get_pulses_per_liter())
    _GPIO_flowmeters[pin] = _flowmeter
    GPIO.add_event_detect(pin, GPIO.RISING, callback=tick_once, bouncetime=20)

sender = DataSender()

# main loop
last_notify_time = 0
while True:
    current_time = int(time.time() * FlowMeter.MS_IN_A_SECOND)

    if current_time - last_notify_time > 2000:
        sender.send_notify_signal()
        last_notify_time = current_time

    for pin in _GPIO_pin_list:
        flowmeter = _GPIO_flowmeters[pin]

        if flowmeter.thisPour > 0.001 and current_time - flowmeter.lastClick > 1000:
            sender.send_flow(pin, flowmeter.thisPour)
            flowmeter.thisPour = 0.0
