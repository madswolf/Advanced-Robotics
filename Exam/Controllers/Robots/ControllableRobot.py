from abc import ABC, abstractmethod

class ControllableRobot(ABC):   
    def __init__():
        pass

    @abstractmethod
    def transmit():
        pass

    @abstractmethod
    def receive():
        pass

    @abstractmethod
    def drive():
        pass

    @abstractmethod
    def stop():
        pass

    @abstractmethod
    def set_color():
        pass

    @abstractmethod
    def get_state():
        pass

    @abstractmethod
    def get_zone():
        pass