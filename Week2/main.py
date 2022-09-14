#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

import sys

from random import choice


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

sensor_threshold = 10
robot_speed = 100 # mm/s
time_factor = 60 / robot_speed # 60 = magic number that everything is calibrated with
turn_speed = 90 # deg/s
sensor_state = [False, False]

# Create your objects here.
ev3 = EV3Brick()
colL = ColorSensor(Port.S3)
colR = ColorSensor(Port.S2)
colM = ColorSensor(Port.S4)
motorL = Motor(Port.C)
motorR = Motor(Port.B)
robot = DriveBase(motorL, motorR, wheel_diameter=56, axle_track=130)
angle = robot.state()[2]

ev3.speaker.set_volume(20)

def intersection_move(direction):
    clamped_time_factor = max(time_factor, 0.6)
    if direction == "straight":
        robot.drive(robot_speed, 0)
        wait(1500 * time_factor)
    elif direction == "right":
        robot.drive(90 / clamped_time_factor, 90 / clamped_time_factor)
        wait(1000 * clamped_time_factor)
        robot.drive(robot_speed, 0)
        wait(1000 * clamped_time_factor)
    elif direction == "left":
        robot.drive(50 / clamped_time_factor, -90 / clamped_time_factor)
        wait(1000 * clamped_time_factor)
        robot.drive(robot_speed, 0)
        wait(1000 * clamped_time_factor)
    elif direction == "180":
        robot.drive(70, 180)
        wait(1000)
        robot.drive(robot_speed, 0)
        wait(1000 * time_factor)
    elif direction == "backwards":
        robot.drive(-robot_speed, 0)
        wait(2000 * time_factor)
        robot.drive(70, 180)
        wait(1000)
    elif direction == "stop":
        sys.exit(0)

move_sequence = ["straight", "left"]
move_pointer = 0

# Write your program here.
while True:
    detectedL = colL.reflection() >= sensor_threshold
    detectedR = colR.reflection() >= sensor_threshold
    detectedM = colM.reflection() >= sensor_threshold
    new_state = [detectedL, detectedR, detectedM]

    if new_state != sensor_state:
        sensor_state = new_state
        robot.drive(robot_speed, (detectedM*2-1) * turn_speed*0.2 / time_factor)
    elif not (detectedL and detectedR):
        intersection_move(move_sequence[move_pointer])
        angle = robot.state()[2]
        move_pointer = (move_pointer + 1) % len(move_sequence)