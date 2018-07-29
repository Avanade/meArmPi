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
"""Module defining a meArm servo property class"""
import json
from jsonschema import validate, RefResolver, Draft4Validator
from controller import ServoAttributes, ES08MAIIAttributes, CustomServoAttributes, MiuzeiSG90Attributes, ServoSchema
from .schemas import arm_servo_schema, me_arm_schema, schema_store

class me_armServo(object):
    """This class describes a servo attached to the meArm and associated attributes"""

    def __init__(self, channel: int, attributes: ServoAttributes, neutral: float, min: float, max: float):
        """__init___
        Initializes me_armServo. 

        :param channel: The conroller channel for the servo
        :type channel: int

        :param attributes: THe servo attributes
        :type attributes: ServoAttributes

        :param neutral: The angle of the servo when the arm is in neutral position
        :type neutral: float

        :param max: The maximum meArm angle for this servo
        :type max: float

        :param min: The minimum meArm angle for this servo
        :type min: float
        """
        self._channel = channel
        self._servo = attributes
        self._neutral = neutral
        self._max = max
        self._min = min

    @classmethod
    def from_json_file(cls, json_file:str):
        """from_json_file
        Generates me_armServo from json file
        :param json_file: name of the file containing the json data. Must adhere to arm.ServoSchema
        :type json_file: str
        """
        with open(json_file) as file:
            data = json.load(file)
            resolver = RefResolver('', arm_servo_schema, schema_store)
            validator = Draft4Validator(arm_servo_schema, [], resolver)
            #validator.validate()
            validator.is_valid(data)
        instance = cls.from_dict(data)
        return instance

    @classmethod
    def from_json(cls, json_string:str):
        """from_json
        Generates me_armServo from json data
        :param json_string: String containing the json data. Must adhere to arm.ServoSchema
        :type json_string: str
        """
        data = json.loads(json_string)
        validate(data, arm_servo_schema)
        instance = cls.from_dict(data)
        return instance

    @classmethod
    def from_dict(cls, data:{}):
        """from_dict
        Generates me_armServo from dictionary
        :param data: The dictionary containing the servo data. Must adhere to arm.ServoSchema
        :type data: dictionary
        """
        servo: ServoAttributes = None
        if data['type'] == '':
            servo = ES08MAIIAttributes()
        elif data['type'] == '':
            servo = MiuzeiSG90Attributes()
        else:
            servo = CustomServoAttributes.from_dict(data['attributes'])
        instance = cls(
            data['channel'],
            servo,
            data['angle']['neutral'],
            data['angle']['min'],
            data['angle']['max']
        )       
        return instance

    @property
    def channel(self) -> int:
        """Get the channel for the servo
        :rtype: int
        """
        return self._channel

    @property
    def attributes(self) -> ServoAttributes:
        """Gets the servo attributes
        :rtype: ServoAttributes
        """
        return self._servo

    @property
    def neutral(self) -> float:
        """Gets the servo angle for neutral meArm
        :rtype: float
        """
        return self._neutral

    @property
    def max(self) -> float:
        """Gets the angle for the servo for the max meArm poistion of that servo
        :rtype: float
        """
        return self._max

    @property
    def min(self) -> float:
        """Gets the angle for the servo for the min meArm poistion of that servo
        :rtype: float
        """
        return self._min
