import os
import time
import gevent
from PyQt5.QtCore import QTimer

from Network.RyderClient import RyderClient
from Utils.Transitioner import Transitioner
from Utils.InternalMetrics import InternalMetrics
from UIModules.ForegroundProcess import ForegroundProcess
from Utils.ConfigurationParser import ConfigurationParser


class Home(object):
    _ui = []
    _fps = 1
    _window = None
    _timer : QTimer
    _status = None
    _last_update = 0

    # Class constructor
    def __init__(self, window):
        self._window = window
        RyderClient().addEndPoint('status', self._newStatus)

    # UI Elements
    def create_ui(self, path, ui, settings):
        # Initialize
        self._fps, self._ui = ConfigurationParser.createUI(self._window, path, ui, settings)

        # Refresher
        self._timer = QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.start(1000 / self._fps)

    def _newStatus(self, data):
        self._status = data[1]
        InternalMetrics().update(self._status)

    def update(self):
        # Update UI
        for elem in self._ui:
            elem.update(self._status)
        # Reset
        if self._status is not None:
            self._last_update = time.time()
            self._status = None
