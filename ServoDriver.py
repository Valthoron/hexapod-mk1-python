from math import *
import numpy

import PCA9685
import Tools

class ServoDriver:
    device: PCA9685.PCA9685 = None

    def __init__(self, channel, address):
        try:
            self.device = PCA9685.PCA9685(channel, address)
            self.device.set_frequency(80)
        except Exception as e:
            print("Error opening ServoDriver device on I2C address 0x%02X:" % (address))
            print("\t", e)

        self.azimuth_angles = [-45, 0, 45]
        self.azimuth_pulses = [1800, 1325, 850]
        self.hip_angles = [-47, 0, 55]
        self.hip_pulses = [1900, 1415, 860]
        self.knee_angles = [-118, -90, 0]
        self.knee_pulses = [820, 1100, 2000]

        self.biases = [0] * 9

    def set_joint_angles(self, angles_degree):
        pulses = [0] * 9

        for leg in range(3):
            pulses[(3 * leg) + 0] = self.biases[(3 * leg) + 0] + numpy.interp(angles_degree[(3 * leg) + 0], self.azimuth_angles, self.azimuth_pulses)
            pulses[(3 * leg) + 1] = self.biases[(3 * leg) + 1] + numpy.interp(angles_degree[(3 * leg) + 1], self.hip_angles, self.hip_pulses)
            pulses[(3 * leg) + 2] = self.biases[(3 * leg) + 2] + numpy.interp(angles_degree[(3 * leg) + 2], self.knee_angles, self.knee_pulses)

        try:
            self.device.write_pulses(pulses)
        except:
            pass
