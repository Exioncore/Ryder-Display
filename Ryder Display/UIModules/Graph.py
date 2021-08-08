from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap

from UIModules.Utils import *
from QtComponents.QtGraph import QtGraph
from UIModules.DynamicText import DynamicText
from Utils.InternalMetrics import InternalMetrics

class Graph(object):
    def __init__(self, window, settings):
        # Retrieve settings
        ### UI Related
        stylesheet = settings['stylesheet'] if 'stylesheet' in settings and len(settings['stylesheet']) == 2 else ["",""]
        color = settings['color'] if 'color' in settings else '#2ecc71'
        thickness = settings['thickness'] if 'thickness' in settings else 4
        longest_text = settings['max_text_length'] if 'max_text_length' in settings else ''
        n_values = settings['n_values'] if 'n_values' in settings else 30
        alignment = settings['alignment'] if 'alignment' in settings else 'top-left'
        self._pos = settings['pos'] if 'pos' in settings else [0, 0]
        self._size = settings['size'] if 'size' in settings else [50, 50]
        self._pos = getPosFromAlignment(self._pos, self._size, alignment)
        ### Metric related
        self._metric = settings['metric']['name']
        unit = settings['unit'] if 'unit' in settings else ""
        # Create components
        ## MinMax labels
        self._elem_max_label = DynamicText(window, {'stylesheet': stylesheet[0], 'max_text_length':longest_text, 'unit': unit, 'alignment':'top-right', 'pos':self._pos, 'metric:':None})
        self._elem_min_label = DynamicText(window, {'stylesheet': stylesheet[0], 'max_text_length':longest_text, 'unit': unit, 'alignment':'bottom-right', 'pos':self._pos, 'metric:':None})
        self._elem_max_label.move(
            self._pos[0] + self._elem_max_label.width(), 
            self._pos[1]
        )
        self._elem_min_label.move(
            self._pos[0] + self._elem_min_label.width(),
            self._pos[1] + self._size[1]
        )
        ## Current value label
        self._elem_label = DynamicText(window, {'stylesheet': stylesheet[1], 'max_text_length':longest_text, 'unit': unit, 'alignment':'left', 'pos':self._pos, 'metric:':None})
        self._elem_label.move((self._pos[0] + self._size[0]) - self._elem_label.width(), self._pos[1] + (self._elem_label.height() / 2))
        self._half_elem_label_height = self._elem_label.height() / 2
        ## Graph
        self._elem = QtGraph(window)
        self._elem.setForegroundColor(QColor(color))
        self._elem.setThickness(thickness)
        self._elem.setGeometry(
            self._pos[0] + self._elem_max_label.width() + 1, self._pos[1],
            self._size[0] - self._elem_max_label.width() - self._elem_label.width() - 2, self._size[1]
        )
        self._elem.setNumberOfValues(n_values)
        # Graph values bounds
        if isinstance(settings['metric']['bounds'][0], list):
            bound_min = settings['metric']['bounds'][0][0]
            dynamic_min = settings['metric']['bounds'][0][1]
        else:
            bound_min = settings['metric']['bounds'][0]
            dynamic_min = None
        if isinstance(settings['metric']['bounds'][1], list):
            bound_max = settings['metric']['bounds'][1][0]
            dynamic_max = settings['metric']['bounds'][1][1]
        else:
            bound_max = settings['metric']['bounds'][1]
            dynamic_max = None
        self._elem.setBounds(bound_min, bound_max, dynamic_min, dynamic_max)

        self._elem.show()

    def setParent(self, p):
        self._elem.setParent(p)
        self._elem_label.setParent(p)
        self._elem_max_label.setParent(p)
        self._elem_min_label.setParent(p)

    def deleteLater(self):
        self._elem.deleteLater()
        self._elem_label.deleteLater()
        self._elem_max_label.deleteLater()
        self._elem_min_label.deleteLater()

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
                value = InternalMetrics().metrics[self._metric[0][1:]]

            # Update Graph
            self._elem.setValue(value)
            self._elem.update()
            # Update Label
            scalar = (self._size[1] - self._elem_label.height()) / (self._elem._bounds_range)
            self._elem_label.updateDirect(value)
            self._elem_label.move(
                self._elem_label.x(),
                (self._pos[1] + self._size[1] - self._half_elem_label_height) - (value - self._elem._bounds[0]) * scalar
            )
            # Update Max and Min Labels
            self._elem_max_label.updateDirect(self._elem._bounds[1])
            self._elem_min_label.updateDirect(self._elem._bounds[0])