from math import *
import mgen
import numpy

from GaitControllers.LegModelController import LegModelController
import HexapodConstants
import Tools

class VectorField(LegModelController):
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
        rotation_angle = numpy.radians(30.0)

        stance = Tools.ramp(controls.get_axis(4), 0.0, 20.0, 1.0, -50.0)
        lift = lift_height * (controls.get_axis(2) + 1.0)
        stride_x = stride_length * controls.get_axis(0)
        stride_y = stride_length * controls.get_axis(1)
        rotation = rotation_angle * controls.get_axis(3)

        offset_z_odd = stance + lift * max(0.0, sin(gait_period * pi))
        offset_z_even = stance + lift * max(0.0, sin(gait_period * pi + pi))

        if (gait_period < 1.0):
            t = Tools.ramp(gait_period, 0.0, -1.0, 1.0, 1.0)
        else:
            t = Tools.ramp(gait_period, 1.0, 1.0, 2.0, -1.0)

        offset_x_odd = stride_x * t
        offset_y_odd = stride_y * t
        rotation_matrix_odd = mgen.rotation_around_z(rotation * t)

        offset_x_even = stride_x * -t
        offset_y_even = stride_y * -t
        rotation_matrix_even = mgen.rotation_around_z(rotation * -t)

        for i in range(6):
            if (i % 2):
                offset = [offset_x_odd, offset_y_odd, offset_z_odd]
                rotation_matrix = rotation_matrix_odd
            else:
                offset = [offset_x_even, offset_y_even, offset_z_even]
                rotation_matrix = rotation_matrix_even

            tip_location_translate = numpy.add(HexapodConstants.TIP_LOCATION_DEFAULT[i], offset)
            tip_location = rotation_matrix.dot(tip_location_translate)
            angles, can_calculate_angles = self.legs[i].solve_joint_angles(tip_location)

            if (can_calculate_angles):
                self.joint_angles[3 * i] = angles[0]
                self.joint_angles[3 * i + 1] = angles[1]
                self.joint_angles[3 * i + 2] = angles[2]

        self.time_step += 1

    def _field_longitudinal(self, coordinate):
        return [0.0, 0.0]

    def _field_lateral(self, coordinate):
        return [0.0, 0.0]

    def _field_turn(self, coordinate):
        return [0.0, 0.0]
