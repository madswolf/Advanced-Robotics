from cv2 import threshold
from shapely import affinity
from shapely.geometry import LinearRing, LineString, Point
import numpy as np
from numpy import sin, cos, pi, sqrt
from random import random

# A prototype simulation of a differential-drive robot with one sensor

# Constants
###########
R = 0.0225  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

W = 2.0  # width of arena
H = 2.0  # height of arena

robot_timestep = 0.1        # 1/robot_timestep equals update frequency of robot
simulation_timestep = 0.01  # timestep in kinematics sim (probably don't touch..)

# the world is a rectangular arena with width W and height H
world = LinearRing([(W/2,H/2),(-W/2,H/2),(-W/2,-H/2),(W/2,-H/2)])
lastRay = LineString()
Q = np.zeros((5, 2))
state, action = None, None
target_distance = 0.5

# Variables 
###########

x = 0.0   # robot position in meters - x direction - positive to the right 
y = 0.0   # robot position in meters - y direction - positive up
q = 0.0   # robot heading with respect to x-axis in radians 

speed = 0.2
distance_threshold = 0.02

left_wheel_velocity =  speed   # robot left wheel velocity in radians/s
right_wheel_velocity =  speed  # robot right wheel velocity in radians/s

# Kinematic model
#################
# updates robot position and heading based on velocity of wheels and the elapsed time
# the equations are a forward kinematic model of a two-wheeled robot - don't worry just use it
def simulationstep():
    global x, y, q

    for step in range(int(robot_timestep/simulation_timestep)):     #step model time/timestep times
        v_x = cos(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2) 
        v_y = sin(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        omega = (R*right_wheel_velocity - R*left_wheel_velocity)/(2*L)    
    
        x += v_x * simulation_timestep
        y += v_y * simulation_timestep
        q += omega * simulation_timestep

# Simulation loop
#################
file = open("trajectory.dat", "w")

def max_future(state):
    return max(Q[state, 0], Q[state, 1])

def get_reward(action):
    reward = 0
    if(state == 2):
        #-distance_threshold < distance[0]-target_distance < distance_threshold
        reward = 100
    return reward

def update_table(state, action, new_state):
    alpha = 0.1
    gamma = 0.9
    reward = get_reward(action)
    Q[state, action] = Q[state, action] + alpha * (reward + gamma * max_future(new_state) - Q[state, action])
    Q[0, 0] = 0 # Never allowed to go forwards when too close
    Q[4, 1] = 0 # Never allowed to go backwards when too far away

# 
def calc_state(distance):
    if distance < 0.2: #way too close
        return 0
    elif distance < target_distance-distance_threshold: ## too close
        return 1
    elif -distance_threshold < distance-target_distance < distance_threshold: #goal
        return 2
    elif 1.2 > distance > target_distance+distance_threshold: ## too far
        return 3
    else:
        return 4 # way too far


def line_distance(angle = 0):
    global x, y, q, lastRay
    projection = LineString([(x, y), (x+cos(q)*2*W,(y+sin(q)*2*H)) ])  # a line from robot to a point outside arena in direction of q
    lastRay = projection
    ray = affinity.rotate(projection, angle, (x,y))
    s = world.intersection(ray)
    return (sqrt((s.x-x)**2+(s.y-y)**2), angle) #the distance to wall


def robot_distance_to_wall():
    angles = [-40, -20, 0, 20, 40]
    distances = list(map(line_distance, angles))
    return min(distances, key=lambda x: x[0])


for cnt in range(10000):
    #simple single-ray sensor
    distance = robot_distance_to_wall()
    #front_ray = LineString([(x, y), (x+cos(q)*2*W,-(y+sin(q)*2*H)) ])  # a line from robot to a point outside arena in direction of q
    #s = world.intersection(front_ray)
    #distance = sqrt((s.x-x)**2+(s.y-y)**2)                    # distance to wall

    if cnt%50 == 0:
        print(f"action: {action}, state: {state}, distance: {distance[0]}")
    if action == None and state != None:
        if state == 0:
            action = 1
        elif state == len(Q)-1:
            action = 0
        elif random() <= 0.2:
            # explore
            action = int(random()<=0.5)
        else:
            # exploit
            action = np.argmax(Q[state])
    else:
        new_state = calc_state(distance[0])
        if new_state != state:
            if action != None:
                update_table(state, action, new_state)
            state = new_state
            action = None

    if cnt%5==0:
        if(action == 0):
            left_wheel_velocity = speed
            right_wheel_velocity = speed
        else:
            left_wheel_velocity = -speed
            right_wheel_velocity = -speed

    #step simulation
    simulationstep()

    #check collision with arena walls 
    col = world.distance(Point(x,y))
    if (col<L/2):
        print("exiting due to leaving arena", cnt)
        break
        
    if random() <= 0.1:
        file.write( str(x) + ", " + str(y) + ", " + str(cos(q)*0.05) + ", " + str(sin(q)*0.05) + "\n")
        
last = lastRay.coords[1]
file.write(f"{str(x)}, {str(y)}, {last[0]}, {last[1]} \n")
print(Q)
file.close()
    
