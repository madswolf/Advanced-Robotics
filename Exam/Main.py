import sys
import Controllers as Controllers
import Controllers.Robots as Robots

robot = Robots.Simio() if "--simulated" in sys.argv else Robots.Thymio()

controller = Controllers.AvoiderController(robot) if sys.argv[1] == "avoider" else Controllers.SeekerController(robot) if sys.argv[1] == "seeker" else None
if controller is None: 
    raise Exception(f"Illegal robot type: {sys.argv[1]}")


count = 10000
for i in range(count):
    controller.step(count)