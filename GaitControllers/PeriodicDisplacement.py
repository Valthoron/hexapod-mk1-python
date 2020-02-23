from math import *
import mgen
import numpy

from GaitControllers.LegModelController import LegModelController
import HexapodConstants
import Tools

LEG_LIFT_HEIGHT = 40.0
BODY_LIFT_HEIGHT = 30.0
HALF_STRIDE_X = 30.0
HALF_STRIDE_Y = 30.0
HALF_ROTATION = numpy.radians(15.0)
TILT_SPEED = numpy.radians(10.0)
TILT_LIMIT_FORWARD = numpy.radians(20.0)
TILT_LIMIT_SIDE = numpy.radians(20.0)
TWIST_LIMIT = numpy.radians(25.0)

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
    def __init__(self):
        super().__init__()
        self.time = 0.0
        self.tilt_forward = 0.0
        self.tilt_side = 0.0
        self.twist = 0.0
        self.leg_phase = [0.0 for _ in range(6)]

        self.axis_forward = 0.0
        self.axis_side = 0.0
        self.axis_speed = 0.0
        self.axis_turn = 0.0
        self.axis_leg_lift = 0.0
        self.axis_body_lift = 0.0
        self.axis_tilt_forward = 0.0
        self.axis_tilt_side = 0.0

    def initialize(self):
        self.time = 0

        for i in range(6):
            self.leg_phase[i] = 0.0

    def update(self, dt, controls):
        # Read controls into intermediate variables
        phase_table_switch = controls.get_switch(0)
        control_mode_switch = controls.get_switch(1)

        if (control_mode_switch == 0):
            # Move
            self.axis_forward = Tools.toward(self.axis_forward, controls.get_axis(0), 4.0 * dt)
            self.axis_side = Tools.toward(self.axis_side, controls.get_axis(1), 4.0 * dt)
            self.axis_speed = Tools.toward(self.axis_speed, Tools.ramp(controls.get_axis(2), -1.0, 0.0, 1.0, 1.0), 2.0 * dt)
            self.axis_turn = Tools.toward(self.axis_turn, controls.get_axis(3), 4.0 * dt)
            self.axis_leg_lift = Tools.toward(self.axis_leg_lift, Tools.ramp(controls.get_axis(4), -1.0, 0.5, 0.0, 1.0), 0.5 * dt)
            self.axis_body_lift = Tools.toward(self.axis_body_lift, Tools.ramp(controls.get_axis(4), 0.0, 0.0, 1.0, 1.0), 0.5 * dt)
        elif (control_mode_switch == 1):
            # Tilt incremental
            self.axis_tilt_forward = Tools.toward(self.axis_tilt_forward, -1.0 * controls.get_axis(0), 4.0 * dt)
            self.axis_tilt_side = Tools.toward(self.axis_tilt_side, controls.get_axis(1), 4.0 * dt)

            # Reset movement inputs
            self.axis_forward = Tools.toward(self.axis_forward, 0.0, 4.0 * dt)
            self.axis_side = Tools.toward(self.axis_side, 0.0, 4.0 * dt)
            self.axis_turn = Tools.toward(self.axis_turn, 0.0, 4.0 * dt)
        else:
            # Tilt absolute
            self.axis_tilt_forward = 0.0
            self.axis_tilt_side = 0.0
            self.tilt_forward = controls.get_axis(0) * TILT_LIMIT_FORWARD
            self.tilt_side = controls.get_axis(1) * TILT_LIMIT_SIDE
            self.twist = controls.get_axis(3) * TWIST_LIMIT

            # Reset movement inputs
            self.axis_forward = Tools.toward(self.axis_forward, 0.0, 4.0 * dt)
            self.axis_side = Tools.toward(self.axis_side, 0.0, 4.0 * dt)
            self.axis_turn = Tools.toward(self.axis_turn, 0.0, 4.0 * dt)

        # Calculate movement parameters
        minimum_movement = max(abs(self.axis_forward), abs(self.axis_side), abs(self.axis_turn))
        leg_lift_enabler = Tools.ramp(minimum_movement, 0.0, 0.0, 0.1, 1.0)

        leg_lift = LEG_LIFT_HEIGHT * self.axis_leg_lift * leg_lift_enabler
        body_lift = BODY_LIFT_HEIGHT * Tools.ramp(self.axis_body_lift, 0.0, 0.0, 1.0, -1.0)
        stride_x = HALF_STRIDE_X * self.axis_forward
        stride_y = HALF_STRIDE_Y * self.axis_side
        rotation = HALF_ROTATION * self.axis_turn

        if (phase_table_switch == 1):
            phase_table = PHASE_TABLE_BUG
        else:
            phase_table = PHASE_TABLE_THREEPOINT

        gait_period = fmod(self.time * 1.0, 2.0)

        # Calculate auxiliary parameters
        self.tilt_forward += (self.axis_tilt_forward * TILT_SPEED * dt)
        self.tilt_side = Tools.saturate(self.tilt_side, -TILT_LIMIT_SIDE, TILT_LIMIT_SIDE)

        self.tilt_side += (self.axis_tilt_side * TILT_SPEED * dt)
        self.tilt_forward = Tools.saturate(self.tilt_forward, -TILT_LIMIT_FORWARD, TILT_LIMIT_FORWARD)

        tilt_matrix = numpy.matmul(mgen.rotation_around_z(self.twist), numpy.matmul(mgen.rotation_around_y(self.tilt_forward), mgen.rotation_around_x(self.tilt_side)))

        # Work out each leg
        for i in range(6):
            self.leg_phase[i] = Tools.toward(self.leg_phase[i], phase_table[i], 0.5 * dt)
            leg_period = fmod(gait_period + self.leg_phase[i], 2.0)

            if (leg_period < 1.0):
                stride_progress = Tools.ramp(leg_period, 0.0, -1.0, 1.0, 1.0)
            else:
                stride_progress = Tools.ramp(leg_period, 1.0, 1.0, 2.0, -1.0)

            offset_x = stride_x * stride_progress
            offset_y = stride_y * stride_progress
            offset_z = body_lift + (leg_lift * max(0.0, sin(leg_period * pi)))
            offset = [offset_x, offset_y, offset_z]

            rotation_matrix = mgen.rotation_around_z(rotation * stride_progress)

            tip_location_translate = numpy.add(HexapodConstants.TIP_LOCATION_DEFAULT[i], offset)
            tip_location = tilt_matrix.dot(rotation_matrix.dot(tip_location_translate))
            angles, can_calculate_angles = self.legs[i].solve_joint_angles(tip_location)

            # Only update angles if calculation was successful
            if (can_calculate_angles):
                self.joint_angles[3 * i] = angles[0]
                self.joint_angles[3 * i + 1] = angles[1]
                self.joint_angles[3 * i + 2] = angles[2]

        # Increment time
        time_multiplier = Tools.ramp(self.axis_speed, 0.0, 0.5, 1.0, 3.0)
        self.time += dt * time_multiplier
