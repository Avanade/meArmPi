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


servo_frequency = 200
servo_min_pulse = 0.7
servo_max_pulse = 2.1
servo_neutral_pulse = 1.4
servo_min_angle = -85.0
servo_max_angle = 70.0
servo_neutral_angle = -6.0
chan = 15


pwm.add_servo(chan, servo_frequency, servo_min_pulse, servo_max_pulse, servo_neutral_pulse,
              servo_min_angle, servo_max_angle, servo_neutral_angle, 4256)
pwm.add_servo(14, servo_frequency, servo_min_pulse, servo_max_pulse, servo_neutral_pulse,
              servo_min_angle, servo_max_angle, servo_neutral_angle, 4256)
pwm.add_servo(13, servo_frequency, servo_min_pulse, servo_max_pulse, servo_neutral_pulse,
              servo_min_angle, servo_max_angle, servo_neutral_angle, 4256)
pwm.add_servo(12, servo_frequency, servo_min_pulse, servo_max_pulse, servo_neutral_pulse,
              servo_min_angle, servo_max_angle, servo_neutral_angle, 4256)

logger.info('Moving servo on channel %d, press Ctrl-C to quit...', chan)
try:

    angle1 = -10.0
    angle2 = 40.0
    angle3 = -55.0
    angle4 = 0.0
    while True:
        pwm.set_servo_angle(15, 0) #base
        pwm.set_servo_angle(14, angle3) #gripper
        pwm.set_servo_angle(13, angle2) #hip
        pwm.set_servo_angle(12, angle1) #shoulder

        inc = 0.25


        while angle1 < servo_max_angle:
            pwm.set_servo_angle(12, angle1)
            angle1 += inc

        while angle2 > servo_min_angle+70:
            pwm.set_servo_angle(13, angle2)
            angle2 -= inc

        while angle4 > servo_min_angle:
            pwm.set_servo_angle(15, angle4)
            angle4 -= inc

        while angle2 < servo_max_angle-20:
            pwm.set_servo_angle(13, angle2)
            angle2 += inc

        while angle1 > servo_min_angle+60:
            pwm.set_servo_angle(12, angle1)
            angle1 -= inc

        while angle4 < servo_max_angle:
            pwm.set_servo_angle(15, angle4)
            angle4 += inc

        time.sleep(1)
        pwm.set_servo_angle(14, -5) #gripper
        time.sleep(1)

        while angle4 > 0:
            pwm.set_servo_angle(15, angle4)
            angle4 -= inc

finally:
    pwm.set_servo_angle(15, 0)
    pwm.set_servo_angle(13, servo_min_angle+70)
    pwm.set_servo_angle(12, servo_max_angle)
    pwm.set_servo_angle(14, -55)

    time.sleep(5)
    servo.software_reset()
