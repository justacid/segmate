import numpy as np
from PySide2.QtCore import Qt, Signal

import segmate.util as util
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

    def on_create(self):
        self._brush_size = 2
        self._eraser_size = 4

    def on_show(self):
        self._last_point = None
        self._draw = False
        self._have_undo_copy = False
        self._undo_copy = None

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
         return "icons/dot-cursor.png"

    def mouse_pressed(self, event):
        if event.buttons() & (Qt.LeftButton | Qt.RightButton):
            self._pressed(event.pos(), event.button() == Qt.RightButton)
            return True
        return False

    def mouse_released(self, event):
        if (event.button() == Qt.LeftButton or event.button() == Qt.RightButton) and self._draw:
            self._released(event.pos(), event.button() == Qt.RightButton)
            return True
        return False

    def mouse_moved(self, event):
        if event.buttons() & (Qt.LeftButton | Qt.RightButton) and self._draw:
            self._moved(event.pos(), event.buttons() & Qt.RightButton)
            return True
        return False

    def tablet_event(self, event):
        if event.type() == QEvent.TabletPress and event.button() == Qt.LeftButton:
            self._pressed(event.pos(), event.button() == Qt.MidButton)
        elif event.type() == QEvent.TabletMove and event.buttons() & Qt.LeftButton:
            self._moved(event.pos(), event.buttons() & Qt.MidButton)
        elif event.type() == QEvent.TabletRelease and event.button() == Qt.LeftButton:
            self._released(event.pos(), event.button() == Qt.MidButton)

    def _pressed(self, pos, erase):
        if not self.is_editable:
            self.send_status_message("This layer is not editable...")
            return
        if not self._have_undo_copy:
            self._undo_copy = self.canvas.copy()
            self._have_undo_copy = True
        self._last_point = pos
        self._draw_line(pos, erase)
        self._draw = True

    def _released(self, pos, erase):
        if not self.is_editable:
            return
        self._draw_line(pos, erase)
        self._draw = False
        if self._have_undo_copy:
            self.push_undo_snapshot(self._undo_copy, self.canvas, undo_text="Draw")
            self._have_undo_copy = False

    def _moved(self, pos, erase):
        if not self.is_editable:
            return
        self._draw_line(pos, erase)

    def _draw_line(self, end_point, erase):
        p0 = [self._last_point.y(), self._last_point.x()]
        p1 = [end_point.y(), end_point.x()]
        color = (*self.color, 255) if not erase else (0, 0, 0, 0)
        width = self._brush_size if not erase else self._eraser_size
        util.draw.line(self.canvas, p0, p1, color, width=width)
        self._last_point = end_point
        self.notify_dirty()
