from .RobotController import RobotController

class AvoiderController(RobotController):
    def __init__(self):
        super().__init__()
        self.Tagged = False

    def get_reward(self, state, action):
        if self.tagged:
            return 0
        else:
            return 1
