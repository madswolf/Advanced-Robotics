from abc import ABC, abstractmethod
import numpy as np
from random import random, randint
import sys
sys.path.append("..")


from .Robots.ControllableRobot import ControllableRobot
from Models.States import States
from Models.Actions import Actions
from Models.Zones import Zones


class RobotController(ABC):
    def __init__(self, robot: ControllableRobot):
        # Variables 
        ###########

        self.State = None
        self.Zone = None
        self.Action = None
        self.Speed = 1
        self.Distance_threshold = 0.15
        self.Robot = robot
        self.Last_action = -9999

        #Learning (Actions, states, zones
        self.Q = np.zeros((3,10,5))
        self.Illegal_zone_actions = [
            (Actions.Forward, Zones.EdgeFront),
            (Actions.Forward, Zones.EdgeLeft),
            (Actions.Forward, Zones.EdgeRight)
        ]
        self.Illegal_state_actions = [
            # when a robot is in the way, seen with robot_in_way, then forward illegal
        ]
        self.Illegal_actions = []


    #Abstract Methods
    @abstractmethod
    def get_reward(self, action, state, zone):
        pass


    #Methods
    def step(self, count):
        new_zone = self.Robot.get_zone()
        new_state = self.Robot.get_state()

        if count - self.Last_action > 100:
            self.Action = None

        if new_state != self.State or new_zone != self.Zone or self.Action is None:
            new_zone
            new_state
            
            if self.Action != None:
                self.update_table(self.Action, self.State, new_state, self.Zone, new_zone)

            if random() <= 0.2:
            # explore
                action = randint(0, 2)
                while (action, new_zone) in self.Illegal_zone_actions or (action, new_state) in self.Illegal_state_actions or (action, new_state, new_zone) in self.Illegal_actions:
                    action = randint(0,2)
                self.Action = action
            else:
                # exploit
                self.Action = self.best_action(new_state, new_zone)
            self.Last_action = count
        
        if count % 5 == 0:
            speeds = self.speed_from_action(self.Action)
            self.Robot.drive(speeds[0], speeds[1])
        

    def max_future(self, state, zone):
        return np.max(self.Q[:, state, zone])

    def best_action(self, state, zone):
        return np.argmax(self.Q[:, state, zone])

    def update_table(self, action, state, new_state, zone, new_zone):
        alpha = 0.1
        gamma = 0.9
        reward = self.get_reward(action, new_state, new_zone)
        self.Q[action, state, zone] = self.Q[action, state, zone] + alpha * (reward + gamma * self.max_future(new_state, new_zone) - self.Q[action, new_state, new_zone])

        for act in self.Illegal_zone_actions:
            self.Q[act[0], :, act[1]] = -10

        for act in self.Illegal_state_actions:
            self.Q[act[0], act[1], :] = -10

        for act in self.Illegal_actions: #don't weight illegal actions positively
            self.Q[act[0], act[1], act[2]] = -10


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
