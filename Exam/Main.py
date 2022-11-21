import sys
from Controllers import AvoiderController, RobotController, SeekerController
from Controllers.Robots import ControllableRobot, Thymio, Simio

robot:ControllableRobot = Simio() if "--simulated" in sys.argv else Thymio()

controller = AvoiderController(robot) if sys.argv[1] == "avoider" else SeekerController(robot) if sys.argv[1] == "seeker" else None
if controller is None: raise f"Illegal robot type: {sys.argv[1]}"


count = 500
for i in range(count):
    controller.act(count)