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
robot_speed = 80 # mm/s
straight_speed = 120
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

def middle_detect_black():
    return not (colM.reflection() >= sensor_threshold)

def intersection_move(direction):
    clamped_time_factor = max(time_factor, 0.6)
    if direction == "up":
        robot.drive(robot_speed, 0)
        wait(1500 * time_factor)
    elif direction == "right":
        robot.drive(110, 93) # usually (90,90), but changed due to batteries being weak
        wait(1000)
        robot.drive(robot_speed, 0)
        wait(333 * clamped_time_factor)
    elif direction == "left":
        robot.drive(45, -93) # usually (50,-90), but changed due to batteries being weak
        wait(1000)
        robot.drive(robot_speed, 0)
        wait(333 * clamped_time_factor)
    elif direction == "down":
        robot.drive(70, 190)
        wait(1000)
        robot.drive(robot_speed, 0)
        wait(1000 * time_factor)
    elif direction == "backwards":
        robot.drive(-robot_speed, 0)
        wait(2000 * time_factor)
        robot.drive(35, 90) # usually (70,180), but changed due to batteries being weak
        wait(2000)
    elif direction == "stop":
        sys.exit(0)

instruction_file = open("instructions", "r")
instruction_file.readline()
move_sequence = instruction_file.readline().split()
move_pointer = 0

# Write your program here.
while True:
    detectedL = colL.reflection() >= sensor_threshold
    detectedR = colR.reflection() >= sensor_threshold
    detectedM = colM.reflection() >= sensor_threshold
    new_state = [detectedL, detectedR, detectedM]

    if new_state != sensor_state:
        sensor_state = new_state
        robot.drive(straight_speed, (detectedM*2-1) * turn_speed*0.2 / time_factor)
    elif not (detectedL and detectedR):
        intersection_move(move_sequence[move_pointer])
        angle = robot.state()[2]
        move_pointer = (move_pointer + 1) % len(move_sequence)