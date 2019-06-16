import numpy as np

from ..editortool import EditorTool
from ..selection import RectSelection
from ..widgets import EditorToolWidget, Button
from ... import util


class MasksTool(EditorTool):

    def on_show(self):
        self._selection = RectSelection(self)

    def on_hide(self):
        self._selection.reset()

    def on_paint(self):
        image = self.canvas.copy()
        self._selection.paint(image)
        return image

    def on_show_widget(self):
        return MasksToolInspector(
            self._copy_previous_mask, self._clear_mask, self._merge_masks, self._clr_merge)

    def _copy_previous_mask(self):
        mask = util.mask.binary(self.get_layers(
            self.layer_index, max(self.image_index-1, 0)))
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
        current_mask = util.mask.binary(self.canvas)
        output = np.zeros(self.canvas.shape[:2], dtype=np.uint8)

        for i, layer in enumerate(self.get_layers()[1:]):
            mask = util.mask.binary(layer)
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


class MasksToolInspector(EditorToolWidget):

    def __init__(self, copy_cb, clear_cb, merge_cb, clr_merge_cb):
        super().__init__("Masks")
        self.add_widget(Button("Copy Previous Mask", callback=copy_cb))
        self.add_separator()
        self.add_widget(Button("Clear Mask", callback=clear_cb))
        self.add_widget(Button("Merge Masks", callback=merge_cb))
        self.add_widget(Button("Clear && Merge Masks", callback=clr_merge_cb))
