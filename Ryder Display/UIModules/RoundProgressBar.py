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
        geometry = settings['geometry'] if 'geometry' in settings else [0, 0, 50, 50, 7]
        angle = settings['angle'] if 'angle' in settings else [0, 360]
        colors = settings['colors'] if 'colors' in settings else ["#2ecc71", "#141414", "white"]
        thickness = settings['thickness'] if 'thickness' in settings else [4, 0]
        center_out = settings['center-out'] if 'center-out' in settings else False
        edges_type = settings['edges-type'] if 'edges-type' in settings else [0, 0]
        edges_removal = settings['edges-removal'] if 'edges-removal' in settings else [0, 0]
        # Ensure edges_type and edges_removal is an array of 2 elements
        if isinstance(edges_type, list):
            if len(edges_type) < 2:
                edges_type.append(edges_type[0])
        else:
            edges_type = [edges_type, edges_type]
        if isinstance(edges_removal, list):
            if len(edges_removal) < 2:
                edges_removal.append(edges_removal[0])
        else:
            edges_removal = [edges_removal, edges_removal]
        # Process alignment
        if len(geometry) == 4: geometry.append(7)
        geometry, _ = getPosFromGeometry(geometry)
        ### Metric related
        self._metric = settings['metric']['name']
        self._elem_t = Transitioner(
            settings['metric']['bounds'][0],
            abs(settings['metric']['bounds'][1] - settings['metric']['bounds'][0]) / 100.0
        )
        self._elem_t.setMinMax(settings['metric']['bounds'][0], settings['metric']['bounds'][1])
        # Pre-process some parameters
        if not center_out:
            dir = 1 if angle[0] < angle[1] else -1
        else:
            dir = 0
        newAngle = []
        newAngle.append(angle[0] if angle[0] < angle[1] else angle[1])
        newAngle.append(angle[0] if angle[0] >= angle[1] else angle[1])
        for i in range(len(colors)): colors[i] = QColor(colors[i])
        if len(colors) < 3: colors.append(QColor('white'))
        if isinstance(thickness, list): 
            if len(thickness) < 2: thickness.append(0)
        else: 
            thickness = [thickness, 0]
        # Create component
        self._elem = QtRoundProgressBar(window)
        self._elem.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        self._elem.setup(
            settings['metric']['bounds'], newAngle, dir, colors, 
            thickness, edges_type, edges_removal
        )
        self._elem.redraw()
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
