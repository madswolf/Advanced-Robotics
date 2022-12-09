#!/usr/bin/python3
import time
from shapely import affinity
from shapely.geometry import LinearRing, LineString, Point, Polygon
import numpy as np
from numpy import sin, cos, pi, sqrt
from Models import Zones, States, Colors
import os
import random
from math import atan, radians, cos, sin
import sys

from .ControllableRobot import ControllableRobot

Simios = []

#start_positions = [(-0.9, -0.4), (-0.8, 0.4), (-0.8, 0.4), (-0.8, 0.4), (-0.8, 0.4)] # seeker is always last
start_positions = [(-0.8, -0.4), (-0.8, 0.4), (0.8, 0.4), (0.8, -0.4), (0.0, 0.4)] # seeker is always last
names = ["Hamilton", "Stroll", "Lando", "Alonso", "Verstappen"]

class Simio(ControllableRobot):
    # Simulation constants
    ###########
    W = 2.0  # width of arena
    H = 1.2  # height of arena
    R = 0.0225  # radius of wheels in meters
    L = 0.095   # distance between wheels in meters
    distance_threshold = 0.15  # distance threshold for collision avoidance
    robot_timestep = 0.1        # 1/robot_timestep equals update frequency of robot
    simulation_timestep = 0.01  # timestep in kinematics sim (probably don't touch..)
    receive_range = 0.2
    camera_range = 2
    front_angle = 80
    back_angle = 40
    simulation_speed = 2.98 * 0.90

    def __init__(self):
        super().__init__()
        self.TimeStep = 0.1

        self.name = names[len(Simios)]
        self.x = start_positions[len(Simios)][0]   # robot position in meters - x direction - positive to the right 
        self.y = start_positions[len(Simios)][1]   # robot position in meters - y direction - positive up
        self.q = random.random() * pi  # robot heading with respect to x-axis in radians 
        self.robot_circle = Point(self.x, self.y).buffer(Simio.L)
        self.left_wheel_velocity = 0.0
        self.right_wheel_velocity = 0.0
        self.color = Colors.Blue
        self.current_message = "0"
        self.tagged = False
        
        Simios.append(self)
        
        current_time = time.strftime("%m-%d--%H_%M")
        self.file = open(os.getcwd()+"/Exam/visualization/trajectories/trajectory_" +  str(current_time) + "_" + self.name + ".dat", "w")
        
    def simulationstep(self):
        #for step in range(int(Simio.robot_timestep/Simio.simulation_timestep)):     #step model time/timestep times
        v_x = cos(self.q)*(Simio.R*self.left_wheel_velocity/2 + Simio.R*self.right_wheel_velocity/2) 
        v_y = sin(self.q)*(Simio.R*self.left_wheel_velocity/2 + Simio.R*self.right_wheel_velocity/2)
        omega = (Simio.R*self.right_wheel_velocity - Simio.R*self.left_wheel_velocity)/(2*Simio.L)    
    
        self.x += v_x #* Simio.simulation_timestep
        self.y += v_y #* Simio.simulation_timestep
        self.q += omega #* Simio.simulation_timestep
        self.robot_circle = Point(self.x, self.y).buffer(Simio.L)
        #if step % 5 == 0:
        if "--no-visualization" not in sys.argv:
            self.file.write( str(self.x) + ", " + str(self.y) + ", " + str(cos(self.q)*0.05) + ", " + str(sin(self.q)*0.05) + "\n")
                
    
    # the world is a rectangular arena with width W and height H
    world = LinearRing([(W/2,H/2),(-W/2,H/2),(-W/2,-H/2),(W/2,-H/2)])
    world_edge = LinearRing([(W/2.2,H/2.2),(-W/2.2,H/2.2),(-W/2.2,-H/2.2),(W/2.2,-H/2.2)])
    safeZone = LinearRing([[-0.09, -0.075], [-0.09, 0.075], [0.09, 0.075], [0.09, -0.075]])

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
        projection = LineString([(self.x, self.y), (self.x+cos(self.q)*2*Simio.W,(self.y+sin(self.q)*2*Simio.H)) ])  # a line from robot to a point outside arena in direction of q
        intersection = projection.intersection(Polygon(Simio.world_edge).exterior)
        distance_to_intersection = intersection.distance(Point(self.x, self.y))
        if distance_to_intersection < Simio.L * 1.1:
            intersectionX, intersectionY = intersection.xy

            angle_of_intersection = np.arctan2(intersectionY[0]-self.y, intersectionX[0]-self.x)
            # is in front of robot within 30 degrees
            if abs(angle_of_intersection - self.q) < radians(30):
                return (True, 'front')
            # is on left side
            elif angle_of_intersection - self.q > 0:
                return (True, 'left')
            # is on right side
            else: 
                return (True, 'right')

        else:
            return (False, 'none')

    def is_in_safe_zone(self):
        # line of length L from robot in direction of q
        projection = LineString([(self.x, self.y), (self.x+cos(self.q)*Simio.L*0.4,(self.y+sin(self.q)*Simio.L*0.4))])
        return projection.intersects(Polygon(Simio.safeZone))

    def placement_in_view(self, other):
        view_triangle = Polygon(LinearRing([(self.x, self.y), (self.x+cos(self.q)*self.camera_range,(self.y+sin(self.q)*self.camera_range)), (self.x+cos(self.q+pi/2)*self.camera_range,(self.y+sin(self.q+pi/2)*self.camera_range))]))
        if view_triangle.overlaps(other.robot_circle):
            # send a ray from self to other and see if it intersects another robot on the way
            projection = LineString([(self.x, self.y), (other.x, other.y)])
            for simio in Simios:
                if simio == self or simio == other:
                    continue
                if projection.intersects(simio.robot_circle):
                    return None
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
        else: 
            edge_status = self.is_on_world_edge()
            if edge_status[0]:
                if edge_status[1] == 'front':
                    return Zones.EdgeFront
                elif edge_status[1] == 'left':
                    return Zones.EdgeLeft
                elif edge_status[1] == 'right':
                    return Zones.EdgeRight
            else:
                return Zones.Normal

    def get_state(self):
        simios = list(filter(lambda sim: sim != self and self.placement_in_view(sim) is not None and not sim.tagged, Simios))

        seekers = [x for x in simios if x.color in [Colors.Red, Colors.Orange]]
        avoiders = [x for x in simios if x.color in [Colors.Blue]]
        avoiders_safe_zone = [x for x in simios if x.color in [Colors.Green]]

        simio = None
        if not len(seekers) == 0:
            simio = seekers[0]
        elif not len(avoiders) == 0:
            # get the closest avoider
            simio = min(avoiders, key=lambda x: x.robot_circle.distance(Point(self.x, self.y)))
        elif not len(avoiders_safe_zone) == 0:
            simio = avoiders_safe_zone[0]
        else:
            return States.NoObs

        location = self.placement_in_view(simio)
        color = simio.color
        
        if location is not None:
            if color == Colors.Red or color == Colors.Orange:
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
        within_threshold = []
        for simio in Simios:
            if simio == self:
                continue
            distances = self.distance_to_robot(simio)
            distances.sort(key = lambda x: 999 if x[0] is None else x[0])
            if distances[0][0] is not None and distances[0][0] < Simio.distance_threshold:
                within_threshold.append((distances[0][0], distances[0][1])) # True, angle
        within_threshold.sort(key = lambda x: x[0]) # sort by distance
        if len(within_threshold) > 0:
            return (True, within_threshold[0][1]) # True, angle
        return (False, None) # no robot in way

    def set_color(self, color):
        self.color = color

    def transmit(self, message):
        self.current_message = message

    def receive(self):
        front_fov = radians(Simio.front_angle / 2)
        
        angle = self.q
        x1 = self.x + cos(angle + front_fov) * Simio.receive_range
        x2 = self.x + cos(angle - front_fov) * Simio.receive_range
        y1 = self.y + sin(angle + front_fov) * Simio.receive_range
        y2 = self.y + sin(angle - front_fov) * Simio.receive_range
        front_triangle = Polygon(LinearRing([(self.x, self.y), (x1, y1), (x2, y2)]))

        angle2 = angle+radians(180)
        back_fov = radians(Simio.back_angle / 2)
        x1b = self.x + cos(angle2 + back_fov) * Simio.receive_range
        x2b = self.x + cos(angle2 - back_fov) * Simio.receive_range
        y1b = self.y + sin(angle2 + back_fov) * Simio.receive_range
        y2b = self.y + sin(angle2 - back_fov) * Simio.receive_range
        back_triangle = Polygon(LinearRing([(self.x, self.y), (x1b, y1b), (x2b, y2b)]))
        
        within_triangles = []

        for simio in Simios:
            if simio == self:
                continue
            if front_triangle.intersects(simio.robot_circle) or back_triangle.intersects(simio.robot_circle):
                within_triangles.append(simio)
        
        for simio in within_triangles:
            # cast ray from simio to self and see if it hits any other simio on the way
            ray = LineString([(simio.x, simio.y), (self.x, self.y)])
            for simio2 in within_triangles:
                if simio2 == simio or simio2 == self:
                    continue
                if ray.intersects(simio2.robot_circle):
                    break
            if -radians(Simio.front_angle) < simio.q - self.q < radians(Simio.front_angle) or \
                   -radians(Simio.front_angle) < abs(simio.q - self.q) % pi < radians(Simio.back_angle):
                    if simio.current_message == "1":
                        return simio.current_message
        return None

    def drive(self, left_speed, right_speed):
        self.left_wheel_velocity = left_speed * self.simulation_speed
        self.right_wheel_velocity = right_speed * self.simulation_speed
        self.simulationstep()

    def stop(self):
        self.drive(0,0)
    
