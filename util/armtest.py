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
"""Simple test routine for meArm on RPI"""
import time
import logging
import atexit
import json
from arm import me_arm, arm_attributes, me_armServo
from controller import PCA9685, software_reset

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
print('Press Ctrl-C to quit...')

test = me_armServo.from_json_file('me_arm.servo.json')

resolution = 4096
frequency = 26500000 # This has been tweaked to provide exact pulse timing for the board. 
servo_frequency = 50

# Initialise the PCA9685 using the default address (0x40).
controller = PCA9685(
    0x40,
    None,
    frequency,
    resolution,
    servo_frequency)

def shutdown():
    """shutdown
        Deletes the arm and then resets the controller
    """
    logger.info('Resetting servo and controller...')
    logger.info('Deleting registered meArms [%s]' % ', '.join(map(str, me_arm.get_names())))
    me_arm.delete_all()
    software_reset()

# restier shutdown steps
atexit.register(shutdown)

my_arm = me_arm.createWithServoParameters(controller, 15, 12, 13, 14)
my_arm.close()
time.sleep(2)
my_arm.open()
time.sleep(2)
my_arm.test()
