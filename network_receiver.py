# -*- coding: utf-8 -*-

import socket
from threading import *
from configreader import *
from collections import deque


class NetworkReceiver(Thread):
    config = ConfigReader()
    cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message_deque = deque([])

    def __init__(self, event):
        self.event = event
        Thread.__init__(self)

    def run(self):
        try:
            self.cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.cs.bind(('', self.config.get_flowmeter_port()))

            while True:
                self.event.wait()
                message, address = self.cs.recvfrom(1024)
                if message:
                    self.message_deque.append(message)
                self.event.clear()

        except socket.error, exc:
            print "Caught exception socket.error : %s" % exc

    def is_message_come(self):
        if not self.message_deque:
            return False
        else:
            return True

    def get_message(self):
        return self.message_deque.popleft()


