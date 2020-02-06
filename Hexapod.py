from math import *
import numpy

import ArduinoControls
import HexapodConstants
import ServoDriver
import Tools
import UdpSend

import GaitController
import GaitControllers.PeriodicDisplacement
import GaitControllers.ThreePointBasic
import GaitControllers.VectorField

LOOP_PERIOD = 0.025

I2C_CHANNEL = 1
I2C_ADDRESS_ARDUINOCONTROLS = 0x04
I2C_ADDRESS_SERVODRIVERRIGHT = 0x40
I2C_ADDRESS_SERVODRIVERLEFT = 0x41

device_Controls = ArduinoControls.ArduinoControls(I2C_CHANNEL, I2C_ADDRESS_ARDUINOCONTROLS)
device_ServoDriverRight = ServoDriver.ServoDriver(I2C_ADDRESS_SERVODRIVERRIGHT)
device_ServoDriverLeft = ServoDriver.ServoDriver(I2C_ADDRESS_SERVODRIVERLEFT)

time_step = 0
gait_controller : GaitController

def hexapod_setup():
    # Done
    global gait_controller
    gait_controller = GaitControllers.PeriodicDisplacement.PeriodicDisplacement()
    gait_controller.initialize()

    print("Setup complete.")
    UdpSend.connect()

def hexapod_main():
    device_Controls.read_controls()
    gait_controller.update(LOOP_PERIOD, device_Controls)
    joint_angles = gait_controller.get_joint_angles()
    UdpSend.send_angles(numpy.degrees(joint_angles))

def hexapod_shutdown():
    UdpSend.disconnect()

def set_leg_angles(device: ServoDriver.ServoDriver, leg, angles_degree):
    device.set_servo_angle(3 * leg, angles_degree[0])
    device.set_servo_angle(3 * leg + 1, angles_degree[1])
    device.set_servo_angle(3 * leg + 2, angles_degree[2])
