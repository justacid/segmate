from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from editor.tools import NoneTool, DrawTool


class EditorItem(QGraphicsItem):

    def __init__(self, image, pen_color=None):
        super().__init__()
        self.image = image
        self.pen_color = pen_color
        self.tool = NoneTool(self.image)

    def paint(self, painter, option, widget):
        canvas = self.tool.paint()
        painter.drawImage(0, 0, canvas)

    def boundingRect(self):
        return self.tool.canvas.rect()

    def setActive(self, active):
        self.setAcceptedMouseButtons(Qt.LeftButton if active else 0)

    def setTool(self, tool, status_callback=None):
        if tool == "cursor_tool":
            self.tool = NoneTool(self.image)
        elif tool == "draw_tool":
            self.tool = DrawTool(self.image)
            self.tool.penColor = self.pen_color
            self.tool.setStatusCallback(status_callback)

        self.setCursor(self.tool.cursor())

    def mousePressEvent(self, event):
        if self.tool:
            handled = self.tool.mousePressEvent(event)
            if not handled:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.tool:
            handled = self.tool.mouseReleaseEvent(event)
            if not handled:
                super().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)
        self.update()

    def mouseMoveEvent(self, event):
        if self.tool:
            handled = self.tool.mouseMoveEvent(event)
            if not handled:
                super().mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)
        self.update()
