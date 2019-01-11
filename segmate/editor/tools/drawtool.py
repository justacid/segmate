from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from segmate.util import from_qimage
from segmate.editor.tools.editortool import EditorTool


class DrawTool(EditorTool):

    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self._last_point = None
        self._draw = False
        self._have_undo_copy = False
        self._undo_copy = None

    def paint_canvas(self):
        return self.canvas

    def paint_result(self):
        return self.canvas

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

    def tablet_event(self, event, pos):
        if event.type() == QEvent.TabletPress and event.button() == Qt.LeftButton:
            self._pressed(pos)
        elif event.type() == QEvent.TabletMove and event.buttons() & Qt.LeftButton:
            self._moved(pos, event.buttons() & Qt.MidButton)
        elif event.type() == QEvent.TabletRelease and event.button() == Qt.LeftButton:
            self._released(pos, event.buttons() & Qt.MidButton)

    def _pressed(self, pos):
        if not self._have_undo_copy:
            self._undo_copy = QImage(self.canvas)
            self._have_undo_copy = True
        self._last_point = pos
        self._draw = True

    def _released(self, pos, erase):
        self.draw_line(pos, erase)
        self._draw = False
        if self._have_undo_copy:
            self.push_undo_snapshot(self._undo_copy, self.canvas, undo_text="Draw")
            self._have_undo_copy = False

    def _moved(self, pos, erase):
        self.draw_line(pos, erase)

    def draw_line(self, end_point, erase):
        painter = QPainter(self.canvas)

        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)
        if erase:
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            pen.setWidth(4)
        else:
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            pen.setWidth(2)
        pen.setColor(QColor(*self.pen_color))
        painter.setPen(pen)

        painter.drawLine(self._last_point, end_point)
        self._last_point = end_point