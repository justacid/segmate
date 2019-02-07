from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from segmate.util import from_qimage, to_qimage
import segmate.editor.tools as tools


class EditorItem(QGraphicsObject):

    image_modified = Signal()

    def __init__(self, scene):
        super().__init__()

        self._tool_box = {
            "bucket_tool": tools.BucketFillTool(),
            "cursor_tool": tools.CursorTool(),
            "contour_tool": tools.ContourTool(),
            "draw_tool": tools.DrawTool(),
            "masks_tool": tools.MasksTool(),
            "morphology_tool": tools.MorphologyTool()
        }

        self.scene = scene
        self.is_active = False
        self.image_idx = -1
        self.layer_idx = -1

        self._undo_stack = scene.undo_stack
        self._undo_stack.indexChanged.connect(lambda _: self.update())
        self._tool = self._tool_box["cursor_tool"]

    def load(self, image_idx, layer_idx):
        self.image_idx = image_idx
        self.layer_idx = layer_idx
        self._image = self.scene.data_store[image_idx][layer_idx]
        self._is_mask = self.scene.data_store.masks[layer_idx]
        self._is_editable = self.scene.data_store.editable[layer_idx]
        self._color = self.scene.data_store.colors[layer_idx]
        self._tool.canvas = QImage(self._image)
        self._tool.item = self

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
        if tool not in self._tool_box:
            raise IndexError(f"'{tool}'' is not a valid tool.")

        result = QImage(self._tool.paint_result())

        self._tool = self._tool_box[tool]
        self._tool.canvas = result
        self._tool.item = self
        self._tool.color = self._color
        self._tool.undo_stack = self._undo_stack
        self._tool.status_callback = status_callback
        self._tool.is_mask = self._is_mask
        self._tool.is_editable = self._is_editable
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

    def tabletEvent(self, event):
        if self._tool:
            self._tool.tablet_event(event)
        self.update()
