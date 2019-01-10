from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from util import from_qimage
from .editortool import EditorTool


class DrawUndoCommand(QUndoCommand):

    def __init__(self, before, after):
        super().__init__("Draw")
        self.triggered_undo = None
        self.triggered_redo = None
        self.before_image = QImage(before)
        self.after_image = QImage(after)

    def undo(self):
        if self.triggered_undo:
            self.triggered_undo(QImage(self.before_image))

    def redo(self):
        if self.triggered_redo:
            self.triggered_redo(QImage(self.after_image))


class DrawTool(EditorTool):

    def __init__(self, canvas):
        super().__init__(canvas)
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
            if not self._have_undo_copy:
                self._undo_copy = QImage(self.canvas)
                self._have_undo_copy = True
            self._last_point = event.pos()
            self._draw = True
            return True
        return False

    def mouse_released(self, event):
        if (event.button() == Qt.LeftButton or event.button() == Qt.RightButton) and self._draw:
            self.draw_line(event.pos(), event.button() == Qt.RightButton)
            self._draw = False
            if self._have_undo_copy:
                draw_command = DrawUndoCommand(self._undo_copy, self.canvas)
                draw_command.triggered_undo = self.undo_command
                draw_command.triggered_redo = self.redo_command
                self.push_undo_command(draw_command)
                self._have_undo_copy = False
            return True
        return False

    def mouse_moved(self, event):
        if event.buttons() & (Qt.LeftButton | Qt.RightButton) and self._draw:
            self.draw_line(event.pos(), event.buttons() & Qt.RightButton)
            return True
        return False

    def draw_line(self, end_point, erase):
        painter = QPainter(self.canvas)

        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)
        if erase:
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
        else:
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        pen.setColor(QColor(*self.pen_color))
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawLine(self._last_point, end_point)
        self._last_point = end_point

    def undo_command(self, image):
        self.send_status_message("Undo...")
        self.canvas = image

    def redo_command(self, image):
        self.canvas = image
