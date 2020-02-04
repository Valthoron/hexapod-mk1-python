from math import *
import numpy

import PCA9685
import Tools

class ServoDriver:
    device: PCA9685.PCA9685 = None
    lookup_angle = [-90, 0, 90]
    lookup_pulse = [500, 1500, 2500]

    def __init__(self, i2c_address):
        try:
            self.device = PCA9685.PCA9685(I2C_ADDRESS_SERVODRIVER1, False)
            self.device.setPWMFreq(50)
        except:
            print("Error opening ServoDriver device on I2C address 0x%02X." % (i2c_address))

    def set_servo_angle(self, servo, angle_degree):
        if (servo >= 16):
            return

        pulseWidth = numpy.interp(angle_degree, self.lookup_angle, self.lookup_pulse)

        try:
            self.device.setServoPulse(servo, pulseWidth)
        except:
            pass
