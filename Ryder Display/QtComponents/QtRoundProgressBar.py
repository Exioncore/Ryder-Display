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
              thickness = [10, 0], capType = [0, 0], edgesRemoval = [0, 0]
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
        self._arc_ofst = math.ceil((self._thickness[0] + self._thickness[1]) / 2.0)
        self._rect_arc = QRect(
            self._arc_ofst, self._arc_ofst,
            self.width() - self._arc_ofst * 2.0, self.height() - self._arc_ofst * 2.0
        )
        # Cap
        self._cap = capType
        # Edge Removal
        self._edgesRemoval = edgesRemoval
        # Internal variables
        self._pen = QPen(self._colors[0], self._thickness[0], Qt.SolidLine)
        self._pen.setWidth(self._thickness[0])
        # Offset caused by SquareCap and RoundCap when border is enabled
        self._ofst1 = [0, 0]    # This offset is required only if the border is enabled
        self._ofst2 = [0, 0]    # This offset is additional for Qt.RoundCap (Needed regardless of border)
        for i in range(2):
            if self._thickness[1] > 0:
                if self._cap[i] ==1:
                    self._ofst1[i] = 180 / math.pi * (((self._thickness[0] * 0.05) / 2) / (self._rect_arc.width() / 2))
            # Additional Offset specific to RoundCap
            if self._cap[i] == 1:
                self._ofst2[i] = 180 / math.pi * ((self._thickness[0] / 2) / (self._rect_arc.width() / 2))
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
            self._arc_ofst = math.ceil((self._thickness[0] + self._thickness[1]) / 2.0)
            self._rect_arc = QRect(
                self._arc_ofst, self._arc_ofst,
                self.width() - self._arc_ofst * 2.0, self.height() - self._arc_ofst * 2.0
            )
        # Reset PixMaps
        self._background_buffer = QPixmap(self.width(), self.height())
        self._background_buffer.fill(Qt.transparent)
        self._foreground_t_buffer = QPixmap(self.width(), self.height())
        self._foreground_t_buffer.fill(Qt.transparent)
        self._foreground_buffer = QPixmap(self.width(), self.height())
        self._foreground_buffer.fill(Qt.transparent)

    def paintEvent(self, e):
        """ Override Paint Function """
        if not self._initialized: return
        paint = QPainter()
        # Draw the bar components
        if self._redraw:
            self._background_buffer.fill(Qt.transparent)
            self._foreground_t_buffer.fill(Qt.transparent)            
            # Draw Border
            paint.begin(self._background_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            if self._thickness[1] > 0:
                self._pen.setColor(self._colors[2])
                # Process each cap
                startAngle = self._angle_bounds[0]
                angleStep = self._max_angle / 2 + self._max_angle / 4
                # Draw Bar Border
                for i in range(2):
                    self._pen.setWidth(self._thickness[0] + self._thickness[1])
                    self._pen.setCapStyle(Qt.RoundCap if self._cap[i] == 1 else Qt.FlatCap)
                    paint.setPen(self._pen) 
                    # Draw Border as a full bar
                    paint.drawArc(self._rect_arc, (startAngle + self._ofst1[i] + self._ofst2[i]) * 16.0, (angleStep - self._ofst1[i] * (i + 1) - self._ofst2[i] * (i + 1)) * 16.0)  
                    # Erase insides of the bar to create the border (Necessary to enable the use of transparent background)
                    paint.setCompositionMode(QPainter.CompositionMode_Clear)
                    self._pen.setWidth(self._thickness[0])
                    paint.setPen(self._pen)
                    paint.drawArc(self._rect_arc, (startAngle + self._ofst2[i]) * 16.0, (angleStep - self._ofst2[i] * (i + 1)) * 16.0)
                    paint.setCompositionMode(QPainter.CompositionMode_SourceOver)
                    startAngle += angleStep - self._max_angle / 2
                if self._cap[0] == 0 or self._cap[1] == 0:
                    self._pen.setWidth(self._thickness[1])
                    self._pen.setCapStyle(Qt.FlatCap)
                    paint.setPen(self._pen)
                    outerRadius = self.width() / 2
                    innerRadius = outerRadius - self._thickness[0] - self._thickness[1]
                    for i in range(2):
                        if self._cap[i] == 0:
                            rads = math.radians(self._angle_bounds[i])
                            p1 = [
                                (self.width()  / 2) + innerRadius * math.cos(rads), 
                                (self.height() / 2) - innerRadius * math.sin(rads)
                            ]
                            p2 = [
                                (self.width()  / 2) + outerRadius * math.cos(rads), 
                                (self.height() / 2) - outerRadius * math.sin(rads)
                            ]
                            print(p1)
                            print(p2)
                            paint.drawLine(p1[0], p1[1], p2[0], p2[1])
                    self._pen.setWidth(self._thickness[0])
                # Draw Square Border End Caps
                # Outer edge removal
                if self._edgesRemoval[0] > 0 or self._edgesRemoval[1] > 0:
                    paint.setCompositionMode(QPainter.CompositionMode_Clear)
                    rt = 2 if (self._thickness[0] + self._thickness[1]) % 2 != 0 else 1
                    self._pen.setWidth(self._thickness[1] + rt)
                    paint.setPen(self._pen)
                    if self._edgesRemoval[0] > 0:
                        # Outer edge removal
                        paint.drawArc(self._rect, 0 * 16.0, 360 * 16.0) 
                    if self._edgesRemoval[1] > 0:
                        # Inner edge removal
                        t_rect = QRect(self._arc_ofst * 2, self._arc_ofst * 2, self.width() - self._arc_ofst * 4, self.height() - self._arc_ofst * 4)
                        paint.drawArc(t_rect, 0 * 16.0, 360 * 16.0)
                    self._pen.setWidth(self._thickness[0])
                    paint.setCompositionMode(QPainter.CompositionMode_SourceOver)
            else:
                self._pen.setWidth(self._thickness[0])
            # Draw Background
            startAngle = self._angle_bounds[0]
            angleStep = self._max_angle / 2 + self._max_angle / 4
            self._pen.setColor(self._colors[1])
            for i in range(2):
                self._pen.setCapStyle(Qt.RoundCap if self._cap[i] == 1 else Qt.FlatCap)
                paint.setPen(self._pen) 
                paint.drawArc(self._rect_arc, (startAngle + self._ofst2[i]) * 16.0, (angleStep - self._ofst2[i] * (i + 1)) * 16.0)
                startAngle += angleStep - self._max_angle / 2
            paint.end()
            # Draw Foreground
            paint.begin(self._foreground_t_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            self._pen.setWidth(self._thickness[0])
            self._pen.setColor(self._colors[0])
            startAngle = self._angle_bounds[0]
            angleStep = self._max_angle / 2 + self._max_angle / 4
            for i in range(2):
                self._pen.setCapStyle(Qt.RoundCap if self._cap[i] == 1 else Qt.FlatCap)
                paint.setPen(self._pen) 
                paint.drawArc(self._rect_arc, (startAngle + self._ofst2[i]) * 16.0, (angleStep - self._ofst2[i] * (i + 1)) * 16.0)
                startAngle += angleStep - self._max_angle / 2
            paint.end()
            # Set pen to foreground styling
            self._pen.setCapStyle(Qt.FlatCap)
            self._pen.setWidth(self._thickness[0] + 2)
            # Update Flags
            self._redraw = False

        # Cut foreground to appropriate length
        if self._current_angle != self._target_angle or self._redraw:
            paint.begin(self._foreground_buffer)
            paint.setCompositionMode(QPainter.CompositionMode_SourceOver)
            paint.drawPixmap(self._rect, self._foreground_t_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            paint.setCompositionMode(QPainter.CompositionMode_Clear)
            paint.setPen(self._pen)
            if self._fill_direction > 0:
                paint.drawArc(self._rect_arc, (self._angle_bounds[0] + self._target_angle) * 16.0, (self._max_angle - self._target_angle + 1.0) * 16.0)
            elif self._fill_direction < 0:
                paint.drawArc(
                    self._rect_arc,
                    (self._angle_bounds[0] - 1.0) * 16.0, (self._max_angle - self._target_angle) * 16.0
                )
            else:
                ofst = self._target_angle / 2
                paint.drawArc(self._rect_arc, self._angle_bounds[0] * 16.0, ((self._angle_bounds[1] - (self._mid + ofst))) * 16.0)
                paint.drawArc(self._rect_arc, (self._mid + ofst) * 16.0, ((self._max_angle - self._target_angle / 2)) * 16.0)
            paint.setCompositionMode(QPainter.CompositionMode_SourceOver)
            paint.end()
            # Update Flags
            self._current_angle = self._target_angle

        paint.begin(self)
        paint.setRenderHint(QPainter.SmoothPixmapTransform)
        paint.drawPixmap(self._rect, self._background_buffer)
        if self._current_angle > 0:
            paint.drawPixmap(self._rect, self._foreground_buffer)
        paint.end()
