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
import json
from jsonschema import validate
from .servo_attributes import ServoAttributes

"""
    Implements the properties class for a custom servo reading from json
"""

schema = {
    "$id": "http://theRealThor.com/meArm.servo-attributes.schema.json",
    "title": "Servo Attributes",
    "description": "Describes key servo attributes for tuning.",
    "definitions": {
        "servo_attributes": {
            "type" : "object",
            "properties" : {
                "max_pulse" : {"type" : "number"},
                "min_pulse" : {"type" : "number"},
                "neutral_pulse" : {"type": "number"},
                "max_angle": {"type": "number"},
                "min_angle": {"type": "number"},
                "neutral_angle": {"type": "number"}
            },
            "required": [ "max_pulse", "min_pulse", "neutral_pulse", "max_angle", "min_angle", "neutral_angle" ]
        },
    },
    "allOf": [
        {"$ref": "#/definitions/servo_attributes"}
    ]
}

class CustomServoAttributes(ServoAttributes):
    """
    Implements an abstract base class for servo properties
    """

    max_pulse = 0
    min_pulse = 0
    neutral_pulse = 0
    min_angle = 0
    max_angle = 0
    neutral_angle = 0

    @classmethod
    def from_json_file(cls, json_file:str):
        """from_json_file
        Generates CustomServoAttributes from json data
        """
        with open(json_file) as file:
            data = json.load(file)
            validate(data, schema)
        instance = cls.from_dict(data)
        return instance

    @classmethod
    def from_json(cls, json_string:str):
        """from_json
        Generates CustomServoAttributes from json data
        """
        data = json.loads(json_string)
        validate(data, schema)
        instance = cls.from_dict(data)
        return instance

    @classmethod
    def from_dict(cls, data:{}):
        instance = cls()
        instance.max_pulse = data['max_pulse']
        instance.min_pulse = data['min_pulse']
        instance.neutral_pulse = data['neutral_pulse']
        instance.min_angle = data['min_angle']
        instance.max_angle = data['max_angle']
        instance.neutral_angle = data['neutral_angle']
        return instance
