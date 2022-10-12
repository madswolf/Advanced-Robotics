from numpy import sin, cos, pi, sqrt
from random import random

#!/usr/bin/python3
import os

# initialize asebamedulla in background and wait 0.3s to let
# asebamedulla startup
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")
import matplotlib.pyplot as plt
from time import sleep
import dbus
import dbus.mainloop.glib
from threading import Thread


class Thymio:
    def __init__(self):
        self.aseba = self.setup()

    def drive(self, left_wheel_speed, right_wheel_speed):
        print("Left_wheel_speed: " + str(left_wheel_speed))
        print("Right_wheel_speed: " + str(right_wheel_speed))

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


# ------------------ Main -------------------------

robot = Thymio()
def main():
    left_wheel_velocity = random()*200+100   # robot left wheel velocity in radians/s
    right_wheel_velocity = random()*200+100  # robot right wheel velocity in radians/s
    count = 0
    
    while count < 500:
        count += 1
        robot.drive(left_wheel_velocity,right_wheel_velocity)
        distances = list(map(int, robot.sens()))[::-1]
        print(distances)
        distance = (max(distances), distances.index(max(distances))-2) # center the sensors around 0, so 0 is straight ahead
        print(distance[0])
        if (distance[0] > 2500):
            left_wheel_velocity = -100
            right_wheel_velocity = 100  
                
        else:                
            if count%10==0:
                left_wheel_velocity = random()*200+100
                right_wheel_velocity = random()*200+100
        sleep(0.1)
    
    robot.stop()

if __name__ == '__main__':
    try:
        main()
        os.system("pkill -n asebamedulla")
    except:
        print("Stopping robot")
        exit_now = True
        robot.stop()
        #sleep(5)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")
