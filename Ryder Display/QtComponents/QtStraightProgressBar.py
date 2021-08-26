from enum import Enum
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap

class QtStraightProgressBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialized = self._redraw = False

    def setup(self,
              bounds = [0, 100], fillDirection = 6, border_thickness = 0,
              colors = [QColor('red'), QColor('black'), QColor('white')], capType = [0, 0]
        ):
        # Bounds
        self._bounds = bounds
        self._bounds_range = self._bounds[1] - self._bounds[0]
        self._old_value = self._current_value = self._bounds[0]
        # Fill Direction
        self._fill_direction = fillDirection
        if self._fill_direction == 4 or self._fill_direction == 6 or self._fill_direction == 46 or self._fill_direction == 64:
            self._horizontal = True
        elif self._fill_direction == 8 or self._fill_direction == 2 or self._fill_direction == 82 or self._fill_direction == 28:
            self._horizontal = False
        # Colors [0 = foreground color, 1 = background color, 2 = border color]
        self._colors = colors
        # Border Thickness
        self._border_thickness = border_thickness
        # Cap 0 = SquareCap, 1 = RoundCap, 2 = FlatCap
        self._cap = capType
        # Internal variables
        self._pen = QPen(self._colors[0], 0, Qt.SolidLine)
        self._pen.setCapStyle(Qt.FlatCap)
        # Ready Flag
        self._initialized = True

    def setValue(self, val):
        self._current_value = max(self._bounds[0], min(val, self._bounds[1]))

    def setGeometry(self, x, y, w, h):
        """ Override setGeometry method """
        super().setGeometry(x, y, w, h)
        if self._initialized:
            s = [self.width() - self._border_thickness, self.height() - self._border_thickness]
            self._length = s[0] if self._horizontal else s[1]
            self._thickness = s[1] if self._horizontal else s[0]
            self._mul = self._length / self._bounds_range
            if self._fill_direction == 46 or self._fill_direction == 64:
                self._mid = self.width() / 2
                self._mul /= 2
            elif self._fill_direction == 82 or self._fill_direction == 28:
                self._mid = self.height() / 2
                self._mul /= 2
        # Reset PixMaps
        self._background_buffer = QPixmap(self.width(), self.height())
        self._background_buffer.fill(Qt.transparent)
        self._foreground_t_buffer = QPixmap(self.width(), self.height())
        self._foreground_t_buffer.fill(Qt.transparent)
        self._foreground_buffer = QPixmap(self.width(), self.height())
        self._foreground_buffer.fill(Qt.transparent)

    def redraw(self):
        self._redraw = True

    def _drawLine(self, paint, ofst_start, ofst_end):
        self._pen.setCapStyle(Qt.FlatCap)
        paint.setPen(self._pen)
        # Draw Main Bar
        if self._horizontal == True:
            paint.drawLine(ofst_start, self.height() / 2, self.width() - ofst_end, self.height() / 2)
        else:
            paint.drawLine(self.width() / 2, ofst_start, self.width() / 2, self.height() - ofst_end)
        # Draw Round Caps
        if self._cap[0] == 1 or self._cap[1] == 1:
            self._pen.setCapStyle(Qt.RoundCap)
            paint.setPen(self._pen)
            if self._horizontal == True:
                if self._cap[0] == 1: paint.drawLine(ofst_start, self.height() / 2, self.width() / 2, self.height() / 2)
                if self._cap[1] == 1: paint.drawLine(self.width() / 2, self.height() / 2, self.width() - ofst_end, self.height() / 2)
            else:
                if self._cap[0] == 1: paint.drawLine(self.width() / 2, ofst_start, self.width() / 2, self.height() / 2)
                if self._cap[1] == 1: paint.drawLine(self.width() / 2, self.height() / 2, self.width() / 2, self.height() - ofst_end)

    def paintEvent(self, e):
        """ Override Paint Function """
        if not self._initialized: return
        paint = QPainter()
        # Draw the bar components
        if self._redraw:
            self._background_buffer.fill(Qt.transparent)
            self._foreground_t_buffer.fill(Qt.transparent)
            self._foreground_buffer.fill(Qt.transparent)
            ofst = [0, 0]
            for i in range(2): ofst[i] = 0 if self._cap[i] != 1 else (self.height() / 2 if self._horizontal else (self.width() / 2))
            # Draw Border
            paint.begin(self._background_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            if self._border_thickness > 0:
                self._pen.setColor(self._colors[2])
                self._pen.setWidthF(self._thickness + self._border_thickness)
                paint.setPen(self._pen)
                # Draw Bar
                self._drawLine(paint, ofst[0], ofst[1])
            # Draw Background and Foreground
            for i in range(2):
                self._pen.setColor(self._colors[1 - i])
                self._pen.setCapStyle(Qt.FlatCap)
                if i == 0:
                    self._pen.setWidthF(self._thickness)
                    for i in range(2): ofst[i] += self._border_thickness / 2 if self._cap[i] == 0 else 0
                    if self._fill_direction == 4 or self._fill_direction == 8:
                        self._ofst = 0 if self._cap[1] == 2 else self._border_thickness / 2
                    elif self._fill_direction == 6 or self._fill_direction == 2:
                        self._ofst = 0 if self._cap[0] == 2 else self._border_thickness / 2
                else:
                    paint.begin(self._foreground_t_buffer)
                    paint.setRenderHint(QPainter.Antialiasing)
                    self._pen.setWidthF(self._thickness - 2)
                # Draw Bar
                self._drawLine(paint, ofst[0], ofst[1])
                paint.end()
                # Setup pen for updates
                self._pen.setWidth(self.height() if self._horizontal else self.width())
                self._pen.setCapStyle(Qt.FlatCap)
            # Update Flags
            self._redraw = False
        # Cut foreground to appropriate length
        if self._current_value != self._old_value:
            paint.begin(self._foreground_buffer)
            paint.setPen(self._pen)
            paint.setCompositionMode(QPainter.CompositionMode_SourceOver)
            paint.drawPixmap(0, 0, self.width(), self.height(), self._foreground_t_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            paint.setCompositionMode(QPainter.CompositionMode_Clear)
            delta = self._current_value - self._bounds[0]
            if self._fill_direction == 4:
                paint.drawLine(0, self.height() / 2, self.width() - self._ofst - self._mul * delta, self.height() / 2)
            elif self._fill_direction == 6:
                paint.drawLine(self._ofst + self._mul * delta, self.height() / 2, self.width(), self.height() / 2)
            elif self._fill_direction == 46 or self._fill_direction == 64:
                paint.drawLine(0, self.height() / 2, self._mid - self._mul * delta, self.height() / 2)
                paint.drawLine(self._mid + self._mul * delta, self.height() / 2, self.width(), self.height() / 2)
            elif self._fill_direction == 8:
                paint.drawLine(self.width() / 2, 0, self.width() / 2, self.height() - self._ofst - self._mul * delta)
            elif self._fill_direction == 2:
                paint.drawLine(self.width() / 2, self._ofst + self._mul * delta, self.width() / 2, self.height())
            elif self._fill_direction == 82 or self._fill_direction == 28:
                paint.drawLine(self.width() / 2, 0, self.width() / 2, self._mid - self._mul * delta)
                paint.drawLine(self.width() / 2, self._mid + self._mul * delta, self.width() / 2, self.height())
            paint.setCompositionMode(QPainter.CompositionMode_SourceOver)
            paint.setPen(self._pen)
            paint.end()
            # Update Flags
            self._old_value = self._current_value

        paint.begin(self)
        paint.setRenderHint(QPainter.SmoothPixmapTransform)
        paint.drawPixmap(0, 0, self.width(), self.height(), self._background_buffer)
        if self._current_value > self._bounds[0]:
            paint.drawPixmap(0, 0, self.width(), self.height(), self._foreground_buffer)
        paint.end()

        
