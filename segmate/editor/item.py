from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import segmate.util as util
import segmate.editor.tools as tools
import segmate.editor.event as tevent


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
        self.image_idx = -1
        self.layer_idx = -1

        self._is_active = False
        self._undo_stack = scene.undo_stack
        self._undo_stack.indexChanged.connect(lambda _: self.update())
        self._tool = self._tool_box["cursor_tool"]
        self.setAcceptedMouseButtons(0)

    def load(self, image_idx, layer_idx):
        self.image_idx = image_idx
        self.layer_idx = layer_idx
        self._image = self.scene.data_store[image_idx][layer_idx]
        self._is_mask = self.scene.data_store.masks[layer_idx]
        self._is_editable = self.scene.data_store.editable[layer_idx]
        self._color = self.scene.data_store.colors[layer_idx]
        self._tool.canvas = self._image.copy()
        self._tool.item = self

    @property
    def data(self):
        result = self._tool.on_finalize()
        if result is None:
            return self._image.copy()
        return result

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
        if not active:
            self._tool._on_hide()
            self.update()

    @property
    def tool_widget(self):
        if self._tool is None:
            return None
        return self._tool.on_show_widget()

    @property
    def is_editable(self):
        return self._is_editable

    def change_tool(self, tool, status_callback=None):
        if tool not in self._tool_box:
            raise IndexError(f"'{tool}'' is not a valid tool.")

        self._tool._on_hide()
        result = self._tool.on_finalize()
        if result is not None:
            result = result.copy()
        else:
            result = self._image.copy()

        self._tool = self._tool_box[tool]
        self._tool.canvas = result
        self._tool.item = self
        self._tool.color = self._color
        self._tool.undo_stack = self._undo_stack
        self._tool.status_callback = status_callback
        self._tool.is_mask = self._is_mask
        self._tool.is_editable = self._is_editable
        self._tool.on_show()

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
        canvas = self._tool.on_paint()
        if canvas is None:
            qimage = util.to_qimage(self._image)
        else:
            qimage = util.to_qimage(canvas)
        painter.drawImage(0, 0, qimage)

    def boundingRect(self):
        y, x = self._image.shape[:2]
        return QRect(0, 0, x, y)

    def mousePressEvent(self, event):
        if self._tool:
            self._tool.on_mouse_pressed(tevent.MouseEvent(event))
            self.update()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._tool:
            self._tool.on_mouse_released(tevent.MouseEvent(event, True))
            self.update()
            return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._tool:
            self._tool.on_mouse_moved(tevent.MouseEvent(event))
            self.update()
            return
        super().mouseMoveEvent(event)

    def tabletEvent(self, event):
        if self._tool is None:
            return
        if event.type() == QEvent.TabletPress:
            self._tool.on_tablet_pressed(tevent.MouseEvent(event))
        elif event.type() == QEvent.TabletMove:
            self._tool.on_tablet_moved(tevent.MouseEvent(event))
        elif event.type() == QEvent.TabletRelease:
            self._tool.on_tablet_released(tevent.MouseEvent(event, True))
        self.update()

    def keyPressEvent(self, event):
        if self._tool is None:
            return
        self._tool.on_key_pressed(tevent.KeyEvent(event))

    def keyReleaseEvent(self, event):
        if self._tool is None:
            return
        self._tool.on_key_released(tevent.KeyEvent(event))
