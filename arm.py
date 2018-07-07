# pylint: disable=C0103
"""Simple test program for servo actuation"""
import time
import logging
import servo
import kinematics
import atexit

# Uncomment to enable debug output.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class me_arm(object):
    """Control meArm"""

    # servo defaults
    servo_frequency = 50            # default servo frequency
    servo_min_pulse = 0.6           # default servo min pulse (tuned for SG90S from Mizui)
    servo_max_pulse = 2.3           # default servo max pulse (tuned for SG90S from Mizui)
    servo_neutral_pulse = 1.4       # default servo neutral pulse (tuned for SG90S from Mizui)
    servo_min_angle = -85.0         # default servo min angle (tuned for SG90S from Mizui)
    servo_max_angle = 85.0          # default servo max angle (tuned for SG90S from Mizui)
    servo_neutral_angle = -0.0      # default servo neutral angle (tuned for SG90S from Mizui)
    servo_resolution = 4256         # tuned to generate exact pulse width accounting for calculation rounding error

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
    inc = 0.5                       # servo movement increment in degrees

    Instance = None

    def __init__(self, 
            hip_channel:int=15,
            elbow_channel:int=12,
            shoulder_channel:int=13,
            gripper_channel:int=14,
            initialize:bool=True):
        """Default initialization of arm"""
        if me_arm.Instance is not None:
            msg = "meArm Instance already exists. Cannot create a new instance. Release the existing \
                instance by calling me_arm.Instance.shutdown()"
            logger.error(msg)
            raise Exception(msg)

        self.kinematics:kinematics.Kinematics = kinematics.Kinematics()
        self.logger:logging.Logger = logging.getLogger(__name__)
        self.hip_channel:int = hip_channel
        self.elbow_channel:int = elbow_channel
        self.shoulder_channel:int = shoulder_channel
        self.gripper_channel:int = gripper_channel
        self.__setup_defaults()

        # Initialise the PCA9685 using the default address (0x40).
        self.pwm:servo.PCA9685 = servo.PCA9685(address=0x40)  
            # Alternatively specify a different address and/or bus: servo.PCA9685(address=0x40, busnum=2)
        if initialize: self.initialize()
        me_arm.Instance = self
    
    def __setup_defaults(self):
        """Setup defaults for the servos based on static defaults."""
        self.frequency = me_arm.servo_frequency

        # defaults for hip servo
        self.hip_min_pulse:float = me_arm.servo_min_pulse
        self.hip_max_pulse:float = me_arm.servo_max_pulse
        self.hip_neutral_pulse:float = me_arm.servo_neutral_pulse
        self.hip_min_angle:float = me_arm.servo_min_angle
        self.hip_max_angle:float = me_arm.servo_max_angle
        self.hip_neutral_angle:float = me_arm.servo_neutral_angle
        self.hip_resolution:float = me_arm.servo_resolution

        # defaults for shoulder servo
        self.shoulder_min_pulse:float = me_arm.servo_min_pulse
        self.shoulder_max_pulse:float = me_arm.servo_max_pulse
        self.shoulder_neutral_pulse:float = me_arm.servo_neutral_pulse
        self.shoulder_min_angle:float = me_arm.servo_min_angle
        self.shoulder_max_angle:float = me_arm.servo_max_angle
        self.shoulder_neutral_angle:float = me_arm.servo_neutral_angle
        self.shoulder_resolution:float = me_arm.servo_resolution

        # defaults for elbow servo
        self.elbow_min_pulse:float = me_arm.servo_min_pulse
        self.elbow_max_pulse:float = me_arm.servo_max_pulse
        self.elbow_neutral_pulse:float = me_arm.servo_neutral_pulse
        self.elbow_min_angle:float = me_arm.servo_min_angle
        self.elbow_max_angle:float = me_arm.servo_max_angle
        self.elbow_neutral_angle:float = me_arm.servo_neutral_angle
        self.elbow_resolution:float = me_arm.servo_resolution

        # defaults for gripper servo
        self.gripper_min_pulse:float = me_arm.servo_min_pulse
        self.gripper_max_pulse:float = me_arm.servo_max_pulse
        self.gripper_neutral_pulse:float = me_arm.servo_neutral_pulse
        self.gripper_min_angle:float = me_arm.servo_min_angle
        self.gripper_max_angle:float = me_arm.servo_max_angle
        self.gripper_neutral_angle:float = me_arm.servo_neutral_angle
        self.gripper_resolution:float = me_arm.servo_resolution

        #current angles
        self.elbow_angle:float = me_arm.elbow_neutral_angle
        self.shoulder_angle:float = me_arm.shoulder_neutral_angle
        self.hip_angle:float = me_arm.hip_neutral_angle
        x, y, z = self.kinematics.toCartesian(self.hip_angle, self.shoulder_angle, self.elbow_angle)
        self.position:kinematics.Point = kinematics.Point.fromCartesian(x, y, z)        

    @classmethod
    def createWithServoParameters(cls,
            hip_channel:int, elbow_channel:int, shoulder_channel:int, gripper_channel:int) -> me_arm:
        if me_arm.Instance is not None: return me_arm.Instance

        obj = cls(hip_channel, elbow_channel, shoulder_channel, gripper_channel, False)

        #override defaults for servos

        obj.initialize()
        me_arm.Instance = obj
        return obj

    def close(self):
        """Close the gripper, grabbing onto anything that might be there"""
        self.pwm.set_servo_angle(self.gripper_channel, me_arm.gripper_closed_angle)
        time.sleep(0.3)

    def is_reachable(self, point:kinematics.Point) -> (bool, float, float, float):
        """Returns True if the point is (theoretically) reachable by the gripper"""
        hip, shoulder, elbow = self.kinematics.fromCartesian(point.x, point.y, point.z)
        isReachable = True
        if hip < me_arm.hip_min_angle or hip > me_arm.hip_max_angle: isReachable = False
        if shoulder < me_arm.shoulder_min_angle or shoulder > me_arm.shoulder_max_angle: isReachable = False
        if elbow < me_arm.elbow_min_angle or elbow > me_arm.elbow_max_angle: isReachable = False
        return isReachable, hip, shoulder, elbow
    
    def get_position(self) -> kinematics.Point:
        """Returns the current position of the gripper"""
        return self.position

    def go_directly_to_point(self, target:kinematics.Point):
        """Set servo angles so as to place the gripper at a given Cartesian point as quickly as possible, without caring what path it takes to get there"""

        is_reachable, hip, shoulder, elbow = self.is_reachable(target)
        if not is_reachable:
            msg = "Point x: %f, y: %f, x: %f is not reachable" % (target.x, target.y, target.z)
            self.logger.error(msg)
            raise Exception(msg)       

        self.pwm.set_servo_angle(self.hip_channel, hip)
        self.pwm.set_servo_angle(self.shoulder_channel, shoulder)
        self.pwm.set_servo_angle(self.elbow_channel, elbow)
        self.position = target
        self.hip_angle = hip
        self.shoulder_angle = shoulder
        self.elbow_angle = elbow
        self.logger("Goto point x: %d, y: %d, z: %d", target.x, target.y, target.z)

    def go_to_point(self, target:kinematics.Point, resolution:int=10):
        """Travel in a straight line from current position to a requested position"""
        if not self.is_reachable(target)[0]:
            raise Exception("Point x: %f, y: %f, x: %f is not reachable" % (target.x, target.y, target.z))
        
        dist = self.position.distance(target)
        i = 0
        while i < dist:
            p = kinematics.Point.fromCartesian(
                self.position.x + (target.x - self.position.x) * i / dist, 
                self.position.y + (target.y - self.position.y) * i / dist, 
                self.position.z + (target.z - self.position.z) * i / dist)
            self.go_directly_to_point(p)
            time.sleep(0.05)
            i += resolution
        self.go_directly_to_point(target)
        time.sleep(0.05)

    def initialize(self):
        """Registers the servo."""
        self.pwm.add_servo(self.hip_channel, self.frequency, 
            self.hip_min_pulse, self.hip_max_pulse, self.hip_neutral_pulse,
            self.hip_min_angle, self.hip_max_angle, self.hip_neutral_angle,
            self.hip_resolution)
        self.pwm.add_servo(self.shoulder_channel, self.frequency, 
            self.shoulder_min_pulse, self.shoulder_max_pulse, self.shoulder_neutral_pulse,
            self.shoulder_min_angle, self.shoulder_max_angle, self.shoulder_neutral_angle,
            self.shoulder_resolution)
        self.pwm.add_servo(self.elbow_channel, self.frequency, 
            self.elbow_min_pulse, self.elbow_max_pulse, self.elbow_neutral_pulse,
            self.elbow_min_angle, self.elbow_max_angle, self.elbow_neutral_angle,
            self.elbow_resolution)
        self.pwm.add_servo(self.gripper_channel, self.frequency, 
            self.gripper_min_pulse, self.gripper_max_pulse, self.gripper_neutral_pulse,
            self.gripper_min_angle, self.gripper_max_angle, self.gripper_neutral_angle,
            self.gripper_resolution)

    def open(self):
        """Open the gripper, dropping whatever is being carried"""
        self.pwm.set_servo_angle(self.gripper_channel, me_arm.gripper_open_angle)
        time.sleep(0.3)

    def shutdown(self):
        """Resets the arm at neutral position and then resets the controller"""
        self.logger.info('Resetting arm and controller...')
        self.pwm.set_servo_angle(self.hip_channel, me_arm.hip_neutral_angle)
        self.pwm.set_servo_angle(self.shoulder_channel, me_arm.shoulder_neutral_angle)
        self.pwm.set_servo_angle(self.elbow_channel, me_arm.elbow_neutral_angle)
        self.pwm.set_servo_angle(self.gripper_channel, me_arm.gripper_open_angle)
        time.sleep(0.3)
        servo.software_reset()
        me_arm.Instance = None

    def test(self):
        """Simple loop to test the arm"""
        self.logger.info('Press Ctrl-C to quit...')
        self.pwm.set_servo_angle(self.hip_channel, self.hip_angle)
        self.pwm.set_servo_angle(self.shoulder_channel, self.shoulder_angle)
        self.pwm.set_servo_angle(self.elbow_channel, self.elbow_angle)
        self.close()
        while True:     
            while self.elbow_angle < me_arm.elbow_max_angle:
                self.pwm.set_servo_angle(self.elbow_channel, self.elbow_angle)
                self.elbow_angle += me_arm.inc

            while self.shoulder_angle > me_arm.shoulder_min_angle:
                self.pwm.set_servo_angle(self.shoulder_channel, self.shoulder_angle)
                self.shoulder_angle -= me_arm.inc

            self.close()

            while self.hip_angle > me_arm.hip_min_angle:
                self.pwm.set_servo_angle(self.hip_channel, self.hip_angle)
                self.hip_angle -= me_arm.inc

            while self.shoulder_angle < me_arm.shoulder_max_angle:
                self.pwm.set_servo_angle(self.shoulder_channel, self.shoulder_angle)
                self.shoulder_angle += me_arm.inc

            while self.elbow_angle > me_arm.elbow_min_angle:
                self.pwm.set_servo_angle(self.elbow_channel, self.elbow_angle)
                self.elbow_angle -= me_arm.inc

            while self.hip_angle < me_arm.hip_max_angle:
                self.pwm.set_servo_angle(self.hip_channel, self.hip_angle)
                self.hip_angle += me_arm.inc

            self.open()

            while self.hip_angle > me_arm.hip_neutral_angle:
                self.pwm.set_servo_angle(self.hip_channel, self.hip_angle)
                self.hip_angle -= me_arm.inc

# Initialise the PCA9685 using the default address (0x40).
pwm = servo.PCA9685(address=0x40)

# Alternatively specify a different address and/or bus:
#pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

servo_frequency = 50
servo_min_pulse = 0.6
servo_max_pulse = 2.3
servo_neutral_pulse = 1.4
servo_min_angle = -85.0
servo_max_angle = 85.0
servo_neutral_angle = -0.0
hip_channel = 15
elbow_channel = 12
shoulder_channel = 13
gripper_channel = 14

pwm.add_servo(hip_channel, servo_frequency, servo_min_pulse, servo_max_pulse, servo_neutral_pulse,
              servo_min_angle, servo_max_angle, servo_neutral_angle, 4256)
pwm.add_servo(gripper_channel, servo_frequency, servo_min_pulse, servo_max_pulse, servo_neutral_pulse,
              servo_min_angle, servo_max_angle, servo_neutral_angle, 4256)
pwm.add_servo(shoulder_channel, servo_frequency, servo_min_pulse, servo_max_pulse, servo_neutral_pulse,
              servo_min_angle, servo_max_angle, servo_neutral_angle, 4256)
pwm.add_servo(elbow_channel, servo_frequency, servo_min_pulse, servo_max_pulse, servo_neutral_pulse,
              servo_min_angle, servo_max_angle, servo_neutral_angle, 4256)

def shutdown():
    """Resets the arm at neutral position and then resets the controller"""
    logger.info('Resetting arm and controller...')
    pwm.set_servo_angle(hip_channel, hip_neutral_angle)
    pwm.set_servo_angle(shoulder_channel, shoulder_neutral_angle)
    pwm.set_servo_angle(elbow_channel, elbow_neutral_angle)
    pwm.set_servo_angle(gripper_channel, gripper_open_angle)
    time.sleep(5)
    servo.software_reset()

# restier shutdown steps
atexit.register(shutdown)

# arm neutrals and boundaries
elbow_neutral_angle = 0
shoulder_neutral_angle = 40
hip_neutral_angle = 0

elbow_max_angle = 84.5
shoulder_max_angle = 65
hip_max_angle = 84.5

elbow_min_angle = -25
shoulder_min_angle = -15
hip_min_angle = -84.5

gripper_closed_angle = 27.5
gripper_open_angle = -20

# current angles
elbow_angle = elbow_neutral_angle
shoulder_angle = shoulder_neutral_angle
hip_angle = hip_neutral_angle

# movement increment in degrees
inc = 0.5

logger.info('Press Ctrl-C to quit...')
pwm.set_servo_angle(hip_channel, hip_angle) #hip
pwm.set_servo_angle(gripper_channel, gripper_open_angle) #gripper
pwm.set_servo_angle(shoulder_channel, shoulder_angle) #shoulder
pwm.set_servo_angle(elbow_channel, elbow_angle) #elbow
while True:     
    while elbow_angle < elbow_max_angle:
        pwm.set_servo_angle(elbow_channel, elbow_angle)
        elbow_angle += inc

    while shoulder_angle > shoulder_min_angle:
        pwm.set_servo_angle(shoulder_channel, shoulder_angle)
        shoulder_angle -= inc

    time.sleep(1)
    pwm.set_servo_angle(gripper_channel, gripper_closed_angle) #gripper
    time.sleep(1)

    while hip_angle > hip_min_angle:
        pwm.set_servo_angle(hip_channel, hip_angle)
        hip_angle -= inc

    while shoulder_angle < shoulder_max_angle:
        pwm.set_servo_angle(shoulder_channel, shoulder_angle)
        shoulder_angle += inc

    while elbow_angle > elbow_min_angle:
        pwm.set_servo_angle(elbow_channel, elbow_angle)
        elbow_angle -= inc

    while hip_angle < hip_max_angle:
        pwm.set_servo_angle(hip_channel, hip_angle)
        hip_angle += inc

    time.sleep(1)
    pwm.set_servo_angle(gripper_channel, gripper_open_angle) #gripper
    time.sleep(1)

    while hip_angle > hip_neutral_angle:
        pwm.set_servo_angle(hip_channel, hip_angle)
        hip_angle -= inc
