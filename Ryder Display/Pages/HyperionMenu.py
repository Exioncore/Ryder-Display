import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton

from Network.Hyperion import Hyperion

class HyperionMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Hyperion")
        self.setWindowFlag(Qt.Popup)
        self.setStyleSheet(
            'border: 1px solid rgba(237,174,28,100%);'
        )

        self._br_color = 'color:rgb(200, 200, 200);'
        self._active_br_color = 'color:rgb(36, 138, 179);'
        self._off_br_color = 'color:rgb(179, 36, 36);'

    def setParent(self, p):
        return

    def deleteLater(self):
        return

    def createUI(self, path, pos=[0,0]):
        gap = 25
        size = [100, 100]
        w_size = [size[0] * 3 + gap * 4, size[1] + int(size[1] * (278 / 512)) + gap * 3]
        self._path = path

        self.setGeometry(
            pos[0] - w_size[0] / 2, pos[1] - w_size[1] / 2,
            w_size[0], w_size[1]
        )

        # Brightness Buttons
        self._btn_br = []
        self._btn_br_style = (
            'background-color:rgb(35, 35, 35); border-color:rgb(55, 55, 55);' +
            'font: bold 14px; text-align: center;'
        )
        self.br_vals = [0, 25, 50, 75, 100]
        btn_br_width = (w_size[0] - gap * 2) / len(self.br_vals)
        btn_br_x = gap
        for i in range(len(self.br_vals)):
            btn = QPushButton('', self)
            # Set Text
            if i == 0:
                btn.setText('Off')
            else:
                btn.setText(str(self.br_vals[i]) + '%')
            # Set the button position, sizing and hook click/tap method
            btn.setGeometry(btn_br_x, gap * 2 + size[1], btn_br_width, size[1] / 2)
            btn.clicked.connect(lambda x, i=i: self.onClickSetBrightness(i))
            btn.show()
            btn_br_x = btn_br_x + btn_br_width

            self._btn_br.append(btn)
        # Screen Capture Button
        self._monitor = QPushButton('', self)
        self._monitor.setIcon(QIcon(path + '/Resources/Hyperion/Monitor.png'))
        self._monitor.setIconSize(QSize(size[0], size[1]))
        self._monitor.setGeometry(gap, gap, size[0], size[1])
        self._monitor.setStyleSheet('border: none;')
        self._monitor.clicked.connect(lambda:self.onClickMonitor()) 
        # Notifcations Button
        self._notifications = QPushButton('', self)
        self._notifications.setIconSize(QSize(size[0], size[1]))
        self._notifications.setGeometry(size[0] + gap * 2, gap, size[0], size[1])
        self._notifications.setStyleSheet('border: none;')
        self._notifications.clicked.connect(lambda:self.onClickNotifications())
        if Hyperion().notifications:
            self._notifications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell.png'))
        else:
            self._notifications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell-crossed.png'))
        # Mood Lamp Button
        self._lamp = QPushButton('', self)
        self._lamp.setIcon(QIcon(path + '/Resources/Hyperion/Lamp.png'))
        self._lamp.setIconSize(QSize(size[0], size[1]))
        self._lamp.setGeometry(size[0] * 2 + gap * 3, gap, size[0], size[1])
        self._lamp.setStyleSheet('border: none;')
        self._lamp.clicked.connect(lambda:self.onClickLamp())

        self._monitor.show()
        self._notifications.show()
        self._lamp.show()

    def show(self):
        super().show()
        # Highlight correct brightness button
        for i in range(len(self.br_vals)):
            if Hyperion().brightness == self.br_vals[i]:
                if i == 0:
                    self._curr_i = i
                    self._btn_br[i].setStyleSheet(self._btn_br_style + self._off_br_color)
                else:
                    self._curr_i = i
                    if Hyperion().ledState:
                        self._btn_br[i].setStyleSheet(self._btn_br_style + self._active_br_color)
                    else:
                        self._btn_br[i].setStyleSheet(self._btn_br_style + self._off_br_color)
            else:
                self._btn_br[i].setStyleSheet(self._btn_br_style + self._br_color)

    @pyqtSlot()
    def onClickSetBrightness(self, i):
        # Reset button styling
        self._btn_br[self._curr_i].setStyleSheet(self._btn_br_style + self._br_color)
        # Apply birghtness value
        if i > 0:
            if not Hyperion().ledState:
                Hyperion().setLedState(True)
            Hyperion().setBrightness(self.br_vals[i])
            self._curr_i = i
        else:
            Hyperion().setUsbCaptureState(False)
            Hyperion().setLedState(False)
            Hyperion().clear(50)
            Hyperion().moodLamp = False
        # Set button styling
        if i == 0:
            self._btn_br[self._curr_i].setStyleSheet(self._btn_br_style + self._off_br_color)
        else:
            self._btn_br[self._curr_i].setStyleSheet(self._btn_br_style + self._active_br_color)

    @pyqtSlot()
    def onClickMonitor(self):
        # Ensure leds are enabled
        if not Hyperion().ledState:
            Hyperion().setLedState(True)
            self._btn_br[self._curr_i].setStyleSheet(self._btn_br_style + self._active_br_color)
        # Enable or disable screen capture
        if not Hyperion().usbState:
            Hyperion().clear(50)
            Hyperion().setUsbCaptureState(True)
            Hyperion().moodLamp = False
        else:
            Hyperion().setUsbCaptureState(False)

    @pyqtSlot()
    def onClickNotifications(self):
        Hyperion().notifications = not Hyperion().notifications
        if Hyperion().notifications:
            self._notifications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell.png'))
        else:
            self._notifications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell-crossed.png'))

    @pyqtSlot()
    def onClickLamp(self):
        # Ensure leds are enabled
        if not Hyperion().ledState:
            Hyperion().setLedState(True)
            self._btn_br[self._curr_i].setStyleSheet(self._btn_br_style + self._active_br_color)
        # Ensure screen capture is off
        Hyperion().setUsbCaptureState(False)
        # Toggle mood lamp effect
        if not Hyperion().moodLamp:
            Hyperion().setEffect('Mood Lamp', 50, -1)
        else:
            Hyperion().clear(50)
        Hyperion().moodLamp = not Hyperion().moodLamp
         