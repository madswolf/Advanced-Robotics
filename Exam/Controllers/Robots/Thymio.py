import os
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")
import dbus
import dbus.mainloop.glib
from Models import Colors, Zones, States
import Vision.LED_capture as capture

from .ControllableRobot import ControllableRobot

class Thymio(ControllableRobot): 
    color_state_pairs = {
        
        Colors.Red: States.SeekerFront,
        Colors.Orange: States.SeekerFront,
        Colors.Blue: States.AvoiderFront,
        Colors.Green: States.AvoiderInSafeZoneFront,
        Colors.Purple: States.NoObs
    }

    def __init__(self):
        super().__init__()
        self.aseba = self.setup()
        self.color = Colors.Blue

    def drive(self, left_wheel_speed, right_wheel_speed):
        left_wheel = left_wheel_speed * 200
        right_wheel = right_wheel_speed * 200

        self.aseba.SendEventName("motor.target", [left_wheel, right_wheel])

    def stop(self):
        self.drive(0, 0)

    def robot_in_way(self): # (horizontal[5], ground[2])
        values = list(self.aseba.GetVariable("thymio-II", "prox.horizontal"))[:5]
        angles = [-40, -20, 0, 20, 40]
        stuff = [(x, angles[i]) for i,x in enumerate(values)]
        highest = max(stuff, key=lambda item: item[0])
        if(highest[0] < 200):
            return (True, highest[1])
        else:
            return (False, None)


    def get_zone(self):
        reflected = list(self.aseba.GetVariable("thymio-II", "prox.ground.reflected"))
        ambient = list(self.aseba.GetVariable("thymio-II", "prox.ground.ambiant"))
        
        ambient_high = ambient[0] > 0 or ambient[1] > 0
        reflected_left_high = reflected[0] > 400
        reflected_right_high = reflected[1] > 400


        if ambient_high:
            return Zones.Normal
        elif reflected_left_high or reflected_right_high:
            return Zones.Safe
        else:
            if not reflected_left_high:
                return Zones.EdgeLeft
            elif not reflected_right_high:
                return Zones.EdgeRight
            else:
                return Zones.EdgeFront
                
        

    def transmit(self, message):
        self.aseba.SendEventName("prox.comm.tx", [message])


    def receive(self):
        rx = self.aseba.GetVariable("thymio-II", "prox.comm.rx")
        if rx[0] != 0:
            return rx[0]
        return None

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
        # only check for opps 
        if self.color == Colors.Red or self.color == Colors.Orange:
            return self.check_for_color(Colors.Blue)
        elif self.color == Colors.Blue or self.color == Colors.Green:
            return self.check_for_color(Colors.RedOrange)
        return States.NoObs

    def check_for_color(self, color):
        keypoints = capture.get_keypoints(color)
        if len(keypoints) > 0:
            if keypoints[0].pt[0] < (640 / 3):
                return self.color_state_pairs[color] + 1
            elif keypoints[0].pt[0] > (640 / 3) * 2:
                return self.color_state_pairs[color] + 2
            else:
                return self.color_state_pairs[color]
        return States.NoObs

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
