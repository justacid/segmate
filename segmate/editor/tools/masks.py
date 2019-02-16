import numpy as np
from PySide2.QtWidgets import QPushButton

from segmate.editor.editortool import EditorTool
from segmate.editor.widgets import EditorToolWidget
from segmate.editor.selection import RectSelection
import segmate.util as util


class MasksToolInspector(EditorToolWidget):

    def __init__(self, copy_cb, clear_cb, merge_cb, clr_merge_cb):
        super().__init__("Masks")
        copy_button = QPushButton("Copy Previous Mask")
        copy_button.pressed.connect(copy_cb)
        clear_button = QPushButton("Clear Mask")
        clear_button.pressed.connect(clear_cb)
        merge_button = QPushButton("Merge Masks")
        merge_button.pressed.connect(merge_cb)
        clr_merge_btn = QPushButton("Clear && Merge Masks")
        clr_merge_btn.pressed.connect(clr_merge_cb)
        self.add_widget(copy_button)
        self.add_separator()
        self.add_widget(clear_button)
        self.add_widget(merge_button)
        self.add_widget(clr_merge_btn)


class MasksTool(EditorTool):

    def on_show(self):
        self._selection = RectSelection(self)

    def on_hide(self):
        self._selection.reset()

    def on_paint(self):
        image = self.canvas.copy()
        self._selection.paint(image)
        return image

    def _copy_previous_mask(self):
        idx = max(self.item.image_idx - 1, 0)
        layer = self.item.layer_idx
        mask = util.mask.binary(self.item.scene.data_store[idx][layer])
        current_mask = util.mask.binary(self.canvas)

        output = np.zeros(mask.shape, dtype=np.uint8)
        if self._selection.is_active:
            sel_mask = np.zeros(mask.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            output[current_mask == 1] = 1
            output[(mask == 1) & (sel_mask == 1)] = 1
        else:
            output[mask == 1] = 1
        output = util.mask.color(output, self.color)

        self.push_undo_snapshot(self.canvas, output, undo_text="Copy Mask")
        self.canvas = output
        self.notify_dirty()

    def _clear_mask(self):
        mask = util.mask.binary(self.canvas)
        if self._selection.is_active:
            mask[self._selection.indices] = 0
        else:
            mask = np.zeros(mask.shape, dtype=np.uint8)

        image = util.mask.color(mask, self.color)
        self.push_undo_snapshot(self.canvas, image, undo_text="Clear Mask")
        self.canvas = image
        self.notify_dirty()

    def _merge_masks(self):
        idx = self.item.image_idx
        layer = self.item.layer_idx

        current_mask = util.mask.binary(self.canvas)
        output = np.zeros(self.canvas.shape[:2], dtype=np.uint8)

        for i in range(self.item.scene.data_store.num_layers):
            if not self.item.scene.data_store.masks[i]:
                continue
            mask = util.mask.binary(self.item.scene.data_store[idx][i])
            if self._selection.is_active:
                sel_mask = np.zeros(mask.shape, dtype=np.bool)
                sel_mask[self._selection.indices] = True
                output[(mask == 1) & (sel_mask == 1)] = 1
                output[current_mask == 1] = 1
            else:
                output[mask == 1] = 1

        output = util.mask.color(output, self.color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Merge Mask")
        self.canvas = output
        self.notify_dirty()

    def _clr_merge(self):
        self._clear_mask()
        self._merge_masks()

    @property
    def widget(self):
        return MasksToolInspector(
            self._copy_previous_mask, self._clear_mask, self._merge_masks, self._clr_merge)
