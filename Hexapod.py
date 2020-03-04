import numpy

from math import *
from threading import Thread

import ArduinoControls
import HexapodConfiguration
import HexapodConstants
import ServoDriver
import Tools
import UdpSend

#import Camera
import GaitController
import GaitControllers.PeriodicDisplacement

LOOP_PERIOD = 0.025

I2C_CHANNEL = 1
I2C_ADDRESS_ARDUINOCONTROLS = 0x04
I2C_ADDRESS_SERVODRIVERRIGHT = 0x40
I2C_ADDRESS_SERVODRIVERLEFT = 0x41

device_controls : ArduinoControls.ArduinoControls
device_servo_driver_right : ServoDriver.ServoDriver
device_servo_driver_left : ServoDriver.ServoDriver
gait_controller : GaitController.GaitController
#thread_camera : Thread

def hexapod_setup():
    HexapodConfiguration.load_configuration()

    global device_controls
    device_controls = ArduinoControls.ArduinoControls(I2C_CHANNEL, I2C_ADDRESS_ARDUINOCONTROLS)

    global device_servo_driver_right
    device_servo_driver_right = ServoDriver.ServoDriver(I2C_CHANNEL, I2C_ADDRESS_SERVODRIVERRIGHT)
    device_servo_driver_right.azimuth_angles = HexapodConfiguration.azimuth_angles
    device_servo_driver_right.azimuth_pulses = HexapodConfiguration.azimuth_pulses
    device_servo_driver_right.hip_angles = HexapodConfiguration.hip_angles
    device_servo_driver_right.hip_pulses = HexapodConfiguration.hip_pulses
    device_servo_driver_right.knee_angles = HexapodConfiguration.knee_angles
    device_servo_driver_right.knee_pulses = HexapodConfiguration.knee_pulses
    device_servo_driver_right.biases = HexapodConfiguration.biases

    global device_servo_driver_left
    device_servo_driver_left = ServoDriver.ServoDriver(I2C_CHANNEL, I2C_ADDRESS_SERVODRIVERLEFT)
    device_servo_driver_left.azimuth_angles = HexapodConfiguration.azimuth_angles
    device_servo_driver_left.azimuth_pulses = HexapodConfiguration.azimuth_pulses
    device_servo_driver_left.hip_angles = HexapodConfiguration.hip_angles
    device_servo_driver_left.hip_pulses = HexapodConfiguration.hip_pulses
    device_servo_driver_left.knee_angles = HexapodConfiguration.knee_angles
    device_servo_driver_left.knee_pulses = HexapodConfiguration.knee_pulses
    device_servo_driver_left.biases = HexapodConfiguration.biases

    global gait_controller
    gait_controller = GaitControllers.PeriodicDisplacement.PeriodicDisplacement()
    gait_controller.initialize()

    #UdpSend.connect()

    #global thread_camera
    #thread_camera = Thread(target = Camera.camera_run)
    #thread_camera.start()

    print("Setup complete.")

def hexapod_main():
    device_controls.read_controls()

    gait_controller.update(LOOP_PERIOD, device_controls)

    joint_angles = gait_controller.get_joint_angles()
    joint_angles_degree = numpy.degrees(joint_angles)

    device_servo_driver_right.set_joint_angles(joint_angles_degree[0:9])
    device_servo_driver_left.set_joint_angles(joint_angles_degree[9:18])

    #UdpSend.send_angles(numpy.degrees(joint_angles))

def hexapod_shutdown():
    #UdpSend.disconnect()
    #Camera.camera_stop()
    #thread_camera.join()
    pass
