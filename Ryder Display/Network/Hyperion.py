import json
import requests
import socket

from Utils.Singleton import Singleton

class Hyperion(object, metaclass=Singleton):
    def __init__(self):
        self._url = ''
        self._timeout = 2.0
        self.notifications = True
        self.moodLamp = False
        self.usbState = False
        self.ledState = False
        self.effects = []

    def setUrl(self, ip, port):
        self._url = 'http://' + ip + ':' + str(port) + '/json-rpc'

    def getState(self):
        state = requests.post(self._url, data=json.dumps({'command':'serverinfo'}), timeout=self._timeout).json()
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
        return requests.post(
            self._url,
            data=json.dumps({
                'command':'effect',
                'effect': {'name': name},
                'priority': priority,
                'duration': duration,
                'origin':'Ryder Display'
            }if duration > 0 else 
            {
                'command':'effect',
                'effect': {'name': name},
                'priority': priority,
                'origin':'Ryder Display'
            }),
            timeout=self._timeout
        ).json()

    def setLedState(self, enable: bool):
        self.ledState = enable
        return requests.post(
            self._url,
            data=json.dumps({
                'command':'componentstate',
                'componentstate': {'component':'LEDDEVICE','state': enable}
            }),
            timeout=self._timeout
        ).json()

    def setUsbCaptureState(self, enable: bool):
        self.usbState = enable
        return requests.post(
            self._url,
            data=json.dumps({
                'command':'componentstate',
                'componentstate': {'component':'V4L','state': enable}
            }),
            timeout=self._timeout
        ).json()

    def clear(self, priority):
        return requests.post(
            self._url,
            data=json.dumps({
                'command':'clear',
                'priority': priority
            }),
            timeout=self._timeout
        ).json()
