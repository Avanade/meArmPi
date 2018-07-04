# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
# pylint: disable=C0103
"""Simple test program for servo actuation"""
import time
import logging
import servo

# Uncomment to enable debug output.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialise the PCA9685 using the default address (0x40).
pwm = servo.PCA9685(address=0x40)

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)


servo_frequency = 50

servo_min_pulse = 0.6
servo_max_pulse = 2.3
servo_neutral_pulse = 1.4
servo_min_angle = -85.0
servo_max_angle = 85.0
servo_neutral_angle = -0.0
chan = 0


pwm.add_servo(chan, servo_frequency, servo_min_pulse, servo_max_pulse, servo_neutral_pulse,
              servo_min_angle, servo_max_angle, servo_neutral_angle, 4256)
logger.info('Moving servo on channel %d, press Ctrl-C to quit...', chan)
try:
    while True:
        angle = servo_min_angle
        inc = 0.5

        while angle < servo_max_angle:
            pwm.set_servo_angle(chan, angle)
            angle += inc

        time.sleep(0.5)

        while angle > servo_min_angle:
            pwm.set_servo_angle(chan, angle)
            angle -= inc

        time.sleep(0.5)

finally:
    pwm.set_servo_pulse(chan, servo_min_pulse)
    time.sleep(5)
    pwm.set_servo_pulse(chan, servo_max_pulse)
    time.sleep(5)
    pwm.set_servo_pulse(chan,25)
    time.sleep(0.5)
    servo.software_reset()