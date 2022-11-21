from shapely import affinity
from shapely.geometry import LinearRing, LineString, Point, Polygon
import numpy as np
from numpy import sin, cos, pi, sqrt
from Models import Zones, Actions, States, Colors

from .ControllableRobot import ControllableRobot

Simios = []

class Simio(ControllableRobot):
    # Simulation constants
    ###########
    W = 2.0  # width of arena
    H = 2.0  # height of arena
    R = 0.0225  # radius of wheels in meters
    L = 0.095   # distance between wheels in meters
    distance_threshold = 0.15  # distance threshold for collision avoidance
    robot_timestep = 0.1        # 1/robot_timestep equals update frequency of robot
    simulation_timestep = 0.01  # timestep in kinematics sim (probably don't touch..)
    receive_range = 0.5
    camera_range = 0.5


    def simulationstep(self):
        for step in range(int(Simio.robot_timestep/Simio.simulation_timestep)):     #step model time/timestep times
            v_x = cos(self.q)*(Simio.R*self.left_wheel_velocity/2 + Simio.R*self.right_wheel_velocity/2) 
            v_y = sin(self.q)*(Simio.R*self.left_wheel_velocity/2 + Simio.R*self.right_wheel_velocity/2)
            omega = (Simio.R*self.right_wheel_velocity - Simio.R*self.left_wheel_velocity)/(2*Simio.L)    
        
            self.x += v_x * Simio.simulation_timestep
            self.y += v_y * Simio.simulation_timestep
            self.q += omega * Simio.simulation_timestep
    
    # the world is a rectangular arena with width W and height H
    world = LinearRing([(W/2,H/2),(-W/2,H/2),(-W/2,-H/2),(W/2,-H/2)])
    world_edge = LinearRing([(W/2.2,H/2.2),(-W/2.2,H/2.2),(-W/2.2,-H/2.2),(W/2.2,-H/2.2)])
    safeZone = LinearRing([(W/10,H/10),(-W/10,H/10),(-W/10,-H/10),(W/10,-H/10)])

    world_all = [world, safeZone, world_edge]

    def distance_to_other_robot(self, other, angle = 0):
        projection = LineString([(self.x, self.y), (self.x+cos(self.q)*2*Simio.W,(self.y+sin(self.q)*2*Simio.H)) ])  # a line from robot to a point outside arena in direction of q
        ray = affinity.rotate(projection, angle, (self.x,self.y))
        if ray.intersects(other.robot_circle):
            return (ray.intersection(other.robot_circle).distance(Point(self.x, self.y)), angle)
        return (None, angle)

    def distance_to_robot(self, other):
        angles = [-40, -20, 0, 20, 40]
        distances = [x for x in map(lambda angle: self.distance_to_other_robot(other, angle), angles)]
        return distances

    def is_on_world_edge(self):
        return self.robot_circle.intersects(Polygon(Simio.world_edge.exterior))

    def is_in_safe_zone(self):
        # middle of robot is in safe zone
        return Point(self.x, self.y).intersects(Polygon(Simio.safeZone))

    def placement_in_view(self, other):
        view_triangle = Polygon(LinearRing([(self.x, self.y), (self.x+cos(self.q)*self.camera_range,(self.y+sin(self.q)*self.camera_range)), (self.x+cos(self.q+pi/2)*self.camera_range,(self.y+sin(self.q+pi/2)*self.camera_range))]))
        if view_triangle.overlaps(other.robot_circle):
            ## is on left side of robot
            if (other.x-self.x)*cos(self.q) + (other.y-self.y)*sin(self.q) > 0.2:
                return 'left'
            ## is on right side of robot
            elif (other.x-self.x)*cos(self.q) + (other.y-self.y)*sin(self.q) < -0.2:
                return 'right'
            ## is in front of robot
            else:
                return 'front'
        else:
            return None       

    def get_zone(self):
        if self.is_in_safe_zone():
            return Zones.Safe
        elif self.is_on_world_edge():
            return Zones.Edge
        else:
            return Zones.Normal

    def get_state(self):
        for simio in Simios:
            if simio == self:
                continue
            color = simio.color
            location = self.placement_in_view(simio)

            if location is not None:
                if color == Colors.Red:
                    if location == 'left':
                        return States.SeekerLeft
                    elif location == 'right':
                        return States.SeekerRight
                    else:
                        return States.SeekerFront

                elif color == Colors.Blue:
                    if location == 'left':
                        return States.AvoiderLeft
                    elif location == 'right':
                        return States.AvoiderRight
                    else:
                        return States.AvoiderFront

                elif color == Colors.Green:
                    if location == 'left':
                        return States.AvoiderInSafeZoneLeft
                    elif location == 'right':
                        return States.AvoiderInSafeZoneRight
                    else:
                        return States.AvoiderInSafeZoneFront

        return States.NoObs

    def robot_in_way(self):
        for simio in Simios:
            if simio == self:
                continue
            distances = self.distance_to_robot(simio)
            for distance in distances:
                if distance[0] is not None and distance[0] < Simio.distance_threshold:
                    return (True, distance[1])
            

    def __init__(self):
        super().__init__()
        self.TimeStep = 0.1

        self.x = 0.0   # robot position in meters - x direction - positive to the right 
        self.y = 0.0   # robot position in meters - y direction - positive up
        self.q = 0.0   # robot heading with respect to x-axis in radians 
        self.robot_circle = Point(self.x, self.y).buffer(Simio.L)
        self.left_wheel_velocity = 0.0
        self.right_wheel_velocity = 0.0
        self.color = Colors.Blue

        Simios.append(self)

    def set_color(self, color):
        self.color = color
    
    def transmit(self, message):
        self.current_message = message

    def receive(self):
        front_triangle = Polygon(LinearRing([(self.x, self.y), (self.x+cos(self.q)*self.receive_range,(self.y+sin(self.q)*self.receive_range)), (self.x+cos(self.q+pi/2)*self.receive_range,(self.y+sin(self.q+pi/2)*self.receive_range))]))
        back_triangle = Polygon(LinearRing([(self.x, self.y), (self.x+cos(self.q)*self.receive_range,(self.y+sin(self.q)*self.receive_range)), (self.x+cos(self.q-pi/2)*self.receive_range,(self.y+sin(self.q-pi/2)*self.receive_range))]))
        for simio in Simios:
            if simio == self:
                continue
            if front_triangle.intersects(simio.robot_circle) or back_triangle.intersects(simio.robot_circle):
                return simio.current_message

    def drive(self, left_speed, right_speed):
        self.left_wheel_velocity = left_speed
        self.right_wheel_velocity = right_speed
        self.simulationstep()

    def stop(self):
        self.left_wheel_velocity = 0.0
        self.right_wheel_velocity = 0.0
        self.simulationstep()
    
