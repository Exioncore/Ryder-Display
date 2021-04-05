import json
import requests
import socket
from Network.Client import Client
from Utils.Singleton import Singleton

class Hyperion(object, metaclass=Singleton):
    def __init__(self):
        self._url = ''
        self._timeout = 2.5
        self.notifications = True
        self.moodLamp = False
        self.usbState = False
        self.ledState = False
        self.effects = []

    def setUrl(self, ip, port):
        self._url = 'http://' + ip + ':' + str(port) + '/json-rpc'

    def getState(self):
        state = Client.sendQuerySync(self._url,{'command':'serverinfo'}, self._timeout)
        if state is not None:
            self.usbState = state['info']['components'][6]['enabled']
            self.ledState = state['info']['components'][7]['enabled']
            for effect in state['info']['activeEffects']:
                if effect['name'] == 'Mood Lamp' and effect['priority'] == 50:
                    self.moodLamp = True
            self.effects = []
            for effect in state['info']['effects']:
                self.effects.append(effect['name'])
            return True
        return False

    def setEffect(self, name, priority, duration):
        return Client.sendQuerySync(
            self._url,
            {
                'command':'effect',
                'effect': {'name': name},
                'priority': priority,
                'duration': duration,
                'origin':'Ryder Display'
            },
            self._timeout
        )

    def setLedState(self, enable: bool):
        self.ledState = enable
        return Client.sendQuerySync(
            self._url,
            {
                'command':'componentstate',
                'componentstate': {'component':'LEDDEVICE','state': enable}
            },
            self._timeout
        )

    def setUsbCaptureState(self, enable: bool):
        self.usbState = enable
        return Client.sendQuerySync(
            self._url,
            {
                'command':'componentstate',
                'componentstate': {'component':'V4L','state': enable}
            },
            self._timeout
        )

    def clear(self, priority):
        return Client.sendQuerySync(
            self._url,
            {
                'command':'clear',
                'priority': priority
            },
            self._timeout
        )
