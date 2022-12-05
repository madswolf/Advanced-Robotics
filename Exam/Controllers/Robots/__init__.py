import sys
from .ControllableRobot import ControllableRobot
if not "--simulated" in sys.argv: 
    from .Thymio import Thymio
else:
    from .Simio import Simio
