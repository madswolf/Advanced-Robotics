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

# initialize asebamedulla in background and wait 0.3s to let
# asebamedulla startup
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")


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

def drive_robot():
    global ball_location
    while(True):
        print(ball_location)
        if ball_location == "left":
            robot.drive(-100, 100)
        elif ball_location == "middle":
            robot.stop()
        else:
            robot.drive(100, -100)

def main():
    t = Thread(target=get_ball_location)
    t.start()
    drive_robot()

if __name__ == '__main__':
    try:
        main()
        os.system("pkill -n asebamedulla")
    except:
        print("Stopping robot")
        exit_now = True
        robot.stop()
        #time.sleep(5)
        os.system("pkill -n asebamedulla")
        print("asebamodulla killed")



