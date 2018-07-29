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
"""Module defining a controller and servo related json schemas"""

controller_schema = {
    "$id": "http://theRealThor.com/meArm.servo-controller.schema.json",
    "title": "Servo Controller",
    "description": "Describes key servo controller attributes for tuning.",
    "definitions": {
        "controller_attributes": {
            "type" : "object",
            "properties" : {
                "address" : {"type" : "number"},
                "frequency" : {"type" : "number"},
                "resolution" : {"type": "number"},
                "servo_frequency": {"type": "number"}
            },
            "required": [ "address", "frequency", "resolution", "servo_frequency" ]
        },
    },
    "allOf": [
        {"$ref": "#/definitions/controller_attributes"}
    ]
}

servo_schema = {
    "$id": "http://theRealThor.com/meArm.servo-attributes.schema.json",
    "title": "Servo Attributes",
    "description": "Describes key servo attributes for tuning.",
    "definitions": {
        "range": {
            "type" : "object",
            "properties" : {
                "max" : {"type" : "number"},
                "min" : {"type" : "number"},
                "neutral" : {"type": "number"}
            },
            "required": [ "max", "min", "neutral" ]
        },
        "servo_attributes": {
            "type" : "object",
            "properties" : {
                "pulse": { "$ref": "#/definitions/range"},
                "angle": { "$ref": "#/definitions/range"}
            },
            "required": [ "pulse", "angle" ]
        },
    },
    "allOf": [
        {"$ref": "#/definitions/servo_attributes"}
    ]
}
