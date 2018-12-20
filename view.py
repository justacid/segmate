from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class SegmentationView(QGraphicsView):

    zoom_changed = Signal(float)
    fitview_changed = Signal(bool)

    def __init__(self, scene=None):
        super().__init__(scene)
        self._scale = 1.0
        self._fit = False
        self._pan = True
        self._pan_start = QPointF(0.0, 0.0)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.zoom((delta / 12.0) / 100.0)
        event.accept()

    def zoom(self, amount):
        if self._fit:
            return
        if self._scale + amount <= 0:
            return
        if self._scale + amount > 8.0:
            self._scale = 8.0
            self.zoom_changed.emit(self._scale)
            return

        self._scale += amount
        self.resetMatrix()
        self.scale(self._scale, self._scale)
        self.zoom_changed.emit(self._scale)

    def toggleZoomToFit(self):
        self._fit = not self._fit
        if self._fit:
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        else:
            self.resetMatrix()
            self.scale(self._scale, self._scale)
        self.fitview_changed.emit(self._fit)

    def resizeEvent(self, event):
        if self._fit:
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
            event.accept()
            return

        self.resetMatrix()
        self.scale(self._scale, self._scale)
        event.ignore()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
            return
        event.ignore()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
            return
        event.ignore()

    def mouseMoveEvent(self, event):
        if self._pan:
            delta = QPointF(event.pos()) - self._pan_start
            hs = self.horizontalScrollBar().value()
            vs = self.verticalScrollBar().value()
            self.horizontalScrollBar().setValue(hs - delta.x())
            self.verticalScrollBar().setValue(vs - delta.y())
            self._pan_start = event.pos()
            event.accept()
            return
        event.ignore()
