from abc import ABC, abstractmethod
import numpy as np
from random import random, randint
import sys
sys.path.append("..")


from .Robots.ControllableRobot import ControllableRobot
from Models.States import States
from Models.Actions import Actions
from Models.Zones import Zones
from Models.IllegalActions import IllegalActions, IllegalStateActions, IllegalZoneActions


class RobotController(ABC):
    def __init__(self, robot: ControllableRobot, Qtable: np.ndarray):
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
        self.speeds = [0,0]
        self.state_statistics = [0 for _ in range(10)]

        #Learning (Actions, states, zones)
        self.Q = Qtable
        self.illegal_zone_actions = IllegalZoneActions.General
        self.illegal_state_actions = IllegalStateActions.General
        self.illegal_actions = IllegalActions.General


    #Abstract Methods
    @abstractmethod
    def get_reward(self, action, state, zone):
        pass

    @abstractmethod
    def total_reward(self):
        pass

    def stop(self):
        self.robot.stop()

    #Methods
    def step(self, count):
        self.total_steps += 1
        new_zone = self.robot.get_zone()
        new_state = self.robot.get_state()
        
        if count - self.last_action > 100:
            self.action = None

        is_robot_in_way = self.robot.robot_in_way()
        # if we are stuck in this robot in the way state for a long time,
        # for example 1000 count, then we should just allow forward to push people out of the way
        if is_robot_in_way[0] and count - self.last_action < 1000: 
            avoid_action = Actions.Left
            self.speeds = self.speed_from_action(avoid_action)
        else:
            if (new_state != self.state or new_zone != self.zone or self.action is None) and (count - self.last_action > 3 or self.action not in [Actions.Left, Actions.Right]):
                self.state_statistics[new_state] += 1
                #if self.action != None:
                #    self.update_table(self.action, self.state, new_state, self.zone, new_zone)

                if random() <= 0.2:
                # explore
                    action = randint(0, 2)
                    while (action, new_zone) in self.illegal_zone_actions or (action, new_state) in self.illegal_state_actions or (action, new_state, new_zone) in self.illegal_actions:
                        action = randint(0,2)
                    self.action = action
                else:
                    # exploit
                    self.action = self.best_action(new_state, new_zone)
                self.last_action = count
                self.state = new_state
                self.zone = new_zone
                
            self.speeds = self.speed_from_action(self.action)        
        
        self.robot.drive(*self.speeds)        
        

    def max_future(self, state, zone):
        return np.max(self.Q[:, state, zone])

    def best_action(self, state, zone):
        action = np.argmax(self.Q[:, state, zone])
        return action

    def update_table(self, action, state, new_state, zone, new_zone):
        alpha = 0.1
        gamma = 0.9
        reward = self.get_reward(action, new_state, new_zone)
        self.Q[action, state, zone] = self.Q[action, state, zone] + alpha * (reward + gamma * self.max_future(new_state, new_zone) - self.Q[action, new_state, new_zone])

        for act in self.illegal_zone_actions:
            self.Q[act[0], :, act[1]] = -10

        for act in self.illegal_state_actions:
            self.Q[act[0], act[1], :] = -10

        for act in self.illegal_actions: #don't weight illegal actions positively
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
