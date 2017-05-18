# -*- coding: utf-8 -*-
import time


class FlowMeter:
    PINTS_IN_A_LITER = 2.11338
    SECONDS_IN_A_MINUTE = 60
    MS_IN_A_SECOND = 1000.0
    display_format = 'metric'
    enabled = True
    pulses_per_liter = 0.0
    clicks = 0
    lastClick = 0
    clickDelta = 0
    hertz = 0.0
    flow = 0  # in Liters per second
    thisPour = 0.0  # in Liters
    totalPour = 0.0  # in Liters

    price = 0.0

    def __init__(self, pulses_per_liter):
        self.clicks = 0
        self.lastClick = int(time.time() * FlowMeter.MS_IN_A_SECOND)
        self.clickDelta = 0
        self.hertz = 0.0
        self.flow = 0.0
        self.thisPour = 0.0
        self.totalPour = 0.0
        self.enabled = True
        self.pulses_per_liter = pulses_per_liter
        self.price = 0.0

    def set_display_format(self, display_format):
        self.display_format = display_format

    def set_price(self, price):
        self.price = price

    def tick(self):
        if not self.enabled:
            return
        current_time = int(time.time() * FlowMeter.MS_IN_A_SECOND)
        self.clicks += 1
        # get the time delta
        self.clickDelta = max((current_time - self.lastClick), 1)
        if self.enabled == True and self.clickDelta < 1000:
            inst_pour = 1 / self.pulses_per_liter
            self.thisPour += inst_pour
            self.totalPour += inst_pour
        # Update the last click
        self.lastClick = current_time

    def getFormattedClickDelta(self):
        return str(self.clickDelta) + ' ms'

    def getFormattedHertz(self):
        return str(round(self.hertz, 3)) + ' Hz'

    def getFormattedFlow(self):
        if self.display_format == 'metric':
            return str(round(self.flow, 3)) + ' L/s'
        else:
            return str(round(self.flow * FlowMeter.PINTS_IN_A_LITER, 3)) + ' pints/s'

    def getFormattedThisPour(self):
        if self.display_format == 'metric':
            return str(round(self.thisPour, 3)) + ' L'
        else:
            return str(round(self.thisPour * FlowMeter.PINTS_IN_A_LITER, 3)) + ' pints'

    def getFormattedTotalPour(self):
        if self.display_format == 'metric':
            return str(round(self.totalPour, 3)) + ' L'
        else:
            return str(round(self.totalPour * FlowMeter.PINTS_IN_A_LITER, 3)) + ' pints'

    def clear(self):
        self.thisPour = 0;
        self.totalPour = 0;
