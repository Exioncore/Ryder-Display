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
        self._pos = settings['pos'] if 'pos' in settings else [0, 0]
        self._size = settings['size'] if 'size' in settings else [50, 50]
        alignment = settings['alignment'] if 'alignment' in settings else 7

        if 'graph' in settings:
            gs = settings['graph']
            n_values = gs['n_values'] if 'n_values' in gs else 30
            self._layout = gs['layout'] if 'layout' in gs else 0
            color = gs['color'] if 'color' in gs else '#2ecc71'
            thickness = gs['thickness'] if 'thickness' in gs else 4
        else:
            n_values = 30
            self._layout = 0
            color = '#2ecc71'
            thickness = 4

        if 'labels' in settings:
            ls = settings['labels']
            longest_text = ls['max_text_length'] if 'max_text_length' in ls else ''
            min_max_label_stylesheet = ls['min_max_stylesheet'] if 'min_max_stylesheet' in ls else ''
            current_label_stylesheet = ls['current_stylesheet'] if 'current_stylesheet' in ls else ''
        else:
            longest_text = ''
            min_max_label_stylesheet = ''
            current_label_stylesheet = ''
        # Process alignment
        self._pos, _ = getPosFromAlignment(self._pos, self._size, alignment)
        ### Metric related
        self._metric = settings['metric']['name']
        unit = settings['unit'] if 'unit' in settings else ""
        # Create components
        ## MinMax labels
        if self._layout == 0:
            self._elem_max_label = DynamicText(window, {'stylesheet': min_max_label_stylesheet, 'max_text_length':longest_text, 'unit': unit, 'alignment':9, 'pos':self._pos, 'metric:':None})
            self._elem_min_label = DynamicText(window, {'stylesheet': min_max_label_stylesheet, 'max_text_length':longest_text, 'unit': unit, 'alignment':3, 'pos':self._pos, 'metric:':None})
            self._elem_max_label.move(
                self._pos[0] + self._elem_max_label.width(), 
                self._pos[1]
            )
            self._elem_min_label.move(
                self._pos[0] + self._elem_min_label.width(),
                self._pos[1] + self._size[1]
            )
        elif self._layout == 1:
            self._elem_max_label = DynamicText(window, {'stylesheet': min_max_label_stylesheet, 'max_text_length':longest_text, 'unit': unit, 'alignment':3, 'pos':self._pos, 'metric:':None})
            self._elem_min_label = DynamicText(window, {'stylesheet': min_max_label_stylesheet, 'max_text_length':longest_text, 'unit': unit, 'alignment':1, 'pos':self._pos, 'metric:':None})
        ## Current value label
        if self._layout == 0:
            self._elem_label = DynamicText(window, {'stylesheet': current_label_stylesheet, 'max_text_length':longest_text, 'unit': unit, 'alignment':4, 'pos':self._pos, 'metric:':None})
            self._elem_label.move((self._pos[0] + self._size[0]) - self._elem_label.width(), self._pos[1] + (self._elem_label.height() / 2))
            self._half_elem_label_height = self._elem_label.height() / 2
        elif self._layout == 1:
            self._elem_label = DynamicText(window, {'stylesheet': current_label_stylesheet, 'max_text_length':longest_text, 'unit': unit, 'alignment':2, 'pos':self._pos, 'metric:':None})
        ## Graph
        self._elem = QtGraph(window)
        self._elem.setForegroundColor(QColor(color))
        self._elem.setThickness(thickness)
        if self._layout == 0:
            self._elem.setGeometry(
                self._pos[0] + self._elem_max_label.width() + 1, self._pos[1],
                self._size[0] - self._elem_max_label.width() - self._elem_label.width() - 2, self._size[1]
            )
        elif self._layout == 1:
            # Labels positioning
            if self._elem_max_label.height() > self._elem_label.height():
                label_max_height = self._elem_max_label.height()
                self._elem_max_label.move(
                    self._pos[0] + self._size[0], 
                    self._pos[1] + self._size[1]
                )
                self._elem_min_label.move(
                    self._pos[0],
                    self._pos[1] + self._size[1]
                )
                self._elem_label.move(
                    self._pos[0] + self._size[0] / 2, 
                    self._pos[1] + self._size[1] - label_max_height + self._elem_label.height()
                )
            else:
                label_max_height = self._elem_label.height()
                self._elem_max_label.move(
                    self._pos[0] + self._size[0], 
                    self._pos[1] + self._size[1] - label_max_height + self._elem_max_label.height()
                )
                self._elem_min_label.move(
                    self._pos[0],
                    self._pos[1] + self._size[1] -  label_max_height + self._elem_min_label.height()
                )
                self._elem_label.move(
                    self._pos[0] + self._size[0] / 2, 
                    self._pos[1] + self._size[1]
                )
            # Graph sizing
            self._elem.setGeometry(
                self._pos[0], self._pos[1],
                self._size[0], self._size[1] - label_max_height
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
            value = self._elem.setValue(value)
            self._elem.update()
            # Update Label
            self._elem_label.updateDirect(value)
            if self._layout == 0:
                scalar = (self._size[1] - self._elem_label.height()) / (self._elem._bounds_range)
                self._elem_label.move(
                    self._elem_label.x(),
                    (self._pos[1] + self._size[1] - self._half_elem_label_height) - (value - self._elem._bounds[0]) * scalar
                )
            # Update Max and Min Labels
            self._elem_max_label.updateDirect(self._elem._bounds[1])
            self._elem_min_label.updateDirect(self._elem._bounds[0])