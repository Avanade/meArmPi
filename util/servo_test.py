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
"""Simple test for servo actuation"""
import time
import logging
import atexit
import controller

# Uncomment to enable debug output.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

resolution = 4096
frequency = 26500000 # This has been tweaked to provide exact pulse timing for the board. 
servo_frequency = 50
chan = 1

# Initialise the PCA9685 using the default address (0x40).
pwm = controller.PCA9685(
    0x40,
    None,
    frequency,
    resolution,
    servo_frequency)

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# use to tune the servo
# for Emax ES08MAII
servo_min_pulse = 0.6
servo_max_pulse = 2.4
servo_neutral_pulse = 1.5
servo_min_angle = -90.0
servo_max_angle = 90.0
servo_neutral_angle = -0.0

# for Miuzei SG90
# servo_min_pulse = 0.6
# servo_max_pulse = 2.3
# servo_neutral_pulse = 1.4
# servo_min_angle = -85.0
# servo_max_angle = 85.0
# servo_neutral_angle = -0.0

def shutdown():
    """
        Puts the servo through it limit positions returning to netural and then
        resets the controller
    """
    logger.info('Resetting servo and controller...')
    pwm.set_servo_pulse(chan, servo_min_pulse)
    time.sleep(5)
    pwm.set_servo_pulse(chan, servo_max_pulse)
    time.sleep(5)
    pwm.set_servo_pulse(chan, servo_neutral_pulse)
    time.sleep(5)
    controller.software_reset()

# restier shutdown steps
atexit.register(shutdown)

#add the servo
pwm.add_servo(
    chan,
    servo_min_pulse,
    servo_max_pulse,
    servo_neutral_pulse,
    servo_min_angle,
    servo_max_angle,
    servo_neutral_angle)

logger.info('Moving servo on channel %d, press Ctrl-C to quit...', chan)
while True:
    #perform continous back and forth until user aborts
    angle = servo_min_angle + 0.01
    inc = 0.5

    pwm.set_servo_pulse(chan, servo_neutral_pulse)
    time.sleep(5)
    pwm.set_servo_pulse(chan, servo_min_pulse)
    time.sleep(5)
    pwm.set_servo_pulse(chan, servo_max_pulse)
    time.sleep(5)

    while angle < servo_max_angle - 0.5:
        pwm.set_servo_angle(chan, angle)
        angle += inc

    time.sleep(0.5)

    while angle > servo_min_angle + 0.5:
        pwm.set_servo_angle(chan, angle)
        angle -= inc

    time.sleep(0.5)
    