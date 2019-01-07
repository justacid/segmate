from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from .editortool import EditorTool


class DrawTool(EditorTool):

    def __init__(self, image):
        super().__init__(image)

        self.last_point = None
        self.draw = False
        self.erase = False

    def paint(self):
        return self.canvas

    def cursor(self):
        return QCursor(QPixmap("icons/dot-cursor.png"))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
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
