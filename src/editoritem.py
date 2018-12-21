from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class EditorItem(QGraphicsItem):

    def __init__(self, data, pen_color=None):
        super().__init__()
        self.pen_color = pen_color
        self.image = data
        self.last_point = None
        self.draw = False

    def paint(self, painter, option, widget):
        painter.drawImage(0, 0, self.image)

    def boundingRect(self):
        return self.image.rect()

    def setActive(self, active):
        self.setAcceptedMouseButtons(Qt.LeftButton if active else 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()
            self.draw = True
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.draw:
            self.draw_line(event.pos())
            self.draw = False
            return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.draw:
            self.draw_line(event.pos())
            return
        super().mouseMoveEvent(event)

    def draw_line(self, end_point):
        painter = QPainter(self.image)

        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)
        if self.pen_color:
            pen.setColor(self.pen_color)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawLine(self.last_point, end_point)
        self.update()
        self.last_point = end_point
