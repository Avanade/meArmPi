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

    def __init__(self, controller, channel: int,
                 min_pulse: float = 0.7, max_pulse: float = 2.1, neutral_pulse: float= 1.4,
                 min_angle: float = -90, max_angle: float = 90, neutral_angle: float = 0):
        """__init__
        Initialize Servo
            Attributes:
        :param controller: The controller hosting the servo.
        :type controller: PCA9685

        :param channel: The channel on which the servo is operating.
        :type channel: int

        :param min_pulse: The minimum signal pulse length.
        :type min_pulse: float

        :param max_pulse: The maximum signal pulse length.
        :type max_pulse: float

        :param neutral_pulse: The lenght of a pulse for the neutral position
        :type neutral_pulse: float

        :param min_angle: The minimum servo angle achieved via min_pulse.
        :type min_angle: float

        :param max_angle: The maximum servo angle achieved via max_pulse.
        :type max_angle: float

        :param neutral_angle: The neutral angle achieved via neutral_pulse.
        :type neutral_angle: float
        """
        self._controller = controller
        self._channel = channel
        self._min_pulse = min_pulse
        self._max_pulse = max_pulse
        self._neutral_pulse = neutral_pulse
        self._min_angle = min_angle
        self._max_angle = max_angle
        self._neutral_angle = neutral_angle
        self._ticks = 0
        self._angle = 0
        self._pulse = 0
        self._logger = logging.getLogger(__name__)

        #caluclate boundary ticks for servo
        self._servo_min = self._calculate_servo_ticks_from_pulse(self._min_pulse)
        self._servo_max = self._calculate_servo_ticks_from_pulse(self._max_pulse)
        self._servo_neutral = self._calculate_servo_ticks_from_pulse(self._neutral_pulse)
        
        #initialize servo
        self.set_angle(self._neutral_angle)
        
    @property
    def angle(self) -> float:
        """Gets the current angle of the servo.

        :return: The current servo angle.
        :rtype: float
        """
        return self._ticks

    @property
    def channel(self) -> int:
        """Gets the channel for the servo.

        :return: The servo channel.
        :rtype: int
        """
        return self._channel

    @property
    def pulse(self) -> float:
        """Gets the current pulse lenght of the servo.

        :return: The current servo pulse lenght.
        :rtype: float
        """
        return self._pulse

    @property
    def ticks(self) -> int:
        """Gets the current number of ticks on the servo.

        :return: The current servo ticks.
        :rtype: int
        """
        return self._ticks


    def _calculate_servo_ticks_from_pulse(self, pulse: float) -> int:
        """calculate_servo_ticks_from_pulse
        Calculate the number of on ticks to achieve a certain pulse.
        
        :param pulse: The length of the pulse for which to calculate the ticks
        :type pulse: float

        :return: The number of ticks to achieve the pulse
        :rtype: int
        """

        if str(pulse) < str(self._min_pulse) or str(pulse) > str(self._max_pulse):
            raise Exception('Pulse %f out of range. Must be between %f and %f' %
                            (pulse, self._min_pulse, self._max_pulse))

        pulse_length = 1000000.0                              # 1,000,000 us per second
        pulse_length /= float(self._controller.frequency)     # signal frequency
        pulse_length /= float(self._controller.resolution)    # pusle resolution
        pulse *= 1000.0
        pulse //= pulse_length
        return int(pulse)

    def _calculate_servo_ticks_from_angle(self, angle: float) -> (float, int):
        """_calculate_servo_ticks_from_angle
        Calculate the number of on ticks to achieve a certain servo angle.
        
        :param angle: The angle for which to calculate the ticks
        :type angle: float

        :return: The number of ticks to achieve the angle and the corresponding pulse
        :rtype: (float, int)        
        """

        if angle < self._min_angle or angle > self._max_angle:
            raise Exception('Angle %d out of range. Must be between %d and %d' %
                            (angle, self._min_angle, self._max_angle))

        pulse = self._neutral_pulse
        if angle > self._neutral_angle:
            pulse += ((angle - self._neutral_angle) * (self._max_pulse - self._neutral_pulse)) / \
                (self._max_angle - self._neutral_angle)
        elif angle < self._neutral_angle:
            pulse -= ((angle + self._neutral_angle) * (self._neutral_pulse - self._min_pulse)) / \
                (self._min_angle + self._neutral_angle)
        self._logger.info('Angle %d -> pulse %f', angle, pulse)
        return self._calculate_servo_ticks_from_pulse(pulse), pulse

    def set_pulse(self, pulse: float):
        """set_pulse
        Sets the servo to a certain pulse width.
        
        :param pulse: The desired pulse lenght
        :type pulse: float
        """
        ticks = self._calculate_servo_ticks_from_pulse(pulse)
        self._logger.info('Channel %d: %f pulse -> %d ticks', self._channel, pulse, ticks)
        self._controller.set_pwm(self._channel, 0, ticks)
        self._pulse = pulse
        self._ticks = ticks

    def set_angle(self, angle: float):
        """set_angle
        Sets the servo to a certain angle.
        
        :param angle: The desired angle to achieve. 
        :type angle: float
        """
        ticks, pulse = self._calculate_servo_ticks_from_angle(angle)
        self._logger.info('Channel %d: %f angle -> %d ticks', self._channel, angle, ticks)
        self._controller.set_pwm(self._channel, 0, ticks)
        self._angle = angle
        self._ticks = ticks
        self._pulse = pulse
