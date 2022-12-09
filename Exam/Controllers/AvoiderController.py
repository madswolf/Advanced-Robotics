#!/usr/bin/python3
from .RobotController import RobotController
from Models import Colors, Zones, Actions, States
from Models.IllegalActions import IllegalActions, IllegalStateActions, IllegalZoneActions
import math, time

class AvoiderController(RobotController):
    def __init__(self, robot, Qtable, seeker_controller):
        super().__init__(robot, Qtable)
        self.robot.set_color(Colors.Blue)
        self.illegal_zone_actions = IllegalZoneActions.Avoider # TODO remove after safe zone logik)
        self.illegal_actions = IllegalActions.Avoider
        self.illegal_state_actions = IllegalStateActions.Avoider
        self.time_alive = 0
        self.total_distance_from_seeker = 0
        self.seeker_controller = seeker_controller
        self.safezone_prohibition = -999

    def get_reward(self, action, state, zone):
        if action == Actions.Forward:
            return 1.02
        elif state in [States.SeekerFront, States.SeekerRight, States.SeekerLeft]:
            return 0.99
        elif self.robot.tagged:
            return 0
        else:
            return 1

    def total_reward(self):
        safezone_bonus = 1000 if self.robot.get_zone() == Zones.Safe else 0
        return self.total_distance_from_seeker + safezone_bonus

    def step(self, count):
        if not self.robot.tagged:
            self.time_alive = count
            our_zone = self.robot.get_zone()
            safe_zone_bonus_multiplier = 1
            if our_zone == Zones.Safe and self.safezone_prohibition+10 < count:
                self.robot.set_color(Colors.Green)
                safe_zone_bonus_multiplier = 5
                self.robot.drive(0,0)
            else:
                safe_zone_bonus_multiplier = 1
                self.robot.set_color(Colors.Blue)
                if self.safezone_prohibition+10 > count:
                    self.robot.transmit(0)
                else:
                    self.robot.transmit(2)
                super().step(count)
            if self.seeker_controller is not None:
                dist = math.dist([self.robot.x, self.robot.y], [self.seeker_controller.robot.x, self.seeker_controller.robot.y])
                if self.state in [States.SeekerFront, States.SeekerLeft, States.SeekerRight]:
                    dist = dist / 4    
                self.total_distance_from_seeker += dist * safe_zone_bonus_multiplier
            self.time_alive = count
            super().step(count)
            our_zone = self.robot.get_zone()
            if our_zone == Zones.Safe:
                self.robot.set_color(Colors.Green)
                #self.robot.transmit("2")
            elif our_zone == Zones.Normal:
                self.robot.set_color(Colors.Blue)
                #self.robot.transmit("0")
            receive_message = self.robot.receive()
            if receive_message == "1" and (our_zone != Zones.Safe or self.safezone_prohibition+10 > count):
                # At the moment, we dont clear this buffer or and we also dont in the safe zone until we get a two, which means that
                # we will get tagged the moment we leave the safe zone, if we dont get a random different message before that.
                print("oiv bruv i got fokken tagged lad ffs right fooken bummer that 1 mate, hilsen " + self.robot.name)
                self.robot.tagged = True
            elif receive_message == 2 and our_zone == Zones.Safe:
                self.robot.set_color(Colors.Blue)
                self.robot.transmit(0)
                self.safezone_prohibition = count
        else:
            self.robot.set_color(Colors.Purple)
            self.robot.stop()
            
