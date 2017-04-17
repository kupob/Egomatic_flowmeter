from socket import *
from uuid import getnode as get_mac
from threading import *

from configreader import *


class DataSender:
    cs = socket(AF_INET, SOCK_DGRAM)
    mac = get_mac()
    config = ConfigReader()

    def __init__(self):
        self.cs.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.cs.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.cs.connect((self.config.get_server_host(), self.config.get_server_port()))

    def __send_data(self, *args):
        data_to_send = [self.mac] + list(args)
        message = str(data_to_send).strip('[]')
        self.cs.send(message)

    def send_flow(self, pin, flow):
        t1 = Thread(target=self.__send_data, args=(pin, 0, flow))
        t1.start()
        t1.join()

    def send_stop_signal(self, pin):
        t1 = Thread(target=self.__send_data, args=(pin, 1))
        t1.start()
        t1.join()