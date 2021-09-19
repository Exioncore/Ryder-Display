import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QSlider, QLabel

from Network.Monitor import Monitor
from Network.Hyperion import Hyperion
from Network.RyderClient import RyderClient

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
        # Settings
        window_gap = 25
        v_gap = 10
        title_h = 25
        img_size = [100, 100]
        img_gap = [25, 25]
        slider_h = 10
        w_size = [
            img_size[0] * 3 + window_gap * 2 + img_gap[0] * 2, 
            img_size[1] + window_gap * 3 + v_gap * 5 + slider_h * 2 + title_h * 2
        ]
        # General setup
        self._path = path
        self.setGeometry(
            pos[0] - w_size[0] / 2, pos[1] - w_size[1] / 2,
            w_size[0], w_size[1]
        )
        y = window_gap
        # Hyperion Control Title
        title_stylesheet = "font-size: 18pt;border: 0;"
        title = QLabel("Hyperion", self)
        title.setGeometry(window_gap, y, w_size[0] - window_gap * 2, title_h)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(title_stylesheet)
        title.show()
        y += title_h + v_gap
        # Screen Capture Button
        self._monitor = QPushButton('', self)
        self._monitor.setIcon(QIcon(path + '/Resources/Hyperion/Monitor.png'))
        self._monitor.setIconSize(QSize(img_size[0], img_size[1]))
        self._monitor.setGeometry(window_gap, y, img_size[0], img_size[1])
        self._monitor.setStyleSheet('border: none;')
        self._monitor.clicked.connect(lambda:self.onClickMonitor()) 
        self._monitor.show()
        # Notifcations Button
        self._notifications = QPushButton('', self)
        self._notifications.setIconSize(QSize(img_size[0], img_size[1]))
        self._notifications.setGeometry(img_size[0] + window_gap + img_gap[0], y, img_size[0], img_size[1])
        self._notifications.setStyleSheet('border: none;')
        self._notifications.clicked.connect(lambda:self.onClickNotifications())
        if Hyperion().notifications:
            self._notifications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell.png'))
        else:
            self._notifications.setIcon(QIcon(self._path + '/Resources/Hyperion/Bell-crossed.png'))
        self._notifications.show()
        # Mood Lamp Button
        self._lamp = QPushButton('', self)
        self._lamp.setIcon(QIcon(path + '/Resources/Hyperion/Lamp.png'))
        self._lamp.setIconSize(QSize(img_size[0], img_size[1]))
        self._lamp.setGeometry(img_size[0] * 2 + window_gap + img_gap[0] * 2, y, img_size[0], img_size[1])
        self._lamp.setStyleSheet('border: none;')
        self._lamp.clicked.connect(lambda:self.onClickLamp())
        self._lamp.show()

        y+= img_size[1] + v_gap
        # Hyperion Brightness Control
        sliderStylesheet = (
            "QSlider{"
                "background-color: transparent;"
	            "border-style: outset;"
	            "border-radius: 10px;"
                "border: transparent;"
            "}"
            "QSlider::groove:horizontal{"
	            "height: 12px;"
	            "background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);"
	            "margin: 2px 0;"
                "border-radius:6px;"
            "}"
            "QSlider::handle:horizontal {"
                "width: 16px;"
	            "height: 16px;"
	            "margin: -5px 0px -5px 0px;"
	            "border-radius:11px;"
                "background-color:#0043a1;"
	            "border: 3px solid #0043a1;"
            "}"
        )
        self.lights_brightness_slider = QSlider(Qt.Horizontal, self)
        self.lights_brightness_slider.setFocusPolicy(Qt.NoFocus)
        self.lights_brightness_slider.setTickPosition(QSlider.NoTicks)
        self.lights_brightness_slider.setGeometry(
            window_gap, y,
            w_size[0] - window_gap * 2, window_gap
        )
        self.lights_brightness_slider.setStyleSheet(sliderStylesheet)
        self.lights_brightness_slider.setMinimum(0); self.lights_brightness_slider.setMaximum(100);
        self.lights_brightness_slider.valueChanged.connect(self.onClickSetLightsBrightness)
        self.lights_brightness_slider.setTracking(False)
        self.lights_brightness_slider.show()
        y += slider_h + window_gap
        # Monitor Control Title
        title_stylesheet = "font-size: 18pt;border: 0;"
        title = QLabel("Monitor", self)
        title.setGeometry(window_gap, y, w_size[0] - window_gap * 2, title_h)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(title_stylesheet)
        title.show()
        y += title_h + v_gap
        # Monitor Brightness Control
        self.monitor_brightness_slider = QSlider(Qt.Horizontal, self)
        self.monitor_brightness_slider.setFocusPolicy(Qt.NoFocus)
        self.monitor_brightness_slider.setTickPosition(QSlider.NoTicks)
        self.monitor_brightness_slider.setGeometry(
            window_gap, y,
            w_size[0] - window_gap * 2, window_gap
        )
        self.monitor_brightness_slider.setStyleSheet(sliderStylesheet)
        self.monitor_brightness_slider.setMinimum(0); self.monitor_brightness_slider.setMaximum(100);
        self.monitor_brightness_slider.valueChanged.connect(self.onClickSetMonitorBrightness)
        self.monitor_brightness_slider.setTracking(False)
        self.monitor_brightness_slider.show()

    def show(self):
        super().show()
        self.lights_brightness_slider.setValue(Hyperion().brightness)
        self.monitor_brightness_slider.setValue(Monitor().brightness)

    @pyqtSlot()
    def onClickSetLightsBrightness(self):
        print("Set lights brightness: " + str(self.lights_brightness_slider.value()))
        Hyperion().setBrightness(self.lights_brightness_slider.value())

    @pyqtSlot()
    def onClickSetMonitorBrightness(self):
        print("Set monitor brightness: " + str(self.monitor_brightness_slider.value()))
        RyderClient().send("[\"setMonitorBrightness\","+str(self.monitor_brightness_slider.value())+"]")

    @pyqtSlot()
    def onClickMonitor(self):
        # Ensure leds are enabled
        if not Hyperion().ledState:
            Hyperion().setLedState(True)
            self._btn_br[self._curr_i].setStyleSheet(self._btn_style + self._active_br_color)
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
            self._btn_br[self._curr_i].setStyleSheet(self._btn_style + self._active_br_color)
        # Ensure screen capture is off
        Hyperion().setUsbCaptureState(False)
        # Toggle mood lamp effect
        if not Hyperion().moodLamp:
            Hyperion().setEffect('Mood Lamp', 50, -1)
        else:
            Hyperion().clear(50)
        Hyperion().moodLamp = not Hyperion().moodLamp
         