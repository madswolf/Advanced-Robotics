from .RobotController import RobotController
from Models import Colors

class AvoiderController(RobotController):
    def __init__(self, robot):
        super().__init__(robot)

    def get_reward(self, action, state, zone):
        if self.robot.tagged:
            return 0
        else:
            return 1

    def step(self, count):
        if not self.robot.tagged:
            super().step(count)
            receive_message = self.robot.receive()
            if receive_message == "1":
                print("oiv bruv i got fokken tagged lad ffs right fooken bummer that 1 mate, hilsen " + self.robot.name)
                self.robot.tagged = True
                self.robot.set_color(Colors.Purple)
                self.robot.stop()
        else:
            self.robot.drive(0,0)
            
