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
"""Module defining a meArm related json schemas"""
from controller import ServoSchema, ControllerSchema


arm_servo_schema = {
    "$id": "http://theRealThor.com/meArm.arm-servo.schema.json",
    "title": "Servo Attributes",
    "description": "Describes additional meArm servo attributes.",
    "definitions": {
        "angles": {
            "type": "object",
            "properties": {
                "neutral" : {"type": "number"},
                "max": {"type": "number"},
                "min": {"type": "number"},               
            }
            "required": [ "max", "min", "neutral" ]
        },
        "arm": {
            "type": "object"
        }
    }
    "type" : "object",
    "properties" : {
        "channel" : {"type" : "number"},
        "type": { "type" : "string", "enum": ["custom", "SG-90", "ES08MAII"]},
        "attributes" : {"ref": "http://theRealThor.com/meArm.servo-attributes.schema.json/#/definitions/servo_attributes"},
        "arm-angles": {
            "type": "object",
            "properties": {
                "neutral" : {"type": "number"},
                "max": {"type": "number"},
                "min": {"type": "number"},
            },
            "required": [ "max", "min", "neutral" ]
        },
    },
    "required": [ "channel", "type", "arm-angles"]
}

me_arm_schema = {
    "$id": "http://theRealThor.com/meArm.me-arm.schema.json",
    "title": "meArm",
    "description": "Describes a meArm setup."

}

schema_store = {
    "http://theRealThor.com/meArm.servo-controller.schema.json": ControllerSchema,
    "http://theRealThor.com/meArm.servo-attributes.schema.json": ServoSchema,
    "http://theRealThor.com/meArm.arm-servo.schema.json": arm_servo_schema
}
