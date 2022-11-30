from .RobotController import RobotController
from Models import Colors, Zones, Actions, States

class AvoiderController(RobotController):
    def __init__(self, robot):
        super().__init__(robot)
        self.robot.set_color(Colors.Blue)
        self.illegal_zone_actions.append((Actions.Forward, Zones.Safe)) # TODO remove after safe zone logik)
        self.illegal_zone_actions.append((Actions.Right, Zones.Safe)) # TODO remove after safe zone logik)

    def get_reward(self, action, state, zone):
        if action == Actions.Forward:
            return 1.02
        elif state in [States.SeekerFront, States.SeekerRight, States.SeekerLeft]:
            return 0.99
        elif self.robot.tagged:
            return 0
        else:
            return 1

    def step(self, count):
        if not self.robot.tagged:
            super().step(count)
            if self.robot.get_zone() == Zones.Safe:
                self.robot.set_color(Colors.Green)
            else:
                self.robot.set_color(Colors.Blue)
            receive_message = self.robot.receive()
            if receive_message == "1": # right now we can be tagged in the same zone. maybe consider that.
                print("oiv bruv i got fokken tagged lad ffs right fooken bummer that 1 mate, hilsen " + self.robot.name)
                self.robot.tagged = True
        else:
            self.robot.set_color(Colors.Purple)
            self.robot.stop()
            
