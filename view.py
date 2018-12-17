from PySide2.QtCore import Qt, QPointF
from PySide2.QtWidgets import QGraphicsView, QGraphicsScene
from PySide2.QtGui import QImage, QPixmap


class SegmentationView(QGraphicsView):

    def __init__(self, scene):
        super().__init__(scene)
        self.scene = scene
        self._scale = 1.0
        self._pan = True
        self._pan_start = QPointF(0.0, 0.0)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self._scale += 0.15 if delta > 0 else -0.15
        self.resetMatrix()
        self.scale(self._scale, self._scale)
        event.accept()

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
