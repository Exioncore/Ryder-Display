import math

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QPainterPath

class QtRoundProgressBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialized = False

    def setup(self, 
              bounds = [0, 100], angleBounds = [-45, 225], fillDirection = -1, colors = [QColor('red'), QColor('black'), QColor('white')],
              thickness = [10, 0], capType = Qt.FlatCap
        ):
        self._current_value = bounds[0]
        # Angle Bounds
        self._angle_bounds = angleBounds
        self._max_angle = self._angle_bounds[1] - self._angle_bounds[0]
        # Bounds
        self._bounds = bounds
        self._bounds_range = self._bounds[1] - self._bounds[0]
        mul = (self._current_value - self._bounds[0]) / self._bounds_range
        self._current_value = self._bounds_range * mul + self._bounds[0]
        self._target_angle = self._current_angle = (self._max_angle / self._bounds_range * (self._current_value - self._bounds[0]))
        # Fill Direction
        self._fill_direction = fillDirection
        if self._fill_direction == 0:
            self._mid = (self._angle_bounds[1] - self._angle_bounds[0]) / 2 + self._angle_bounds[0]
        # Colors [0 = foreground color, 1 = background color, 2 = border color]
        self._colors = colors
        # Thickness [0 = thickness, 1 = border thickness]
        self._thickness = thickness
        arc_ofst = math.ceil((self._thickness[0] + self._thickness[1]) / 2.0)
        self._rect_arc = QRect(
            arc_ofst, arc_ofst,
            self.width() - arc_ofst * 2.0, self.height() - arc_ofst * 2.0
        )
        # Cap
        if capType == 0:
            self._cap = Qt.SquareCap
        elif capType == 1:
            self._cap = Qt.RoundCap
        else:
            self._cap = Qt.FlatCap
        # Internal variables
        self._pen = QPen(self._colors[0], self._thickness[0], Qt.SolidLine)
        self._pen.setWidth(self._thickness[0])
        # Offset caused by SquareCap and RoundCap when border is enabled
        self._ofst1 = 0
        if self._thickness[1] > 0:
            if self._cap == Qt.SquareCap:
                self._ofst1 = 180 / math.pi * ((self._thickness[0] / 2) / (self._rect_arc.width() / 2))
            elif self._cap == Qt.RoundCap:
                self._ofst1 = 180 / math.pi * (((self._thickness[0] * 0.05) / 2) / (self._rect_arc.width() / 2))
        # Additional Offset specific to RoundCap
        if self._cap == Qt.RoundCap:
            self._ofst2 = 180 / math.pi * ((self._thickness[0] / 2) / (self._rect_arc.width() / 2))
        else:
            self._ofst2 = 0
        # Ready Flag
        self._initialized = True

    def setValue(self, val):
        self._current_value = max(self._bounds[0], min(val, self._bounds[1]))
        self._target_angle = (self._max_angle / self._bounds_range * (self._current_value - self._bounds[0]))

    def redraw(self):
        self._redraw = True

    def setGeometry(self, x, y, w, h):
        """ Override setGeometry method """
        super().setGeometry(x, y, w, h)
        # Recompute container
        self._rect = QRect(0, 0, self.width(), self.height())
        if self._initialized:
            arc_ofst = math.ceil((self._thickness[0] + self._thickness[1]) / 2.0)
            self._rect_arc = QRect(
                arc_ofst, arc_ofst,
                self.width() - arc_ofst * 2.0, self.height() - arc_ofst * 2.0
            )
        # Reset PixMaps
        self._background_buffer = QPixmap(self.width(), self.height())
        self._background_buffer.fill(Qt.transparent)
        self._foreground_buffer = QPixmap(self.width(), self.height())
        self._foreground_buffer.fill(Qt.transparent)

    def paintEvent(self, e):
        """ Override Paint Function """
        if not self._initialized: return
        paint = QPainter()
        # Draw background of the bar
        if self._redraw:
            self._background_buffer.fill(Qt.transparent)
            paint.begin(self._background_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            # Ignore SquareCap if the border is 0
            if self._cap == Qt.SquareCap and self._thickness[1] == 0:
                self._pen.setCapStyle(Qt.FlatCap)
            else:
                self._pen.setCapStyle(self._cap)
            # Draw Border
            if self._thickness[1] > 0:
                self._pen.setWidth(self._thickness[0] + self._thickness[1])
                # Draw Border as a full bar
                self._pen.setColor(self._colors[2])
                paint.setPen(self._pen) 
                paint.drawArc(self._rect_arc, (self._angle_bounds[0] + self._ofst1 + self._ofst2) * 16.0, (self._max_angle - self._ofst1 * 2 - self._ofst2 * 2) * 16.0)  
                # Erase insides of the bar to create the border (Necessary if the background has an alpha value)
                if self._cap == Qt.SquareCap:
                    self._pen.setCapStyle(Qt.FlatCap)
                paint.setCompositionMode(QPainter.CompositionMode_Clear)
                self._pen.setWidth(self._thickness[0])
                paint.setPen(self._pen)
                paint.drawArc(self._rect_arc, (self._angle_bounds[0] + self._ofst2) * 16.0, (self._max_angle - self._ofst2 * 2) * 16.0)
                paint.setCompositionMode(QPainter.CompositionMode_SourceOver)
            else:
                # No need to use SquareCap for the portion inside the border
                if self._cap == Qt.SquareCap:
                    self._pen.setCapStyle(Qt.FlatCap)
            # Draw Background
            self._pen.setColor(self._colors[1])          
            paint.setPen(self._pen) 
            paint.drawArc(self._rect_arc, (self._angle_bounds[0] + self._ofst2) * 16.0, (self._max_angle - self._ofst2 * 2) * 16.0)
            paint.end()
            # Set pen to foreground styling
            self._pen.setCapStyle(Qt.FlatCap)
            self._pen.setColor(self._colors[0])
        # Draw filled portion of the bar
        if self._current_angle != self._target_angle or self._redraw:
            paint.begin(self._foreground_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            self._foreground_buffer.fill(Qt.transparent)
            # Draw guide for the filled portion of the bar
            if self._cap == Qt.RoundCap:
                # This is for RoundCap
                self._pen.setCapStyle(self._cap)
                self._pen.setWidth(self._thickness[0] - 2)
                paint.setPen(self._pen)
                paint.drawArc(self._rect_arc, (self._angle_bounds[0] + self._ofst2) * 16.0, (self._max_angle - self._ofst2 * 2) * 16.0)
                self._pen.setCapStyle(Qt.FlatCap)
                self._pen.setWidth(self._thickness[0])
                paint.setPen(self._pen)
                # Erase excess
                paint.setCompositionMode(QPainter.CompositionMode_Clear)
                if self._fill_direction > 0:
                    paint.drawArc(self._rect_arc, self._angle_bounds[1] * 16.0, -(self._max_angle - self._target_angle) * 16.0)
                elif self._fill_direction < 0:
                    paint.drawArc(self._rect_arc, self._angle_bounds[0] * 16.0, (self._max_angle - self._target_angle) * 16.0)
                else:
                    ofst = self._target_angle / 2
                    paint.drawArc(self._rect_arc, self._angle_bounds[0] * 16.0, ((self._angle_bounds[1] - (self._mid + ofst))) * 16.0)
                    paint.drawArc(self._rect_arc, (self._mid + ofst) * 16.0, ((self._max_angle - self._target_angle / 2)) * 16.0)
            else:
                # This is for SquareCap and FlatCap
                paint.setPen(self._pen)
                if self._fill_direction > 0:
                    paint.drawArc(self._rect_arc, self._angle_bounds[0] * 16.0, self._target_angle * 16.0)
                elif self._fill_direction < 0:
                    paint.drawArc(
                        self._rect_arc,
                        (self._angle_bounds[1] - self._target_angle) * 16.0, self._target_angle * 16.0
                    )
                else:
                    paint.drawArc(self._rect_arc, (self._mid - ofst) * 16.0, self._target_angle * 16.0)
            paint.end()
            # Update flags
            self._current_angle = self._target_angle
            self._redraw = False

        paint.begin(self)
        paint.setRenderHint(QPainter.SmoothPixmapTransform)
        paint.drawPixmap(self._rect, self._background_buffer)
        paint.drawPixmap(self._rect, self._foreground_buffer)
        paint.end()
