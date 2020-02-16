import time
import math
import smbus

class PCA9685:
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD

    leg_pulse_data = [0 for _ in range(12)]
    pulse_scale = 4096 / 20000

    def __init__(self, address):
        self.bus = smbus.SMBus(1)
        self.address = address

        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)

    def read(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def set_frequency(self, frequency):
        self.pulse_scale = 4096 / (1000000 / frequency)
        prescale = round(25000000 / (4096 * frequency)) - 1

        mode1_prev = self.read(self.__MODE1);

        # Sleep
        mode1 = (mode1_prev & 0x7F) | 0x10
        self.write(self.__MODE1, mode1)
        self.write(self.__PRESCALE, int(prescale))
        self.write(self.__MODE1, mode1_prev)

        # Wait for oscillator
        time.sleep(0.005)

        # Restart
        self.write(self.__MODE1, mode1_prev | 0x80)

    def write_pulses(self, pulses):
        self.bus.write_byte_data(self.address, self.__MODE1, 0b00100000)

        for leg in range(3):
            pulse1 = int(pulses[(3 * leg) + 0] * self.pulse_scale)
            pulse2 = int(pulses[(3 * leg) + 1] * self.pulse_scale)
            pulse3 = int(pulses[(3 * leg) + 2] * self.pulse_scale)
            self.leg_pulse_data[2] = pulse1 & 0xff
            self.leg_pulse_data[3] = pulse1 >> 8
            self.leg_pulse_data[6] = pulse2 & 0xff
            self.leg_pulse_data[7] = pulse2 >> 8
            self.leg_pulse_data[10] = pulse3 & 0xff
            self.leg_pulse_data[11] = pulse3 >> 8
            self.bus.write_i2c_block_data(self.address, self.__LED0_ON_L + (leg * 12), self.leg_pulse_data)

        self.bus.write_byte_data(self.address, self.__MODE1, 0)
