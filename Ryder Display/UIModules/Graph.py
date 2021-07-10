from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap

from QtComponents.QtGraph import QtGraph
from UIModules.DynamicText import DynamicText

class Graph(object):
    def __init__(self, window, pos=[0,0], size=[50,50], color="#2ecc71", thickness=4, longest_text="", stylesheet=["",""], unit="", n_values = 30, metric=[]):
        self._metric = metric
        self._height = size[1]
        # UI
        ## MinMax labels
        self._elem_max_label = DynamicText(window, {'stylesheet': stylesheet[0], 'max_text_length':longest_text, 'unit': unit, 'alignment':'right', 'pos':pos, 'metric:':None})
        self._elem_min_label = DynamicText(window, {'stylesheet': stylesheet[0], 'max_text_length':longest_text, 'unit': unit, 'alignment':'right', 'pos':pos, 'metric:':None})
        self._elem_max_label.move(
            pos[0], 
            self._elem_max_label._pos[1]
        )
        self._elem_min_label.move(
            pos[0], 
            pos[1] + size[1] - self._elem_min_label._size[1]
        )
        ## Current value label
        self._elem_label = DynamicText(window, {'stylesheet': stylesheet[1], 'max_text_length':longest_text, 'unit': unit, 'alignment':'left', 'pos':pos, 'metric:':None})
        self._elem_label.move((pos[0] + size[0]) - self._elem_label._size[0], (pos[1] + size[1]) - self._elem_label._size[1])
        self._half_elem_label_height = self._elem_label._size[1] / 2
        ## Graph
        self._elem = QtGraph(window)
        self._elem.setForegroundColor(QColor(color))
        self._elem.setThickness(thickness)
        self._elem.setGeometry(
            pos[0] + self._elem_max_label._size[0] + 1, pos[1],
            size[0] - self._elem_max_label._size[0] - self._elem_label._size[0] - 2, size[1]
        )
        self._elem.setNumberOfValues(n_values)
        self._elem.show()

    def update(self, status):
        if status is not None:
            value = status[self._metric[0]]
            for i in range(1, len(self._metric)):
                value = value[self._metric[i]]

            # Update Graph
            self._elem.setValue(value)
            self._elem.update()
            # Update Label
            scalar = (self._elem_max_label._pos[1] - self._elem_min_label._pos[1]) / (self._elem._bounds_range)
            self._elem_label.updateDirect(value)
            self._elem_label._label.move(
                self._elem_label._pos[0],
                self._elem_min_label._pos[1] + value * scalar
            )
            # Update Max and Min Labels
            self._elem_max_label.updateDirect(self._elem._bounds[1])
            self._elem_min_label.updateDirect(self._elem._bounds[0])