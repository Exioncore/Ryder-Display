import os
import time
import gevent

from PyQt5.QtCore import QTimer
from Utils.HomeConfigurationParser import HomeConfigurationParser
from Utils.Transitioner import Transitioner
from Utils.InternalMetrics import InternalMetrics
from Network.Client import Client
from Network.Server import Server

from UIModules.ForegroundProcess import ForegroundProcess

class Home(object):
    _ui = []
    _fps = 1
    _window = None
    _server : Server
    _timer : QTimer
    _status = None
    _last_update = 0

    # Class constructor
    def __init__(self, window, server : Server):
        self._window = window
        self._server = server
        
        server.add_endpoint('/status', 'status', self._newStatus)

    # UI Elements
    def create_ui(self, path):
        # Initialize
        path =  path + '/config.json'
        self._fps, self._ui = HomeConfigurationParser.parse(self._window, self._server, path)

        # Refresher
        self._timer = QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.start(1000 / self._fps)

    def _newStatus(self, request):
        self._status = request
        InternalMetrics().update(self._status)

    def update(self):
        # Update UI
        for elem in self._ui:
            elem.update(self._status)
        # Reset
        if self._status is not None:
            self._last_update = time.time()
            self._status = None
        # Attempt subscription if more than 10 seconds have passed since last update / attempt
        if time.time() - self._last_update > 10:
            self._last_update = time.time()
            Client().subscribeToRyderEngine()
