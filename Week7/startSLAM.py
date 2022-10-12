# tracking.py
# Created by Michael Marek (2016)
# Track the position of tennis balls in a webcam video feed.
from picamera import PiCamera
import cv2
import numpy as np
from threading import Thread
import time
import os
import dbus
import dbus.mainloop.glib
import numpy

# initialize asebamedulla in background and wait 0.3s to let
# asebamedulla startup
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")

'''
rpslam.py : BreezySLAM Python with SLAMTECH RP A1 Lidar

Copyright (C) 2018 Simon D. Levy
This code is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This code is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU Lesser General Public License
along with this code.  If not, see <http://www.gnu.org/licenses/>.
'''
from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import RPLidarA1 as LaserModel
from rplidar import RPLidar as Lidar
from math import floor


class Thymio:
    def __init__(self):
        self.aseba = self.setup()

    def drive(self, left_wheel_speed, right_wheel_speed):
        #print("Left_wheel_speed: " + str(left_wheel_speed))
        #print("Right_wheel_speed: " + str(right_wheel_speed))

        left_wheel = left_wheel_speed
        right_wheel = right_wheel_speed

        self.aseba.SendEventName("motor.target", [left_wheel, right_wheel])

    def stop(self):
        left_wheel = 0
        right_wheel = 0
        self.aseba.SendEventName("motor.target", [left_wheel, right_wheel])

    def sens(self):
        return list(self.aseba.GetVariable("thymio-II", "prox.horizontal"))[:5]

    ############## Bus and aseba setup ######################################

    def setup(self):
        print("Setting up")
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SessionBus()
        asebaNetworkObject = bus.get_object('ch.epfl.mobots.Aseba', '/')

        asebaNetwork = dbus.Interface(
            asebaNetworkObject, dbus_interface='ch.epfl.mobots.AsebaNetwork'
        )
        # load the file which is run on the thymio
        asebaNetwork.LoadScripts(
            'thympi.aesl', reply_handler=self.dbusError, error_handler=self.dbusError
        )

        # scanning_thread = Process(target=robot.drive, args=(200,200,))
        return asebaNetwork

    def stopAsebamedulla(self):
        os.system("pkill -n asebamedulla")

    def dbusReply(self):
        # dbus replys can be handled here.
        # Currently ignoring
        pass

    def dbusError(self, e):
        # dbus errors can be handled here.
        # Currently only the error is logged. Maybe interrupt the mainloop here
        print("dbus error: %s" % str(e))


width = 640
height = 480
camera = PiCamera()
robot = Thymio()
camera.resolution = (width,height)
camera.framerate = 24

ball_location = "none"
facing = "correct"
margin = 100

# tennis ball colour range
lower = (20, 100, 100)
upper = (70, 255, 255)


def get_ball_location():
    global ball_location
    while(True):
        image = np.empty((height,width,3), dtype=np.uint8)
        camera.capture(image,'bgr')
        frame = cv2.rotate(image, cv2.ROTATE_180)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.GaussianBlur(mask, (5,5), 2)
        mask = cv2.erode(mask, np.ones((6,6), dtype=np.uint8), iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bestCircle = (-1, (-1,-1))
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            if(radius > bestCircle[0]):
                bestCircle = (radius, center)

        ball_place = "none" if bestCircle[1][0] == -1 else "right" if bestCircle[1][0] > width/2+margin else "left" if bestCircle[1][0] < width/2-margin else "middle"
        
        if bestCircle[1][0] != -1:
            cv2.circle(frame, bestCircle[1], bestCircle[0], (0, 255, 0), 2) # tennis ball outline
            cv2.circle(frame, bestCircle[1], 1, (0, 0, 255), 2)      # tennis ball centroid
        if cv2.waitKey(30) & 0xFF == 27:
            exit

        cv2.imwrite("photo.png", frame)
        ball_location = ball_place

def ball_printer():
    global ball_location
    while(True):
        time.sleep(0.1)
        print(ball_location)



MAP_SIZE_PIXELS         = 250
MAP_SIZE_METERS         = 15
LIDAR_DEVICE            = '/dev/ttyUSB0'


# Ideally we could use all 250 or so samples that the RPLidar delivers in one
# scan, but on slower computers you'll get an empty map and unchanging position
# at that rate.
MIN_SAMPLES   = 100


lidar = Lidar(LIDAR_DEVICE)
# Initialize an empty trajectory
trajectory = []

# Initialize empty map
mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)
# Create an RMHC SLAM object with a laser model and optional robot model
slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)
pose = [0, 0, 0]
runThread = True

# from roboviz import MapVisualizer

def update_lidar(thread_name, delay):
    

    # Set up a SLAM display
    # viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')
    # Create an iterator to collect scan data from the RPLidar
    iterator = lidar.iter_scans()

    # We will use these to store previous scan in case current scan is inadequate
    previous_distances = None
    previous_angles    = None

    # First scan is crap, so ignore it
    next(iterator)

    while runThread:

        # Extract (quality, angle, distance) triples from current scan
        # print(next(iterator))
        items = [item for item in next(iterator)]

        # Extract distances and angles from triples
        distances = [item[2] for item in items]
        angles    = [item[1] for item in items]

        # Update SLAM with current Lidar scan and scan angles if adequate
        if len(distances) > MIN_SAMPLES:
            slam.update(distances, scan_angles_degrees=angles)
            previous_distances = distances.copy()
            previous_angles    = angles.copy()

        # If not adequate, use previous
        elif previous_distances is not None:
            slam.update(previous_distances, scan_angles_degrees=previous_angles)

        # Get current robot position
        pose[0], pose[1], pose[2] = slam.getpos()

        # Get current map bytes as grayscale
        slam.getmap(mapbytes)
        time.sleep(delay)


def getPosition():
    return [pose[0]/60, pose[1]/60, pose[2]]

def getMap():
    return mapbytes

def facing_target(current_coords, target_coords):
    distance = [target_coords[0] - current_coords[0], target_coords[1] - current_coords[0]]
    
    a = \
        90 if distance[0] == 0 and distance[1] > 0 \
        else -90 if distance[0] == 0 and distance[1] < 0 \
        else numpy.degrees(numpy.arctan(distance[1] / distance[0]))
    #print(f"target angle: {a}, current: {current_coords[2]}")
    #print(a - current_coords[2])
    print(f"target: {a}, current: {current_coords[2]}")
    if(a - current_coords[2] < 0):
        return "left"
    elif a - current_coords[2] > 0: 
        return "right"

    return "correct"

def drive_robot(thread_name, delay):
    count = 0
    while True and runThread:
        if count < 10: 
            count += 1
            continue
        else: count = 0
        facing = facing_target(getPosition(), [125, 200])
        if facing == "left":
            robot.drive(-30,30)
        elif facing == "right":
            robot.drive(30,-30)
        elif facing == "correct":
            robot.drive(0,0)
            break
        time.sleep(delay)


def main(delay):
    while True and runThread:
        pos = getPosition()
        #print(f"x:{pos[0]} y:{pos[1]} theta {pos[2]}")
        time.sleep(delay)



if __name__ == "__main__":
    t1 = Thread(target=update_lidar, args=('thread1', 0.1))
    t1.daemon = True
    t1.start()
    time.sleep(2)
    t2 = Thread(target=drive_robot, args=('thread2', 0.1))
    t2.daemon = True
    t2.start()
    try:
        while True:
            main(0.1)

    except:
        robot.drive(0,0)
        print(" kinda stopped")
        runThread = False
        t1.join()
        t2.join()
        lidar.stop()
        lidar.disconnect()
        exit(0)


