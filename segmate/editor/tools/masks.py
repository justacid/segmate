import numpy as np

from ..editortool import EditorTool
from ..widgets import EditorToolWidget, Button
from ... import util


class MasksTool(EditorTool):

    def on_show(self):
        self.enable_selection(True)

    def on_show_widget(self):
        return MasksToolInspector(self._clear_mask, self._merge_masks)

    def _clear_mask(self):
        if not self.is_mask:
            return

        mask = util.mask.binary(self.canvas)
        if self.selection_rect:
            mask[util.mask.selection(mask, self.selection_rect)] = 0
        else:
            mask = np.zeros(mask.shape, dtype=np.uint8)
        image = util.mask.color(mask, self.color)

        self.push_undo_snapshot(self.canvas, image, undo_text="Clear Mask")
        self.canvas = image
        self.notify_dirty()

    def _merge_masks(self):
        if not self.is_mask:
            return

        output = util.mask.binary(self.canvas)
        for i, layer in enumerate(self.get_layers()[1:]):
            mask = util.mask.binary(layer)
            if self.selection_rect:
                selection = util.mask.selection(mask, self.selection_rect)
                output[(mask == 1) & (selection == 1)] = 1
            else:
                output[mask == 1] = 1
        output = util.mask.color(output, self.color)

        self.push_undo_snapshot(self.canvas, output, undo_text="Merge Mask")
        self.canvas = output
        self.notify_dirty()


class MasksToolInspector(EditorToolWidget):

    def __init__(self, clear_cb, merge_cb):
        super().__init__("Masks")
        self.add_widget(Button("Clear Mask", callback=clear_cb))
        self.add_widget(Button("Merge Masks", callback=merge_cb))
