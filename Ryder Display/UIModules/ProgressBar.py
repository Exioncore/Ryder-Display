from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from UIModules.Utils import *
from Utils.Transitioner import Transitioner
from Utils.InternalMetrics import InternalMetrics
from QtComponents.QtStraightProgressBar import QtStraightProgressBar

class ProgressBar(object):
    def __init__(self, window, transition_frames, settings):
        # Retrieve settings
        ### UI Related
        self._transition_frames = transition_frames
        geometry = settings['geometry'] if 'geometry' in settings else [0, 0, 50, 7]
        colors = settings['colors'] if 'colors' in settings else ["#2ecc71", "#141414", "white"]
        edges_type = settings['edges-type'] if 'edges-type' in settings else [0, 0]
        thickness = settings['thickness'] if 'thickness' in settings else [4, 0]
        direction = settings['direction'] if 'direction' in settings else 6
        # Ensure edges_type is an array of 2 elements
        if isinstance(edges_type, list):
            if len(edges_type) < 2:
                edges_type.append(edges_type[0])
        else:
            edges_type = [edges_type, edges_type]
        # Ensure thickness is an array of 2 elements
        if isinstance(thickness, list):
            if len(thickness) < 2:
                thickness.append(0)
        else:
            thickness = [thickness, 0]
        # Colors
        for i in range(len(colors)): colors[i] = QColor(colors[i])
        if len(colors) < 3: colors.append(QColor('white'))
        # Process alignment
        if len(geometry) == 3: geometry.append(7)
        if direction == 4 or direction == 6 or direction == 46 or direction == 64:
            w = geometry[2] + thickness[1]
            h = thickness[0] + thickness[1]
        elif direction == 2 or direction == 8 or direction == 82 or direction == 28:
            w = thickness[0] + thickness[1]
            h = geometry[2] + thickness[1]
        geometry[2] = w
        geometry.insert(3, h)
        geometry, _ = getPosFromGeometry(geometry)
        ### Metric related
        if transition_frames > 0:
            self._metric = settings['metric']['name']
            bounds = settings['metric']['bounds']
            self._elem_t = Transitioner(
                bounds[0],
                abs(bounds[1] - bounds[0]) / 100.0
            )
            self._elem_t.setMinMax(bounds[0], bounds[1])
        else:
            bounds = settings['bounds'] if 'bounds' in settings else [0, 100]
        # Create components
        self._elem = QtStraightProgressBar(window)
        self._elem.setup(bounds, direction, thickness[1], colors, edges_type)
        self._elem.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        self._elem.redraw()
        self._elem.show()

    def setParent(self, p):
        self._elem.setParent(p)

    def deleteLater(self):
        self._elem.deleteLater()

    def updateDirect(self, val):
        self._elem.setValue(val)
        self._elem.update()

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
