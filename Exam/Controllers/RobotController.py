from abc import ABC, abstractmethod
import numpy as np
from random import random, randint

from .Robots.ControllableRobot import ControllableRobot
from ..Models.States import States
from ..Models.Actions import  Actions
from ..Models.Zones import Zones


class RobotController(ABC):
    def __init__(self, robot: ControllableRobot):
        # Variables 
        ###########

        self.State = None
        self.Zone = None
        self.Action = None
        self.Speed = 0.2
        self.Distance_threshold = 0.15
        self.Robot = robot
        self.Last_action = -9999

        #Learning (Actions, states, zones
        self.Q = np.zeros((4,10,3))
        self.Illegal_actions = []


    #Abstract Methods
    @abstractmethod
    def get_reward(self, state, action):
        pass


    #Methods
    def step(self, count):
        new_zone = self.Robot.get_zone()
        new_state = self.Robot.get_state()

        if count - self.Last_action > 100:
            self.Action = None

        if new_state != self.State or new_zone != self.Zone or self.Action is None:
            self.Zone = new_zone
            self.State = new_state
            if random() <= 0.2:
            # explore
                action = randint(0, 2)
                while (self.State, action) in self.Illegal_actions:
                    action = randint(0,2)
                self.Action = action
            else:
                # exploit
                self.Action = np.argmax(self.Q[self.State])
            self.Last_action = count

        if count % 5 == 0:
            speeds = self.speed_from_action()
            self.Robot.drive(speeds[0], speeds[1])
        

    def max_future(self):
        return max(self.Q[self.State, 0], self.Q[self.State, 1])

    def best_action(self):
        return np.argmax(self.Q[self.State])

    def update_table(self, state, action, new_state):
        alpha = 0.1
        gamma = 0.9
        reward = self.get_reward(action)
        self.q[state, action] = self.q[state, action] + alpha * (reward + gamma * self.max_future(new_state) - self.q[state, action])

        for act in self.Illegal_actions: #don't weight illegal actions positively
            self.q[act[0], act[1]] = -10


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
