# Copyright (c) 2018 Avanade
# Author: Thor Schueler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# pylint: disable=C0103
"""Module defining a meArm kinematics property class"""

import json
from jsonschema import validate, RefResolver, Draft4Validator, ValidationError
from controller import ServoAttributes, ES08MAIIAttributes, CustomServoAttributes, MiuzeiSG90Attributes, ServoSchema
from .schemas import arm_servo_schema, schema_store

class me_armKinematics(object):
    """This class describes a kinematics attributes for a meArm"""

    def __init__(self):
        """__init___
        Initializes me_armKinematics. 
        """
        self.humerus = 80.0
        self.radius = 80.0
        self.phalanx = 45.0
        self.clavicle = 15.0
        self.x_plane_offset = 0.0
        self.y_plane_offset = 170.0
        self.z_plane_offset = 25.0

    @classmethod
    def from_dict(cls, data:{}):
        """from_dict
        Generates me_armKinematics from dictionary
        :param data: The dictionary containing the kinematics data. Must adhere to arm.KinematicsSchema
        :type data: dictionary
        """
        instance = cls()
        instance.humerus = data['humerus']
        instance.radius = data['radius']
        instance.phalanx = data['phalanx']
        instance.clavicle = data['clavicle']
        instance.x_plane_offset = data['x-plane-offset']
        instance.y_plane_offset = data['y-plane-offset']
        instance.z_plane_offset = data['z-plane-offset']
        return instance
2