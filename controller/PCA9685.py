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
"""
    This library drive GPIO interaction with the Adafruit Servo HAT and provides
    some high level functions to interact with servos on the HAT
"""
import logging
import time
import math
from .servo import Servo

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

class PCA9685(object):
    """PCA9685 PWM LED/servo controller."""

    def __init__(self, address=PCA9685_ADDRESS, i2c=None, frequency=25000000, resolution=4096, servo_frequency=50, **kwargs):
        """__init__

        Initialize the PCA9685.

        :param address: The hardware address of the board. Generally 0x40 unless there is more than one board. 
        :type address: integer

        :param i2c: I2C driver object. Generally should be None to self obtain.  
        :type i2c: Adafruit_GPIO.I2C

        :param frequency: The boards oscillating frequency. Will be around 25MHz, but will slightly vary by board. 
        :type frequency: integer

        :param resolution: The pulse interval resolution. It is 12 bit. You should not have to change that. 
        :type resolution: integer

        :param servo_frequency: The pulse frequency for the attached servos. All servos on the board share the same frequency.
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

    def add_servo(self, channel: int,  
                  min_pulse:float=0.7, max_pulse:float=2.1, neutral_pulse:float=1.4,
                  min_angle:float=-90.0, max_angle:float=90.0, neutral_angle:float=0.0):
        """add_servo
        Adds a servo definition for a given channel.
        :param channel: The channel on which the servo is operating.
        :type channel: integer

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

        pulse_resolution:   the pulse resolution. This will generally be 4096, but can be
                                    adjusted for each servo to achieve the desired width. Use
                                    a scope on the controller to verify that the actual pulse
                                    length corresponds to the requested pulse length and tweak this
                                    parameter until it does.
        """
        if channel < 0 or channel > 15:
            raise ValueError('Channel must be between 0 and 15')

        self.servos[channel] = Servo(self, channel, self._servo_frequency, min_pulse, max_pulse, neutral_pulse,
                                     min_angle, max_angle, neutral_angle,
                                     self._resolution)

    def get_servo_state(self, channel:int) -> (float, float, float):
        """get_servo_state
        Gets the servo state on channel (ticks, pulse and angle).
        
        :param: channel: The channel for which to obtain the servo state. Between 0 and 15. 
        :type channel: integer

        :rtype (float, float, float) - A tuple containing ticks, pulse and angle, in that order. 

        """
        if channel < 0 or channel > 15:
            raise ValueError('Channel must be between 0 and 15')

        servo = self._servos[channel]
        if servo is None:
            raise Exception('There is no servo registered on channel %d' % channel)
        else:
            return servo.get_state()       

    def set_servo_pulse(self, channel:int, pulse:float):
        """set_servo_pulse
        Sets the servo on channel to a certain pulse width.
        
        :param: channel: The channel for which to obtain the servo state. Between 0 and 15. 
        :type channel: integer

        :param: pulse: The pulse length to set. 
        :type pulse: float

        """
        if channel < 0 or channel > 15:
            raise ValueError('Channel must be between 0 and 15')

        servo = self._servos[channel]
        if servo is None:
            raise Exception('There is no servo registered on channel %d' % channel)
        else:
            servo.set_pulse(pulse)

    def set_servo_angle(self, channel:int, angle:float):
        """set_servo_angle
        Sets the servo on channel to a certain angle.

        :param: channel: The channel for which to obtain the servo state. Between 0 and 15. 
        :type channel: integer

        :param: angle: The angle to set. The finest resolution is about 0.5 degrees.
        :type pulse: angle

        """
        if channel < 0 or channel > 15:
            raise ValueError('Channel must be between 0 and 15')

        servo = self._servos[channel]
        if servo is None:
            raise Exception('There is no servo registered on channel %d' % channel)
        else:
            servo.set_angle(angle)

    def set_pwm_freq(self, servo_frequency:int):
        """set_pwm_freq
            Set the PWM frequency to the provided value in hertz.

            :param servo_frequency: The frequency of the servo pulse. 
            :type servo_frequency: integer
        
        """
        prescaleval = self._frequency
        prescaleval /= self._resolution
        prescaleval /= float(servo_frequency)
        prescaleval -= 1.0
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

    def set_pwm(self, channel:int, on_ticks:int, off_ticks:int):
        """set_pwm
        Sets a single PWM channel pulse.
        
        :param: channel: The channel for which to obtain the servo state. Between 0 and 15. 
        :type channel: integer

        :param: on_ticks: Number of ticks into a period at which to switch the pulse on.
        :type pulse: integer

        :param: off_ticks: Number of ticks into a period at which to switch the pulse off.
        :type pulse: integer     

        """
        if channel < 0 or channel > 15:
            raise ValueError('Channel must be between 0 and 15')
        if on_ticks < 0:
            raise ValueError('Value for on_ticks must be greater or equaly to zero')    
        if on_ticks <= off_ticks:
            raise ValueError('Value for on_ticks must be less than value for off_ticks')

        self._device.write8(LED0_ON_L+4*channel, on_ticks & 0xFF)
        self._device.write8(LED0_ON_H+4*channel, on_ticks >> 8)
        self._device.write8(LED0_OFF_L+4*channel, off_ticks & 0xFF)
        self._device.write8(LED0_OFF_H+4*channel, off_ticks >> 8)

    def set_all_pwm(self, on_ticks:int, off_ticks:int):
        """set_pwm
        Sets all PWM channel pulse.

        :param: on_ticks: Number of ticks into a period at which to switch the pulse on.
        :type pulse: integer

        :param: off_ticks: Number of ticks into a period at which to switch the pulse off.
        :type pulse: integer     

        """
        if on_ticks < 0:
            raise ValueError('Value for on_ticks must be greater or equaly to zero')    
        if on_ticks <= off_ticks:
            raise ValueError('Value for on_ticks must be less than value for off_ticks')
        self._device.write8(ALL_LED_ON_L, on_ticks & 0xFF)
        self._device.write8(ALL_LED_ON_H, on_ticks >> 8)
        self._device.write8(ALL_LED_OFF_L, off_ticks & 0xFF)
        self._device.write8(ALL_LED_OFF_H, off_ticks >> 8)

