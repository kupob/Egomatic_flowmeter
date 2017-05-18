# -*- coding: utf-8 -*-
# Egomatic conf file read module
import os.path
import ConfigParser


class ConfigReader:  # Singleton
    class __ConfigReader:
        config_parser = ConfigParser.ConfigParser()

        def __init__(self):
            self.config_parser.read(['../config.ini', '../message_types.ini'])

        def get_GPIO_pins(self):
            return self.config_parser.get('General', 'GPIO_PINS')

        def get_pulses_per_liter(self):
            return self.config_parser.getfloat('General', 'PULSES_PER_LITER')

        def get_server_host(self):
            return self.config_parser.get('General', 'SERVER_HOST')

        def get_server_port(self):
            return self.config_parser.getint('General', 'SERVER_PORT')

        def get_flowmeter_port(self):
            return self.config_parser.getint('General', 'FLOWMETER_PORT')

        def get_message_type(self, message_type):
            return self.config_parser.getint("MessageTypes", message_type)

    instance = None

    def __init__(self):
        if not ConfigReader.instance:
            ConfigReader.instance = ConfigReader.__ConfigReader()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)
