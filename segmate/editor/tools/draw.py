from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from segmate.util import from_qimage
from segmate.editor.editortool import EditorTool
from segmate.editor.widgets import EditorToolWidget, LabeledSlider


class DrawToolInspector(EditorToolWidget):

    brush_size_changed = Signal(int)
    eraser_size_changed = Signal(int)

    def __init__(self, brush_size, eraser_size):
        super().__init__("Brush Settings")
        brush = LabeledSlider("Brush Size", value=brush_size, maximum=50)
        brush.value_changed.connect(self._change_brush_size)
        eraser = LabeledSlider("Eraser Size", value=eraser_size, maximum=50)
        eraser.value_changed.connect(self._change_eraser_size)
        self.add_widget(brush)
        self.add_widget(eraser)

    def _change_brush_size(self, value):
        self.brush_size_changed.emit(value)

    def _change_eraser_size(self, value):
        self.eraser_size_changed.emit(value)


class DrawTool(EditorTool):

    def __init__(self):
        super().__init__()
        self._last_point = None
        self._draw = False
        self._have_undo_copy = False
        self._undo_copy = None
        self._brush_size = 2
        self._eraser_size = 4

    def paint_canvas(self):
        return self.canvas

    @property
    def widget(self):
        def brush_size(value):
            self._brush_size = value
        def eraser_size(value):
            self._eraser_size = value
        inspector = DrawToolInspector(self._brush_size, self._eraser_size)
        inspector.brush_size_changed.connect(brush_size)
        inspector.eraser_size_changed.connect(eraser_size)
        return inspector

    @property
    def cursor(self):
        return QCursor(QPixmap("icons/dot-cursor.png"))

    def mouse_pressed(self, event):
        if event.buttons() & (Qt.LeftButton | Qt.RightButton):
            self._pressed(event.pos())
            return True
        return False

    def mouse_released(self, event):
        if (event.button() == Qt.LeftButton or event.button() == Qt.RightButton) and self._draw:
            self._released(event.pos(), event.buttons() & Qt.RightButton)
            return True
        return False

    def mouse_moved(self, event):
        if event.buttons() & (Qt.LeftButton | Qt.RightButton) and self._draw:
            self._moved(event.pos(), event.buttons() & Qt.RightButton)
            return True
        return False

    def tablet_event(self, event):
        if event.type() == QEvent.TabletPress and event.button() == Qt.LeftButton:
            self._pressed(event.pos())
        elif event.type() == QEvent.TabletMove and event.buttons() & Qt.LeftButton:
            self._moved(event.pos(), event.buttons() & Qt.MidButton)
        elif event.type() == QEvent.TabletRelease and event.button() == Qt.LeftButton:
            self._released(event.pos(), event.buttons() & Qt.MidButton)

    def _pressed(self, pos):
        if not self.is_editable:
            self.send_status_message("This layer is not editable...")
            return
        if not self._have_undo_copy:
            self._undo_copy = QImage(self.canvas)
            self._have_undo_copy = True
        self._last_point = pos
        self._draw = True

    def _released(self, pos, erase):
        if not self.is_editable:
            return
        self.draw_line(pos, erase)
        self._draw = False
        if self._have_undo_copy:
            self.push_undo_snapshot(self._undo_copy, self.canvas, undo_text="Draw")
            self._have_undo_copy = False

    def _moved(self, pos, erase):
        if not self.is_editable:
            return
        self.draw_line(pos, erase)

    def draw_line(self, end_point, erase):
        painter = QPainter(self.canvas)

        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)
        if erase:
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            pen.setWidth(self._eraser_size)
        else:
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen.setWidth(self._brush_size)
        pen.setColor(QColor(*self.color))
        painter.setPen(pen)

        painter.drawLine(self._last_point, end_point)
        self._last_point = end_point
        self.notify_dirty()
