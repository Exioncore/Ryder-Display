import json
import base64
import requests
import socket
import threading
from Utils.Singleton import Singleton

class Client(object, metaclass=Singleton):
    def __init__(self):
        self._url = ''
        self._timeout = 1.0

    def setUrl(self, ip, port):
        self._url = 'http://' + ip + ':' + str(port)

    def subscribeToRyderEngine(self):
        Client.sendQuery(self._url, { "request":"subscribe" }, self._timeout)

    def querySteamLogin(self):
        Client.sendQuery(self._url, { "request":"steamLoginUP" }, self._timeout)

    def querySteam2FA(self):
        Client.sendQuery(self._url, { "request":"steamLogin2FA" }, self._timeout)

    def queryDiscordLogin(self):
        Client.sendQuery(self._url, { "request":"discordLogin" }, self._timeout)

    def request_system_status(self):
        Client.sendQuery(self._url, { "request":"status" }, self._timeout)

    def requestForegroundProcessName(self):
        Client.sendQuery(self._url, { "request":"foregroundProcess" }, self._timeout)

    def requestForegroundProcessIcon(self):
        Client.sendQuery(self._url, { "request":"foregroundProcessIcon" }, self._timeout)

    def sendQuerySync(url, data, timeout):
        try:
            return requests.post(url, data=json.dumps(data), timeout=timeout).json()
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            return None

    def sendQuery(url, data, timeout):
        threading.Thread(target=Client.sendQuerySync, args=(url, data, timeout)).start()
