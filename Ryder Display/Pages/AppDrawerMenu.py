import os
import glob
import base64

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton

from Network.RyderClient import RyderClient

class AppDrawerMenu(QMainWindow):
    apps = None

    def __init__(self):
        super().__init__()
        # Initialize Popup
        self.setWindowTitle("App Drawer")
        self.setWindowFlag(Qt.Popup)
        self.setStyleSheet(
            'border: 1px solid rgba(237,174,28,100%);'
        )

    def createUI(self, path):
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
        gap = 25; iconSize = 60;
        # Size Popup Appropriately
        w_size = [
            gap + delta_x * iconSize + delta_x * gap,
            gap + delta_y * iconSize + delta_y * gap
        ]
        self.setGeometry(
            -w_size[0] / 2, -w_size[1] / 2,
            w_size[0], w_size[1]
        )
        # Place buttons for each App
        for i in range(len(apps)):
            x_loc = apps[i]['x'] - min_x
            y_loc = apps[i]['y'] - min_y
            btn = QPushButton('', self)
            btn.setIcon(QIcon(self._iconsPath + str(i)+'.png'))
            btn.setIconSize(QSize(iconSize, iconSize))
            btn.setGeometry(
                gap + x_loc * iconSize + gap * x_loc,
                gap + y_loc * iconSize + gap * y_loc,
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
