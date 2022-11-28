import os
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")
import dbus
import dbus.mainloop.glib
from abc import ABC, abstractmethod

from enum import Enum
import numpy as np

class RobotController:
    def __init__(self, robot: ControllableRobot, world):
        # Variables 
        ###########

        self.State = States.NoObs        
        self.Speed = 0.2
        self.Distance_threshold = 0.15
        self.Robot = robot

        #Learning (Actions, states, zones
        self.q = np.zeros((4,10,3))

    #Methods
    
    def max_future(self):
        return max(self.q[self.State, 0], Q[state, 1])

    def get_reward(self, action):
        reward = 0
        if state == States.NoObs:
            #left_wheel_velocity >= speed and right_wheel_velocity >= speed
            reward = 100
        #elif action == backwards:
        #    reward = -100
        return reward

    def best_action(self):
        return np.argmax(self.q[state])

    def update_table(self, state, action, new_state):
        alpha = 0.1
        gamma = 0.9
        reward = self.get_reward(action)
        self.q[state, action] = self.q[state, action] + alpha * (reward + gamma * self.max_future(new_state) - self.q[state, action])

        for act in illegal_actions: #don't weight illegal actions positively
            self.q[act[0], act[1]] = -10

    # input all sensor data and output proposed new state
    def calc_state(left, right):
        state = States.NoObs
        return state 

    def getZone(self):
        if(self.IsSimulated):
            world = Self.World
        else:
            return self.thymio.sens
        return Zones.Normal

    def speed_from_action(self, action):
        left_velo = 0
        right_velo = 0
        speed = self.Speed
        if action == Actions.Forward:
            left_velo = speed
            right_velo = speed
        #elif action == backwards:
        #    left_velo = -speed
        #    right_velo = -speed
        elif action == Actions.Left:
            left_velo = -speed
            right_velo = speed
        elif action == Actions.Right:
            left_velo = speed
            right_velo = -speed
        return (left_velo, right_velo)

    def act(self, action):
        left_speed, right_speed = speed_from_action(action)
        
        if(self.IsSimulated):
            simulationstep(left_speed, right_speed)
        else:
            self.Thymio.drive(left_speed, right_speed)

    def simulationstep(left_wheel_velocity, right_wheel_velocity):
        R = self.R
        for step in range(int(self.TimeStep/simulation_timestep)):     #step model time/timestep times
            v_x = cos(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2) 
            v_y = sin(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
            omega = (R*right_wheel_velocity - R*left_wheel_velocity)/(2*self.L)    

            self.x += v_x * simulation_timestep
            self.y += v_y * simulation_timestep
            self.q += omega * simulation_timestep

class AvoiderController(RobotController):
    def __init__():
        super().__init__()

class SeekerController(RobotController):
    def __init__():
        super().__init__()

class Actions(Enum):
    Forward = 0
    Right = 1
    Left = 2

    #new
    SendAvoiderBootFromSafeZone = 3

class States(Enum):
    NoObs = 0

    # new
    SeekerAhead = 1
    SeekerRight = 2
    SeekerLeft = 3
    AvoiderAhead = 4
    AvoiderRight = 5
    AvoiderLeft = 6
    AvoiderInSafeZoneAhead = 7
    AvoiderInSafeZoneRight = 8
    AvoiderInSafeZoneLeft = 9

class Zones(Enum):
    Normal = 0
    Safe = 1

    #expand with left right ahead for easier learning?
    Edge = 2


class ControllableRobot(ABC):   
    def __init__():
        pass

    @abstractmethod(callable)
    def sens():
        pass

    @abstractmethod(callable)
    def transmit():
        pass

    @abstractmethod(callable)
    def drive():
        pass

    @abstractmethod(callable)
    def stop():
        pass


class Thymio(ControllableRobot):
    def __init__(self):
        super().__init__()
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
            list(self.aseba.GetVariable("thymio-II", "prox.ground"))
        )

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



class Simio(ControllableRobot):
    
    # Simulation constants
    ###########
    R = 0.0225  # radius of wheels in meters
    L = 0.095   # distance between wheels in meters
   
    # the world is a rectangular arena with width W and height H
    world = LinearRing([(W/2,H/2),(-W/2,H/2),(-W/2,-H/2),(W/2,-H/2)])
    world_edge = LinearRing([(W/2.2,H/2.2),(-W/2.2,H/2.2),(-W/2.2,-H/2.2),(W/2.2,-H/2.2)])
    safeZone = LinearRing([(W/10,H/10),(-W/10,H/10),(-W/10,-H/10),(W/10,-H/10)])

    world_all = [world, safeZone, world_edge]


    def __init__(self):
        super().__init__()
        self.TimeStep = 0.1

        self.x = 0.0   # robot position in meters - x direction - positive to the right 
        self.y = 0.0   # robot position in meters - y direction - positive up
        self.q = 0.0   # robot heading with respect to x-axis in radians 