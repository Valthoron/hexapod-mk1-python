# Copyright 2020 Serdar Üşenmez
# Distributed under the terms of the GNU General Public License v3.0

from dataclasses import dataclass, field
from math import *
import numpy
import mgen

import Tools

@dataclass
class Configuration:
    def __default_attach_location():
        return [0, 0, 0]

    attach_location: float = field(default_factory=__default_attach_location)
    root_azimuth: float = 0
    attach_length: float = 0.5
    hip_length: float = 0.5
    thigh_length: float = 1
    shin_length: float = 1

class LegModel:
    root_location = [0, 0, 0]
    root_azimuth = 0
    hip_length = 0.5
    thigh_length = 1
    shin_length = 1

    def __init__(self, configuration: Configuration):
        self.root_azimuth = configuration.root_azimuth
        self.hip_length = configuration.hip_length
        self.thigh_length = configuration.thigh_length
        self.shin_length = configuration.shin_length

        attach_to_root_local = [configuration.attach_length, 0, 0]
        attach_to_root = mgen.rotation_around_z(configuration.root_azimuth).dot(attach_to_root_local)
        self.root_location = numpy.add(configuration.attach_location, attach_to_root)

    def solve_tip_location(self, azimuth_angle, hip_angle, knee_angle):
        dx = (self.hip_length + (self.thigh_length * cos(hip_angle)) + (self.shin_length * cos(hip_angle + knee_angle))) * cos(azimuth_angle + self.root_azimuth)
        dy = (self.hip_length + (self.thigh_length * cos(hip_angle)) + (self.shin_length * cos(hip_angle + knee_angle))) * sin(azimuth_angle + self.root_azimuth)
        dz = ((self.thigh_length * sin(hip_angle)) + (self.shin_length * sin(hip_angle + knee_angle)))
        tip_location = numpy.add(self.root_location, [dx, dy, dz])
        return tip_location

    def solve_joint_angles(self, tip_location):
        # displacement is the vector from root to tip point.
        displacement = numpy.subtract(tip_location, self.root_location)
        displacement_x = displacement[0]
        displacement_y = displacement[1]
        displacement_z = displacement[2]

        # leg_extension is the length of the projection of displacement vector on ground plane.
        leg_extension = sqrt(displacement_x**2 + displacement_y**2)

        # hip_to_tip is the distance between hip and tip points.
        hip_to_tip = sqrt(displacement_z**2 + (leg_extension - self.hip_length)**2)

        if (hip_to_tip >= self.thigh_length + self.shin_length):
            return [0, 0, 0], False

        # gamma is the angle between hip_to_tip vector and ground plane.
        # gamma is always positive.
        gamma = atan2(abs(displacement_z), abs(leg_extension - self.hip_length))

        hip_angle = -gamma + acos( \
            (self.thigh_length**2 + hip_to_tip**2 - self.shin_length**2) \
            / (2 * self.thigh_length * hip_to_tip) \
            )

        knee_angle = -pi + acos( \
            (self.thigh_length**2 + self.shin_length**2 - hip_to_tip**2) \
            / (2 * self.thigh_length * self.shin_length) \
            )

        total_azimuth_angle = atan2(displacement_y, displacement_x)
        azimuth_angle = total_azimuth_angle - self.root_azimuth

        joint_angles = [azimuth_angle, hip_angle, knee_angle]
        return joint_angles, True
