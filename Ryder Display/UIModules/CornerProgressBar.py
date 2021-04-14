from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QRect

from QtComponents.QtStraightProgressBar import QtStraightProgressBar
from QtComponents.QtCornerProgressBar import QtCornerProgressBar
from Utils.Transitioner import Transitioner

class CornerProgressBar(object):
    def __init__(self, window, transition_frames, pos=[0,0], size=[50,50], direction=["left","up"], colors=["#2ecc71", "#141414"], thickness=4, radius=20, metric=[]):
        self._transition_frames = transition_frames
        self._metric = metric['name']
        self._elem_t = Transitioner(metric['bounds'][0])
        self._elem_t.setMinMax(metric['bounds'][0], metric['bounds'][1])
        # UI
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
        self._elem.setBounds(metric['bounds'][0], metric['bounds'][1])
        self._elem.redraw()
        self._elem.show()

    def _get_direction_from_text(dir):
        if dir == 'left':
            return QtStraightProgressBar.Direction.LEFT
        elif dir == 'right':
            return QtStraightProgressBar.Direction.RIGHT
        elif dir == 'up':
            return QtStraightProgressBar.Direction.UP
        elif dir == 'down':
            return QtStraightProgressBar.Direction.DOWN

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
