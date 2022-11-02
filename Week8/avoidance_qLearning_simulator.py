from cv2 import threshold
from shapely import affinity
from shapely.geometry import LinearRing, LineString, Point
import numpy as np
from numpy import sin, cos, pi, sqrt
from random import randint, random

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
boxUpper = LinearRing([(-0.8, 0.4), (-0.8, 0.8), (0.8,0.8), (0.8, 0.4)])
boxLower = LinearRing([(-0.8, -0.8), (-0.8, -0.4), (0.8, -0.4), (0.8, -0.8)])

world_all = [world, boxUpper, boxLower]
lastRay = LineString()
Q = np.zeros((4, 3))
state, action = 0, 2

# Actions
forward = 0
right = 1
left = 2

#Obstacle States
noObs = 0
obsLeft = 1
obsRight = 2
obsAhead = 3

illegal_actions = [(obsLeft, forward), (obsRight, forward), (obsAhead, forward)]
# Variables 
###########

x = 0.0   # robot position in meters - x direction - positive to the right 
y = 0.0   # robot position in meters - y direction - positive up
q = 0.0   # robot heading with respect to x-axis in radians 

speed = 0.2
distance_threshold = 0.15

left_wheel_velocity = speed   # robot left wheel velocity in radians/s
right_wheel_velocity = speed  # robot right wheel velocity in radians/s

# Statistics
states = []
actions = []

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
    if state == noObs:
        #left_wheel_velocity >= speed and right_wheel_velocity >= speed
        reward = 100
    #elif action == backwards:
    #    reward = -100
    return reward

def update_table(state, action, new_state):
    alpha = 0.1
    gamma = 0.9
    reward = get_reward(action)
    Q[state, action] = Q[state, action] + alpha * (reward + gamma * max_future(new_state) - Q[state, action])

    for act in illegal_actions: #don't weight illegal actions positively
        Q[act[0], act[1]] = -10

# 
def calc_state(left, right):
    state = noObs
    if not left and not right: 
        state = noObs
    elif not left and right: 
        state = obsRight
    elif left and not right: # obstacle to the right
        state = obsLeft
    elif left and right: # obstacle in front
        state = obsAhead
    return state


def line_distance(angle = 0):
    global x, y, q
    projection = LineString([(x, y), (x+cos(q)*2*W,(y+sin(q)*2*H)) ])  # a line from robot to a point outside arena in direction of q
    ray = affinity.rotate(projection, angle, (x,y))
    
    s_lst = [x.intersection(ray) for x in world_all if x.intersects(ray)]
    for i in range(len(s_lst)):
        if s_lst[i].type == "MultiPoint": 
            s_lst[i] = s_lst[i][0]
    return min([(sqrt((s.x-x)**2+(s.y-y)**2), angle) for s in s_lst]) #the distance to wall


def robot_distance_to_wall():
    angles = [-40, -20, 0, 20, 40]
    distances = list(map(line_distance, angles))
    return (min(distances[0][0], distances[1][0]), min(distances[3][0], distances[4][0]))

def speed_from_action(action):
    left_velo = 0
    right_velo = 0
    if action == forward:
        left_velo = speed
        right_velo = speed
    #elif action == backwards:
    #    left_velo = -speed
    #    right_velo = -speed
    elif action == left:
        left_velo = -speed
        right_velo = speed
    elif action == right:
        left_velo = speed
        right_velo = -speed
    return (left_velo, right_velo)


last_action = 0
for cnt in range(10000):
    #simple single-ray sensor
    dist = robot_distance_to_wall()
    dist_left = dist[0] <= distance_threshold
    dist_right = dist[1] <= distance_threshold

    if cnt - last_action > randint(420, 1337):
        action = None

    if cnt%100 == 0:
        print(f"action: {action}, state: {state}, distance: {dist}")
    if action == None and state != None:
        if random() <= 0.2:
            # explore
            action = randint(0, 2)
            while (state, action) in illegal_actions:
                action = randint(0,2)
            #print(f"random action: {action}, state: {state}, distance: {dist}")
        else:
            # exploit
            action = np.argmax(Q[state])
            #print(f"exploit action: {action}, state: {state}, distance: {dist}")
        actions.append(action)
        last_action = cnt
    else:
        new_state = calc_state(dist_left, dist_right)
        states.append(new_state)
        if new_state != state:
            if action != None:
                update_table(state, action, new_state)
            state = new_state
            action = None

    if cnt%5==0:
        speeds = speed_from_action(action)
        left_wheel_velocity = speeds[0]
        right_wheel_velocity = speeds[1]

    #step simulation
    simulationstep()

    #check collision with arena walls 
    col = min([w.distance(Point(x,y)) for w in world_all])
    if col<L/2:
        print("exiting due to leaving arena", cnt)
        break
        
    if cnt % 10 == 0:
        file.write( str(x) + ", " + str(y) + ", " + str(cos(q)*0.05) + ", " + str(sin(q)*0.05) + "\n")



print("Going forwards: " + str(sum([(action == forward) for action in actions])))
#print("Going backwards: " + str(sum([(action == backwards) for action in actions])))
print("Going right: " + str(sum([(action == right) for action in actions])))
print("Going left: " + str(sum([(action == left) for action in actions])))
print("Total actions: " + str(len(actions)))

print("No obstacles: " + str(sum([(state == noObs) for state in states])))
print("Obstacle ahead: " + str(sum([(state == obsAhead) for state in states])))
print("Obstacle right: " + str(sum([(state == obsRight) for state in states])))
print("Obstacle left: " + str(sum([(state == obsLeft) for state in states])))
print("Total states: " + str(len(states)))

#last = lastRay.coords[1]
#file.write(f"{str(x)}, {str(y)}, {last[0]}, {last[1]} \n")
np.set_printoptions(suppress=True)
print(Q)
file.close()
    
