from math import *
import numpy
import time

import HexapodConfiguration
import PCA9685

I2C_CHANNEL = 1
I2C_ADDRESS_ARDUINOCONTROLS = 0x04
I2C_ADDRESS_SERVODRIVER1 = 0x40
I2C_ADDRESS_SERVODRIVER2 = 0x41

device_ServoDriver1 = PCA9685.PCA9685(I2C_ADDRESS_SERVODRIVER1)
device_ServoDriver2 = PCA9685.PCA9685(I2C_ADDRESS_SERVODRIVER2)

device_ServoDriver1.set_frequency(80)
device_ServoDriver2.set_frequency(80)

while True:
    try:
        HexapodConfiguration.load_configuration()
    except:
        pass

    pulseWidth1 = numpy.interp(0.0, HexapodConfiguration.azimuth_angles, HexapodConfiguration.azimuth_pulses)
    pulseWidth2 = numpy.interp(0.0, HexapodConfiguration.hip_angles, HexapodConfiguration.hip_pulses)
    pulseWidth3 = numpy.interp(-90.0, HexapodConfiguration.knee_angles, HexapodConfiguration.knee_pulses)

    pulses1 = [0] * 9
    pulses2 = [0] * 9

    pulses1[0] = pulseWidth1 + HexapodConfiguration.biases[0]
    pulses1[1] = pulseWidth2 + HexapodConfiguration.biases[1]
    pulses1[2] = pulseWidth3 + HexapodConfiguration.biases[2]

    pulses1[3] = pulseWidth1 + HexapodConfiguration.biases[3]
    pulses1[4] = pulseWidth2 + HexapodConfiguration.biases[4]
    pulses1[5] = pulseWidth3 + HexapodConfiguration.biases[5]

    pulses1[6] = pulseWidth1 + HexapodConfiguration.biases[6]
    pulses1[7] = pulseWidth2 + HexapodConfiguration.biases[7]
    pulses1[8] = pulseWidth3 + HexapodConfiguration.biases[8]

    pulses2[0] = pulseWidth1 + HexapodConfiguration.biases[9]
    pulses2[1] = pulseWidth2 + HexapodConfiguration.biases[10]
    pulses2[2] = pulseWidth3 + HexapodConfiguration.biases[11]

    pulses2[3] = pulseWidth1 + HexapodConfiguration.biases[12]
    pulses2[4] = pulseWidth2 + HexapodConfiguration.biases[13]
    pulses2[5] = pulseWidth3 + HexapodConfiguration.biases[14]

    pulses2[6] = pulseWidth1 + HexapodConfiguration.biases[15]
    pulses2[7] = pulseWidth2 + HexapodConfiguration.biases[16]
    pulses2[8] = pulseWidth3 + HexapodConfiguration.biases[17]

    device_ServoDriver1.write_pulses(pulses1)
    device_ServoDriver2.write_pulses(pulses2)

    time.sleep(0.5)
