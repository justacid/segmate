from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class ViewWidget(QGraphicsView):

    zoom_changed = Signal(int)
    fitview_changed = Signal(bool)

    def __init__(self, scene=None):
        super().__init__(scene)
        self._scale = 100
        self._fit = False
        self._pan = True
        self._pan_start = QPointF(0.0, 0.0)
        self.setMouseTracking(True)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            self.zoom(int(delta / 12.0))
            return
        event.ignore()

    def zoom(self, amount):
        if self._fit:
            return
        if self._scale + amount <= 0:
            return
        if self._scale + amount > 800:
            self._scale = 800
            self.zoom_changed.emit(self._scale)
            return

        self._scale += amount
        self.resetMatrix()
        self.scale(self._scale / 100.0, self._scale / 100.0)
        self.zoom_changed.emit(self._scale)

    def setZoom(self, zoom):
        self._scale = zoom
        self.resetMatrix()
        self.scale(self._scale / 100.0, self._scale / 100.0)
        self.zoom_changed.emit(self._scale)

    def toggleZoomToFit(self):
        self._fit = not self._fit
        if self._fit:
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        else:
            self.resetMatrix()
            self.scale(self._scale / 100, self._scale / 100.0)
        self.fitview_changed.emit(self._fit)

    def resizeEvent(self, event):
        if self._fit:
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
            return

        self.resetMatrix()
        self.scale(self._scale / 100.0, self._scale / 100.0)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self._pan = False
            self.setCursor(Qt.ArrowCursor)
            return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan and event.buttons() & Qt.RightButton:
            delta = QPointF(event.pos()) - self._pan_start
            hs = self.horizontalScrollBar().value()
            vs = self.verticalScrollBar().value()
            self.horizontalScrollBar().setValue(hs - delta.x())
            self.verticalScrollBar().setValue(vs - delta.y())
            self._pan_start = event.pos()
            return
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        event.ignore()
