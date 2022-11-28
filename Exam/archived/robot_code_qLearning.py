from numpy import sin, cos, pi, sqrt
import numpy as np
from random import random, randint

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
        return list(self.aseba.GetVariable("thymio-II", "prox.horizontal"))[:5] # 0 is completely left, 4 is completely right

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

speed = 200

Q = np.zeros((4, 3))
state, action = None, None

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

def main():
    global state, action
    robot = Thymio()
    count = 0
    
    while count < 500:
        count += 1
        distances = list(map(int, robot.sens()))[::-1]
        dist_left, dist_right = (max(distances[0], distances[1]), max(distances[3], distances[4]))
        print(dist_left, dist_right)

        if count - last_action > randint(100):
            action = None

        if action == None and state != None:
            if random() <= 0.2:
            # explore
                action = randint(0, 2)
                while (state, action) in illegal_actions:
                    action = randint(0,2)
            else:
                # exploit
                action = np.argmax(Q[state])
            last_action = count
        else:
            new_state = calc_state(dist_left, dist_right)
            if new_state != state:
                if action != None:
                    update_table(state, action, new_state)
                state = new_state
                action = None

        if count%5==0:
            speeds = speed_from_action(action)
            left_speed = speeds[0]
            right_speed = speeds[1]
            robot.drive(left_speed, right_speed)
        
        sleep(0.1)
    
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
