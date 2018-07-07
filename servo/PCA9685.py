# Copyright (c) 2016 Adafruit Industries
# Author: Tony DiCola
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
# pylint: disable=C0103
"""
    This library drive GPIO interaction with the Adafruit Servo HAT and provides
    some high level functions to interact with servos on the HAT
"""
from __future__ import division
import logging
import time
import math


# Registers/etc:
PCA9685_ADDRESS = 0x40
MODE1 = 0x00
MODE2 = 0x01
SUBADR1 = 0x02
SUBADR2 = 0x03
SUBADR3 = 0x04
PRESCALE = 0xFE
LED0_ON_L = 0x06
LED0_ON_H = 0x07
LED0_OFF_L = 0x08
LED0_OFF_H = 0x09
ALL_LED_ON_L = 0xFA
ALL_LED_ON_H = 0xFB
ALL_LED_OFF_L = 0xFC
ALL_LED_OFF_H = 0xFD

# Bits:
RESTART = 0x80
SLEEP = 0x10
ALLCALL = 0x01
INVRT = 0x10
OUTDRV = 0x04


logger = logging.getLogger(__name__)

def ensureI2C(i2c=None):
    """Ensures I2C device interface"""
    if i2c is None:
        logger.info('Initializing I2C.')
        import Adafruit_GPIO.I2C as I2C
        i2c = I2C
    return i2c

def software_reset(i2c=None, **kwargs):
    """Sends a software reset (SWRST) command to all servo drivers on the bus."""
    # Setup I2C interface for device 0x00 to talk to all of them.
    i2c = ensureI2C(i2c)
    d = i2c.get_i2c_device(0x00, **kwargs)
    d.writeRaw8(0x06)  # SWRST
    logger.info('Servo controllers have been reset.')

class Servo(object):
    """Represents a servo on the controller."""

    def __init__(self:Servo, controller, channel:int, frequency:int=200, 
                 min_pulse:float=0.7, max_pulse:float=2.1, neutral_pulse:float=1.4,
                 min_angle:float=-90, max_angle:float=90, neutral_angle:float=0,
                 resolution:int=4096) -> Servo:
        """Initialize Servo
            Attributes:
                controller:         the controller hosting the servo.
                channel:            the channel on which the servo is operating.
                frequency:          the frequency for the servo.
                min_pulse:          the minimum signal pulse length.
                max_pulse:          the maximum signal pulse length.
                neutral_pulse:      the lenght of a pulse for the neutral position
                min_angle:          the minimum servo angle achieved via min_pulse.
                max_angle:          the maximum servo angle achieved via max_pulse.
                neutral_angle:      the neutral angle achieved via neutral_pulse.
                pulse_resolution:   the pulse resolution. This will generally be 4096, but can be
                                    adjusted for each servo to achieve the desired width. Use
                                    a scope on the controller to verify that the actual pulse
                                    length corresponds to the requested pulse length and tweak this
                                    parameter until it does.
        """
        self.controller = controller
        self.channel = channel
        self.frequency = frequency
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.neutral_pulse = neutral_pulse
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.neutral_angle = neutral_angle
        self.pulse_resolution = resolution
        self.ticks = 0
        self.angle = 0
        self.pulse = 0

        #caluclate boundary ticks for servo
        self.servo_min = self.calculate_servo_ticks_from_pulse(self.min_pulse)
        self.servo_max = self.calculate_servo_ticks_from_pulse(self.max_pulse)
        self.servo_neutral = self.calculate_servo_ticks_from_pulse(self.neutral_pulse)
        
        #initialize servo
        self.set_angle(self.neutral_angle)
        
    def calculate_servo_ticks_from_pulse(self:Servo, pulse:float) -> int:
        """Calculate the number of on ticks to achieve a certain pulse."""

        if pulse < self.min_pulse or pulse > self.max_pulse:
            raise Exception('Pulse %f out of range. Must be between %f and %f' %
                            (pulse, self.min_pulse, self.max_pulse))

        pulse_length = 1000000                  # 1,000,000 us per second
        pulse_length /= self.frequency          # signal frequency
        pulse_length /= self.pulse_resolution   # 12 bits of resolution
        pulse *= 1000
        pulse //= pulse_length
        return int(pulse)

    def calculate_servo_ticks_from_angle(self:Servo, angle:float) -> (float, int):
        """Calculate the number of on ticks to achieve a certain servo angle."""

        if angle < self.min_angle or angle > self.max_angle:
            raise Exception('Angle %d out of range. Must be between %d and %d' %
                            (angle, self.min_angle, self.max_angle))

        pulse = self.neutral_pulse
        if angle > self.neutral_angle:
            pulse += ((angle - self.neutral_angle) * (self.max_pulse - self.neutral_pulse)) / \
                (self.max_angle - self.neutral_angle)
        elif angle < self.neutral_angle:
            pulse -= ((angle + self.neutral_angle) * (self.neutral_pulse - self.min_pulse)) / \
                (self.min_angle + self.neutral_angle)
        logger.info('Angle %d -> pulse %f', angle, pulse)
        return self.calculate_servo_ticks_from_pulse(pulse), pulse

    def get_state(self:Servo) -> (float, float, float):
        """Return the current servo state."""
        return self.ticks, self.pulse, self.angle

    def set_pulse(self:Servo, pulse: float):
        """Sets the servo to a certain pulse width."""
        ticks = self.calculate_servo_ticks_from_pulse(pulse)
        logger.info('Channel %d: %f pulse -> %d ticks', self.channel, pulse, ticks)
        self.controller.set_pwm(self.channel, 0, ticks)
        self.pulse = pulse
        self.ticks = ticks

    def set_angle(self:Servo, angle:float):
        """Sets the servo to a certain angle."""
        ticks, pulse = self.calculate_servo_ticks_from_angle(angle)
        logger.info('Channel %d: %f angle -> %d ticks', self.channel, angle, ticks)
        self.controller.set_pwm(self.channel, 0, ticks)
        self.angle = angle
        self.ticks = ticks
        self.pulse = pulse


class PCA9685(object):
    """PCA9685 PWM LED/servo controller."""

    def __init__(self, address=PCA9685_ADDRESS, i2c=None, **kwargs):
        """Initialize the PCA9685."""
        i2c = ensureI2C(i2c)
        self.servos = {}
        self.frequency = None
        self._address = address
        self._device = i2c.get_i2c_device(address, **kwargs)
        self.set_all_pwm(0, 0)
        self._device.write8(MODE2, OUTDRV)
        self._device.write8(MODE1, ALLCALL)
        time.sleep(0.005)  # wait for oscillator
        mode1 = self._device.readU8(MODE1)
        mode1 = mode1 & ~SLEEP  # wake up (reset sleep)
        self._device.write8(MODE1, mode1)
        time.sleep(0.005)  # wait for oscillator

    def add_servo(self, channel: int, frequency:int=200, 
                  min_pulse:float=0.7, max_pulse:float=2.1, neutral_pulse:float=1.4,
                  min_angle:float=-90.0, max_angle:float=90.0, neutral_angle:float=0.0,
                  pulse_resolution:int=4096):
        """Adds a servo definition for a given channel.
           Attributes:
                channel:            the channel on which the servo is operating.
                frequency:          the frequency for the servo.
                min_pulse:          the minimum signal pulse length.
                max_pulse:          the maximum signal pulse length.
                neutral_pulse:      the lenght of a pulse for the neutral position
                min_angle:          the minimum servo angle achieved via min_pulse.
                max_angle:          the maximum servo angle achieved via max_pulse.
                neutral_angle:      the neutral angle achieved via neutral_pulse.
                pulse_resolution:   the pulse resolution. This will generally be 4096, but can be
                                    adjusted for each servo to achieve the desired width. Use
                                    a scope on the controller to verify that the actual pulse
                                    length corresponds to the requested pulse length and tweak this
                                    parameter until it does.
        """
        if self.frequency is None:
            self.frequency = frequency
            self.set_pwm_freq(frequency)
        else:
            if self.frequency != frequency:
                raise Exception('Incompatible frequency %d. All servos must operate on the same \
                    frequency. Presvioulsy registered frequency: %d' % (frequency, self.frequency))

        self.servos[channel] = Servo(frequency, self, channel, min_pulse, max_pulse, neutral_pulse,
                                     min_angle, max_angle, neutral_angle,
                                     pulse_resolution)

    def get_servo_state(self, channel:int) -> (float, float, float):
        """Gets the servo state on channel (ticks, pulse and angle)."""
        servo = self.servos[channel]
        if servo is None:
            raise Exception('There is no servo registered on channel %d' % channel)
        else:
            return servo.get_state()       

    def set_servo_pulse(self, channel:int, pulse:float):
        """Sets the servo on channel to a certain pulse width."""
        servo = self.servos[channel]
        if servo is None:
            raise Exception('There is no servo registered on channel %d' % channel)
        else:
            servo.set_pulse(pulse)

    def set_servo_angle(self, channel:int, angle:float):
        """Sets the servo on channel to a certain angle."""
        servo = self.servos[channel]
        if servo is None:
            raise Exception('There is no servo registered on channel %d' % channel)
        else:
            servo.set_angle(angle)

    def set_pwm_freq(self, freq_hz:int):
        """Set the PWM frequency to the provided value in hertz."""
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        logger.info('Setting PWM frequency to %d Hz', freq_hz)
        logger.info('Estimated pre-scale: %f', prescaleval)
        prescale = int(math.floor(prescaleval + 0.5))
        logger.info('Final pre-scale: %d', prescale)
        oldmode = self._device.readU8(MODE1)
        newmode = (oldmode & 0x7F) | 0x10    # sleep
        self._device.write8(MODE1, newmode)  # go to sleep
        self._device.write8(PRESCALE, prescale)
        self._device.write8(MODE1, oldmode)
        time.sleep(0.005)
        self._device.write8(MODE1, oldmode | 0x80)

    def set_pwm(self, channel:int, on_ticks:int, off_ticks:int):
        """Sets a single PWM channel."""
        self._device.write8(LED0_ON_L+4*channel, on_ticks & 0xFF)
        self._device.write8(LED0_ON_H+4*channel, on_ticks >> 8)
        self._device.write8(LED0_OFF_L+4*channel, off_ticks & 0xFF)
        self._device.write8(LED0_OFF_H+4*channel, off_ticks >> 8)

    def set_all_pwm(self, on_ticks:int, off_ticks:int):
        """Sets all PWM channels."""
        self._device.write8(ALL_LED_ON_L, on_ticks & 0xFF)
        self._device.write8(ALL_LED_ON_H, on_ticks >> 8)
        self._device.write8(ALL_LED_OFF_L, off_ticks & 0xFF)
        self._device.write8(ALL_LED_OFF_H, off_ticks >> 8)

