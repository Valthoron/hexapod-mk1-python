from math import *

from GaitController import GaitController
import LegModel
import HexapodConstants

class LegModelController(GaitController):
    legs = [None for _ in range(6)]

    def __init__(self):
        super().__init__()

        # Configure legs
        leg_configuration = LegModel.Configuration()
        leg_configuration.attach_length = HexapodConstants.LENGTH_LEGATTACHMENT
        leg_configuration.hip_length = HexapodConstants.LENGTH_HIP
        leg_configuration.thigh_length = HexapodConstants.LENGTH_THIGH
        leg_configuration.shin_length = HexapodConstants.LENGTH_SHIN

        # Right front
        leg_configuration.attach_location = [HexapodConstants.LOCATION_X_LEGATTACHMENT_OUTER, HexapodConstants.LOCATION_Y_LEGATTACHMENT_OUTER, 0]
        leg_configuration.root_azimuth = radians(45)
        self.legs[0] = LegModel.LegModel(leg_configuration)

        # Right middle
        leg_configuration.attach_location = [0, HexapodConstants.LOCATION_Y_LEGATTACHMENT_INNER, 0]
        leg_configuration.root_azimuth = radians(90)
        self.legs[1] = LegModel.LegModel(leg_configuration)

        # Right back
        leg_configuration.attach_location = [-HexapodConstants.LOCATION_X_LEGATTACHMENT_OUTER, HexapodConstants.LOCATION_Y_LEGATTACHMENT_OUTER, 0]
        leg_configuration.root_azimuth = radians(135)
        self.legs[2] = LegModel.LegModel(leg_configuration)

        # Left front
        leg_configuration.attach_location = [HexapodConstants.LOCATION_X_LEGATTACHMENT_OUTER, -HexapodConstants.LOCATION_Y_LEGATTACHMENT_OUTER, 0]
        leg_configuration.root_azimuth = radians(-45)
        self.legs[3] = LegModel.LegModel(leg_configuration)

        # Left middle
        leg_configuration.attach_location = [0, -HexapodConstants.LOCATION_Y_LEGATTACHMENT_INNER, 0]
        leg_configuration.root_azimuth = radians(-90)
        self.legs[4] = LegModel.LegModel(leg_configuration)

        # Left back
        leg_configuration.attach_location = [-HexapodConstants.LOCATION_X_LEGATTACHMENT_OUTER, -HexapodConstants.LOCATION_Y_LEGATTACHMENT_OUTER, 0]
        leg_configuration.root_azimuth = radians(-135)
        self.legs[5] = LegModel.LegModel(leg_configuration)

        def print_defaults():
            print("Default tip locations:")
            for i in range(6):
                tip_location = legs[i].solve_tip_location(radians(0), radians(30), radians(-100))
                print("[ %.1lf %.1lf %.1lf ] -> [ %.1lf %.1lf %.1lf ]" % ( \
                    legs[i].root_location[0], legs[i].root_location[1], legs[i].root_location[2], \
                    tip_location[0], tip_location[1], tip_location[2] \
                    ))
