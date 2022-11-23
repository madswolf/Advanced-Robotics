from .RobotController import RobotController
from .Robots.Simio import Simios

class SeekerController(RobotController):
    def __init__(self, robot):
        super().__init__(robot)
        self.robot.transmit("1")

    def get_reward(self, action, state, zone):
        tag_count = self.get_tag_count()
        return tag_count / self.total_steps + ((tag_count == 4) * 1000)
    
    def get_tag_count(self):
        return len(list(filter(lambda x: x.tagged, Simios)))
