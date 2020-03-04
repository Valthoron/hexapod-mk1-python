# Copyright 2020 Serdar Üşenmez
# Distributed under the terms of the GNU General Public License v3.0

import smbus
import Tools

CHANNEL_COUNT = 10
ID_LENGTH = 32
FILTER_CONSTANT = 0.8
AXIS_DEADZONE = 0.03

class ArduinoControls:
    axis = [0.0 for _ in range(5)]
    switch = [0 for _ in range(5)]

    def __init__(self, channel, address):
        self.address = address
        self.bus = smbus.SMBus(channel)

        try:
            msg = self.bus.read_i2c_block_data(self.address, 1, ID_LENGTH)
            print("ArduinoControls version: ", bytearray(msg).decode("ascii"))
        except Exception as e:
            print("Error reading version string from ArduinoControls on I2C address 0x%02X:" % (address))
            print("\t", e)

    def read_controls(self):
        # Read packet of 10 uint16's from i2c
        try:
            msg = self.bus.read_i2c_block_data(self.address, 0, CHANNEL_COUNT * 2)
            for channel in range(CHANNEL_COUNT):
                value = (msg[channel * 2 + 1] << 8) | (msg[channel * 2])
                if (value > 900) and (value < 2100):
                    self.channel_value[channel] = value
        except:
            return

        # Read channels 0 to 4 into analog axes 0 to 4
        # Channel value [1100 .. 1900] mapped to [-1 .. 1] for channels 0 to 3
        # Channel value [1500 .. 1900] mapped to [-1 .. 1] for channel 4
        for a in range(4):
            channel_value = Tools.ramp(self.channel_value[a], 1100, -1, 1860, 1)
            self.axis[a] = (FILTER_CONSTANT * self.axis[a]) + ((1.0 - FILTER_CONSTANT) * channel_value)

        channel_value = Tools.ramp(self.channel_value[4], 1480, -1, 1860, 1)
        self.axis[4] = (FILTER_CONSTANT * self.axis[4]) + ((1.0 - FILTER_CONSTANT) * channel_value)

        # Read channels 5 to 9 into switches 0 to 4
        # Channel value discretized as following:
        #   0 =         value  < 1350
        #   1 = 1350 <= value <= 1650
        #   2 = 1650  < value
        for s in range(5):
            if self.channel_value[5 + s] < 1350:
                self.switch[s] = 0
            elif self.channel_value[5 + s] > 1650:
                self.switch[s] = 2
            else:
                self.switch[s] = 1

    def get_channel_value(self, channel):
        if (channel < 0) or (channel > 9):
            return 0.0

        return self.channel_value[channel]

    def get_axis(self, axis):
        if (axis < 0) or (axis > 4):
            return 0.0

        value = self.axis[axis]

        # Apply deadzone
        if (value < -AXIS_DEADZONE):
            return Tools.ramp(value, -1.0, -1.0, -AXIS_DEADZONE, 0.0)
        elif (value > AXIS_DEADZONE):
            return Tools.ramp(value, AXIS_DEADZONE, 0.0, 1.0, 1.0)

        return 0.0

    def get_switch(self, switch):
        if (switch < 0) or (switch > 4):
            return 0.0

        return self.switch[switch]

    channel_value = [0] * 10
    axis = [0] * 5
    switch = [0] * 5
    address = 0x00
    bus = None
