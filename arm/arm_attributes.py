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
"""Module defining a meArm property class"""
import json
from jsonschema import validate, RefResolver, Draft4Validator
from controller import ServoAttributes, ES08MAIIAttributes, CustomServoAttributes, MiuzeiSG90Attributes, ServoSchema
from .schemas import arm_servo_schema, me_arm_schema, schema_store
from .arm_servo_attributes import me_armServo

class me_armAttributes(object):
    """Defines various me_arm attributes"""

    def __init__(self):
        """__init__
        Initializes meArm attributes
        """
        self._hip = me_armServo(0, MiuzeiSG90Attributes(), 0.0, -85.0, 85.0)
        self._elbow = me_armServo(1, MiuzeiSG90Attributes(), 0.0, -25.0, 84.5)
        self._shoulder = me_armServo(2, MiuzeiSG90Attributes(), 0.0, -15.0, 65.0)
        self._gripper = me_armServo(3, MiuzeiSG90Attributes(), 0, -20.0, 27.5)
        self._increment = 0.5

    @property 
    def hip(self) -> me_armServo:
        """Gets the meArm hip servo properties
        :rtype: me_armServo
        """
        return self._hip

    @property 
    def elbow(self) -> me_armServo:
        """Gets the meArm elbow servo properties
        :rtype: me_armServo
        """
        return self._elbow

    @property 
    def shoulder(self) -> me_armServo:
        """Gets the meArm shoulder servo properties
        :rtype: me_armServo
        """
        return self._shoulder

    @property 
    def gripper(self) -> me_armServo:
        """Gets the meArm gripper servo properties
        :rtype: me_armServo
        """
        return self._gripper

    @property 
    def increment(self) -> float:
        """Gets the meArm servo angle increment
        :rtype: float
        """
        return self._increment

    @classmethod
    def from_json(cls, json_string: str):
        """from_json
        Creates me_armAttributes from json string
        
        :param json_string: the attributes as json string
        :type json_string: str

        :return: An instance of me_armAttributes initializes based on the json data
        :rtype: me_armAttributes
        """
        dict = json.loads(json_string)
        
        instance = cls()
        instance._increment = dict['angle-increment']

        s = None
        
        instance._hip = me_armServo(
            dict['servos']['hip']['channel'],
            None,
            dict['servos']['hip']['arm-angles']['neutral'],
            dict['servos']['hip']['arm-angles']['min'],
            dict['servos']['hip']['arm-angles']['max'],
        )

        return instance
