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
        self._rect_select = None
        self._select_origin = None
        self.setMouseTracking(True)
        self.horizontalScrollBar().valueChanged.connect(self._hide_selection)
        self.verticalScrollBar().valueChanged.connect(self._hide_selection)

    def zoom(self, amount):
        if self._fit:
            return
        if self._scale + amount <= 0:
            return
        if self._scale + amount > 800:
            self._scale = 800
            self.zoom_changed.emit(self._scale)
            return

        if self._rect_select is not None:
            self._rect_select.hide()
        self._scale += amount
        self.resetMatrix()
        self.scale(self._scale / 100.0, self._scale / 100.0)
        self.zoom_changed.emit(self._scale)

    def set_zoom(self, zoom):
        if self._rect_select is not None:
            self._rect_select.hide()
        self._scale = zoom
        self.resetMatrix()
        self.scale(self._scale / 100.0, self._scale / 100.0)
        self.zoom_changed.emit(self._scale)

    def toggle_zoom_to_fit(self):
        if self._rect_select is not None:
            self._rect_select.hide()
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

    def _hide_selection(self):
        if self._rect_select is not None:
            self._rect_select.hide()
            self._rect_select = None
            if self.scene() is not None:
                self.scene().layers.set_selection(None)

    def setScene(self, scene):
        super().setScene(scene)
        if scene is None:
            return
        scene.tool_changed.connect(self._hide_selection)

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
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            if self._rect_select is not None:
                self._rect_select.hide()

            if event.modifiers() & Qt.ControlModifier:
                self._start_pan(event)
                QApplication.setOverrideCursor(Qt.ClosedHandCursor)
                return

        if event.button() == Qt.LeftButton and self.scene() is not None:
            if self.scene().layers.show_selection:
                self._select_origin = event.pos()
                if self._rect_select is None:
                    self._rect_select = QRubberBand(QRubberBand.Rectangle, self)
                self._rect_select.setGeometry(QRect(self._select_origin, QSize()))
                self._rect_select.show()

        if not self._tablet_active:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        QApplication.restoreOverrideCursor()
        if event.button() == Qt.RightButton:
            if event.modifiers() & Qt.ControlModifier:
                self._release_pan()
                return

        if event.button() == Qt.LeftButton and self.scene() is not None:
            if self.scene().layers.show_selection:
                if self._rect_select is not None:
                    origin = self.mapToScene(self._select_origin)
                    target = self.mapToScene(event.pos())
                    selection = QRectF(origin, target).normalized()
                    if selection.width() < 2 or selection.height() < 2:
                        selection = None
                        self._hide_selection()
                    self.scene().layers.set_selection(selection)

        if not self._tablet_active:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan and event.buttons() & Qt.RightButton:
            if event.modifiers() & Qt.ControlModifier:
                self._move_pan(event)
                return

        if event.buttons() & Qt.LeftButton and self.scene() is not None:
            if self.scene().layers.show_selection:
                if self._rect_select is not None:
                    self._rect_select.setGeometry(
                        QRect(self._select_origin, event.pos()).normalized())

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

        if self.scene() is not None:
            pos = event.pos()
            cimg = self.scene().layers.cursor().pixmap()
            w, h = cimg.width(), cimg.height()
            pos = QPoint(pos.x() - w/2, pos.y() - h/2)
            scene_pos = self.mapToScene(pos)

            event = QTabletEvent(event.type(), scene_pos, event.globalPos(),
                event.device(), event.pointerType(), event.pressure(), event.xTilt(),
                event.yTilt(), event.tangentialPressure(), event.rotation(), event.z(),
                event.modifiers(), event.uniqueId(), event.button(), event.buttons())
            self.scene().layers.tabletEvent(event)
            return

        super().tabletEvent(event)

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        scene = self.scene()
        if scene is not None:
            scene.layers.keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        scene = self.scene()
        if scene is not None:
            scene.layers.keyReleaseEvent(event)

    def tabletActive(self, active):
        self._tablet_active = active
