from math import *
import numpy

from GaitControllers.LegModelController import LegModelController
import HexapodConstants
import Tools

class ThreePointBasic(LegModelController):
    time_step = 0

    def __init__(self):
        super().__init__()

    def initialize(self):
        self.time_step = 0

    def update(self, dt, controls):
        time = self.time_step * dt
        gait_period = fmod(time * 1.0, 2.0)

        lift_height = 20.0
        stride_length = 30.0

        offset_z_odd = lift_height * max(0.0, sin(gait_period * pi))
        offset_z_even = lift_height * max(0.0, sin(gait_period * pi + pi))

        if (gait_period < 1.0):
            t = Tools.ramp(gait_period, 0.0, -1.0, 1.0, 1.0)
            offset_x_odd = stride_length * t
            offset_x_even = stride_length * -t
        else:
            t = Tools.ramp(gait_period, 1.0, 1.0, 2.0, -1.0)
            offset_x_odd = stride_length * t
            offset_x_even = stride_length * -t

        for i in range(6):
            if (i % 2):
                offset = [offset_x_odd, 0, offset_z_odd]
            else:
                offset = [offset_x_even, 0, offset_z_even]

            tip_location = numpy.add(HexapodConstants.LOCATION_DEFAULT_TIP[i], offset)
            angles = self.legs[i].solve_joint_angles(tip_location)

            self.joint_angles[3 * i] = angles[0]
            self.joint_angles[3 * i + 1] = angles[1]
            self.joint_angles[3 * i + 2] = angles[2]

        self.time_step += 1
