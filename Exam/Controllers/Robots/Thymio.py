import os
os.system("(asebamedulla ser:name=Thymio-II &) && sleep 0.3")
import dbus
import dbus.mainloop.glib

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