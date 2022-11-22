from .RobotController import RobotController

class SeekerController(RobotController):
    def __init__(self, robot):
        super().__init__(robot)
        self.Tag_count = 0

    def get_reward(self, action, state, zone):
        return self.Tag_count

    