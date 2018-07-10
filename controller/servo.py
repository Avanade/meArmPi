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
"""
    Implements a basic wrapper for a servo
"""
import logging
import time
import math

class Servo(object):
    """Represents a servo on the controller."""

    def __init__(self, controller, channel:int, frequency:int=200, 
                 min_pulse:float=0.7, max_pulse:float=2.1, neutral_pulse:float=1.4,
                 min_angle:float=-90, max_angle:float=90, neutral_angle:float=0,
                 resolution:int=4096):
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
        self.logger = logging.getLogger(__name__)

        #caluclate boundary ticks for servo
        self.servo_min = self.calculate_servo_ticks_from_pulse(self.min_pulse)
        self.servo_max = self.calculate_servo_ticks_from_pulse(self.max_pulse)
        self.servo_neutral = self.calculate_servo_ticks_from_pulse(self.neutral_pulse)
        
        #initialize servo
        self.set_angle(self.neutral_angle)
        
    def calculate_servo_ticks_from_pulse(self, pulse:float) -> int:
        """Calculate the number of on ticks to achieve a certain pulse."""

        if str(pulse) < str(self.min_pulse) or str(pulse) > str(self.max_pulse):
            raise Exception('Pulse %f out of range. Must be between %f and %f' %
                            (pulse, self.min_pulse, self.max_pulse))

        pulse_length = 1000000                  # 1,000,000 us per second
        pulse_length /= self.frequency          # signal frequency
        pulse_length /= self.pulse_resolution   # 12 bits of resolution
        pulse *= 1000
        pulse //= pulse_length
        return int(pulse)

    def calculate_servo_ticks_from_angle(self, angle:float) -> (float, int):
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
        self.logger.info('Angle %d -> pulse %f', angle, pulse)
        return self.calculate_servo_ticks_from_pulse(pulse), pulse

    def get_state(self) -> (float, float, float):
        """Return the current servo state."""
        return self.ticks, self.pulse, self.angle

    def set_pulse(self, pulse: float):
        """Sets the servo to a certain pulse width."""
        ticks = self.calculate_servo_ticks_from_pulse(pulse)
        self.logger.info('Channel %d: %f pulse -> %d ticks', self.channel, pulse, ticks)
        self.controller.set_pwm(self.channel, 0, ticks)
        self.pulse = pulse
        self.ticks = ticks

    def set_angle(self, angle:float):
        """Sets the servo to a certain angle."""
        ticks, pulse = self.calculate_servo_ticks_from_angle(angle)
        self.logger.info('Channel %d: %f angle -> %d ticks', self.channel, angle, ticks)
        self.controller.set_pwm(self.channel, 0, ticks)
        self.angle = angle
        self.ticks = ticks
        self.pulse = pulse
