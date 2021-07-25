import os
import glob
import base64

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, pyqtSlot, Qt, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLayout

from Network.RyderClient import RyderClient

class AppDrawer(object):
    apps = None
    _window: QMainWindow

    def __init__(self, window, settings, path = '', handleWindowSize = False):
        # Retrieve settings
        self._window = window
        self._handleWindowSize = handleWindowSize
        self._pos = settings['pos'] if 'pos' in settings else [0, 0]
        self._max_size = settings['size'] if 'size' in settings else [100, 100]
        self._gap = settings['gap'] if 'gap' in settings else 25
        self._iconSize = settings['iconSize'] if 'iconSize' in settings else 60

        self._buttons = []
        # Create cache folder if it doesn't exist
        self._iconsPath = path + '\\cache\\app_drawer\\'
        if not os.path.exists(self._iconsPath):
            os.makedirs(self._iconsPath)
        # Bind Server
        RyderClient().addEndPoint('on_connect', self._onConnect)
        RyderClient().addEndPoint('appLauncherData', self._updateAppDrawer)
        RyderClient().addEndPoint('appLauncherUpdate', self._requestNewAppLauncherData)

    def _onConnect(self):
        RyderClient().send("[\"appLauncher\"]")

    def _updateAppDrawer(self, data):
        apps = data[1]
        # Clear cache folder
        files = glob.glob(self._iconsPath + "*");
        for f in files:
            os.remove(f)
        # Clear buttons
        for i in range(len(self._buttons)):
            self._buttons[i].setParent(None)
            self._buttons[i].deleteLater()
        self._buttons = []
        # Determine min max coordinates
        min_x = 999; max_x = 0;
        min_y = 999; max_y = 0;
        for i in range(len(apps)):
            # X
            if apps[i]['x'] < min_x:
                min_x = apps[i]['x']
            if apps[i]['x'] > max_x:
                max_x = apps[i]['x']
            # Y
            if apps[i]['y'] < min_y:
                min_y = apps[i]['y']
            if apps[i]['y'] > max_y:
                max_y = apps[i]['y']
            # Icon
            path = self._iconsPath + str(i) + '.png'
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(apps[i]['icon']))
            pixmap.save(path)
        # App Grid Data
        delta_x = max_x + 1 - min_x
        delta_y = max_y + 1 - min_y
        # Size Popup Appropriately
        w_size = [
            self._gap + delta_x * self._iconSize + delta_x * self._gap,
            self._gap + delta_y * self._iconSize + delta_y * self._gap
        ]
        scale_factor = 1
        if w_size[0] > self._max_size[0]:
            scale_factor = self._max_size[0] / w_size[0]
        if w_size[1] > self._max_size[1]:
            factor = self._max_size[1] / w_size[1]
            scale_factor = factor if factor < scale_factor else scale_factor
        self._size = [
            self._gap * scale_factor + delta_x * self._iconSize * scale_factor + 
            delta_x * self._gap * scale_factor,
            self._gap * scale_factor + delta_y * self._iconSize * scale_factor + 
            delta_y * self._gap * scale_factor
        ]
        if self._handleWindowSize:
            self._window.setGeometry(-self._size[0] / 2, -self._size[1] / 2, self._size[0], self._size[1])
        # Place buttons for each App
        iconSize = self._iconSize * scale_factor
        gap = self._gap * scale_factor
        for i in range(len(apps)):
            x_loc = apps[i]['x'] - min_x
            y_loc = apps[i]['y'] - min_y
            btn = QPushButton('', self._window)
            btn.setIcon(QIcon(self._iconsPath + str(i)+'.png'))
            btn.setIconSize(QSize(iconSize, iconSize))
            btn.setGeometry(
                gap + x_loc * iconSize + gap  * x_loc,
                gap + y_loc * iconSize + gap  * y_loc,
                iconSize, iconSize
            )
            btn.setStyleSheet('border: none;')
            btn.clicked.connect(lambda x, i=i: self.onClick(i))
            btn.show()
            self._buttons.append(btn)

    def _requestNewAppLauncherData(self, data):
        RyderClient().send("[\"appLauncher\"]")

    def show(self):
        super().show()

    @pyqtSlot()
    def onClick(self, i: int):
        RyderClient().send("[\"launchApp\"," + str(i) + "]")
