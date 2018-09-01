# Copyright (c) 2016 Adafruit Industries
# Author: Tony DiCola
#
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
# pylint: disable=R0913
"""
    This library drive GPIO interaction with the Adafruit Servo HAT and provides
    some high level functions to interact with servos on the HAT
"""
import logging
import time
import math
import json
from jsonschema import validate
from .servo import Servo
from .servo_attributes import ServoAttributes
from .schemas import controller_schema as schema

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

logger = logging.getLogger('controller')

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

class PCA9685(object):
    """PCA9685 PWM LED/servo controller."""

    def __init__(self, address: int = PCA9685_ADDRESS, i2c = None, 
                 frequency: int = 26500000, resolution: int = 4096,
                 servo_frequency: int = 50, **kwargs):
        """__init__

        Initialize the PCA9685.

        :param address: The hardware address of the board. Generally 0x40 unless there is more
                        than one board.
        :type address: integer

        :param i2c: I2C driver object. Generally should be None to self obtain.
        :type i2c: Adafruit_GPIO.I2C

        :param frequency: The boards oscillating frequency. Will be around 25MHz, but will
                          slightly vary by board.
        :type frequency: integer

        :param resolution: The pulse interval resolution. It is 12 bit. You should not have
                           to change that.
        :type resolution: integer

        :param servo_frequency: The pulse frequency for the attached servos. All servos on the
                                board share the same frequency.
        :type servo_frequency: integer

        :param kwargs: additional arguments
        :type kwards: point to object array

        """
        i2c = ensureI2C(i2c)
        self._servos = {}
        self._servo_frequency = servo_frequency
        self._frequency = frequency
        self._resolution = resolution
        self._address = address
        self._device = i2c.get_i2c_device(address, **kwargs)

        self.set_all_pwm(0, 0)
        self._device.write8(MODE2, OUTDRV)
        self._device.write8(MODE1, ALLCALL)

        time.sleep(0.005)  # wait for oscillator
        mode = self._device.readU8(MODE1)
        mode = mode & ~SLEEP  # wake up (reset sleep)
        self._device.write8(MODE1, mode)
        time.sleep(0.005)  # wait for oscillator
        self.set_pwm_freq(self._servo_frequency)
        logger.info("Registered controller on address %d" % address)

    @classmethod
    def from_json_file(cls, json_file:str):
        """from_json_file
        Generates PCA9685 from json file
        :param json_file: name of the file containing the json data. Must adhere to Controller.ControllerSchema
        :type json_file: str
        """
        with open(json_file) as file:
            data = json.load(file)
            validate(data, schema)
        instance = cls.from_dict(data)
        return instance

    @classmethod
    def from_json(cls, json_string:str):
        """from_json
        Generates PCA9685 from json data
        :param json_string: String containing the json data. Must adhere to Controller.ControllerSchema
        :type json_string: str
        """
        data = json.loads(json_string)
        validate(data, schema)
        instance = cls.from_dict(data)
        return instance

    @classmethod
    def from_dict(cls, data:{}):
        """from_dict
        Generates PCA9685 from dictionary
        :param data: The dictionary containing the servo data. Must adhere to Controller.ControllerSchema
        :type data: dictionary
        """
        instance = cls(
            data['address'],
            None,
            data['frequency'],
            data['resolution'],
            data['servo_frequency']
        )
        if data['logging_level'] is not None:
            logger.setLevel(data['logging_level'])
        return instance

    @property
    def address(self) -> int:
        """Gets the board address.

        :return: The board address.
        :rtype: int
        """
        return self._address

    @property
    def frequency(self) -> int:
        """Gets the servo frequency configured for the board.

        :return: The servo pulse frequency.
        :rtype: int
        """
        return self._servo_frequency

    @property
    def resolution(self) -> int:
        """Gets the pulse resolution for the board.

        :return: The servo pulse resolution.
        :rtype: int
        """
        return self._resolution

    @property
    def servos(self) -> {}:
        """Gets the collection of servos on the board.

        :return: a list of servos registerd on the board.
        :rtype: Collection of Servo
        """
        return self._resolution


    def add_servo(self, channel: int, attributes: ServoAttributes = None):
        """add_servo
        Adds a servo definition for a given channel.

        :param channel: The channel on which the servo is operating.
        :type channel: integer

        :param attributes: The servo attribute (min/max/neutral pulses and angles).
        :type attributes: ServoAttributes

        """
        if channel < 0 or channel > 15:
            raise ValueError('Channel must be between 0 and 15')

        if channel in self._servos:
            raise KeyError('There is already a servo on this channel: %d', channel)


        self._servos[channel] = Servo(self, channel, attributes)

    def get_servo(self, channel: int) -> Servo:
        """get_servo
        Gets the servo on channel.

        :param channel: The channel for which to obtain the servo state. Between 0 and 15.
        :type channel: integer

        :rtype (Servo) -The servo on that channel.

        """
        if channel < 0 or channel > 15:
            raise ValueError('Channel must be between 0 and 15')

        if channel not in self._servos:
            raise KeyError('There is no servo registered on channel %d' % channel)
        
        servo = self._servos[channel]
        return servo

    def set_servo_pulse(self, channel: int, pulse: float):
        """set_servo_pulse
        Sets the servo on channel to a certain pulse width.

        :param channel: The channel for which to obtain the servo state. Between 0 and 15.
        :type channel: integer

        :param pulse: The pulse length to set.
        :type pulse: float

        """
        if channel < 0 or channel > 15:
            raise ValueError('Channel must be between 0 and 15')

        if channel not in self._servos:
            raise KeyError('There is no servo registered on channel %d' % channel)
        
        servo = self._servos[channel]
        servo.set_pulse(pulse)

    def set_servo_angle(self, channel: int, angle: float):
        """set_servo_angle
        Sets the servo on channel to a certain angle.

        :param channel: The channel for which to obtain the servo state. Between 0 and 15.
        :type channel: integer

        :param angle: The angle to set. The finest resolution is about 0.5 degrees.
        :type pulse: angle

        """
        if channel < 0 or channel > 15:
            raise ValueError('Channel must be between 0 and 15')

        if channel not in self._servos:
            raise KeyError('There is no servo registered on channel %d' % channel)
        
        servo = self._servos[channel]
        servo.set_angle(angle)

    def set_pwm_freq(self, servo_frequency: int):
        """set_pwm_freq
        Set the PWM frequency to the provided value in hertz.

        :param servo_frequency: The frequency of the servo pulse.
        :type servo_frequency: integer

        """
        prescaleval = float(self._frequency)
        prescaleval /= float(self._resolution)
        prescaleval /= float(servo_frequency)
        prescaleval -= 1
        logger.info('Setting PWM frequency to %d Hz', servo_frequency)
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

    def set_off(self, channel: int, tf: bool = True):
        """set_off
        Toggles channel off state. Note that turning the channel totally of will not retain the servo angle
        against manual manipulation

        :param channel: The channel on which to operate.
        :type channel: int
        
        :param tf: Set to True to turn the channel off, False to turn the channel back to PWM
        :type tf: bool
        
        """
        oldmode = self._device.readU8(LED0_OFF_H+4*channel)
        if tf == 1:
            mode = oldmode | 0x10
            logger.info('Setting servo on channel %d to OFF', channel)
        else:
            mode = oldmode & 0xEF
            logger.info('Setting servo on channel %d to PWM', channel)
        self._device.write8(LED0_OFF_H+4*channel, mode)


    def set_pwm(self, channel: int, on_ticks: int, off_ticks: int):
        """set_pwm
        Sets a single PWM channel pulse.

        :param channel: The channel for which to obtain the servo state. Between 0 and 15.
        :type channel: integer

        :param on_ticks: Number of ticks into a period at which to switch the pulse on.
        :type pulse: integer

        :param off_ticks: Number of ticks into a period at which to switch the pulse off.
        :type pulse: integer

        """
        if channel < 0 or channel > 15:
            raise ValueError('Channel must be between 0 and 15')
        if on_ticks < 0:
            raise ValueError('Value for on_ticks must be greater or equaly to zero')
        if on_ticks > off_ticks:
            raise ValueError('Value for on_ticks must be less than or equal to value for off_ticks')

        self._device.write8(LED0_ON_L+4*channel, on_ticks & 0xFF)
        self._device.write8(LED0_ON_H+4*channel, on_ticks >> 8)
        self._device.write8(LED0_OFF_L+4*channel, off_ticks & 0xFF)
        self._device.write8(LED0_OFF_H+4*channel, off_ticks >> 8)

    def set_all_pwm(self, on_ticks: int, off_ticks: int):
        """set_pwm
        Sets all PWM channel pulse.

        :param on_ticks: Number of ticks into a period at which to switch the pulse on.
        :type pulse: integer

        :param off_ticks: Number of ticks into a period at which to switch the pulse off.
        :type pulse: integer

        """
        if on_ticks < 0:
            raise ValueError('Value for on_ticks must be greater or equaly to zero')
        if on_ticks > off_ticks:
            raise ValueError('Value for on_ticks must be less than or equal to value for off_ticks')
        self._device.write8(ALL_LED_ON_L, on_ticks & 0xFF)
        self._device.write8(ALL_LED_ON_H, on_ticks >> 8)
        self._device.write8(ALL_LED_OFF_L, off_ticks & 0xFF)
        self._device.write8(ALL_LED_OFF_H, off_ticks >> 8)
