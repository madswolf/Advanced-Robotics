#!/usr/bin/python3
from .RobotController import RobotController
import sys
if "--simulated" in sys.argv:
    from .Robots.Simio import Simios
from Models import Colors, Zones, Actions, States
from Models.IllegalActions import IllegalActions, IllegalStateActions, IllegalZoneActions

class SeekerController(RobotController):
    def __init__(self, robot, Qtable):
        super().__init__(robot, Qtable)
        self.illegal_actions = IllegalActions.Seeker
        self.illegal_state_actions = IllegalStateActions.Seeker
        self.illegal_zone_actions = IllegalZoneActions.Seeker
        self.robot.set_color(Colors.Red)
        self.robot.transmit(1)
        self.total_reward_acc = 0
        self.tag_count = 0
        self.isSeeker = True

    def get_reward(self, action, state, zone):
        return 0

    def total_reward(self):
        return self.total_reward_acc
    
    def get_tag_count(self):
        if "--simulated" not in sys.argv: return 0
        return len(list(filter(lambda x: x.tagged, Simios)))

    def step(self, count):
        super().step(count)
        new_tag_count = self.get_tag_count()
        if new_tag_count > self.tag_count:
            self.total_reward_acc += 1000-count
            self.tag_count = new_tag_count 
        if self.robot.get_zone() == Zones.Safe:
            self.robot.set_color(Colors.Orange)
        else:
            self.robot.set_color(Colors.Red)