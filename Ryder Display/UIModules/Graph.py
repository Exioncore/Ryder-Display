from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap

from UIModules.Utils import *
from QtComponents.QtGraph import QtGraph
from UIModules.DynamicLabel import DynamicLabel
from Utils.InternalMetrics import InternalMetrics

class Graph(object):
    def __init__(self, window, settings):
        self._first = True
        # Retrieve settings
        ### UI Related
        self._geometry = settings['geometry'] if 'geometry' in settings else [0, 0, 50, 50, 7]

        if 'graph' in settings:
            gs = settings['graph']
            self._n_values = gs['n-values'] if 'n-values' in gs else 30
            self._layout = gs['layout'] if 'layout' in gs else 0
            color = gs['color'] if 'color' in gs else '#2ecc71'
            thickness = gs['thickness'] if 'thickness' in gs else 4
        else:
            self._n_values = 30
            self._layout = 0
            color = '#2ecc71'
            thickness = 4

        if 'labels' in settings:
            ls = settings['labels']
            longest_text = ls['max-text-length'] if 'max-text-length' in ls else ''
            min_max_label_stylesheet = ls['min-max-stylesheet'] if 'min-max-stylesheet' in ls else ''
            current_label_stylesheet = ls['current-stylesheet'] if 'current-stylesheet' in ls else ''
        else:
            longest_text = ''
            min_max_label_stylesheet = ''
            current_label_stylesheet = ''
        # Process alignment
        if len(self._geometry) == 4: self._geometry.append(7)
        self._geometry, _ = getPosFromGeometry(self._geometry)
        ### Metric related
        self._metric = settings['metric']['name']
        unit = settings['unit'] if 'unit' in settings else ""
        # Create components
        ## MinMax labels
        if self._layout == 0:
            self._elem_max_label = DynamicLabel(window, {'stylesheet': min_max_label_stylesheet, 'geometry':[self._geometry[0], self._geometry[1], longest_text, 9], 'unit': unit, 'metric:':None})
            self._elem_min_label = DynamicLabel(window, {'stylesheet': min_max_label_stylesheet, 'geometry':[self._geometry[0], self._geometry[1], longest_text, 3], 'unit': unit, 'metric:':None})
            self._elem_max_label.move(
                self._geometry[0] + self._elem_max_label.width(), 
                self._geometry[1]
            )
            self._elem_min_label.move(
                self._geometry[0] + self._elem_min_label.width(),
                self._geometry[1] + self._geometry[3]
            )
        elif self._layout == 1:
            self._elem_max_label = DynamicLabel(window, {'stylesheet': min_max_label_stylesheet, 'geometry':[self._geometry[0], self._geometry[1], longest_text, 3], 'unit': unit, 'metric:':None})
            self._elem_min_label = DynamicLabel(window, {'stylesheet': min_max_label_stylesheet, 'geometry':[self._geometry[0], self._geometry[1], longest_text, 1], 'unit': unit, 'metric:':None})
        ## Current value label
        if self._layout == 0:
            self._elem_label = DynamicLabel(window, {'stylesheet': current_label_stylesheet, 'geometry':[self._geometry[0], self._geometry[1], longest_text, 4], 'unit': unit, 'metric:':None})
            self._elem_label.move((self._geometry[0] + self._geometry[2]) - self._elem_label.width(), self._geometry[1] + (self._elem_label.height() / 2))
            self._half_elem_label_height = self._elem_label.height() / 2
        elif self._layout == 1:
            self._elem_label = DynamicLabel(window, {'stylesheet': current_label_stylesheet, 'geometry':[self._geometry[0], self._geometry[1], longest_text, 2], 'unit': unit, 'metric:':None})
        ## Graph
        self._elem = QtGraph(window)
        self._elem.setForegroundColor(QColor(color))
        self._elem.setThickness(thickness)
        if self._layout == 0:
            self._elem.setGeometry(
                self._geometry[0] + self._elem_max_label.width() + 1, self._geometry[1],
                self._geometry[2] - self._elem_max_label.width() - self._elem_label.width() - 2, self._geometry[3]
            )
        elif self._layout == 1:
            # Labels positioning
            if self._elem_max_label.height() > self._elem_label.height():
                label_max_height = self._elem_max_label.height()
                self._elem_max_label.move(
                    self._geometry[0] + self._geometry[2], 
                    self._geometry[1] + self._geometry[3]
                )
                self._elem_min_label.move(
                    self._geometry[0],
                    self._geometry[1] + self._geometry[3]
                )
                self._elem_label.move(
                    self._geometry[0] + self._geometry[2] / 2, 
                    self._geometry[1] + self._geometry[3] - label_max_height + self._elem_label.height()
                )
            else:
                label_max_height = self._elem_label.height()
                self._elem_max_label.move(
                    self._geometry[0] + self._geometry[2], 
                    self._geometry[1] + self._geometry[3] - label_max_height + self._elem_max_label.height()
                )
                self._elem_min_label.move(
                    self._geometry[0],
                    self._geometry[1] + self._geometry[3] -  label_max_height + self._elem_min_label.height()
                )
                self._elem_label.move(
                    self._geometry[0] + self._geometry[2] / 2, 
                    self._geometry[1] + self._geometry[3]
                )
            # Graph sizing
            self._elem.setGeometry(
                self._geometry[0], self._geometry[1],
                self._geometry[2], self._geometry[3] - label_max_height
            )
        self._elem.setNumberOfValues(self._n_values)
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

            # Update Graph
            if self._first:
                value = self._elem.setHistory(value)
                self._first = False
            else:
                value = self._elem.setValue(value[-1])
            self._elem.update()
            # Update Label
            self._elem_label.updateDirect(value)
            if self._layout == 0:
                scalar = (self._geometry[3] - self._elem_label.height()) / (self._elem._bounds_range)
                self._elem_label.move(
                    self._elem_label.x(),
                    (self._geometry[1] + self._geometry[3] - self._half_elem_label_height) - (value - self._elem._bounds[0]) * scalar
                )
            # Update Max and Min Labels
            self._elem_max_label.updateDirect(self._elem._bounds[1])
            self._elem_min_label.updateDirect(self._elem._bounds[0])