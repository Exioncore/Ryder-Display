import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtCore import QSize, pyqtSlot, Qt
from PyQt5.QtGui import QIcon

from Network.Hyperion import Hyperion

class HyperionMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hyperion")
        self.setWindowFlag(Qt.Popup)

    def createUI(self, instance, path, pos=[0,0]):
        self._instance = instance
        gap = 5
        size = [50, 50]
        w_size = [size[0] * 3 + gap * 2, size[1] + int(size[1] * (278 / 512)) + gap]
        self._path = path

        self.setGeometry(
            pos[0] - w_size[0] / 2, pos[1] - w_size[1] / 2,
            w_size[0], w_size[1]
        )

        self._monitor = QPushButton('', self)
        self._monitor.setIcon(QIcon(path + '/Resources/Hyperion/Monitor.png'))
        self._monitor.setIconSize(QSize(size[0], size[1]))
        self._monitor.setGeometry(0, 0, size[0], size[1])
        self._monitor.clicked.connect(lambda:self.onClickMonitor())

        self._notications = QPushButton('', self)
        if Hyperion().notifications:
            self._notications.setIcon(QIcon(path + '/Resources/Hyperion/Bell.png'))
        else:
            self._notications.setIcon(QIcon(path + '/Resources/Hyperion/Bell-crossed.png'))
        self._notications.setIconSize(QSize(size[0], size[1]))
        self._notications.setGeometry(0 + size[0] + gap, 0, size[0], size[1])
        self._notications.clicked.connect(lambda:self.onClickNotifications())

        self._lamp = QPushButton('', self)
        self._lamp.setIcon(QIcon(path + '/Resources/Hyperion/Lamp.png'))
        self._lamp.setIconSize(QSize(size[0], size[1]))
        self._lamp.setGeometry(0 + size[0] * 2 + gap * 2, 0, size[0], size[1])
        self._lamp.clicked.connect(lambda:self.onClickLamp())

        self._power = QPushButton('', self)
        if Hyperion().ledState:
            self._power.setIcon(QIcon(path + '/Resources/On.png'))
        else:
            self._power.setIcon(QIcon(path + '/Resources/Off.png'))
        self._power.setIconSize(QSize(size[0], int(size[1] * (278 / 512))))
        self._power.setGeometry(0 + size[0] + gap, size[1] + gap, size[0], int(size[1] * (278 / 512)))
        self._power.clicked.connect(lambda:self.onClickPower())

        self._monitor.show()
        self._notications.show()
        self._lamp.show()
        self._power.show()

    @pyqtSlot()
    def onClickMonitor(self):
        Hyperion().clear(50)
        Hyperion().setUsbCaptureState(True)
        Hyperion().moodLamp = False

    @pyqtSlot()
    def onClickNotifications(self):
        Hyperion().notifications = not Hyperion().notifications
        if Hyperion().notifications:
            self._notications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell.png'))
        else:
            self._notications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell-crossed.png'))

    @pyqtSlot()
    def onClickLamp(self):
        Hyperion().setUsbCaptureState(False)
        if not Hyperion().moodLamp:
            Hyperion().setEffect('Mood Lamp', 50, -1)
        else:
            Hyperion().clear(50)
        Hyperion().moodLamp = not Hyperion().moodLamp

    @pyqtSlot()
    def onClickPower(self):
        if Hyperion().ledState:
            self._power.setIcon(QIcon(self._path + '/Resources/Off.png'))
            Hyperion().setUsbCaptureState(False)
            Hyperion().setLedState(False)
            Hyperion().clear(50)
            Hyperion().moodLamp = False
        else:
            self._power.setIcon(QIcon(self._path + '/Resources/On.png'))
            Hyperion().setLedState(True)
            