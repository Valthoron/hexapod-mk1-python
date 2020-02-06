from math import *
import mgen
import numpy

from GaitControllers.LegModelController import LegModelController
import HexapodConstants
import Tools

HALF_LIFT = 20.0
FULL_STANCE = 30.0
HALF_STRIDE_X = 30.0
HALF_STRIDE_Y = 30.0
HALF_ROTATION = numpy.radians(15.0)

PHASE_TABLE_THREEPOINT = [ \
    0.000, \
    1.000, \
    0.000, \
    1.000, \
    0.000, \
    1.000, \
    ]

PHASE_TABLE_BUG = [ \
    0.000, \
    0.667, \
    1.333, \
    1.000, \
    1.667, \
    0.333, \
    ]

class PeriodicDisplacement(LegModelController):
    time = 0

    def __init__(self):
        super().__init__()

    def initialize(self):
        self.time = 0

    def update(self, dt, controls):
        gait_period = fmod(self.time * 1.0, 2.0)

        movement_multiplier = Tools.ramp(controls.get_axis(2), -0.9, 0.0, -0.6, 1.0)

        lift = HALF_LIFT * (controls.get_axis(2) + 1.0)
        stance = FULL_STANCE * Tools.ramp(controls.get_axis(2), 0.0, 0.0, 1.0, -1.0)
        stride_x = HALF_STRIDE_X * controls.get_axis(0) * movement_multiplier
        stride_y = HALF_STRIDE_Y * controls.get_axis(1) * movement_multiplier
        rotation = HALF_ROTATION * controls.get_axis(3) * movement_multiplier

        if (controls.get_switch(0) == 1):
            phase_table = PHASE_TABLE_BUG
        else:
            phase_table = PHASE_TABLE_THREEPOINT


        for i in range(6):
            leg_period = fmod(gait_period + phase_table[i], 2.0)

            offset_z = stance + lift * max(0.0, sin(leg_period * pi))

            if (leg_period < 1.0):
                t = Tools.ramp(leg_period, 0.0, -1.0, 1.0, 1.0)
            else:
                t = Tools.ramp(leg_period, 1.0, 1.0, 2.0, -1.0)

            offset_x = stride_x * t
            offset_y = stride_y * t
            rotation_matrix = mgen.rotation_around_z(rotation * t)

            offset = [offset_x, offset_y, offset_z]
            rotation_matrix = rotation_matrix

            tip_location_translate = numpy.add(HexapodConstants.LOCATION_DEFAULT_TIP[i], offset)
            tip_location = rotation_matrix.dot(tip_location_translate)
            angles = self.legs[i].solve_joint_angles(tip_location)

            self.joint_angles[3 * i] = angles[0]
            self.joint_angles[3 * i + 1] = angles[1]
            self.joint_angles[3 * i + 2] = angles[2]

        time_multiplier = Tools.ramp(controls.get_axis(4), 0.0, 0.5, 1.0, 4.0)
        self.time += dt * time_multiplier
