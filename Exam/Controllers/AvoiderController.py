from .RobotController import RobotController

class AvoiderController(RobotController):
    def __init__(self, robot):
        super().__init__(robot)
        self.Tagged = False

    def get_reward(self, action, state, zone):
        if self.Tagged:
            return 0
        else:
            return 1
