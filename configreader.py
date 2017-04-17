## Egomatic conf file read module
import os.path

class ConfigReader():

  __GPIO_pins = []
  __pulses_per_liter = 0

  __GPIO_pins_default = [20, 21]
  __pulses_per_liter_default = 382

  def __init__(self):
    file_name = './settings.conf'

    if os.path.isfile(file_name):
      file = open(file_name, 'r')
      for line in file:
        if line[0] == '#':
          continue
        
        line_split = line.split()
        if not line_split:
          continue
        if line_split[0] == 'PULSES_PER_LITER':
          self.__pulses_per_liter = float(line_split[1])
        elif line_split[0] == 'PINS':
          for i in line_split[1:]:
            self.__GPIO_pins.append(int(i))

    if not self.__GPIO_pins:
      print("PINS is empty, using defaults")
      self.__GPIO_pins = self.__GPIO_pins_default

    if not self.__pulses_per_liter:
      print("PULSES_PER_LITER is empty, using defaults")
      self.__pulses_per_liter = self.__pulses_per_liter_default

  def get_GPIO_pins(self):
    return self.__GPIO_pins

  def get_pulses_per_liter(self):
    return self.__pulses_per_liter