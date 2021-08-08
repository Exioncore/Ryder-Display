import os
import time
import gevent
from PyQt5.QtCore import QTimer

from Network.RyderClient import RyderClient
from Utils.Transitioner import Transitioner
from Utils.InternalMetrics import InternalMetrics
from UIModules.ForegroundProcess import ForegroundProcess
from Utils.ConfigurationParser import ConfigurationParser
from UIModules.Notifications.NotificationsHandler import NotificationsHandler


class Home(object):
    _ui_dynamic = []
    _ui_static = []
    _fps = 1
    _window = None
    _timer : QTimer = None
    _status = None
    _last_update = 0

    # Class constructor
    def __init__(self, window):
        self._window = window
        RyderClient().addEndPoint('status', self._newStatus)

    # UI Elements
    def create_ui(self, path, ui, settings):
        # Clear UI
        for i in range(len(self._ui_dynamic)):
            self._ui_dynamic[i].setParent(None)
            self._ui_dynamic[i].deleteLater()
        for i in range(len(self._ui_static)):
            self._ui_static[i].setParent(None)
            self._ui_static[i].deleteLater()
        # Handle Timer
        if self._timer != None:
            self._timer.stop()
        else:
            self._timer = QTimer()
            self._timer.timeout.connect(self.update)

        # Initialize UI
        self._fps, self._ui_dynamic, self._ui_static = ConfigurationParser.createUI(self._window, path, ui, settings)
        self._timer.start(1000 / self._fps)

    def update(self):
        # Update UI
        for elem in self._ui_dynamic:
            elem.update(self._status)
        # Reset
        if self._status is not None:
            self._last_update = time.time()
            self._status = None

    def dispose(self):
        self._timer.stop()

    def _newStatus(self, data):
        self._status = data[1]
        InternalMetrics().update(self._status)
