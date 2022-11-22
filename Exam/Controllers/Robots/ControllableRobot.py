from abc import ABC, abstractmethod

class ControllableRobot(ABC):   
    def __init__(self):
        pass

    @abstractmethod
    def transmit(self, message):
        pass

    @abstractmethod
    def receive(self):
        pass

    @abstractmethod
    def drive(self, speed_left, speed_right):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def set_color(self, color):
        pass

    @abstractmethod
    def get_state(self):
        pass

    @abstractmethod
    def get_zone(self):
        pass

    @abstractmethod
    def robot_in_way(self):
        pass