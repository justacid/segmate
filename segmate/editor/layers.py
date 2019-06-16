from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from .. import util, plugins
from . import tools
from . import event as tevent


class LayersGraphicsView(QGraphicsObject):

    image_modified = Signal()

    def __init__(self, scene):
        super().__init__()
        self.scene = scene
        self.active = 0
        self.image_idx = 0
        self.layer_names = self.scene.data_store.folders

        self._layer_data = None
        self._opacities = [1.0] * len(self.scene.data_store.folders)
        self._colors = self.scene.data_store.colors
        self._masks = self.scene.data_store.masks

        self._undo_stack = scene.undo_stack
        self._undo_stack.indexChanged.connect(lambda _: self.update())

        self._tool_box = {
            "bucket_tool": tools.BucketFillTool(),
            "cursor_tool": tools.CursorTool(),
            "contour_tool": tools.ContourTool(),
            "draw_tool": tools.DrawTool(),
            "masks_tool": tools.MasksTool(),
            "morphology_tool": tools.MorphologyTool()
        }

        if plugins.get_plugins():
            for name, tool in plugins.get_plugins().items():
                self._tool_box[name] = tool[1]()

        self.tool = self._tool_box["cursor_tool"]
        self.tool.item = self

    def load(self, image_idx):
        self._layer_data = [img.copy() for img in self.scene.data_store[image_idx]]
        self.tool.canvas = self._layer_data[self.active]
        self.image_idx = image_idx
        self.update()

    def set_opacity(self, layer_idx, value):
        self._opacities[layer_idx] = value
        self.update()

    def set_active(self, layer_idx):
        self._layer_data[self.active] = self.tool.canvas
        self.active = layer_idx
        self.tool.canvas = self._layer_data[self.active]
        self.tool.color = self._colors[self.active]
        self.tool.is_mask = self._masks[self.active]

    @property
    def data(self):
        result = self.tool.on_finalize()
        if not result is None:
            self._layer_data[self.active] = result
        return self._layer_data

    @property
    def tool_widget(self):
        if self.tool is None:
            return None
        return self.tool.on_show_widget()

    def change_tool(self, tool, status_callback=None):
        if tool not in self._tool_box:
            raise IndexError(f"'{tool}' is not a valid tool.")

        self.tool._on_hide()
        result = self.tool.on_finalize()
        if result is not None:
            result = result.copy()
        else:
            result = self._layer_data[self.active].copy()

        self.tool = self._tool_box[tool]
        self.tool.canvas = result
        self.tool.item = self
        self.tool.color = self._colors[self.active]
        self.tool.undo_stack = self._undo_stack
        self.tool.status_callback = status_callback
        self.tool.is_mask = self._masks[self.active]
        self.tool.on_show()

    def undo_tool_command(self, image):
        if self.tool:
            self.tool.canvas = image
            if self.tool.status_callback:
                if self.tool.undo_stack:
                    undo_text = f"'{self.tool.undo_stack.undoText()}'"
                else:
                    undo_text = ""
                self.tool.send_status_message(f"Undo {undo_text}")

    def redo_tool_command(self, image):
        if self.tool:
            self.tool.canvas = image
            if self.tool.status_callback:
                if self.tool.undo_stack:
                    redo_text = f"'{self.tool.undo_stack.redoText()}'"
                else:
                    redo_text = ""
                self.tool.send_status_message(f"Redo {redo_text}")

    def paint(self, painter, option, widget):
        for i, (image, opacity) in enumerate(zip(self._layer_data, self._opacities)):
            if i == self.active:
                canvas = self.tool.on_paint()
                if not canvas is None:
                    image = canvas
            painter.setOpacity(opacity)
            painter.drawImage(0, 0, util.to_qimage(image))

    def boundingRect(self):
        if self._layer_data is None:
            return QRect(0, 0, 1, 1)
        y, x = self._layer_data[0].shape[:2]
        return QRect(0, 0, x, y)

    def mousePressEvent(self, event):
        if self.tool:
            self.tool.on_mouse_pressed(tevent.MouseEvent(event))
            self.update()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.tool:
            self.tool.on_mouse_released(tevent.MouseEvent(event))
            self.update()
            return
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.tool:
            self.tool.on_mouse_moved(tevent.MouseEvent(event))
            self.update()
            return
        super().mouseMoveEvent(event)

    def tabletEvent(self, event):
        if self.tool is None:
            return
        if event.type() == QEvent.TabletPress:
            self.tool.on_tablet_pressed(tevent.MouseEvent(event))
        elif event.type() == QEvent.TabletMove:
            self.tool.on_tablet_moved(tevent.MouseEvent(event))
        elif event.type() == QEvent.TabletRelease:
            self.tool.on_tablet_released(tevent.MouseEvent(event))
        self.update()

    def keyPressEvent(self, event):
        if self.tool is None:
            return
        self.tool.on_key_pressed(tevent.KeyEvent(event))

    def keyReleaseEvent(self, event):
        if self.tool is None:
            return
        self.tool.on_key_released(tevent.KeyEvent(event))
