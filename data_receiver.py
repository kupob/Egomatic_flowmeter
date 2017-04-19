# -*- coding: utf-8 -*-

import socket
from threading import *
from configreader import *
from collections import deque


class DataReceiver(Thread):
    config = ConfigReader()
    cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message_deque = deque([])

    def run(self):
        try:
            self.cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.cs.bind(('', self.config.get_server_port()))

            while True:
                message = self.cs.recv(1024)
                if message:
                    self.message_deque.append(message)

        except socket.error, exc:
            print "Caught exception socket.error : %s" % exc

    def is_message_come(self):
        if not self.message_deque:
            return False
        else:
            return True

    def get_message(self):
        return self.message_deque.popleft()


