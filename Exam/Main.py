import sys
import Controllers as Controllers
import Controllers.Robots as Robots

controllers = []

if "--simulated" in sys.argv:
    controllers = [
        Controllers.AvoiderController(Robots.Simio()),
        Controllers.AvoiderController(Robots.Simio()),
        Controllers.AvoiderController(Robots.Simio()),
        Controllers.AvoiderController(Robots.Simio()),
        Controllers.SeekerController(Robots.Simio()) # seeker is always last
    ]
else:
    if sys.argv[1] == "avoider":
        Controllers.AvoiderController(Robots.Thymio())
    elif sys.argv[1] == "seeker":
        Controllers.SeekerController(Robots.Thymio())
    else:
        raise Exception(f"Illegal robot type: {sys.argv[1]}")


count = 10000
for i in range(count):
    for c in controllers:
        c.step(count)