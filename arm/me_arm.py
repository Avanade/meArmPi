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
import json
from jsonschema import validate, RefResolver, Draft4Validator, ValidationError, SchemaError
from controller import PCA9685, Servo, ServoAttributes, MiuzeiSG90Attributes, ES08MAIIAttributes, CustomServoAttributes, software_reset
from kinematics import Kinematics, Point
from .arm_servo import me_armServo
from .arm_kinematics import me_armKinematics
from .schemas import me_arm_schema, schema_store

class me_arm(object):
    """Control meArm"""

    # arm neutrals and boundaries
    hip_neutral_angle = 0.0         # servo angle for hip neutral position
    hip_max_angle = 84.5            # servo angle for hip max position
    hip_min_angle = -84.5           # servo angle for hip min position
    hip_trim = 0.0

    shoulder_neutral_angle = 40.0   # servo angle for shoulder neutral position
    shoulder_max_angle = 65.0       # servo angle for shoulder max position
    shoulder_min_angle = -15.0      # servo angle for shoulder min position
    shoulder_trim = 5.0

    elbow_neutral_angle = -0.0       # servo angle for elbow neutral position
    elbow_max_angle = 84.5          # servo angle for elbow max position
    elbow_min_angle = -25.0         # servo angle for elbow min position
    elbow_trim = -45.0

    gripper_closed_angle = 27.5     # servo angle for closed gripper
    gripper_open_angle = -20.0      # servo angle for open gripper
    gripper_trim = 0.0
    _inc = 0.5                      # servo movement increment in degrees

    _instances = {}
    _controllers: [int] = []

    def __init__(self, 
            controller: PCA9685,
            hip_channel: int = 15,
            elbow_channel: int = 12,
            shoulder_channel: int = 13,
            gripper_channel: int = 14,
            initialize: bool = True,
            logging_level: str = 'INFO'):
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

        :param logging_level: The logging level to use for this arm. 
        :type logging_level: string
        """
        self._servo_tag: str = str(hip_channel).zfill(2) + str(elbow_channel).zfill(2) + str(shoulder_channel).zfill(2) + str(gripper_channel).zfill(2)
        self._id: str = str(controller.address).zfill(6) + self._servo_tag
        self._logger = logging.getLogger("%s.%s" % (__name__, self._id))
        self._logger.setLevel(logging_level)

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

        if self._id in me_arm._instances:
            msg = "meArm Instance already exists. Cannot create a new instance. Release the existing \
                instance by calling me_arm.delete()"
            self._logger.error(msg)
            raise Exception(msg)
        
        self._controller = controller
        self._kinematics = Kinematics()
        self._turnedOff = False

        self.__setup_defaults(hip_channel, elbow_channel, shoulder_channel, gripper_channel)

        if initialize: self.initialize()
        me_arm._instances[self._id] = self
        if controller.address not in me_arm._controllers: me_arm._controllers.append(controller.address)
        self._logger.info("meArm with id %s created", self._id)
    
    def __setup_defaults(self, hip_channel: int, elbow_channel: int, shoulder_channel: int, gripper_channel: int):
        """__setup_defaults
        Setup defaults for the servos based on static defaults.
        
        :param hip_channel: The channel for the hip servo.
        :type hip_channel: int

        :param elbow_channel: The channel for the elbow servo.
        :type elbow_channel: int

        :param shoulder_channel: The channel for the shoulder servo.
        :type shoulder_channel: int

        :param gripper_channel: The channel for the gripper servo.
        :type gripper_channel: int
        """
        # defaults for servos
        self._hip_servo = me_armServo(hip_channel, MiuzeiSG90Attributes(), 
                                me_arm.hip_neutral_angle, me_arm.hip_min_angle, me_arm.hip_max_angle, me_arm.hip_trim)
        self._shoulder_servo = me_armServo(shoulder_channel, MiuzeiSG90Attributes(), 
                                me_arm.shoulder_neutral_angle, me_arm.shoulder_min_angle, me_arm.shoulder_max_angle, me_arm.shoulder_trim)
        self._elbow_servo = me_armServo(elbow_channel, MiuzeiSG90Attributes(), 
                                me_arm.elbow_neutral_angle, me_arm.elbow_min_angle, me_arm.elbow_max_angle, me_arm.elbow_trim)
        self._gripper_servo = me_armServo(gripper_channel, MiuzeiSG90Attributes(), 
                                0, me_arm.gripper_open_angle, me_arm.gripper_closed_angle, me_arm.gripper_trim)     
        self._position = Point.fromCartesian(0, 0, 0)

    @classmethod
    def boot_from_json_file(cls, json_file:str):
        """boot_from_json_file
        Generates a meArm environment from json file
        :param json_file: name of the file containing the json data. Must adhere to me_arm.meArmSchema
        :type json_file: str
        """
        with open(json_file) as file:
            data = json.load(file)
            resolver = RefResolver('', me_arm_schema, schema_store)
            validator = Draft4Validator(me_arm_schema, [], resolver)
            validator.check_schema(me_arm_schema)
            #if not validator.is_valid(data):
            #    raise ValidationError('Could not validate meArm json. Check your json file', instance = 1)
        return cls.boot_from_dict(data)

    @classmethod
    def boot_from_json(cls, json_string:str):
        """boot_from_json
        Generates a meArm environment from json data
        :param json_string: String containing the json data. Must adhere to me_arm.meArmSchema
        :type json_string: str
        """
        data = json.loads(json_string)
        resolver = RefResolver('', me_arm_schema, schema_store)
        validator = Draft4Validator(me_arm_schema, [], resolver)
        validator.check_schema(me_arm_schema)
        #if not validator.is_valid(data):
        #    raise ValidationError('Could not validate meArm json. Check your json file', instance = 1)
        return cls.boot_from_dict(data)

    @classmethod
    def boot_from_dict(cls, data:{}):
        """boot_from_dict
        Generates a meArm environment from dictionary
        :param data: The dictionary containing the servo data. Must adhere to me_arm.meArmSchema
        :type data: dictionary
        """
        for c in data:
            controller = PCA9685.from_dict(c['controller'])
            for a in c['arms']:
                level = "INFO"
                s = a['servos']
                tag = str(s['hip']['channel']).zfill(2) + str(s['elbow']['channel']).zfill(2) + str(s['shoulder']['channel']).zfill(2) + str(s['gripper']['channel']).zfill(2)
                id = str(controller.address).zfill(6) + tag

                if id in me_arm._instances: continue
                if a['logging_level'] is not None: level = a['logging_level']
                obj = cls(controller, s['hip']['channel'], s['elbow']['channel'], s['shoulder']['channel'], s['gripper']['channel'], False, level)
                obj._hip_servo = me_armServo.from_dict(s['hip'])
                obj._shoulder_servo = me_armServo.from_dict(s['shoulder']) 
                obj._elbow_servo = me_armServo.from_dict(s['elbow']) 
                obj._gripper_servo = me_armServo.from_dict(s['gripper'])
                obj._arm_kinematics = me_armKinematics.from_dict(a['kinematics'])
                obj._kinematics = Kinematics(False, obj._arm_kinematics.humerus, obj._arm_kinematics.radius, obj._arm_kinematics.clavicle + obj._arm_kinematics.phalanx)
                obj._inc = a['angle-increment']
                obj.initialize()
                cls._instances[id] = obj
        return cls._instances

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
        id = str(controller.address).zfill(6) + servo_tag

        if id in me_arm._instances: 
            return me_arm._instances[id]

        obj = cls(controller, hip_channel, elbow_channel, shoulder_channel, gripper_channel, False)

        #override defaults for servos
        obj.initialize()
        cls._instances[id] = obj
        return obj

    @classmethod
    def shutdown(cls, clear:bool = False):
        """shutdown
        Deletes all meArms currently registered and shutsdown environment
        :param clear:   True to remove all arm registrations. Will require complete re-initialization
                        of the infrastructure to operate the arms again. 
        :type clear:    bool
        """
        arm: cls = None
        for key  in me_arm._instances:
            arm = me_arm._instances[key]
            arm.reset()
            arm.turn_off()
        if clear: 
            cls._instances.clear()
            software_reset()

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

    @classmethod
    def get_controllers(cls) -> [int]:
        """get_controllers
        Gets a list of registered controller addresses

        :return: A list of meArm controller addresses
        :rtype: [int]
        """
        return cls._controllers.copy()

    @property
    def controller(self) -> int:
        """Gets the controller address for the arm

        :return: The address of the controller
        :rtype: int
        """
        return self._controller.address

    @property
    def name(self) -> str:
        """Gets the name for the arm

        :return: The name of the arm
        :rtype: str
        """
        return self._id

    @property
    def position(self) -> Point:
        """Gets the current position of the gripper

        :return: The current gripper position
        :rtype: Point
        """
        return self._position

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
        self._controller.set_servo_angle(self._gripper_servo.channel, self._gripper_servo.max - self._gripper_servo.trim)
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
        if hip - self._hip_servo.trim < self._hip_servo.min or hip - self._hip_servo.trim > self._hip_servo.max: isReachable = False
        if shoulder - self._shoulder_servo.trim < self._shoulder_servo.min or shoulder - self._shoulder_servo.trim > self._shoulder_servo.max: isReachable = False
        if elbow - self._elbow_servo.trim < self._elbow_servo.min or elbow - self._elbow_servo.trim > self._elbow_servo.max: isReachable = False
        return isReachable, hip, shoulder, elbow

    def go_directly_to_point(self, target: Point, raiseOutOfBoundsException: bool = True) -> bool:
        """go_directly_to_point
        
        Set servo angles so as to place the gripper at a given Cartesian point as quickly as possible, 
        without caring what path it takes to get there
        
        :param target: The target point of the operation
        :type target: Point
        :param raiseOutOfBoundsException: True to raise an outOfBoundsException if target is not reachable.
        :type raiseOutOfBoundsException: bool

        :return: True if the operation was executed. False otherwise. False will be returned if the 
                 target is considered unreachable by the arm.
        :rtype: bool
        """
        is_reachable, hip, shoulder, elbow = self.is_reachable(target)
        if not is_reachable:
            msg = "Point (%f, %f, %f) is not reachable" % (target.x, target.y, target.z)
            self._logger.error(msg)
            if raiseOutOfBoundsException: raise Exception(msg)
            return False       

        self._controller.set_servo_angle(self._hip_servo.channel, hip - self._hip_servo.trim )
        self._controller.set_servo_angle(self._shoulder_servo.channel, shoulder - self._shoulder_servo.trim)
        self._controller.set_servo_angle(self._elbow_servo.channel, elbow - self._elbow_servo.trim)
        self._position = target
        self._hip_angle = hip
        self._shoulder_angle = shoulder
        self._elbow_angle = elbow
        self._logger.info("Goto point (%f,%f, %f) -> (%f, %f, %f)",
            target.x, target.y, target.z,
            hip - self._hip_servo.trim , shoulder - self._shoulder_servo.trim, elbow - self._elbow_servo.trim)
        return True

    def go_to_point(self, target: Point, resolution: float = 10, raiseOutOfBoundsException: bool = True) -> int:
        """go_to_point
        
        Travel in a straight line from current position to a requested position
        
        :param target: The target point of the operation
        :type target: Point
        :param resolution: The increment for each movement along the path.
        :type resolution: int
        :param raiseOutOfBoundsException: True to raise an outOfBoundsException if target is not reachable.
        :type raiseOutOfBoundsException: bool

        :return: The number of movements executed
        :rtype: int       
        """
        dist = self._position.distance(target)
        p = self._position
        cycles = dist/resolution
        if dist == 0 or cycles == 0: 
            return 0

        dx = (target.x - p.x) / cycles
        dy = (target.y - p.y) / cycles
        dz = (target.z - p.z) / cycles
        i = 1
        c = 1
        while i < cycles:
            p1 = Point.fromCartesian(p.x + dx, p.y + dy, p.z + dz)
            if self.go_directly_to_point(p1, raiseOutOfBoundsException): c += 1
            i += 1
            p = p1
        self.go_directly_to_point(target, raiseOutOfBoundsException)
        return c

    def initialize(self):
        """Registers the servo.""" 
        self._controller.add_servo(self._hip_servo.channel, self._hip_servo.attributes)
        self._controller.add_servo(self._shoulder_servo.channel, self._shoulder_servo.attributes)
        self._controller.add_servo(self._elbow_servo.channel, self._elbow_servo.attributes)
        self._controller.add_servo(self._gripper_servo.channel, self._gripper_servo.attributes)
        self.reset()
        self.turn_off()
        self._logger.info("meArm with id %s initialized,", self._id)

    def open(self):
        """open
        
        Opens the gripper, dropping whatever is being carried
        """
        self._controller.set_servo_angle(self._gripper_servo.channel, self._gripper_servo.min - self._gripper_servo.trim)
        time.sleep(0.3)

    def reset(self):
        """reset
        Resets the arm at neutral position"""
        self._logger.info('Resetting arm %s...', self._id)
        
        # set neutral angles
        elbow = self._elbow_servo.neutral + self._elbow_servo.trim
        shoulder = self._shoulder_servo.neutral + self._shoulder_servo.trim
        hip = self._hip_servo.neutral + self._hip_servo.trim
        x, y, z = self._kinematics.toCartesian(hip, shoulder, elbow)
        self.go_to_point(Point.fromCartesian(x, y, z), 2.5, False)        
        self._logger.info("(%f, %f, %f) -> (%f, %f, %f", 
                          self._hip_servo.neutral, self._shoulder_servo.neutral, self._elbow_servo.neutral,
                          self._position.x, self._position.y, self._position.z)
        time.sleep(0.3)

    def turn_off(self):
        """turn_off
        Turns all servos of the arm to full off
        """
        if not self._turnedOff:
            self._controller.set_off(self._hip_servo.channel, True)
            self._controller.set_off(self._shoulder_servo.channel, True)
            self._controller.set_off(self._elbow_servo.channel, True)
            self._controller.set_off(self._gripper_servo.channel, True)
            self._turnedOff = True

    def turn_on(self):
        """turn_on
        Turns all servos of the arm to pwm
        """
        if self._turnedOff:
            self._controller.set_off(self._hip_servo.channel, False)
            self._controller.set_off(self._shoulder_servo.channel, False)
            self._controller.set_off(self._elbow_servo.channel, False)
            self._controller.set_off(self._gripper_servo.channel, False)
            self._turnedOff = False

    def test(self, repeat: bool = False) -> int:
        """Simple loop to test the arm
        
        :param repeat: If True repeat the test routine until interupted.
        :type repeat: bool

        :return: Number of operations executed
        :rtype: int
        """
        if repeat: self._logger.info('Press Ctrl-C to quit...')
        self._controller.set_servo_angle(self._hip_servo.channel, self._hip_angle - self._hip_servo.trim)
        self._controller.set_servo_angle(self._shoulder_servo.channel, self._shoulder_angle - self._shoulder_servo.trim)
        self._controller.set_servo_angle(self._elbow_servo.channel, self._elbow_angle - self._elbow_servo.trim)
        self.close()
        ops = 0
        keep_going = True
        while keep_going:     
            while self._elbow_angle - self._elbow_servo.trim < self._elbow_servo.max:
                self._controller.set_servo_angle(self._elbow_servo.channel, self._elbow_angle - self._elbow_servo.trim)
                self._elbow_angle += me_arm._inc
                ops += 1

            while self._shoulder_angle - self._shoulder_servo.trim > self._shoulder_servo.min:
                self._controller.set_servo_angle(self._shoulder_servo.channel, self._shoulder_angle - self._shoulder_servo.trim)
                self._shoulder_angle -= me_arm._inc
                ops += 1

            self.close()
            ops += 1

            while self._hip_angle - self._hip_servo.trim > self._hip_servo.min:
                self._controller.set_servo_angle(self._hip_servo.channel, self._hip_angle - self._hip_servo.trim)
                self._hip_angle -= me_arm._inc
                ops += 1

            while self._shoulder_angle - self._shoulder_servo.trim < self._shoulder_servo.max:
                self._controller.set_servo_angle(self._shoulder_servo.channel, self._shoulder_angle - self._shoulder_servo.trim)
                self._shoulder_angle += me_arm._inc
                ops += 1

            while self._elbow_angle - self._elbow_servo.trim > self._elbow_servo.min:
                self._controller.set_servo_angle(self._elbow_servo.channel, self._elbow_angle - self._elbow_servo.trim)
                self._elbow_angle -= me_arm._inc
                ops += 1

            while (self._hip_angle - self._hip_servo.trim) < self._hip_servo.max:
                self._controller.set_servo_angle(self._hip_servo.channel, self._hip_angle - self._hip_servo.trim)
                self._hip_angle += me_arm._inc
                ops += 1

            self.open()
            ops += 1
            
            while self._hip_angle - self._hip_servo.trim > self._hip_servo.neutral:
                self._controller.set_servo_angle(self._hip_servo.channel, self._hip_angle - self._hip_servo.trim)
                self._hip_angle -= me_arm._inc
                ops += 1
            
            if not repeat: keep_going = False
        
        return ops
