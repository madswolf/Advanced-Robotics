import os
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")
import dbus
import dbus.mainloop.glib
from Models import Colors, Zones
import Vision.LED_capture as capture

from .ControllableRobot import ControllableRobot

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

    def robot_in_way(self): # (horizontal[5], ground[2])
        values = list(self.aseba.GetVariable("thymio-II", "prox.horizontal"))[:5]
        def index_to_angle(index):
            if(index == 0):
                return -40
            elif(index == 1):
                return -20
            elif(index == 2):
                return 0
            elif(index == 3):
                return 20
            else:
                return 40

        highest = max([(x, index_to_angle(i)) for x,i in enumerate(values)], key=lambda item: item[0])
        if(highest[0] < 100):
            return (True, highest[1])
        else:
            return (False, None)


    def get_zone(self):
        reflected = list(self.aseba.GetVariable("thymio-II", "prox.ground.reflected")),
        ambient = list(self.aseba.GetVariable("thymio-II", "prox.ground.ambiant"))
        
        ambient_high = ambient[0] > 0 or ambient[1] > 0
        reflected_left_high = reflected[0] > 400
        reflected_right_high = reflected[1] > 400


        if(ambient_high):
            return Zones.Normal
        elif(reflected_left_high or reflected_right_high):
            return Zones.Safe
        else:
            if(not reflected_left_high):
                return Zones.EdgeLeft
            elif(not reflected_right_high):
                return Zones.EdgeRight
            else:
                return Zones.EdgeFront
                
        

    def transmit(self, message):
        self.aseba.SendEventName("prox.comm.tx", [message])

    def receive(self):
        rx = self.aseba.GetVariable("thymio-II", "prox.comm.rx")
        if rx[0] != 0:
            return print(rx[0])

    def set_color(self, color):
        self.color = color
        if color == Colors.Blue:
            self.light_blue()
        elif color == Colors.Green:
            self.light_green()
        elif color == Colors.Orange:
            self.light_orange()
        elif color == Colors.Purple:
            self.light_purple()
        elif color == Colors.Red:
            self.light_red()

    # TODO Computer vision. Also with other colors than red
    def get_state(self):
        keypoints = capture.get_keypoints()

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


def light_red(self):
        self.aseba.SendEventName("leds.top", [32,0,0])
        self.aseba.SendEventName("leds.bottom.left", [32,0,0])
        self.aseba.SendEventName("leds.bottom.right", [32,0,0])
        self.aseba.SendEventName("leds.prox.h", [32,32,32,32,32,32,32,32])
        self.aseba.SendEventName("leds.prox.v", [32,32])
        self.aseba.SendEventName("leds.buttons", [32,32,32,32])
        self.aseba.SendEventName("leds.rc", [32])
        self.aseba.SendEventName("leds.temperature", [32,0])
        self.aseba.SendEventName("leds.sound", [0])
        self.aseba.SendEventName("leds.circle", [0,0,0,0,0,0,0,0])

def light_blue(self):
        self.aseba.SendEventName("leds.top", [0,0,32])
        self.aseba.SendEventName("leds.bottom.left", [0,0,32])
        self.aseba.SendEventName("leds.bottom.right", [0,0,32])
        self.aseba.SendEventName("leds.prox.h", [0,0,0,0,0,0,0,0])
        self.aseba.SendEventName("leds.prox.v", [0,0])
        self.aseba.SendEventName("leds.buttons", [0,0,0,0])
        self.aseba.SendEventName("leds.rc", [0])
        self.aseba.SendEventName("leds.temperature", [0,32])
        self.aseba.SendEventName("leds.sound", [32])
        self.aseba.SendEventName("leds.circle", [0,0,0,0,0,0,0,0])

def light_green(self):
        self.aseba.SendEventName("leds.top", [0,32,0])
        self.aseba.SendEventName("leds.bottom.left", [0,32,0])
        self.aseba.SendEventName("leds.bottom.right", [0,32,0])
        self.aseba.SendEventName("leds.prox.h", [0,0,0,0,0,0,0,0])
        self.aseba.SendEventName("leds.prox.v", [0,0])
        self.aseba.SendEventName("leds.buttons", [0,0,0,0])
        self.aseba.SendEventName("leds.rc", [0])
        self.aseba.SendEventName("leds.temperature", [0,0])
        self.aseba.SendEventName("leds.sound", [0])
        self.aseba.SendEventName("leds.circle", [0,0,0,0,0,0,0,0])

def light_purple(self):
        self.aseba.SendEventName("leds.top", [32,0,32])
        self.aseba.SendEventName("leds.bottom.left", [32,0,32])
        self.aseba.SendEventName("leds.bottom.right", [32,0,32])
        self.aseba.SendEventName("leds.prox.h", [0,0,0,0,0,0,0,0])
        self.aseba.SendEventName("leds.prox.v", [0,0])
        self.aseba.SendEventName("leds.buttons", [0,0,0,0])
        self.aseba.SendEventName("leds.rc", [0])
        self.aseba.SendEventName("leds.temperature", [0,0])
        self.aseba.SendEventName("leds.sound", [0])
        self.aseba.SendEventName("leds.circle", [0,0,0,0,0,0,0,0])

def light_orange(self):
        self.aseba.SendEventName("leds.top", [32,8,0])
        self.aseba.SendEventName("leds.bottom.left", [32,8,0])
        self.aseba.SendEventName("leds.bottom.right", [32,8,0])
        self.aseba.SendEventName("leds.prox.h", [0,0,0,0,0,0,0,0])
        self.aseba.SendEventName("leds.prox.v", [0,0])
        self.aseba.SendEventName("leds.buttons", [0,0,0,0])
        self.aseba.SendEventName("leds.rc", [0])
        self.aseba.SendEventName("leds.temperature", [0,0])
        self.aseba.SendEventName("leds.sound", [0])
        self.aseba.SendEventName("leds.circle", [32,32,32,32,32,32,32,32])
