#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

from random import choice


# This program requires LEGO EV3 MicroPython v2.0 or higher.
# Click "Open user guide" on the EV3 extension tab for more information.

sensor_threshold = 10
robot_speed = 60 # mm/s
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

ev3.speaker.set_volume(33)

def intersection_move(direction):
    if direction == "straight":
        robot.stop()
        ev3.speaker.beep(2000)
        robot.drive(robot_speed, 0)
        wait(1500)
    elif direction == "right":
        robot.stop()
        ev3.speaker.beep(3000)
        robot.drive(90, 90)
        wait(1000)
        robot.drive(robot_speed, 0)
        wait(1000)
    elif direction == "left":
        robot.stop()
        ev3.speaker.beep(1000)
        robot.drive(50, -90)
        wait(1000)
        robot.drive(robot_speed, 0)
        wait(1000)
    elif direction == "180":
        robot.stop()
        ev3.speaker.beep(4000)
        robot.drive(0, 180)
        wait(1000)
        robot.drive(robot_speed, 0)
        wait(1000)

move_sequence = ["right", "left", "straight", "180", "straight", "right", "left", "180"]
move_pointer = 0

# Write your program here.
while True:
    detectedL = colL.reflection() >= sensor_threshold
    detectedR = colR.reflection() >= sensor_threshold
    detectedM = colM.reflection() >= sensor_threshold
    new_state = [detectedL, detectedR, detectedM]

    if new_state != sensor_state:
        sensor_state = new_state
        robot.drive(robot_speed, (detectedM*2-1) * turn_speed*0.2)
    elif not (detectedL and detectedR):
        intersection_move(move_sequence[move_pointer])
        angle = robot.state()[2]
        move_pointer = (move_pointer + 1) % len(move_sequence)