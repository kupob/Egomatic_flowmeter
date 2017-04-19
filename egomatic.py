# -*- coding: utf-8 -*-
# !/usr/bin/python
import os
import time
import math
import logging
import sys
import RPi.GPIO as GPIO
from flowmeter import *
from data_sender import *
from data_receiver import *
from configreader import *

# read configuration settings
config = ConfigReader()
_GPIO_pin_list = config.get_GPIO_pins()

print ('Listening flowmeters on pins ' + str(_GPIO_pin_list).strip('[]'))

GPIO.setmode(GPIO.BCM)  # use real GPIO numbering
GPIO.setup(_GPIO_pin_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# set up the flow meters
flowmeters = {}
flowmeters_stopvalues = {}


def tick_once(channel):
    flowmeters[channel].tick()


i = 0
for pin in _GPIO_pin_list:
    _flowmeter = FlowMeter(config.get_pulses_per_liter())
    flowmeters[pin] = _flowmeter
    flowmeters_stopvalues[pin] = 0.0
    GPIO.add_event_detect(pin, GPIO.RISING, callback=tick_once, bouncetime=20)

sender = DataSender()
sender.daemon = True
sender.start()
receiver = DataReceiver()
receiver.daemon = True
receiver.start()

# main loop
last_notify_time = 0
while True:
    current_time = int(time.time() * FlowMeter.MS_IN_A_SECOND)

    # Notify periodically
    if current_time - last_notify_time > 2000:
        sender.send_notify_signal()
        last_notify_time = current_time

    for pin in _GPIO_pin_list:
        flowmeter = flowmeters[pin]
        flowmeter_stopvalue = flowmeters_stopvalues[pin]

        # Check for stop signal
        if flowmeter.thisPour > flowmeter_stopvalue:
            sender.send_stop_signal(pin)
            sender.send_flow(pin, flowmeter.thisPour)
            flowmeter.thisPour = 0.0

        # Send flow
        if flowmeter.thisPour > 0.0 and current_time - flowmeter.lastClick > 1000:
            sender.send_flow(pin, flowmeter.thisPour)
            flowmeter.thisPour = 0.0

    while receiver.is_message_come():
        message = receiver.get_message()

