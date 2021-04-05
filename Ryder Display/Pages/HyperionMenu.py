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
        self.setStyleSheet(
            'border: 1px solid rgba(237,174,28,100%);'
        )

    def createUI(self, path, pos=[0,0]):
        gap = 25
        size = [100, 100]
        w_size = [size[0] * 3 + gap * 4, size[1] + int(size[1] * (278 / 512)) + gap * 3]
        self._path = path

        self.setGeometry(
            pos[0] - w_size[0] / 2, pos[1] - w_size[1] / 2,
            w_size[0], w_size[1]
        )

        self._monitor = QPushButton('', self)
        self._monitor.setIcon(QIcon(path + '/Resources/Hyperion/Monitor.png'))
        self._monitor.setIconSize(QSize(size[0], size[1]))
        self._monitor.setGeometry(gap, gap, size[0], size[1])
        self._monitor.setStyleSheet('border: none;')
        self._monitor.clicked.connect(lambda:self.onClickMonitor())

        self._notifications = QPushButton('', self)
        self._notifications.setIconSize(QSize(size[0], size[1]))
        self._notifications.setGeometry(size[0] + gap * 2, gap, size[0], size[1])
        self._notifications.setStyleSheet('border: none;')
        self._notifications.clicked.connect(lambda:self.onClickNotifications())

        self._lamp = QPushButton('', self)
        self._lamp.setIcon(QIcon(path + '/Resources/Hyperion/Lamp.png'))
        self._lamp.setIconSize(QSize(size[0], size[1]))
        self._lamp.setGeometry(size[0] * 2 + gap * 3, gap, size[0], size[1])
        self._lamp.setStyleSheet('border: none;')
        self._lamp.clicked.connect(lambda:self.onClickLamp())

        self._power = QPushButton('', self)
        self._power.setIconSize(QSize(size[0], int(size[1] * (278 / 512))))
        self._power.setGeometry(size[0] + gap * 2, size[1] + gap * 2, size[0], int(size[1] * (278 / 512)))
        self._power.setStyleSheet('border: none;')
        self._power.clicked.connect(lambda:self.onClickPower())

        self._monitor.show()
        self._notifications.show()
        self._lamp.show()
        self._power.show()

    def show(self):
        if Hyperion().notifications:
            self._notifications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell.png'))
        else:
            self._notifications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell-crossed.png'))
        if Hyperion().ledState:
            self._power.setIcon(QIcon(self._path + '/Resources/On.png'))
        else:
            self._power.setIcon(QIcon(self._path + '/Resources/Off.png'))
        super().show()

    @pyqtSlot()
    def onClickMonitor(self):
        Hyperion().clear(50)
        Hyperion().setUsbCaptureState(True)
        Hyperion().moodLamp = False
        self.close()

    @pyqtSlot()
    def onClickNotifications(self):
        Hyperion().notifications = not Hyperion().notifications
        if Hyperion().notifications:
            self._notifications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell.png'))
        else:
            self._notifications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell-crossed.png'))

    @pyqtSlot()
    def onClickLamp(self):
        Hyperion().setUsbCaptureState(False)
        if not Hyperion().moodLamp:
            Hyperion().setEffect('Mood Lamp', 50, -1)
        else:
            Hyperion().clear(50)
        Hyperion().moodLamp = not Hyperion().moodLamp
        self.close()

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
            