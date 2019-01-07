from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

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

    def __init__(self, image):
        super().__init__(image)

        self.last_point = None
        self.draw = False
        self.erase = False
        self.have_undo_copy = False
        self.undo_copy = None

    def paint(self):
        return self.canvas

    def cursor(self):
        return QCursor(QPixmap("icons/dot-cursor.png"))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.have_undo_copy:
                self.undo_copy = QImage(self.canvas)
                self.have_undo_copy = True
            self.last_point = event.pos()
            self.draw = True
            if event.modifiers() & Qt.ControlModifier:
                self.erase = True
                self.sendStatusMessage("Eraser: On")
            return True
        return False

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.draw:
            self.drawLine(event.pos())
            self.draw = False
            if self.erase:
                self.sendStatusMessage("Eraser: Off")
                self.erase = False
            if self.have_undo_copy:
                draw_command = DrawUndoCommand(self.undo_copy, self.canvas)
                draw_command.triggered_undo = self.undo
                draw_command.triggered_redo = self.redo
                self.addUndoCommand(draw_command)
                self.have_undo_copy = False
            return True
        return False

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.draw:
            self.drawLine(event.pos())
            return True
        return False

    def drawLine(self, end_point):
        painter = QPainter(self.canvas)

        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)
        if self.erase:
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
        else:
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        pen.setColor(self.penColor)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawLine(self.last_point, end_point)
        self.last_point = end_point

    def undo(self, image):
        self.sendStatusMessage("Undo...")
        self.canvas = image

    def redo(self, image):
        self.canvas = image
