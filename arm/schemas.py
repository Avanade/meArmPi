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
        "arm_servo": {
            "type": "object",
            "properties": {
                "channel": {"type": "number"},
                "type": { "type": "string", "enum": ["custom", "SG-90", "ES08MAII"]},
                "attributes": {"ref": "http://theRealThor.com/meArm.servo-attributes.schema.json/#/definitions/servo_attributes"},
                "range": { "ref": "http://theRealThor.com/meArm.servo-attributes.schema.json/#/definitions/range"},
                "trim": {"type": "number"}
            },
            "required": [ "channel", "type", "range", "trim"]
        }
    },
    "allOf": [
        { "$ref": "#/definitions/arm_servo" }
    ]
}

me_arm_schema = {
    "$id": "http://theRealThor.com/meArm.me-arm.schema.json",
    "title": "meArm",
    "description": "Describes a meArm setup.",
    "definitions": {
        "arm": {
            "type": "object",
            "properties": {
                "logging_level": {"type": "string", "enum": ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]},
                "angle-increment": {"type": "number"},
                "servos": {
                    "type": "object",
                    "properties": {
                        "hip": { "$ref": "http://theRealThor.com/meArm.arm-servo.schema.json/#/definitions/arm_servo"},
                        "eblow": { "$ref": "http://theRealThor.com/meArm.arm-servo.schema.json/#/definitions/arm_servo"},
                        "shoulder": { "$ref": "http://theRealThor.com/meArm.arm-servo.schema.json/#/definitions/arm_servo"},
                        "gripper": { "$ref": "http://theRealThor.com/meArm.arm-servo.schema.json/#/definitions/arm_servo"}
                    },
                    "required": ["hip", "elbow", "shoulder", "gripper"]
                },
                "kinematics": {
                    "type": "object",
                    "properties": {
                        "humerus": {"type": "number"},
                        "radius": {"type": "number"},     
                        "phalanx":  {"type": "number"},
                        "clavicle": {"type": "number"},
                        "x-plane-offset": {"type": "number"},
                        "y-plane-offset": {"type": "number"},
                        "z-plane-offset": {"type": "number"}
                    },
                    "required": ["humerus", "radius", "phalanx", "clavicle", "x-plane-offset", "y-plane-offset", "z-plane-offset"]
                }
            },
            "required": ["angle-increment", "servos"]
        },
        "arm-controller": {
            "type": "object",
            "properties": {
                "controller": { "$ref": "http://theRealThor.com/meArm.servo-controller.schema.json/#/definitions/controller_attributes"},
                "arms": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/arm"},
                    "minItems": 1
                }
            },
            "required": ["controller", "arms"]
        },
        "environment": {
            "type": "array",
            "items": {"$ref": "#/definitions/arm-controller"},
            "minItems": 1,
            "maxItems": 255
        }
    },
    "oneOf": [
        { "$ref": "#/definitions/arm" },
        { "$ref": "#/definitions/arm_controller" },
        { "$ref": "#/definitions/environment" }
    ]
}

schema_store = {
    "http://theRealThor.com/meArm.servo-controller.schema.json": ControllerSchema,
    "http://theRealThor.com/meArm.servo-attributes.schema.json": ServoSchema,
    "http://theRealThor.com/meArm.arm-servo.schema.json": arm_servo_schema,
    "http://theRealThor.com/meArm.me-arm.schema.json": me_arm_schema
}
