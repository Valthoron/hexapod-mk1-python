from math import *
import numpy
import mgen

import ArduinoControls
import HexapodConstants
import LegModel
import ServoDriver
import Tools
import UdpSend

import GaitController
import GaitControllers.ThreePointBasic

LOOP_PERIOD = 0.025

I2C_CHANNEL = 1
I2C_ADDRESS_ARDUINOCONTROLS = 0x04
I2C_ADDRESS_SERVODRIVERRIGHT = 0x40
I2C_ADDRESS_SERVODRIVERLEFT = 0x41

device_Controls = ArduinoControls.ArduinoControls(I2C_CHANNEL, I2C_ADDRESS_ARDUINOCONTROLS)
device_ServoDriverRight = ServoDriver.ServoDriver(I2C_ADDRESS_SERVODRIVERRIGHT)
device_ServoDriverLeft = ServoDriver.ServoDriver(I2C_ADDRESS_SERVODRIVERLEFT)

legs = [None for _ in range(6)]

time_step = 0

def hexapod_setup():
    # Configure legs
    leg_configuration = LegModel.Configuration()
    leg_configuration.attach_length = HexapodConstants.LENGTH_LEGATTACHMENT
    leg_configuration.hip_length = HexapodConstants.LENGTH_HIP
    leg_configuration.thigh_length = HexapodConstants.LENGTH_THIGH
    leg_configuration.shin_length = HexapodConstants.LENGTH_SHIN

    # Right front
    leg_configuration.attach_location = [HexapodConstants.LOCATION_X_LEGATTACHMENT_OUTER, HexapodConstants.LOCATION_Y_LEGATTACHMENT_OUTER, 0]
    leg_configuration.root_azimuth = radians(45)
    legs[0] = LegModel.LegModel(leg_configuration)

    # Right middle
    leg_configuration.attach_location = [0, HexapodConstants.LOCATION_Y_LEGATTACHMENT_INNER, 0]
    leg_configuration.root_azimuth = radians(90)
    legs[1] = LegModel.LegModel(leg_configuration)

    # Right back
    leg_configuration.attach_location = [-HexapodConstants.LOCATION_X_LEGATTACHMENT_OUTER, HexapodConstants.LOCATION_Y_LEGATTACHMENT_OUTER, 0]
    leg_configuration.root_azimuth = radians(135)
    legs[2] = LegModel.LegModel(leg_configuration)

    # Left front
    leg_configuration.attach_location = [HexapodConstants.LOCATION_X_LEGATTACHMENT_OUTER, -HexapodConstants.LOCATION_Y_LEGATTACHMENT_OUTER, 0]
    leg_configuration.root_azimuth = radians(-45)
    legs[3] = LegModel.LegModel(leg_configuration)

    # Left middle
    leg_configuration.attach_location = [0, -HexapodConstants.LOCATION_Y_LEGATTACHMENT_INNER, 0]
    leg_configuration.root_azimuth = radians(-90)
    legs[4] = LegModel.LegModel(leg_configuration)

    # Left back
    leg_configuration.attach_location = [-HexapodConstants.LOCATION_X_LEGATTACHMENT_OUTER, -HexapodConstants.LOCATION_Y_LEGATTACHMENT_OUTER, 0]
    leg_configuration.root_azimuth = radians(-135)
    legs[5] = LegModel.LegModel(leg_configuration)

    # Done
    print("Setup complete.")

    print()
    print("Default tip locations:")
    for i in range(6):
        tip_location = legs[i].solve_tip_location(radians(0), radians(30), radians(-100))
        print("[ %.1lf %.1lf %.1lf ] -> [ %.1lf %.1lf %.1lf ]" % ( \
            legs[i].root_location[0], legs[i].root_location[1], legs[i].root_location[2], \
            tip_location[0], tip_location[1], tip_location[2] \
            ))

    print()
    print("Solve for default angles:")
    for i in range(6):
        joint_angles = legs[i].solve_joint_angles(HexapodConstants.LOCATION_DEFAULT_TIP[i])
        print("azi = %.1lf  hip = %.1lf  kne = %.1lf" % (degrees(joint_angles[0]), degrees(joint_angles[1]), degrees(joint_angles[2])))

    UdpSend.connect()

def hexapod_main():
    global time_step
    time = time_step * LOOP_PERIOD

    #device_Controls.read_controls()

    gait_period = fmod(time * 1.0, 2.0)

    offset_z_odd = 20.0 * max(0.0, sin(gait_period * pi))
    offset_z_even = 20.0 * max(0.0, sin(gait_period * pi + pi))

    stride_length = 30.0;

    if (gait_period < 1.0):
        t = Tools.ramp(gait_period, 0.0, -1.0, 1.0, 1.0)
        offset_x_odd = stride_length * t
        offset_x_even = stride_length * -t
    else:
        t = Tools.ramp(gait_period, 1.0, 1.0, 2.0, -1.0)
        offset_x_odd = stride_length * t
        offset_x_even = stride_length * -t

    all_angles = [0.0 for _ in range(18)]

    plane_normal = \
        mgen.rotation_around_z(numpy.radians(60.0 * time)).dot( \
        mgen.rotation_around_y(numpy.radians(10.0)).dot([0.0, 0.0, -1.0])
        )

    for i in range(6):
        if (i % 2):
            offset = [offset_x_odd, 0, offset_z_odd]
        else:
            offset = [offset_x_even, 0, offset_z_even]

        # z = \
        #     ( \
        #         (plane_normal[0] * HexapodConstants.LOCATION_DEFAULT_TIP[i][0]) \
        #         + (plane_normal[1] * HexapodConstants.LOCATION_DEFAULT_TIP[i][1]) \
        #     ) / (-plane_normal[2])
        #
        # offset = [0, 0, z]

        # offset = [0, 0, 0]

        tip_location = numpy.add(HexapodConstants.LOCATION_DEFAULT_TIP[i], offset)
        angles = legs[i].solve_joint_angles(tip_location)

        if (i < 3):
            set_leg_angles(device_ServoDriverRight, i, numpy.degrees(angles))
        else:
            set_leg_angles(device_ServoDriverLeft, i, numpy.degrees(angles))

        all_angles[3 * i] = angles[0]
        all_angles[3 * i + 1] = angles[1]
        all_angles[3 * i + 2] = angles[2]

        #if (i == 0):
        #    print(numpy.degrees(angles))

    UdpSend.send_angles(numpy.degrees(all_angles))

    time_step += 1
    return

def hexapod_shutdown():
    UdpSend.disconnect()

def set_leg_angles(device: ServoDriver.ServoDriver, leg, angles_degree):
    device.set_servo_angle(3 * leg, angles_degree[0])
    device.set_servo_angle(3 * leg + 1, angles_degree[1])
    device.set_servo_angle(3 * leg + 2, angles_degree[2])
