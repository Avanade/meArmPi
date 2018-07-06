# pylint: disable=C0103
"""Simple test program for servo actuation"""
import time
import logging
import servo
import atexit

# Uncomment to enable debug output.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
