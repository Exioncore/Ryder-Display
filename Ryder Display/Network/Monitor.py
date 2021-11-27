import json

from Utils.Singleton import Singleton
from Network.RyderClient import RyderClient

class Monitor(object, metaclass=Singleton):
    """description of class"""
    def __init__(self):
        self.brightness = 100
        # Bind Server
        RyderClient().addEndPoint('on_connect', self._onConnect)
        RyderClient().addEndPoint('monitorBrightness', self._newMonitorBrightness)

    def setBrightness(self, value):
        RyderClient().send("[\"setMonitorBrightness\"," + str(value) + "]")
        self.brightness = value

    def _onConnect(self):
        RyderClient().send("[\"getMonitorBrightness\"]")

    def _newMonitorBrightness(self, data):
        self.brightness = data[1]
