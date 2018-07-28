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
"""Module allowing control of a meArm using the RPI"""
import time
import logging

from controller import PCA9685, Servo
from kinematics import Kinematics, Point

class me_arm(object):
    """Control meArm"""

    # servo defaults
    servo_min_pulse = 0.6           # default servo min pulse (tuned for SG90S from Mizui)
    servo_max_pulse = 2.3           # default servo max pulse (tuned for SG90S from Mizui)
    servo_neutral_pulse = 1.4       # default servo neutral pulse (tuned for SG90S from Mizui)
    servo_min_angle = -85.0         # default servo min angle (tuned for SG90S from Mizui)
    servo_max_angle = 85.0          # default servo max angle (tuned for SG90S from Mizui)
    servo_neutral_angle = -0.0      # default servo neutral angle (tuned for SG90S from Mizui)

    # arm neutrals and boundaries
    elbow_neutral_angle = 0.0       # servo angle for elbow neutral position
    shoulder_neutral_angle = 40.0   # servo angle for shoulder neutral position
    hip_neutral_angle = 0.0         # servo angle for hip neutral position

    elbow_max_angle = 84.5          # servo angle for elbow max position
    shoulder_max_angle = 65.0       # servo angle for shoulder max position
    hip_max_angle = 84.5            # servo angle for hip max position

    elbow_min_angle = -25.0         # servo angle for elbow min position
    shoulder_min_angle = -15.0      # servo angle for shoulder min position
    hip_min_angle = -84.5           # servo angle for hip min position

    gripper_closed_angle = 27.5     # servo angle for closed gripper
    gripper_open_angle = -20.0      # servo angle for open gripper
    _inc = 0.5                       # servo movement increment in degrees

    _instances = {}

    def __init__(self, 
            controller: PCA9685,
            hip_channel: int = 15,
            elbow_channel: int = 12,
            shoulder_channel: int = 13,
            gripper_channel: int = 14,
            initialize: bool = True):
        """__init__
        Default initialization of arm. Avoid using this and instead create a meArm using the meArm.createWithParameters
        method, which ensures that a meArm is not registered twice.
        
        :param controller: The controller to which the arm is attached. 
        :type controller: PCA9685

        :param hip_channel: The channel for the hip servo.
        :type hip_channel: int

        :param elbow_channel: The channel for the elbow servo.
        :type elbow_channel: int

        :param shoulder_channel: The channel for the shoulder servo.
        :type shoulder_channel: int

        :param gripper_channel: The channel for the gripper servo.
        :type gripper_channel: int

        :param initialize: True to immidiately run the servo initialization, false to adjuist values after construction.
        :type initialize: bool      

        """
        self._logger = logging.getLogger(__name__)

        if hip_channel < 0 or hip_channel > 15 or \
           elbow_channel < 0 or elbow_channel > 15 or \
           shoulder_channel < 0 or shoulder_channel > 15 or \
           gripper_channel < 0 or gripper_channel > 15:
            msg = "Servo channel values must be between 0 and 15"
            self._logger.error(msg)
            raise ValueError(msg)            

        if controller is None:
            msg = "You must supply a valid controller object to create a meArm"
            self._logger.error(msg)
            raise Exception(msg)

        self._servo_tag = str(hip_channel).zfill(2) + str(elbow_channel).zfill(2) + str(shoulder_channel).zfill(2) + str(gripper_channel).zfill(2)
        self._id = str(controller.add_servo) + self._servo_tag

        if self._id in me_arm._instances:
            msg = "meArm Instance already exists. Cannot create a new instance. Release the existing \
                instance by calling me_arm.delete()"
            self._logger.error(msg)
            raise Exception(msg)
        
        self._controller = controller
        self._kinematics = Kinematics()

        self._hip_channel = hip_channel
        self._elbow_channel = elbow_channel
        self._shoulder_channel = shoulder_channel
        self._gripper_channel = gripper_channel
        self.__setup_defaults()

        if initialize: self.initialize()
        me_arm._instances[self._id] = self
    
    def __setup_defaults(self):
        """__setup_defaults
        Setup defaults for the servos based on static defaults.
        """
        # defaults for hip servo
        self._hip_min_pulse = me_arm.servo_min_pulse
        self._hip_max_pulse = me_arm.servo_max_pulse
        self._hip_neutral_pulse = me_arm.servo_neutral_pulse
        self._hip_min_angle = me_arm.servo_min_angle
        self._hip_max_angle = me_arm.servo_max_angle
        self._hip_neutral_angle = me_arm.servo_neutral_angle

        # defaults for shoulder servo
        self._shoulder_min_pulse = me_arm.servo_min_pulse
        self._shoulder_max_pulse = me_arm.servo_max_pulse
        self._shoulder_neutral_pulse = me_arm.servo_neutral_pulse
        self._shoulder_min_angle = me_arm.servo_min_angle
        self._shoulder_max_angle = me_arm.servo_max_angle
        self._shoulder_neutral_angle = me_arm.servo_neutral_angle

        # defaults for elbow servo
        self._elbow_min_pulse = me_arm.servo_min_pulse
        self._elbow_max_pulse = me_arm.servo_max_pulse
        self._elbow_neutral_pulse = me_arm.servo_neutral_pulse
        self._elbow_min_angle = me_arm.servo_min_angle
        self._elbow_max_angle = me_arm.servo_max_angle
        self._elbow_neutral_angle = me_arm.servo_neutral_angle

        # defaults for gripper servo
        self._gripper_min_pulse = me_arm.servo_min_pulse
        self._gripper_max_pulse = me_arm.servo_max_pulse
        self._gripper_neutral_pulse = me_arm.servo_neutral_pulse
        self._gripper_min_angle = me_arm.servo_min_angle
        self._gripper_max_angle = me_arm.servo_max_angle
        self._gripper_neutral_angle = me_arm.servo_neutral_angle

        #current angles
        self._elbow_angle = me_arm.elbow_neutral_angle
        self._shoulder_angle = me_arm.shoulder_neutral_angle
        self._hip_angle = me_arm.hip_neutral_angle
        x, y, z = self._kinematics.toCartesian(self._hip_angle, self._shoulder_angle, self._elbow_angle)
        self._position = Point.fromCartesian(x, y, z)        

    @classmethod
    def createWithServoParameters(cls, controller: PCA9685,
            hip_channel: int, elbow_channel: int, shoulder_channel: int, gripper_channel: int):
        """createWithServoParameters
        Creates a meArm using parameters.

        :param controller: The controller to which the arm is attached. 
        :type controller: PCA9685
                
        :param hip_channel: The channel for the hip servo.
        :type hip_channel: int

        :param elbow_channel: The channel for the elbow servo.
        :type elbow_channel: int

        :param shoulder_channel: The channel for the shoulder servo.
        :type shoulder_channel: int

        :param gripper_channel: The channel for the gripper servo.
        :type gripper_channel: int

        :return: A meArm instance.
        :rtype: meArm
        """

        servo_tag = str(hip_channel).zfill(2) + str(elbow_channel).zfill(2) + str(shoulder_channel).zfill(2) + str(gripper_channel).zfill(2)
        id = str(controller.address) + servo_tag

        if id in me_arm._instances: 
            return me_arm._instances[id]

        obj = cls(controller, hip_channel, elbow_channel, shoulder_channel, gripper_channel, False)

        #override defaults for servos
        obj.initialize()
        me_arm._instances[id] = obj
        return obj

    @classmethod
    def delete_all(cls):
        """delete_all
        Deletes all meArms currently registered
        """
        arm: cls = None
        id: str = ""
        for id, arm in me_arm._instances.items():
            arm.delete()
            del me_arm._instances[id]

    @classmethod
    def get(cls, id: str):
        """get
        Gets the meArm with specified id. 

        :param id: The meArm id.
        :type id: str

        :return: meArm
        :rtype: me_arm
        """
        if id in me_arm._instances:
            return me_arm._instances[id]
        raise KeyError("No meArm with id %s", id)

    @classmethod
    def get_names(cls) -> [str]:
        """get_names
        Gets a list of registered meArms.

        :return: A list of meArm names (ids)
        :rtype: [str]
        """
        return cls._instances.keys()

    @property
    def position(self) -> Point:
        """Gets the current position of the gripper

        :return: The current gripper position
        :rtype: Point
        """
        return self.position

    def delete(self):
        """delete

        Deletes the meArm
        """
        self.reset()
        del me_arm._instances[self._id]


    def close(self):
        """close
        Close the gripper, grabbing onto anything that might be there
        """
        self._controller.set_servo_angle(self._gripper_channel, me_arm.gripper_closed_angle)
        time.sleep(0.3)

    def is_reachable(self, point: Point) -> (bool, float, float, float):
        """is_reachable

        Returns True if the point is (theoretically) reachable by the gripper and the associated 
        servo angles

        :param point: The point to evaluate
        :type point: Point

        :return: A tuple indicating whether the point is reachable and the associated hip, shoulder and elbow angles
        :rtype: (bool, float, float, float)
        
        """
        hip, shoulder, elbow = self._kinematics.fromCartesian(point.x, point.y, point.z)
        isReachable = True
        if hip < me_arm.hip_min_angle or hip > me_arm.hip_max_angle: isReachable = False
        if shoulder < me_arm.shoulder_min_angle or shoulder > me_arm.shoulder_max_angle: isReachable = False
        if elbow < me_arm.elbow_min_angle or elbow > me_arm.elbow_max_angle: isReachable = False
        return isReachable, hip, shoulder, elbow

    def go_directly_to_point(self, target: Point):
        """go_directly_to_point
        
        Set servo angles so as to place the gripper at a given Cartesian point as quickly as possible, 
        without caring what path it takes to get there
        
        :param target: The target point of the operation
        :type target: Point
        """

        is_reachable, hip, shoulder, elbow = self.is_reachable(target)
        if not is_reachable:
            msg = "Point x: %f, y: %f, x: %f is not reachable" % (target.x, target.y, target.z)
            self._logger.error(msg)
            raise Exception(msg)       

        self._controller.set_servo_angle(self._hip_channel, hip)
        self._controller.set_servo_angle(self._shoulder_channel, shoulder)
        self._controller.set_servo_angle(self._elbow_channel, elbow)
        self.position = target
        self._hip_angle = hip
        self._shoulder_angle = shoulder
        self._elbow_angle = elbow
        self._logger("Goto point x: %d, y: %d, z: %d", target.x, target.y, target.z)

    def go_to_point(self, target: Point, resolution: int = 10) -> int:
        """go_to_point
        
        Travel in a straight line from current position to a requested position
        
        :param target: The target point of the operation
        :type target: Point

        :param resolution: The increment for each movement along the path.
        :type resolution: int

        :return: The number of movements executed
        :rtype: int       
        """
        if not self.is_reachable(target)[0]:
            raise Exception("Point x: %f, y: %f, x: %f is not reachable" % (target.x, target.y, target.z))
        
        dist = self.position.distance(target)
        i = 0
        c = 1
        while i < dist:
            p = Point.fromCartesian(
                self.position.x + (target.x - self.position.x) * i / dist, 
                self.position.y + (target.y - self.position.y) * i / dist, 
                self.position.z + (target.z - self.position.z) * i / dist)
            self.go_directly_to_point(p)
            time.sleep(0.05)
            i += resolution
            c += 1
        self.go_directly_to_point(target)
        time.sleep(0.05)
        return c

    def initialize(self):
        """Registers the servo."""
        self._controller.add_servo(self._hip_channel, 
            self._hip_min_pulse, self._hip_max_pulse, self._hip_neutral_pulse,
            self._hip_min_angle, self._hip_max_angle, self._hip_neutral_angle)
        self._controller.add_servo(self._shoulder_channel, 
            self._shoulder_min_pulse, self._shoulder_max_pulse, self._shoulder_neutral_pulse,
            self._shoulder_min_angle, self._shoulder_max_angle, self._shoulder_neutral_angle)
        self._controller.add_servo(self._elbow_channel, 
            self._elbow_min_pulse, self._elbow_max_pulse, self._elbow_neutral_pulse,
            self._elbow_min_angle, self._elbow_max_angle, self._elbow_neutral_angle)
        self._controller.add_servo(self._gripper_channel, 
            self._gripper_min_pulse, self._gripper_max_pulse, self._gripper_neutral_pulse,
            self._gripper_min_angle, self._gripper_max_angle, self._gripper_neutral_angle)

    def open(self):
        """open
        
        Opens the gripper, dropping whatever is being carried
        """
        self._controller.set_servo_angle(self._gripper_channel, me_arm.gripper_open_angle)
        time.sleep(0.3)

    def reset(self):
        """shutdown
        Resets the arm at neutral position"""
        self._logger.info('Resetting arm ...')
        self._controller.set_servo_angle(self._hip_channel, me_arm.hip_neutral_angle)
        self._controller.set_servo_angle(self._shoulder_channel, me_arm.shoulder_neutral_angle)
        self._controller.set_servo_angle(self._elbow_channel, me_arm.elbow_neutral_angle)
        self._controller.set_servo_angle(self._gripper_channel, me_arm.gripper_open_angle)
        time.sleep(0.3)

    def test(self):
        """Simple loop to test the arm"""
        self._logger.info('Press Ctrl-C to quit...')
        self._controller.set_servo_angle(self._hip_channel, self._hip_angle)
        self._controller.set_servo_angle(self._shoulder_channel, self._shoulder_angle)
        self._controller.set_servo_angle(self._elbow_channel, self._elbow_angle)
        self.close()
        while True:     
            while self._elbow_angle < me_arm.elbow_max_angle:
                self._controller.set_servo_angle(self._elbow_channel, self._elbow_angle)
                self._elbow_angle += me_arm._inc

            while self._shoulder_angle > me_arm.shoulder_min_angle:
                self._controller.set_servo_angle(self._shoulder_channel, self._shoulder_angle)
                self._shoulder_angle -= me_arm._inc

            self.close()

            while self._hip_angle > me_arm.hip_min_angle:
                self._controller.set_servo_angle(self._hip_channel, self._hip_angle)
                self._hip_angle -= me_arm._inc

            while self._shoulder_angle < me_arm.shoulder_max_angle:
                self._controller.set_servo_angle(self._shoulder_channel, self._shoulder_angle)
                self._shoulder_angle += me_arm._inc

            while self._elbow_angle > me_arm.elbow_min_angle:
                self._controller.set_servo_angle(self._elbow_channel, self._elbow_angle)
                self._elbow_angle -= me_arm._inc

            while self._hip_angle < me_arm.hip_max_angle:
                self._controller.set_servo_angle(self._hip_channel, self._hip_angle)
                self._hip_angle += me_arm._inc

            self.open()

            while self._hip_angle > me_arm.hip_neutral_angle:
                self._controller.set_servo_angle(self._hip_channel, self._hip_angle)
                self._hip_angle -= me_arm._inc
