import sys
from .ControllableRobot import ControllableRobot
from .Simio import Simio
if not "--simulated" in sys.argv: from .Thymio import Thymio