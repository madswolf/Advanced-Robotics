from shapely import affinity
from shapely.geometry import LinearRing, LineString, Point
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

# Variables 
###########

x = 0.0   # robot position in meters - x direction - positive to the right 
y = 0.0   # robot position in meters - y direction - positive up
q = 0.0   # robot heading with respect to x-axis in radians 

left_wheel_velocity =  random()   # robot left wheel velocity in radians/s
right_wheel_velocity =  random()  # robot right wheel velocity in radians/s

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

def line_distance(rotation = 0):
    global x, y, q, lastRay
    projection = LineString([(x, y), (x+cos(q)*2*W,(y+sin(q)*2*H)) ])  # a line from robot to a point outside arena in direction of q
    lastRay = projection
    ray = affinity.rotate(projection, rotation, (x,y))
    s = world.intersection(ray)
    return sqrt((s.x-x)**2+(s.y-y)**2) #the distance to wall


def robot_distance_to_wall():
    angles = [-40, -20, 0, 20, 40]
    distances = list(map(line_distance, angles))
    return min(distances)


for cnt in range(10000):
    #simple single-ray sensor
    distance = robot_distance_to_wall()
    #front_ray = LineString([(x, y), (x+cos(q)*2*W,-(y+sin(q)*2*H)) ])  # a line from robot to a point outside arena in direction of q
    #s = world.intersection(front_ray)
    #distance = sqrt((s.x-x)**2+(s.y-y)**2)                    # distance to wall
    
    #simple controller - change direction of wheels every 10 seconds (100*robot_timestep) unless close to wall then turn on spot
    if (distance < 0.1):
        left_wheel_velocity = -0.5
        right_wheel_velocity = 0.5  
    else:                
        if cnt%100==0:
            left_wheel_velocity = random()
            right_wheel_velocity = random()
        
    #step simulation
    simulationstep()

    #check collision with arena walls 
    col = world.distance(Point(x,y))
    if (col<L/2):
        print("exiting due to leaving arena", cnt)
        break
        
    if cnt%50==0:
        file.write( str(x) + ", " + str(y) + ", " + str(cos(q)*0.05) + ", " + str(sin(q)*0.05) + "\n")
        
first, last = lastRay.boundary
file.write(f"{str(x)}, {str(y)}, {last.x}, {last.y} \n")
file.close()
    
