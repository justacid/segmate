from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from segmate.editor.tools.editortool import EditorTool
from segmate.editor.toolwidget import EditorToolWidget


class CopyMaskToolInspector(EditorToolWidget):

    def __init__(self, callback):
        super().__init__("Copy Mask Tool")
        button = QPushButton("Copy layer from previous frame")
        button.pressed.connect(callback)
        self.add_widget(button)


class CopyMaskTool(EditorTool):

    def paint_canvas(self):
        return self.canvas

    def paint_result(self):
        return self.canvas

    def _copy_previous_mask(self):
        self.is_dirty = True
        idx = max(self.item.image_idx - 1, 0)
        layer = self.item.layer_idx
        mask = self.item.scene.data_loader[idx][layer]
        self.push_undo_snapshot(self.canvas, mask, undo_text="Copy Mask")
        self.canvas = QImage(mask)

    @property
    def inspector_widget(self):
        if not self.is_editable:
            return None
        return CopyMaskToolInspector(self._copy_previous_mask)
