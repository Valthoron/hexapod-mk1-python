import smbus
import Tools

class ArduinoControls:
    axis = [0.0 for _ in range(5)]
    switch = [0 for _ in range(5)]

    def __init__(self, channel, address):
        self.address = address
        self.bus = smbus.SMBus(channel)

    def read_controls(self):
        # Read packet of 10 uint16's from i2c
        try:
            msg = self.bus.read_i2c_block_data(self.address, 16, 10 * 2)
            for channel in range(10):
                value = (msg[channel * 2 + 1] << 8) | (msg[channel * 2])
                if (value > 900) and (value < 2100):
                    self.channel_value[channel] = value
        except:
            return

        # Read channels 0 to 4 into analog axes 0 to 4
        # Channel value [1100 .. 1900] mapped to [-1 .. 1]
        filter_constant = 0.95
        for a in range(5):
            self.axis[a] = (filter_constant * self.axis[a]) + ((1.0 - filter_constant) * Tools.ramp(self.channel_value[a], 1100, -1, 1900, 1))

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
            return 0

        return self.channel_value[channel]

    def get_axis(self, axis):
        if (axis < 0) or (axis > 4):
            return 0

        return self.axis[axis]

    def get_switch(self, switch):
        if (switch < 0) or (switch > 4):
            return 0

        return self.switch[switch]

    channel_value = [0] * 10
    axis = [0] * 5
    switch = [0] * 5
    address = 0x00
    bus = None
