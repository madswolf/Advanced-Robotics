from .RobotController import RobotController

class SeekerController(RobotController):
    def __init__(self):
        super().__init__()
        self.Tag_count = 0

    def get_reward(self, state, action):
        return self.Tag_count

    