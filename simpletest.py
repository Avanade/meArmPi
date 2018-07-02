# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
# pylint: disable=C0103
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
chan = 15


pwm.add_servo(chan, servo_frequency, servo_min_pulse, servo_max_pulse, servo_neutral_pulse, 4256)
logger.info('Moving servo on channel %d, press Ctrl-C to quit...', chan)
try:
    while True:
        # Move servo on channel O between extremes.
        pwm.set_servo_pulse(chan, servo_min_pulse)
        time.sleep(1)
        pwm.set_servo_pulse(chan, servo_neutral_pulse)
        time.sleep(1)
        pwm.set_servo_pulse(chan, servo_max_pulse)
        time.sleep(1)
finally:
    pwm.set_servo_pulse(chan, servo_neutral_pulse)
    servo.software_reset()
    
