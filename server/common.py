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
"""Common module for meArm tracking globals and singeltons."""
import platform
import atexit
import logging
import json

from server.models.status import Status
from server.models.point import Point
from arm import me_arm

global VERSION
global HOSTNAME

VERSION = "0.0.1"
HOSTNAME = platform.node()

def init():
    """Initialize globals."""

    global token
    global status
    global inactivity_timer

    token = {}
    status = {}
    inactivity_timer = {}

    me_arm.boot_from_json_file('me_arm.json')
    for name in me_arm.get_names():
        inactivity_timer[name] = None
        token[name] = None
        status[name] = Status(HOSTNAME, VERSION, False)
        arm = me_arm.get(name)
        status[name].position = Point(
            arm.position.x,
            arm.position.y,
            arm.position.z,
            arm.position.r,
            arm.position.lat,
            arm.position.lng)

def shutdown():
    """shutdown
        Deletes the arm and then resets the controller
    """
    me_arm.shutdown(True)

# restier shutdown steps
atexit.register(shutdown)