

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
import threading
import time

MAP_SIZE_PIXELS         = 250
MAP_SIZE_METERS         = 15
LIDAR_DEVICE            = '/dev/ttyUSB0'

# Pose will be modified in our threaded code
pose = [0, 0, 0]


# Ideally we could use all 250 or so samples that the RPLidar delivers in one
# scan, but on slower computers you'll get an empty map and unchanging position
# at that rate.
MIN_SAMPLES   = 50
# Connect to Lidar unit
lidar = Lidar(LIDAR_DEVICE)
# Initialize an empty trajectory
trajectory = []

# Initialize empty map
mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

def updateLidar(thread_name, delay):
    # Create an RMHC SLAM object with a laser model and optional robot model
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

    # Set up a SLAM display
    # viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')
    # Create an iterator to collect scan data from the RPLidar
    iterator = lidar.iter_scans()

    # We will use these to store previous scan in case current scan is inadequate
    previous_distances = None
    previous_angles    = None

    # First scan is crap, so ignore it
    next(iterator)
    pose = [0, 0, 0]

    while True:

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
    return pose

def getMap():
    return mapbytes       

def mainLoop(threadName, delay):
    while True:
        pos = getPosition()
        print(f"x:{(pos[0])} y:{(pos[1])} theta {(pos[2])}")
        time.sleep(delay)

if __name__ == "__main__":
    t1 = threading.Thread(target=updateLidar, args=('thread1', 0.1))
    t2 = threading.Thread(target=mainLoop, args=('thread1', 0.1))
    t1.start()
    t2.start()
     # Shut down the lidar connection
    lidar.stop()
    lidar.disconnect()