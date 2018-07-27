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
"""Simple test program for servo actuation"""
import time
import logging
import atexit
from controller import PCA9685, Servo, ServoAttributes, MiuzeiSG90Attributes, ES08MAIIAttributes, software_reset

# Uncomment to enable debug output.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

frequency = 26500000 # This has been tweaked to provide exact pulse timing for the board. 
resolution = 4096
servo_frequency = 50

# Initialise the PCA9685 using the default address (0x40).
pwm = PCA9685(
    0x40, 
    None,
    frequency,
    resolution,
    servo_frequency)

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

attributes = MiuzeiSG90Attributes()
hip_channel = 15
elbow_channel = 12
shoulder_channel = 13
gripper_channel = 14

pwm.add_servo(hip_channel, attributes)
pwm.add_servo(gripper_channel, attributes)
pwm.add_servo(shoulder_channel, attributes)
pwm.add_servo(elbow_channel, attributes)

def shutdown():
    """Resets the arm at neutral position and then resets the controller"""
    logger.info('Resetting arm and controller...')
    pwm.set_servo_angle(hip_channel, hip_neutral_angle)
    pwm.set_servo_angle(shoulder_channel, shoulder_neutral_angle)
    pwm.set_servo_angle(elbow_channel, elbow_neutral_angle)
    pwm.set_servo_angle(gripper_channel, gripper_open_angle)
    time.sleep(5)
    software_reset()

# restier shutdown steps
atexit.register(shutdown)

# arm neutrals and boundaries
elbow_neutral_angle = 0
shoulder_neutral_angle = 40
hip_neutral_angle = 0

elbow_max_angle = 84.5
shoulder_max_angle = 65
hip_max_angle = 84.5

elbow_min_angle = -25
shoulder_min_angle = -15
hip_min_angle = -84.5

gripper_closed_angle = 27.5
gripper_open_angle = -20

# current angles
elbow_angle = elbow_neutral_angle
shoulder_angle = shoulder_neutral_angle
hip_angle = hip_neutral_angle

# movement increment in degrees
inc = 0.5

logger.info('Press Ctrl-C to quit...')
pwm.set_servo_angle(hip_channel, hip_angle) #hip
pwm.set_servo_angle(gripper_channel, gripper_open_angle) #gripper
pwm.set_servo_angle(shoulder_channel, shoulder_angle) #shoulder
pwm.set_servo_angle(elbow_channel, elbow_angle) #elbow
while True:
    while elbow_angle < elbow_max_angle:
        pwm.set_servo_angle(elbow_channel, elbow_angle)
        elbow_angle += inc

    while shoulder_angle > shoulder_min_angle:
        pwm.set_servo_angle(shoulder_channel, shoulder_angle)
        shoulder_angle -= inc

    time.sleep(1)
    pwm.set_servo_angle(gripper_channel, gripper_closed_angle) #gripper
    time.sleep(1)

    while hip_angle > hip_min_angle:
        pwm.set_servo_angle(hip_channel, hip_angle)
        hip_angle -= inc

    while shoulder_angle < shoulder_max_angle:
        pwm.set_servo_angle(shoulder_channel, shoulder_angle)
        shoulder_angle += inc

    while elbow_angle > elbow_min_angle:
        pwm.set_servo_angle(elbow_channel, elbow_angle)
        elbow_angle -= inc

    while hip_angle < hip_max_angle:
        pwm.set_servo_angle(hip_channel, hip_angle)
        hip_angle += inc

    time.sleep(1)
    pwm.set_servo_angle(gripper_channel, gripper_open_angle) #gripper
    time.sleep(1)

    while hip_angle > hip_neutral_angle:
        pwm.set_servo_angle(hip_channel, hip_angle)
        hip_angle -= inc
