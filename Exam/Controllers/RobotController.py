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

        self.state = None
        self.zone = None
        self.action = None
        self.speed = 1
        self.distance_threshold = 0.15
        self.robot = robot
        self.last_action = -9999
        self.total_steps = 0

        #Learning (Actions, states, zones
        self.Q = np.zeros((3,10,5))
        self.illegal_zone_actions = [
            (Actions.Forward, Zones.EdgeFront),
            (Actions.Forward, Zones.EdgeLeft),
            (Actions.Forward, Zones.EdgeRight)
        ]
        self.iIllegal_state_actions = [
            # when a robot is in the way, seen with robot_in_way, then forward illegal
        ]
        self.iIllegal_actions = []


    #Abstract Methods
    @abstractmethod
    def get_reward(self, action, state, zone):
        pass


    #Methods
    def step(self, count):
        self.total_steps += 1
        new_zone = self.robot.get_zone()
        new_state = self.robot.get_state()

        if count - self.last_action > 100:
            self.action = None

        if new_state != self.state or new_zone != self.zone or self.action is None:
            new_zone
            new_state
            
            if self.action != None:
                self.update_table(self.action, self.state, new_state, self.zone, new_zone)

            if random() <= 0.2:
            # explore
                action = randint(0, 2)
                while (action, new_zone) in self.illegal_zone_actions or (action, new_state) in self.iIllegal_state_actions or (action, new_state, new_zone) in self.iIllegal_actions:
                    action = randint(0,2)
                self.action = action
            else:
                # exploit
                self.action = self.best_action(new_state, new_zone)
            self.last_action = count
        
        if count % 5 == 0:
            speeds = self.speed_from_action(self.action)
            self.robot.drive(speeds[0], speeds[1])
        

    def max_future(self, state, zone):
        return np.max(self.Q[:, state, zone])

    def best_action(self, state, zone):
        return np.argmax(self.Q[:, state, zone])

    def update_table(self, action, state, new_state, zone, new_zone):
        alpha = 0.1
        gamma = 0.9
        reward = self.get_reward(action, new_state, new_zone)
        self.Q[action, state, zone] = self.Q[action, state, zone] + alpha * (reward + gamma * self.max_future(new_state, new_zone) - self.Q[action, new_state, new_zone])

        for act in self.illegal_zone_actions:
            self.Q[act[0], :, act[1]] = -10

        for act in self.iIllegal_state_actions:
            self.Q[act[0], act[1], :] = -10

        for act in self.iIllegal_actions: #don't weight illegal actions positively
            self.Q[act[0], act[1], act[2]] = -10


    def speed_from_action(self, action):
        left_velo = 0
        right_velo = 0
        speed = self.speed
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
