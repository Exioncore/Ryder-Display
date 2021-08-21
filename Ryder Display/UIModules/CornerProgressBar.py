from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap

from UIModules.Utils import *
from Utils.Transitioner import Transitioner
from Utils.InternalMetrics import InternalMetrics
from QtComponents.QtCornerProgressBar import QtCornerProgressBar
from QtComponents.QtStraightProgressBar import QtStraightProgressBar

class CornerProgressBar(object):
    def __init__(self, window, transition_frames, settings): 
        # Retrieve settings
        ### UI Related
        self._transition_frames = transition_frames
        alignment = settings['alignment'] if 'alignment' in settings else 7
        direction = settings['direction'] if 'direction' in settings and len(settings['direction']) == 2 else [4, 8]
        colors = settings['colors'] if 'colors' in settings and len(settings['colors']) == 2 else ['#2ecc71', '#141414']
        thickness = settings['thickness'] if 'thickness' in settings else 4
        gap = settings['gap'] if 'gap' in settings else 2
        radius = settings['cornerRadius'] if 'cornerRadius' in settings else 20
        pos = settings['pos'] if 'pos' in settings else [0, 0]
        size = settings['size'] if 'size' in settings else [50, 50]
        pos, _ = getPosFromAlignment(pos, size, alignment)
        ### Metric related
        self._metric = settings['metric']['name']
        self._elem_t = Transitioner(
            settings['metric']['bounds'][0],
            abs(settings['metric']['bounds'][1] - settings['metric']['bounds'][0]) / 100.0
        )
        self._elem_t.setMinMax(settings['metric']['bounds'][0], settings['metric']['bounds'][1])
        # Create components
        self._elem = QtCornerProgressBar(window)
        self._elem.setGeometry(pos[0], pos[1], size[0], size[1])
        self._elem.setFillDirection(
            CornerProgressBar._get_direction_from_text(direction[0]),
            CornerProgressBar._get_direction_from_text(direction[1])
        )
        self._elem.setForegroundColor(QColor(colors[0]))
        self._elem.setBackgroundColor(QColor(colors[1]))
        self._elem.setThickness(thickness)
        self._elem.setRadius(radius)
        self._elem.setGap(gap)
        self._elem.setBounds(settings['metric']['bounds'][0],settings['metric']['bounds'][1])
        self._elem.redraw()
        self._elem.show()

    def setParent(self, p):
        self._elem.setParent(p)

    def deleteLater(self):
        self._elem.deleteLater()

    def _get_direction_from_text(dir):
        if dir == 4:
            return QtStraightProgressBar.Direction.LEFT
        elif dir == 6:
            return QtStraightProgressBar.Direction.RIGHT
        elif dir == 8:
            return QtStraightProgressBar.Direction.UP
        elif dir == 2:
            return QtStraightProgressBar.Direction.DOWN

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
