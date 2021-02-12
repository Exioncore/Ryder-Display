import json
import base64
import requests
import socket

class Client(object):
    def __init__(self):
        self.url = 'http://192.168.1.114:9519'
        self.timeout = 2.5
        self.info = None
        self.status = None

    def subscribeToRyderEngine(self):
        return self._sendQuery({ "request":"subscribe" })

    def querySteamLogin(self):
        return self._sendQuery({ "request":"steamLoginUP" })

    def querySteam2FA(self):
        return self._sendQuery({ "request":"steamLogin2FA" })

    def update_system_info(self):
        self.info = self._sendQuery({ "request":"info" })
        return self.info

    def update_system_status(self):
        self.status = self._sendQuery({ "request":"status" })
        return self.status

    def requestForegroundProcessName(self):
        return self._sendQuery({ "request":"foregroundProcess" })

    def requestForegroundProcessIcon(self):
        return self._sendQuery({ "request":"foregroundProcessIcon" })

    def _sendQuery(self, data):
        try:
            return requests.post(self.url, data=json.dumps(data), timeout=self.timeout).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            return None



