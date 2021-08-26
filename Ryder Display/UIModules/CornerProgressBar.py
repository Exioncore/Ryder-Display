import math

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap

from UIModules.Utils import *
from Utils.Transitioner import Transitioner
from UIModules.ProgressBar import ProgressBar
from Utils.InternalMetrics import InternalMetrics
from UIModules.RoundProgressBar import RoundProgressBar

class CornerProgressBar(object):
    def __init__(self, window, transition_frames, settings): 
        # Retrieve settings
        ### UI Related
        self._transition_frames = transition_frames
        geometry = settings['geometry'] if 'geometry' in settings else [0, 0, 50, 50, 7]
        direction = settings['direction'] if 'direction' in settings and len(settings['direction']) == 2 else [4, 8]
        colors = settings['colors'] if 'colors' in settings else ['#2ecc71', '#141414', 'white']
        thickness = settings['thickness'] if 'thickness' in settings else [4, 0]
        gap = settings['gap'] if 'gap' in settings else 2
        radius = settings['corner-radius'] if 'corner-radius' in settings else 20
        # Process alignment
        if len(geometry) == 4: geometry.append(7)
        geometry, _ = getPosFromGeometry(geometry)
        ### Metric related
        self._metric = settings['metric']['name']
        bounds = settings['metric']['bounds']
        boundsRange = bounds[1] - bounds[0]
        self._elem_t = Transitioner(
            settings['metric']['bounds'][0],
            abs(boundsRange) / 100.0
        )
        self._elem_t.setMinMax(bounds[0], bounds[1])
        # Pre-Process some parameters
        if len(colors) < 3: colors.append(QColor('white'))
        if isinstance(thickness, list): 
            if len(thickness) < 2: thickness.append(0)
        else: 
            thickness = [thickness, 0]
        # Create components
        self._bars = []
        pos_x = {1: geometry[0], 7: geometry[0], 3: geometry[0] + geometry[2], 9: geometry[0] + geometry[2]}
        pos_y = {7: geometry[1], 9: geometry[1], 1: geometry[1] + geometry[3], 3: geometry[1] + geometry[3]}
        diameter = radius * 2
        segment_size = [0, radius * math.pi / 2, 0]
        # Horizontal to Vertical
        if direction[0] == 6 or direction[0] == 4:
            segment_size[0] = geometry[2] - thickness[1] - gap - radius; segment_size[2] = geometry[3] - thickness[1] - gap - radius
            size = segment_size[0] + segment_size[1] + segment_size[2]
            mul = boundsRange / size
            if direction[0] == 6 and direction[1] == 2:
                geometry1 = [pos_x[7], pos_y[7], geometry[2] - thickness[1] - gap - radius, 7]
                geometry2 = [pos_x[9], pos_y[9], diameter, diameter, 9]
                geometry3 = [pos_x[3], pos_y[3], geometry[3] - thickness[1] - gap - radius, 3]
                angle = [90, 0]
            elif direction[0] == 6 and direction[1] == 8:
                geometry1 = [pos_x[1], pos_y[1], geometry[2] - thickness[1] - gap - radius, 1]
                geometry2 = [pos_x[3], pos_y[3], diameter, diameter, 3]
                geometry3 = [pos_x[9], pos_y[9], geometry[3] - thickness[1] - gap - radius, 9]
                angle = [-90, 0]
            elif direction[0] == 4 and direction[1] == 8:
                geometry1 = [pos_x[3], pos_y[3], geometry[2] - thickness[1] - gap - radius, 3]
                geometry2 = [pos_x[1], pos_y[1], diameter, diameter, 1]
                geometry3 = [pos_x[7], pos_y[7], geometry[3] - thickness[1] - gap - radius, 7]
                angle = [270, 180]
            elif direction[0] == 4 and direction[1] == 2:
                geometry1 = [pos_x[9], pos_y[9], geometry[2] - thickness[1] - gap - radius, 9]
                geometry2 = [pos_x[7], pos_y[7], diameter, diameter, 7]
                geometry3 = [pos_x[1], pos_y[1], geometry[3] - thickness[1] - gap - radius, 1]
                angle = [90, 180]
        # Vertical to Horizontal
        elif direction[0] == 8 or direction[0] == 2:   
            segment_size[0] = geometry[3] - thickness[1] - gap - radius; segment_size[2] = geometry[2] - thickness[1] - gap - radius
            size = segment_size[0] + segment_size[1] + segment_size[2]
            mul = boundsRange / size
            if direction[0] == 8 and direction[1] == 6:
                geometry1 = [pos_x[1], pos_y[1], geometry[3] - thickness[1] - gap - radius, 1]
                geometry2 = [pos_x[7], pos_y[7], diameter, diameter, 7]
                geometry3 = [pos_x[9], pos_y[9], geometry[2] - thickness[1] - gap - radius, 9]
                angle = [180, 90]
            elif direction[0] == 8 and direction[1] == 4:
                geometry1 = [pos_x[3], pos_y[3], geometry[3] - thickness[1] - gap - radius, 3]
                geometry2 = [pos_x[9], pos_y[9], diameter, diameter, 9]
                geometry3 = [pos_x[7], pos_y[7], geometry[2] - thickness[1] - gap - radius, 7]
                angle = [0, 90]
            elif direction[0] == 2 and direction[1] == 4:
                geometry1 = [pos_x[9], pos_y[9], geometry[3] - thickness[1] - gap - radius, 9]
                geometry2 = [pos_x[3], pos_y[3], diameter, diameter, 3]
                geometry3 = [pos_x[1], pos_y[1], geometry[2] - thickness[1] - gap - radius, 1]
                angle = [0, -90]
            elif direction[0] == 2 and direction[1] == 6:
                geometry1 = [pos_x[7], pos_y[7], geometry[3] - thickness[1] - gap - radius, 7]
                geometry2 = [pos_x[1], pos_y[1], diameter, diameter, 1]
                geometry3 = [pos_x[3], pos_y[3], geometry[2] - thickness[1] - gap - radius, 3]
                angle = [180, 270]
        bounds1 = [bounds[0], bounds[0] + mul * segment_size[0]]
        bounds2 = [bounds1[1], bounds1[1] + mul * segment_size[1]]
        bounds3 = [bounds2[1], bounds[1]]
        # Create Bars
        self._bars.append(
            ProgressBar(window, 0, {
                'geometry': geometry1,
                'colors': colors,
                'thickness': thickness,
                'direction': direction[0],
                'bounds': bounds1
            })
        )
        self._bars.append(
            RoundProgressBar(window, 0, {
                'geometry': geometry2,
                'colors': colors,
                'thickness': thickness,
                'angle': angle,
                'edges-type': 0,
                'bounds': bounds2
            })
        )
        self._bars.append(
            ProgressBar(window, 0, {
                'geometry': geometry3,
                'colors': colors,
                'thickness': thickness,
                'direction': direction[1],
                'bounds': bounds3
            })
        )

    def setParent(self, p):
        for i in range(len(self._bars)):
            self._bars[i].setParent(p)

    def deleteLater(self):
        for i in range(len(self._bars)):
            self._bars[i].deleteLater()

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
            val = self._elem_t.update()
            for i in range(3):
                self._bars[i].updateDirect(val)
