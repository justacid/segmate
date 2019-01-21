from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from segmate.util import from_qimage, to_qimage
import segmate.editor.tools as tools


class EditorItem(QGraphicsObject):

    image_modified = Signal()

    def __init__(self, image_idx, layer_idx, scene):
        super().__init__()

        self.tool_box = {
            "bucket_tool": tools.BucketFillTool,
            "cursor_tool": tools.CursorTool,
            "contour_tool": tools.ContourTool,
            "draw_tool": tools.DrawTool,
            "masks_tool": tools.MasksTool,
            "morphology_tool": tools.MorphologyTool
        }

        self.scene = scene
        self.image_idx = image_idx
        self.layer_idx = layer_idx

        self._image = scene.data_loader[image_idx][layer_idx]
        self._pen_color = scene.data_loader.pen_colors[layer_idx]
        self._editable = scene.data_loader.editable[layer_idx]
        self._undo_stack = scene._undo_stack
        self._undo_stack.indexChanged.connect(lambda _: self.update())
        self._tool = self.tool_box["cursor_tool"](self._image, self)
        self.is_active = False

    @property
    def data(self):
        return self._tool.paint_result()

    @property
    def is_dirty(self):
        return self._tool.is_dirty

    @is_dirty.setter
    def is_dirty(self, value):
        self._tool.is_dirty = value

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, active):
        buttons = Qt.LeftButton | Qt.RightButton | Qt.MidButton
        self.setAcceptedMouseButtons(buttons if active else 0)
        self._is_active = active

    def change_tool(self, tool, status_callback=None):
        if tool not in self.tool_box:
            raise IndexError(f"'{tool}'' is not a valid tool.")

        self._tool = self.tool_box[tool](QImage(self._tool.paint_result()), self)
        self._tool.pen_color = self._pen_color
        self._tool.undo_stack = self._undo_stack
        self._tool.status_callback = status_callback
        self._tool.is_editable = self._editable
        self.setCursor(self._tool.cursor)

    def undo_tool_command(self, image):
        if self._tool:
            self._tool.canvas = image
            if self._tool.status_callback:
                if self._tool.undo_stack:
                    undo_text = f"'{self._tool.undo_stack.undoText()}'"
                else:
                    undo_text = ""
                self._tool.send_status_message(f"Undo {undo_text}")

    def redo_tool_command(self, image):
        if self._tool:
            self._tool.canvas = image
            if self._tool.status_callback:
                if self._tool.undo_stack:
                    redo_text = f"'{self._tool.undo_stack.redoText()}'"
                else:
                    redo_text = ""
                self._tool.send_status_message(f"Redo {redo_text}")

    def paint(self, painter, option, widget):
        painter.drawImage(0, 0, self._tool.paint_canvas())

    def boundingRect(self):
        return self._image.rect()

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
