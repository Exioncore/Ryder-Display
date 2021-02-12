import math
from math import ceil
from QtComponents.QtRoundProgressBar import QtRoundProgressBar
from QtComponents.QtStraightProgressBar import QtStraightProgressBar
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QRect

class QtCornerProgressBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._bounds = [0, 100]
        self._bounds_range = self._bounds[1] - self._bounds[0]
        self._current_value = 0
        self._fill_direction = [QtStraightProgressBar.Direction.UP, 1, QtStraightProgressBar.Direction.RIGHT]

        # Cache commonly reused variables
        self._thickness = 10
        self._radius = 20

        self.bars = [QtStraightProgressBar(self), QtRoundProgressBar(self), QtStraightProgressBar(self)]
        self.bars[1].setRefreshOverdraw(5.0)
        self._setupBars()

    def _setupBars(self):
        p0 = [0, 0]
        s0 = [0, 0]
        p1 = [0, 0]
        s1 = [0, 0]
        c = [0, 0]
        c_a = [0, 0]
        c_d = 1
        w = self.width() - self._radius - 1
        h = self.height() - self._radius - 1

        if self._fill_direction[2] == QtStraightProgressBar.Direction.UP:
            ### Sizing
            # First bar
            s0[0] = w
            s0[1] = self._thickness
            # Second bar
            s1[0] = self._thickness
            s1[1] = h
            ### Position
            p0[1] = self.height() - self._thickness
            p1[1] = 0
            c[1] = self.height() - self._radius * 2
            if self._fill_direction[0] == QtStraightProgressBar.Direction.LEFT:
                p0[0] = self._radius + 1
                p1[0] = 0
                c[0] = 0
                c_a = [180, 270]
                c_d = -1
            elif self._fill_direction[0] == QtStraightProgressBar.Direction.RIGHT:
                p0[0] = 0
                p1[0] = self.width() - self._thickness
                c[0] = self.width() - self._radius * 2
                c_a = [-90, 0]
                c_d = 1
        elif self._fill_direction[2] == QtStraightProgressBar.Direction.DOWN:
            ### Sizing
            # First bar
            s0[0] = w
            s0[1] = self._thickness
            # Second bar
            s1[0] = self._thickness
            s1[1] = h
            ### Position
            p0[1] = 0
            p1[1] = self._radius + 1
            c[1] = 0
            if self._fill_direction[0] == QtStraightProgressBar.Direction.LEFT:
                p0[0] = self._radius + 1
                p1[0] = 0
                c[0] = 0
                c_a = [90, 180]
                c_d = 1
            elif self._fill_direction[0] == QtStraightProgressBar.Direction.RIGHT:
                p0[0] = 0
                p1[0] = self.width() - self._thickness
                c[0] = self.width() - self._radius * 2
                c_a = [0, 90]
                c_d = -1
        elif self._fill_direction[2] == QtStraightProgressBar.Direction.RIGHT:
            ### Sizing
            # First bar
            s0[0] = self._thickness
            s0[1] = h
            # Second bar
            s1[0] = w
            s1[1] = self._thickness
            ### Position
            p1[0] = self._radius + 1
            p0[0] = 0
            c[0] = 0
            if self._fill_direction[0] == QtStraightProgressBar.Direction.UP:
                p1[1] = 0
                p0[1] = self._radius + 1
                c[1] = 0
                c_a = [90, 180]
                c_d = -1
            elif self._fill_direction[0] == QtStraightProgressBar.Direction.DOWN:
                p1[1] = self.height() - self._thickness
                p0[1] = 0
                c[1] = self.height() - self._radius * 2
                c_a = [180, 270]
                c_d = 1
        elif self._fill_direction[2] == QtStraightProgressBar.Direction.LEFT:
            ### Sizing
            # First bar
            s0[0] = self._thickness
            s0[1] = h
            # Second bar
            s1[0] = w
            s1[1] = self._thickness
            ### Position
            p1[0] = 0
            p0[0] = self.width() - self._thickness
            c[0] = self.width() - self._radius * 2
            if self._fill_direction[0] == QtStraightProgressBar.Direction.UP:
                p1[1] = 0
                p0[1] = self._radius + 1
                c[1] = 0
                c_a = [0, 90]
                c_d = 1
            elif self._fill_direction[0] == QtStraightProgressBar.Direction.DOWN:
                p1[1] = self.height() - self._thickness
                p0[1] = 0
                c[1] = self.height() - self._radius * 2
                c_a = [-90, 0]
                c_d = -1

        self._fill_direction[1] = c_d
        # Setup each bar
        self.bars[0].setGeometry(p0[0], p0[1], s0[0], s0[1])
        self.bars[0].setFillDirection(self._fill_direction[0])
        self.bars[1].setGeometry(c[0], c[1], self._radius * 2, self._radius * 2)
        self.bars[1].setThickness(self._thickness)
        self.bars[1].setAngleBounds(c_a[0], c_a[1])
        self.bars[1].setFillDirection(self._fill_direction[1])
        self.bars[1].redraw()
        self.bars[2].setGeometry(p1[0], p1[1], s1[0], s1[1])
        self.bars[2].setFillDirection(self._fill_direction[2])
        # Calculate length of each bar
        segment_lengths = [0, self._radius * math.pi / 2, 0]
        if self._fill_direction[0] == QtStraightProgressBar.Direction.UP or self._fill_direction[0] == QtStraightProgressBar.Direction.DOWN:
            segment_lengths[0] = h
            segment_lengths[2] = w
        else:
            segment_lengths[0] = w
            segment_lengths[2] = h
        # Set value bounds for each bar
        total_len = segment_lengths[0] + segment_lengths[1] + segment_lengths[2]
        start = 0
        end = self._bounds_range * (segment_lengths[0] / total_len) + self._bounds[0]
        self.bars[0].setBounds(start, end)
        start = end
        end = self._bounds_range * ((segment_lengths[0] + segment_lengths[1])  / total_len) + self._bounds[0]
        self.bars[1].setBounds(start, end)
        self.bars[2].setBounds(end, self._bounds[1])

    def setFillDirection(self, dir0, dir2):
        self._fill_direction[0] = dir0
        self._fill_direction[2] = dir2
        self._setupBars()

    def setRadius(self, val):
        self._radius = val
        self._setupBars()

    def setBounds(self, start, end):
        self._bounds = [start, end]
        self._bounds_range = end - start
        self._setupBars()

    def setForegroundColor(self, color):
        for i in range(3):
            self.bars[i].setForegroundColor(color)

    def setBackgroundColor(self, color):
        for i in range(3):
            self.bars[i].setBackgroundColor(color)

    def redraw(self):
        for i in range(3):
            self.bars[i].redraw()

    def setValue(self, val):
        self._current_value = max(self._bounds[0], min(val, self._bounds[1]))

    def setThickness(self, val):
        self._thickness = val
        self._setupBars()

    def setGeometry(self, x, y, w, h):
        """ Override setGeometry method """
        super().setGeometry(x, y, w, h)

        self._setupBars()

    def paintEvent(self, e):
        """ Override Paint Function """
        for i in range(3):
            self.bars[i].setValue(self._current_value)



