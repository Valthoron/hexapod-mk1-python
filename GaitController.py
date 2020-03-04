# Copyright 2020 Serdar Üşenmez
# Distributed under the terms of the GNU General Public License v3.0

class GaitController:
    joint_angles = [0.0 for _ in range(18)]

    def __init__(self):
        pass

    def get_joint_angles(self):
        return self.joint_angles

    def initialize(self):
        self.joint_angles = [0.0 for _ in range(18)]

    def update(self, dt, controls):
        pass
