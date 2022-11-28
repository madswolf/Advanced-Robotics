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

    def sens(self): # (horizontal[5], ground[2])
        return (
            list(self.aseba.GetVariable("thymio-II", "prox.horizontal"))[:5],
            list(self.aseba.GetVariable("thymio-II", "prox.ground.reflected")),
            list(self.aseba.GetVariable("thymio-II", "prox.ground.ambiant")),
            list(self.aseba.GetVariable("thymio-II", "prox.ground.delta"))
        )

    def sendInformation(self, number):
        self.aseba.SendEventName("prox.comm.tx", [number])

    def receiveInformation(self):
        rx = self.aseba.GetVariable("thymio-II", "prox.comm.rx")
        if rx[0] != 0:
            print(rx[0])

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
        # communication
        asebaNetwork.SendEventName( "prox.comm.enable", [1])

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


############## setup ###################
###############################################

# ------------------ Main -------------------------

def main():
    robot = Thymio()
    #left_wheel_velocity = random()*200+100   # robot left wheel velocity in radians/s
    #right_wheel_velocity = random()*200+100  # robot right wheel velocity in radians/s
    count = 0
    
    while count < 501:
        count += 1
        robot.sendInformation(count)
        robot.receiveInformation()
        sleep(0.25)
    
    robot.stop()

if __name__ == '__main__':
    try:
        main()
        os.system("pkill -n asebamedulla")
    except:
        print("Stopping robot")
        exit_now = True
        sleep(5)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")
