from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget

from UIModules.Utils import *
from Utils.Transitioner import Transitioner
from Utils.InternalMetrics import InternalMetrics
from QtComponents.QtRoundProgressBar import QtRoundProgressBar

class RoundProgressBar(object):
    def __init__(self, window, transition_frames, settings):
        # Retrieve settings
        ### UI Related
        self._transition_frames = transition_frames
        alignment = settings['alignment'] if 'alignment' in settings else 'top-left'
        pos = settings['pos'] if 'pos' in settings else [0, 0]
        size = settings['size'] if 'size' in settings else [50, 50]
        angle = settings['angle'] if 'angle' in settings else [0, 360]
        colors = settings['colors'] if 'colors' in settings else ["#2ecc71", "#141414"]
        thickness = settings['thickness'] if 'thickness' in settings else 4
        pos = getPosFromAlignment(pos, size, alignment)
        ### Metric related
        self._metric = settings['metric']['name']
        self._elem_t = Transitioner(
            settings['metric']['bounds'][0],
            abs(settings['metric']['bounds'][1] - settings['metric']['bounds'][0]) / 100.0
        )
        self._elem_t.setMinMax(settings['metric']['bounds'][0], settings['metric']['bounds'][1])
        # Create components
        self._elem = QtRoundProgressBar(window)
        self._elem.setGeometry(pos[0], pos[1], size[0], size[1])
        dir = 1 if angle[0] < angle[1] else -1
        min_angle = angle[0] if angle[0] < angle[1] else angle[1]
        max_angle = angle[0] if angle[0] >= angle[1] else angle[1]
        self._elem.setAngleBounds(min_angle, max_angle)
        self._elem.setForegroundColor(QColor(colors[0]))
        self._elem.setBackgroundColor(QColor(colors[1]))
        self._elem.setThickness(thickness)
        self._elem.setFillDirection(dir)
        self._elem.setBounds(settings['metric']['bounds'][0], settings['metric']['bounds'][1])
        self._elem.redraw()
        self._elem.show()

    def update(self, status):
        if status is not None:
            if self._metric[0][0] != "*":
                value = status
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

            self._elem_t.transition(value, self._transition_frames)

        if not self._elem_t.isDone():
            self._elem.setValue(self._elem_t.update())
            self._elem.update()
