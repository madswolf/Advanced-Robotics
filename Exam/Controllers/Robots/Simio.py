from shapely import affinity
from shapely.geometry import LinearRing, LineString, Point

from .ControllableRobot import ControllableRobot

Simios = []

class Simio(ControllableRobot):
    # Simulation constants
    ###########
    W = 2.0  # width of arena
    H = 2.0  # height of arena
    R = 0.0225  # radius of wheels in meters
    L = 0.095   # distance between wheels in meters
   
    # the world is a rectangular arena with width W and height H
    world = LinearRing([(W/2,H/2),(-W/2,H/2),(-W/2,-H/2),(W/2,-H/2)])
    world_edge = LinearRing([(W/2.2,H/2.2),(-W/2.2,H/2.2),(-W/2.2,-H/2.2),(W/2.2,-H/2.2)])
    safeZone = LinearRing([(W/10,H/10),(-W/10,H/10),(-W/10,-H/10),(W/10,-H/10)])

    world_all = [world, safeZone, world_edge]


    def __init__(self):
        super().__init__()
        self.TimeStep = 0.1

        self.x = 0.0   # robot position in meters - x direction - positive to the right 
        self.y = 0.0   # robot position in meters - y direction - positive up
        self.q = 0.0   # robot heading with respect to x-axis in radians 

        Simios.append(self)