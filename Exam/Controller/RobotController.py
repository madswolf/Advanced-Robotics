from abc import ABC, abstractmethod
import numpy as np

from .Robots.ControllableRobot import ControllableRobot
from ..Models.States import States
from ..Models.Actions import  Actions
from ..Models.Zones import Zones


class RobotController(ABC):
    def __init__(self, robot: ControllableRobot):
        # Variables 
        ###########

        self.State = States.NoObs       
        self.Speed = 0.2
        self.Distance_threshold = 0.15
        self.Robot = robot

        #Learning (Actions, states, zones
        self.Q = np.zeros((4,10,3))
        self.Illegal_actions = []

    #Methods
    
    def max_future(self):
        return max(self.Q[self.State, 0], self.Q[self.State, 1])

    @abstractmethod(callable)
    def get_reward(self, state, action):
        reward = 0
        if state == States.NoObs:
            #left_wheel_velocity >= speed and right_wheel_velocity >= speed
            reward = 100
        #elif action == backwards:
        #    reward = -100
        return reward

    def best_action(self):
        return np.argmax(self.Q[self.State])

    def update_table(self, state, action, new_state):
        alpha = 0.1
        gamma = 0.9
        reward = self.get_reward(action)
        self.q[state, action] = self.q[state, action] + alpha * (reward + gamma * self.max_future(new_state) - self.q[state, action])

        for act in self.Illegal_actions: #don't weight illegal actions positively
            self.q[act[0], act[1]] = -10

    # input all sensor data and output proposed new state
    def calc_state(left, right):
        state = States.NoObs
        return state 

    def getZone(self):
        reading = self.Robot.sens()
        #implement zone logic
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
        left_speed, right_speed = self.speed_from_action(action)
        
        self.Robot.drive(left_speed, right_speed)
        
    def simulationstep(self, left_wheel_velocity, right_wheel_velocity):
        R = self.R
        for step in range(int(self.TimeStep/simulation_timestep)):     #step model time/timestep times
            v_x = cos(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2) 
            v_y = sin(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
            omega = (R*right_wheel_velocity - R*left_wheel_velocity)/(2*self.L)    

            self.x += v_x * simulation_timestep
            self.y += v_y * simulation_timestep
            self.q += omega * simulation_timestep