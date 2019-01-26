from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class SceneViewWidget(QGraphicsView):

    zoom_changed = Signal(int)
    fitview_changed = Signal(bool)

    def __init__(self, scene=None):
        super().__init__(scene)
        self._scale = 100
        self._fit = False
        self._pan = False
        self._pan_start = QPointF(0.0, 0.0)
        self._tablet_zoom = False
        self._tablet_zoom_start = QPointF(0.0, 0.0)
        self._tablet_active = False
        self.setMouseTracking(True)

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

    def set_zoom(self, zoom):
        self._scale = zoom
        self.resetMatrix()
        self.scale(self._scale / 100.0, self._scale / 100.0)
        self.zoom_changed.emit(self._scale)

    def toggle_zoom_to_fit(self):
        self._fit = not self._fit
        if self._fit:
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
        else:
            self.resetMatrix()
            self.scale(self._scale / 100, self._scale / 100.0)
        self.fitview_changed.emit(self._fit)

    def _start_tablet_zoom(self, event):
        self._tablet_zoom = True
        self._tablet_zoom_start = event.pos()

    def _move_tablet_zoom(self, event):
        delta = QPointF(event.pos()) - self._tablet_zoom_start
        self.zoom(-delta.y() / 50)

    def _release_tablet_zoom(self, event):
        self._tablet_zoom = False

    def _start_pan(self, event):
        self._pan = True
        self._pan_start = event.pos()

    def _release_pan(self):
        self._pan = False

    def _move_pan(self, event):
        delta = QPointF(event.pos()) - self._pan_start
        hs = self.horizontalScrollBar().value()
        vs = self.verticalScrollBar().value()
        self.horizontalScrollBar().setValue(hs - delta.x())
        self.verticalScrollBar().setValue(vs - delta.y())
        self._pan_start = event.pos()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            self.zoom(int(delta / 12.0))
            return
        event.ignore()

    def resizeEvent(self, event):
        if self._fit:
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
            return

        self.resetMatrix()
        self.scale(self._scale / 100.0, self._scale / 100.0)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            if event.modifiers() & Qt.ControlModifier:
                self._start_pan(event)
                QApplication.setOverrideCursor(Qt.ClosedHandCursor)
                return
        if not self._tablet_active:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        QApplication.restoreOverrideCursor()
        if event.button() == Qt.RightButton:
            if event.modifiers() & Qt.ControlModifier:
                self._release_pan()
                return
        if not self._tablet_active:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan and event.buttons() & Qt.RightButton:
            if event.modifiers() & Qt.ControlModifier:
                self._move_pan(event)
                return
        if not self._tablet_active:
            super().mouseMoveEvent(event)

    def tabletEvent(self, event):
        if event.type() == QEvent.TabletPress and event.button() == Qt.LeftButton:
            if event.modifiers() & Qt.ControlModifier:
                QApplication.setOverrideCursor(Qt.ClosedHandCursor)
                self._start_pan(event)
                return
            if event.modifiers() & Qt.ShiftModifier:
                self._start_tablet_zoom(event)
                return
        if event.type() == QEvent.TabletMove and event.buttons() & Qt.LeftButton:
            if self._pan and event.modifiers() & Qt.ControlModifier:
                self._move_pan(event)
                return
            if self._tablet_zoom and event.modifiers() & Qt.ShiftModifier:
                self._move_tablet_zoom(event)
                return
        if event.type() == QEvent.TabletRelease and event.button() == Qt.LeftButton:
            QApplication.restoreOverrideCursor()
            if self._pan and event.modifiers() & Qt.ControlModifier:
                self._release_pan()
                return
            if self._tablet_zoom and event.modifiers() & Qt.ShiftModifier:
                self._release_tablet_zoom(event)
                return

        # propagate tablet event through the scene
        if self.scene():
            active_layer = self.scene().layers[self.scene().active_layer]

            pos = event.pos()
            cimg = active_layer.cursor().pixmap()
            w, h = cimg.width(), cimg.height()
            pos = QPoint(pos.x() - w/2, pos.y() - h/2)
            scene_pos = self.mapToScene(pos)

            event = QTabletEvent(event.type(), scene_pos, event.globalPos(),
                event.device(), event.pointerType(), event.pressure(), event.xTilt(),
                event.yTilt(), event.tangentialPressure(), event.rotation(), event.z(),
                event.modifiers(), event.uniqueId(), event.button(), event.buttons())
            active_layer.tabletEvent(event)
            return

        super().tabletEvent(event)

    def tabletActive(self, active):
        self._tablet_active = active

    def resizeEvent(self, event):
        self.setAlignment(Qt.AlignCenter)
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        event.ignore()
