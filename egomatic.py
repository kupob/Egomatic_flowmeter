# -*- coding: utf-8 -*-
# !/usr/bin/python
import threading
import RPi.GPIO as GPIO
from flowmeter import *
from network_sender import *
from network_receiver import *
from configreader import *
import ast
from cyrillic_converter import *

import Adafruit_CharLCD as LCD

lcd_rs = 19  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en = 26
lcd_d4 = 12
lcd_d5 = 16
lcd_d6 = 20
lcd_d7 = 21

lcd_columns = 16
lcd_rows    = 2

lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows)

lcd.clear()

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
customer_id = None


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

lcd_string = ''

# main loop
last_notify_time = 0
last_lcd_update_time = 0
last_acton_time = 0
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

    totalPour = 0.0

    for pin in _GPIO_pin_list:
        flowmeter = flowmeters[pin]
        flowmeter_stopvalue = flowmeters_stopvalues[pin]

        # Check for stop signal
        # TODO рассчитать точное значение слева знака
        if flowmeter.thisPour > 0.0 or flowmeter.totalPour > 0.0:
            totalPour = flowmeter.totalPour
            customer_balance -= flowmeter.thisPour * flowmeter.price
            last_acton_time = max(last_acton_time, flowmeter.lastClick)
            if 5.0 > customer_balance:
                sender.send_stop_signal(pin)
                sender_event.set()
                print "SEND BALANCE"
                sender.send_flow(pin, flowmeter.totalPour, customer_balance, customer_id)
                sender_event.set()

            # Send flow
            if current_time - flowmeter.lastClick > 5000:
                print "SEND BALANCE"
                sender.send_flow(pin, flowmeter.totalPour, customer_balance, customer_id)
                sender_event.set()
                flowmeter.totalPour = 0.0

            flowmeter.thisPour = 0.0

    flow_string = u'В бокале: {:.3f}л'.format(totalPour)
    balance_string = u'На счете:{}{:.1f}р'.format((u'', u' ')[customer_balance < 1000.0], customer_balance)

    if not customer_id or current_time - last_acton_time > 12000:
        new_lcd_string = u'Вставьте карту'
    else:
        new_lcd_string = balance_string + '\n' + flow_string

    if lcd_string != new_lcd_string and current_time - last_lcd_update_time > 200:
        last_lcd_update_time = current_time
        lcd_string = new_lcd_string
        lcd.clear()
        lcd.message(from_cyrillic(lcd_string))

    receiver_event.set()
    while receiver.is_message_come():
        message = receiver.get_message()
        message_split = message.split()
        message_type = int(message_split[0])

        if message_type == config.get_message_type('MSG_PRICES'):
            message_parsed = ast.literal_eval(message[2:])
            prices_loaded = True
            for price_pairs in message_parsed:
                if price_pairs[0] in flowmeters:
                    flowmeters[price_pairs[0]].set_price(price_pairs[1])
        elif message_type == config.get_message_type('MSG_BALANCE'):
            print "BALANCE COME " + ' '.join(message_split)
            customer_balance = float(message_split[1])
            customer_id = message_split[2]
            last_acton_time = current_time
        else:
            print message

