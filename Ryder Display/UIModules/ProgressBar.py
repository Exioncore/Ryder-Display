from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import Qt

from UIModules.Utils import *
from Utils.Transitioner import Transitioner
from Utils.InternalMetrics import InternalMetrics

class ProgressBar(object):
    def __init__(self, window, transition_frames, settings):
        # Retrieve settings
        ### UI Related
        self._transition_frames = transition_frames
        alignment = settings['alignment'] if 'alignment' in settings else 7
        direction = settings['direction'] if 'direction' in settings else 6
        pos = settings['pos'] if 'pos' in settings else [0, 0]
        size = settings['size'] if 'size' in settings else [50, 50]
        style = settings['stylesheet'] if 'stylesheet' in settings else ""
        colors = settings['colors'] if 'colors' in settings and len(settings['colors']) == 2 else ['#2ecc71', '#141414']
        # Process alignment
        pos, _ = getPosFromAlignment(pos, size, alignment)
        ### Metric related
        self._metric = settings['metric']['name']
        self._elem_t = Transitioner(
            settings['metric']['bounds'][0],
            abs(settings['metric']['bounds'][1] - settings['metric']['bounds'][0]) / 100.0
        )
        self._elem_t.setMinMax(settings['metric']['bounds'][0], settings['metric']['bounds'][1])
        # Create components
        self._elem = QProgressBar(window)
        self._elem.setGeometry(pos[0], pos[1], size[0], size[1])
        if direction == 4:
            self._elem.setOrientation(Qt.Horizontal)
            self._elem.setInvertedAppearance(True)
        elif direction == 6:
            self._elem.setOrientation(Qt.Horizontal)
        elif direction == 2:
            self._elem.setOrientation(Qt.Vertical)
            self._elem.setInvertedAppearance(True)
        elif direction == 8:
            self._elem.setOrientation(Qt.Vertical)
        self._elem.setMinimum(settings['metric']['bounds'][0])
        self._elem.setMaximum(settings['metric']['bounds'][1])
        self._elem.setTextVisible(False)
        # Glitch workaround for background color not applying
        if style == "":
            style = "border: 0;"
        self._elem.setStyleSheet("QProgressBar{"+style+"background:"+colors[1]+";}QProgressBar::chunk{"+style+"background:"+colors[0]+";}")
        self._elem.show()

    def setParent(self, p):
        self._elem.setParent(p)

    def deleteLater(self):
        self._elem.deleteLater()

    def update(self, refresh = False):
        if refresh:
            if self._metric[0][0] != "*":
                value = InternalMetrics().metrics
                # Navigate status json to desired metric
                for i in range(0, len(self._metric)):
                    if self._metric[i] in value:
                        value = value[self._metric[i]]
                    else:
                        # Interrupt update if desired metric is not found
                        return
            else:
                # Get computed metric
                value = InternalMetrics().metrics[self._metric[0]]
            value = value[-1]

            self._elem_t.transition(value, self._transition_frames)

        if not self._elem_t.isDone():
            self._elem.setValue(self._elem_t.update())
            self._elem.update()
