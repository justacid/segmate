import numpy as np
from scipy import ndimage as ndi
from skimage.filters import rank
import skimage.morphology as morph

from ..editortool import EditorTool
from ..widgets import EditorToolWidget, Button
from ... import util


class MorphologyTool(EditorTool):

    def on_show(self):
        self.enable_selection(True)

    def on_show_widget(self):
        return MorphologyToolInspector(
            self._fill_holes, self._dilate, self._erode,
            self._skeletonize, self._watershed)

    def on_key_pressed(self, event):
        if event.key.Key_W:
            self._watershed()
        elif event.key.Key_E:
            self._erode()
        elif event.key.Key_S:
            self._skeletonize()
        elif event.key.Key_D:
            self._dilate()
        elif event.key.Key_F:
            self._fill_holes()

    def _fill_holes(self):
        if not self.is_mask:
            return

        mask = util.mask.binary(self.canvas)
        filled = ndi.binary_fill_holes(mask)

        if self.selection_rect:
            selection = util.mask.selection(mask, self.selection_rect)
            filled[~selection] = mask[~selection]

        output = util.mask.color(filled, self.color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Fill Holes")
        self.canvas = output
        self.notify_dirty()

    def _dilate(self):
        if not self.is_mask:
            return

        mask = util.mask.binary(self.canvas)
        dilated = morph.binary_dilation(mask)

        if self.selection_rect:
            selection = util.mask.selection(mask, self.selection_rect)
            dilated[~selection] = mask[~selection]

        output = util.mask.color(dilated, self.color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Dilate")
        self.canvas = output
        self.notify_dirty()

    def _erode(self):
        if not self.is_mask:
            return

        mask = util.mask.binary(self.canvas)
        eroded = morph.binary_erosion(mask)

        if self.selection_rect:
            selection = util.mask.selection(mask, self.selection_rect)
            eroded[~selection] = mask[~selection]

        output = util.mask.color(eroded, self.color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Erode")
        self.canvas = output
        self.notify_dirty()

    def _skeletonize(self):
        if not self.is_mask:
            return

        mask = util.mask.binary(self.canvas)
        skeletonized = morph.skeletonize(mask)

        if self.selection_rect:
            selection = util.mask.selection(mask, self.selection_rect)
            skeletonized[~selection] = mask[~selection]

        output = util.mask.color(skeletonized, self.color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Skeletonize")
        self.canvas = output
        self.notify_dirty()

    def _watershed(self):
        if not self.is_mask:
            return

        markers = util.mask.binary(self.canvas)
        markers = morph.label(markers, background=0)
        markers[0, markers.shape[1] - 1] = np.max(markers) + 1

        image = util.mask.grayscale(self.get_layers(0))
        basin = rank.gradient(image, morph.disk(1))
        watershed = morph.watershed(basin, markers)

        result_mask = np.zeros(watershed.shape, dtype=np.uint8)
        result_mask[watershed != watershed[0][0]] = 1

        if self.selection_rect:
            selection = util.mask.selection(markers, self.selection_rect)
            result_mask[~selection] = util.mask.binary(self.canvas)[~selection]

        output = util.mask.color(result_mask, self.color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Watershed")
        self.canvas = output
        self.notify_dirty()


class MorphologyToolInspector(EditorToolWidget):

    def __init__(self, cb_fill, cb_dilate, cb_erode, cb_skel, cb_wshed):
        super().__init__("Morphology")
        self.add_widget(Button("Fill Holes", callback=cb_fill))
        self.add_separator()
        self.add_widget(Button("Dilate", callback=cb_dilate))
        self.add_widget(Button("Erode", callback=cb_erode))
        self.add_separator()
        self.add_widget(Button("Skeletonize", callback=cb_skel))
        self.add_widget(Button("Watershed", callback=cb_wshed))
