from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from segmate.util import from_qimage, to_qimage
import segmate.editor.tools as tools


class EditorItem(QGraphicsItem):

    def __init__(self, image, undo_stack, pen_color=None):
        super().__init__()

        self.tool_box = {
            "bucket_tool": tools.BucketFillTool,
            "cursor_tool": tools.NoneTool,
            "contour_tool": tools.ContourTool,
            "draw_tool": tools.DrawTool,
        }

        self._image = image
        self._pen_color = pen_color
        self._undo_stack = undo_stack
        self._undo_stack.indexChanged.connect(lambda _: self.update())
        self._tool = self.tool_box["cursor_tool"](self._image, self)

    def paint(self, painter, option, widget):
        painter.drawImage(0, 0, self._tool.paint_canvas())

    def boundingRect(self):
        return self._image.rect()

    def setActive(self, active):
        buttons = Qt.LeftButton | Qt.RightButton | Qt.MidButton
        self.setAcceptedMouseButtons(buttons if active else 0)

    def setTool(self, tool, status_callback=None):
        if tool not in self.tool_box:
            raise IndexError(f"'{tool}'' is not a valid tool.")

        self._tool = self.tool_box[tool](QImage(self._tool.paint_result()), self)
        self._tool.pen_color = self._pen_color
        self._tool.undo_stack = self._undo_stack
        self._tool.status_callback = status_callback
        self.setCursor(self._tool.cursor)

    def mousePressEvent(self, event):
        if self._tool:
            handled = self._tool.mouse_pressed(event)
            if not handled:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
        self.update()

    def mouseReleaseEvent(self, event):
        if self._tool:
            handled = self._tool.mouse_released(event)
            if not handled:
                super().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)
        self.update()

    def mouseMoveEvent(self, event):
        if self._tool:
            handled = self._tool.mouse_moved(event)
            if not handled:
                super().mouseMoveEvent(event)
        else:
            super().mouseMoveEvent(event)
        self.update()

    def tabletEvent(self, event, pos):
        if self._tool:
            self._tool.tablet_event(event, pos)
        self.update()

    def undoToolCommand(self, image):
        if self._tool:
            self._tool.canvas = image
            if self._tool.status_callback:
                if self._tool.undo_stack:
                    undo_text = f"'{self._tool.undo_stack.undoText()}'"
                else:
                    undo_text = ""
                self._tool.send_status_message(f"Undo {undo_text}")

    def redoToolCommand(self, image):
        if self._tool:
            self._tool.canvas = image
            if self._tool.status_callback:
                if self._tool.undo_stack:
                    redo_text = f"'{self._tool.undo_stack.redoText()}'"
                else:
                    redo_text = ""
                self._tool.send_status_message(f"Redo {redo_text}")