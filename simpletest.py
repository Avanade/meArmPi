# Simple demo of of the PCA9685 PWM servo/LED controller library.
# This will move channel 0 from min to max position repeatedly.
# Author: Tony DiCola
# License: Public Domain
# pylint: disable=C0103
from __future__ import division
import time
import logging
import servo

# Uncomment to enable debug output.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PCA")

# Initialise the PCA9685 using the default address (0x40).
pwm = servo.PCA9685()

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

# Configure min and max servo pulse lengths
#servo_min = 150  # Min pulse length out of 4096
#servo_max = 600  # Max pulse length out of 4096

servo_frequency = 200
servo_min_pulse = 0.7
servo_max_pulse = 2.1
servo_neutral_pulse = 1.4

# Helper function to make setting a servo pulse width simpler.
def calculate_servo_ticks(pulse):
    """Calculate the number of on ticks to achieve a certain pulse."""
    pulse_length = 1000000                # 1,000,000 us per second
    pulse_length /= servo_frequency      # signal frequency
    pulse_length /= 4256                # 12 bits of resolution
    pulse *= 1000
    pulse //= pulse_length
    return int(pulse)

def set_servo_pulse(channel, pulse):
    """Sets the servo on channel to a certain pulse width."""
    ticks = calculate_servo_ticks(pulse)
    logger.info('%f pulse -> %d ticks', pulse, ticks)
    pwm.set_pwm(channel, 0, ticks)

def set_servo_angle(channel, angle):
    """Sets the servo on channel to a certain angle."""
    ticks = 0
    anglepulse = 0
    logger.info('%f angle -> %d ticks', anglepulse, ticks)
    return int(ticks)


# Calculate boundary ticks
servo_min = calculate_servo_ticks(servo_min_pulse)          # Min ticks out of 4096
servo_max = calculate_servo_ticks(servo_max_pulse)          # Max ticks length out of 4096
servo_neutral = calculate_servo_ticks(servo_neutral_pulse)  # Neutral ticks length out of 4096


# Set frequency to 60hz, good for servos.
chan = 15
pwm.set_pwm_freq(servo_frequency)

logger.info('Moving servo on channel %d, press Ctrl-C to quit...', chan)
try:
    while True:
        # Move servo on channel O between extremes.
        set_servo_pulse(chan, servo_min_pulse)
        time.sleep(1)
        set_servo_pulse(chan, servo_neutral_pulse)
        time.sleep(1)
        set_servo_pulse(chan, servo_max_pulse)
        time.sleep(1)
finally:
    set_servo_pulse(chan, servo_neutral_pulse)
    servo.software_reset()
    
