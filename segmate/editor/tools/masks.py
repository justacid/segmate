import numpy as np
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from segmate.editor.tools.editortool import EditorTool
from segmate.editor.toolwidget import EditorToolWidget
import segmate.util as util


class MasksToolInspector(EditorToolWidget):

    def __init__(self, copy_cb, clear_cb, merge_cb):
        super().__init__("Masks")
        copy_button = QPushButton("Copy Previous Mask")
        copy_button.pressed.connect(copy_cb)
        clear_button = QPushButton("Clear Mask")
        clear_button.pressed.connect(clear_cb)
        merge_button = QPushButton("Merge Masks")
        merge_button.pressed.connect(merge_cb)
        self.add_widget(copy_button)
        self.add_widget(clear_button)
        self.add_widget(merge_button)


class MasksTool(EditorTool):

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

    def _clear_mask(self):
        mask = np.zeros((self.canvas.height(), self.canvas.width()), dtype=np.uint8)
        mask = util.color_binary_mask(mask, self.pen_color)
        self.push_undo_snapshot(self.canvas, mask, undo_text="Clear Mask")
        self.canvas = mask

    def _merge_masks(self):
        self.is_dirty = True

        idx = self.item.image_idx
        layer = self.item.layer_idx

        output = np.zeros((self.canvas.height(), self.canvas.width()), dtype=np.uint8)
        for i in range(1, len(self.item.scene.layers)):
            mask = util.extract_binary_mask(self.item.scene.data_loader[idx][i])
            output[mask == 1] = 1
        output = util.color_binary_mask(output, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Merge Mask")
        self.canvas = output

    @property
    def inspector_widget(self):
        if not self.is_editable:
            return None
        return MasksToolInspector(
            self._copy_previous_mask, self._clear_mask, self._merge_masks)
