#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

sensor_threshold = 10
robot_speed = 100 # mm/s
turn_speed = 90 # deg/s
sensor_state = [False, False]

# Create your objects here.
ev3 = EV3Brick()
colL = ColorSensor(Port.S3)
colR = ColorSensor(Port.S2)
motorL = Motor(Port.C)
motorR = Motor(Port.B)
robot = DriveBase(motorL, motorR, wheel_diameter=55.5, axle_track=104)

# Write your program here.
while True:
    detectedL = colL.reflection() >= sensor_threshold
    detectedR = colR.reflection() >= sensor_threshold
    new_state = [detectedL, detectedR]

    if new_state != sensor_state:
        sensor_state = new_state
        robot.stop()
        robot.drive((detectedL and detectedR) * robot_speed, (detectedR-detectedL) * turn_speed)
    elif robot.state()[1] == 0 and robot.state()[3] == 0:
        robot.drive(0, -turn_speed)
