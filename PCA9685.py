# Copyright 2020 Serdar Üşenmez
# Distributed under the terms of the GNU General Public License v3.0

# Based on PCA9685 datasheet and code by Adafruit
# https://cdn-shop.adafruit.com/datasheets/PCA9685.pdf
# https://github.com/adafruit/Adafruit_Python_PCA9685

import time
import math
import smbus

class PCA9685:
    # Constants
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
    pulse_scale = 4096 / 20000 # Default value for 50 Hz

    def __init__(self, channel, address):
        self.bus = smbus.SMBus(channel)
        self.address = address

        self.bus.write_byte_data(self.address, self.__MODE1, 0x00)

    def set_frequency(self, frequency):
        self.pulse_scale = 4096 / (1000000 / frequency)
        prescale = round(25000000 / (4096 * frequency)) - 1

        mode1_prev = self.bus.read_byte_data(self.address, self.__MODE1);

        # Sleep
        mode1 = (mode1_prev & 0x7F) | 0x10
        self.bus.write_byte_data(self.address, self.__MODE1, mode1)
        self.bus.write_byte_data(self.address, self.__PRESCALE, int(prescale))
        self.bus.write_byte_data(self.address, self.__MODE1, mode1_prev)

        # Wait for oscillator
        time.sleep(0.005)

        # Restart
        self.bus.write_byte_data(self.address, self.__MODE1, mode1_prev | 0x80)

    def write_pulses(self, pulses):
        # Enable auto-increment
        self.bus.write_byte_data(self.address, self.__MODE1, 0b00100000)

        # Write pulse times for each leg
        for leg in range(3):
            pulse1 = int(pulses[(3 * leg) + 0] * self.pulse_scale)
            pulse2 = int(pulses[(3 * leg) + 1] * self.pulse_scale)
            pulse3 = int(pulses[(3 * leg) + 2] * self.pulse_scale)

            # Only need to set LEDx_OFF_L/H bytes
            self.leg_pulse_data[2] = pulse1 & 0xff
            self.leg_pulse_data[3] = pulse1 >> 8
            self.leg_pulse_data[6] = pulse2 & 0xff
            self.leg_pulse_data[7] = pulse2 >> 8
            self.leg_pulse_data[10] = pulse3 & 0xff
            self.leg_pulse_data[11] = pulse3 >> 8
            # Unset bytes are LEDx_ON_L/H bytes, preset to zero

            # Uses auto-increment to write bytes subsequently
            self.bus.write_i2c_block_data(self.address, self.__LED0_ON_L + ((2 - leg) * 12), self.leg_pulse_data)

        # Disable auto-increment
        self.bus.write_byte_data(self.address, self.__MODE1, 0)
