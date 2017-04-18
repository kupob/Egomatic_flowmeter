# -*- coding: utf-8 -*-
import socket
import sys
from uuid import getnode as get_mac
from threading import *
from time import sleep

from configreader import *

'''
Виды сообщений, передаваемые по сети
0 - передача периодического оповещения
1 - передача стоп-сигнала для клапана
2 - передача данных о расходе со счётчика
'''


class DataSender:
    mac = get_mac()
    config = ConfigReader()
    cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (config.get_server_host(), config.get_server_port())

    def __init__(self):
        self.cs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.cs.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.cs.connect(self.server_address)

    def __send_data(self, *args):
        data_to_send = [self.mac] + list(args)
        message = str(data_to_send).strip('[]')
        try:
            self.cs.sendto(message, self.server_address)
        except socket.error, exc:
            print "__send_data caught exception socket.error : %s" % exc

    def send_notify_signal(self):
        t1 = Thread(target=self.__send_data, args=(0, ))
        t1.start()
        t1.join()

    def send_flow(self, pin, flow):
        t1 = Thread(target=self.__send_data, args=(2, pin, flow))
        t1.start()
        t1.join()

    def send_stop_signal(self, pin):
        t1 = Thread(target=self.__send_data, args=(1, pin))
        t1.start()
        t1.join()

