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
from abc import ABCMeta, abstractmethod

"""
    Implements an abstract class describing key servo properties
"""

class ServoAttributes(metaclass=ABCMeta):
    """
    Implements an abstract base class for servo properties
    """

    @property
    @abstractmethod
    def min_pulse(self) -> float:
        """Gets the minimum pulse for the servo.
        :return: The minimum pulse for the servo leading to the minimum actuaction.
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def max_pulse(self) -> float:
        """Gets the maximum pulse for the servo.
        :return: The maximum pulse for the servo leading to the maximum actuaction.
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def neutral_pulse(self) -> float:
        """Gets the neutral pulse for the servo.
        :return: The neutral pulse for the servo leading to the neutral actuaction.
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def min_angle(self) -> float:
        """Gets the minimum angle for the servo.
        :return: The minimum angle the servo can achieve.
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def max_angle(self) -> float:
        """Gets the maximum angle for the servo.
        :return: The maximum angle the servo can achieve.
        :rtype: float
        """
        pass

    @property
    @abstractmethod
    def neutral_angle(self) -> float:
        """Gets the neutral angle for the servo.
        :return: The neutral angle for the servo.
        :rtype: float
        """
        pass
