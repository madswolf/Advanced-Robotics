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
        self.robot.transmit("1")

    def get_reward(self, action, state, zone):
        return 0

    def total_reward(self):
        tag_count = self.get_tag_count()
        return tag_count / (max(self.total_steps,0)) + ((tag_count == 4) * 1000)
    
    def get_tag_count(self):
        return len(list(filter(lambda x: x.tagged, Simios)))

    def step(self, count):
        super().step(count)
        if self.robot.get_zone() == Zones.Safe:
            self.robot.set_color(Colors.Orange)
        else:
            self.robot.set_color(Colors.Red)