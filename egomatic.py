# -*- coding: utf-8 -*-
# !/usr/bin/python
import threading
import RPi.GPIO as GPIO
from flowmeter import *
from network_sender import *
from network_receiver import *
from configreader import *
import ast

# read configuration settings
config = ConfigReader()
_GPIO_pin_list = [int(s) for s in config.get_GPIO_pins().split()]

print ('Listening flowmeters on pins ' + str(_GPIO_pin_list).strip('[]'))

GPIO.setmode(GPIO.BCM)  # use real GPIO numbering
GPIO.setup(_GPIO_pin_list, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# set up the flow meters
flowmeters = {}
flowmeters_stopvalues = {}
prices_loaded = False
customer_balance = 0.0


def tick_once(channel):
    flowmeters[channel].tick()


i = 0
for pin in _GPIO_pin_list:
    _flowmeter = FlowMeter(config.get_pulses_per_liter())
    flowmeters[pin] = _flowmeter
    flowmeters_stopvalues[pin] = 0.0
    GPIO.add_event_detect(pin, GPIO.RISING, callback=tick_once, bouncetime=20)

sender_event = threading.Event()
sender = NetworkSender(sender_event)
sender.daemon = True
sender.start()
receiver_event = threading.Event()
receiver = NetworkReceiver(receiver_event)
receiver.daemon = True
receiver.start()

# main loop
last_notify_time = 0
while True:
    current_time = int(time.time() * FlowMeter.MS_IN_A_SECOND)

    # Notify periodically
    if current_time - last_notify_time > 2000:
        sender_event.set()
        sender.send_notify_signal()
        last_notify_time = current_time
        if not prices_loaded:
            sender_event.set()
            sender.send_prices_request()

    for pin in _GPIO_pin_list:
        flowmeter = flowmeters[pin]
        flowmeter_stopvalue = flowmeters_stopvalues[pin]

        # Check for stop signal
        if flowmeter.totalPour - customer_balance:
            sender_event.set()
            sender.send_stop_signal(pin)
            sender_event.set()
            sender.send_flow(pin, flowmeter.thisPour)
            flowmeter.thisPour = 0.0

        # Send flow
        if flowmeter.thisPour > 0.0 and current_time - flowmeter.lastClick > 1000:
            sender_event.set()
            sender.send_flow(pin, flowmeter.thisPour)

            flowmeter.clear()

    receiver_event.set()
    while receiver.is_message_come():
        message = receiver.get_message()
        message_split = message.split()
        message_type = int(message_split[0])

        if message_type == config.get_message_type('MSG_PRICES'):
            message_parsed = ast.literal_eval(message[2:])
            for price_pairs in message_parsed:
                if flowmeters[price_pairs[0]]:
                    prices_loaded = True
                    flowmeters[price_pairs[0]].set_price(price_pairs[1])

        elif message_type == config.get_message_type('MSG_BALANCE'):
            customer_balance = float(message_split[1])
        else:
            print message

