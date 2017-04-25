# -*- coding: utf-8 -*-
# Egomatic conf file read module
import os.path


class ConfigReader:  # Singleton
    class __ConfigReader:
        __GPIO_PINS = []
        __PULSES_PER_LITER = 0
        __SERVER_HOST = ""
        __SERVER_PORT = 0
        __MSG_TYPES = {}

        def __init__(self):
            file_name = '../settings.conf'

            if os.path.isfile(file_name):
                file = open(file_name, 'r')
                for line in file:
                    if line[0] == '#':
                        continue

                    line_split = line.split()

                    if not line_split:
                        continue

                    code = line_split[0]
                    value = line_split[1]

                    if code == 'PULSES_PER_LITER':
                        self.__PULSES_PER_LITER = float(value)
                    elif code == "GPIO_PINS":
                        for i in line_split[1:]:
                            self.__GPIO_PINS.append(int(i))
                    elif code == "SERVER_HOST":
                        self.__SERVER_HOST = value
                    elif code == "SERVER_PORT":
                        self.__SERVER_PORT = int(value)
                    elif code == "SERVER_HOST":
                        self.__SERVER_HOST = value
                    elif code == "SERVER_PORT":
                        self.__SERVER_PORT = int(value)
                    elif code[0:5] == "MSG_":
                        self.__MSG_TYPES[code] = int(value)

        def get_GPIO_pins(self):
            return self.__GPIO_PINS

        def get_pulses_per_liter(self):
            return self.__PULSES_PER_LITER

        def get_server_host(self):
            return self.__SERVER_HOST

        def get_server_port(self):
            return self.__SERVER_PORT

        def message_types(self, message_type):
            return self.__MSG_TYPES[message_type]

    instance = None

    def __init__(self):
        if not ConfigReader.instance:
            ConfigReader.instance = ConfigReader.__ConfigReader()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)
