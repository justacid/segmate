import numpy as np
from scipy import ndimage as ndi
from skimage.filters import rank
import skimage.morphology as morph

from segmate.editor.editortool import EditorTool
from segmate.editor.selection import RectSelection
from segmate.editor.widgets import EditorToolWidget, Button
import segmate.util as util


class MorphologyTool(EditorTool):

    def on_show(self):
        self._selection = RectSelection(self)

    def on_hide(self):
        self._selection.reset()

    def on_paint(self):
        image = self.canvas.copy()
        self._selection.paint(image)
        return image

    def on_show_widget(self):
        return MorphologyToolInspector(
            self._fill_holes, self._dilate, self._erode,
            self._skeletonize, self._watershed)

    def _fill_holes(self):
        mask = util.mask.binary(self.canvas)
        filled = ndi.binary_fill_holes(mask)

        if self._selection.is_active:
            sel_mask = np.zeros(mask.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            filled[~sel_mask] = mask[~sel_mask]

        output = util.mask.color(filled, self.color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Fill Holes")
        self.canvas = output
        self.notify_dirty()

    def _dilate(self):
        mask = util.mask.binary(self.canvas)
        dilated = morph.binary_dilation(mask)

        if self._selection.is_active:
            sel_mask = np.zeros(mask.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            dilated[~sel_mask] = mask[~sel_mask]

        output = util.mask.color(dilated, self.color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Dilate")
        self.canvas = output
        self.notify_dirty()

    def _erode(self):
        mask = util.mask.binary(self.canvas)
        eroded = morph.binary_erosion(mask)

        if self._selection.is_active:
            sel_mask = np.zeros(mask.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            eroded[~sel_mask] = mask[~sel_mask]

        output = util.mask.color(eroded, self.color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Erode")
        self.canvas = output
        self.notify_dirty()

    def _skeletonize(self):
        mask = util.mask.binary(self.canvas)
        skeletonized = morph.skeletonize(mask)

        if self._selection.is_active:
            sel_mask = np.zeros(mask.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            skeletonized[~sel_mask] = mask[~sel_mask]

        output = util.mask.color(skeletonized, self.color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Skeletonize")
        self.canvas = output
        self.notify_dirty()

    def _watershed(self):
        markers = util.mask.binary(self.canvas)
        markers = morph.label(markers, background=0)
        markers[0, markers.shape[1] - 1] = np.max(markers) + 1

        image = self.item._layer_data[0]
        image = util.mask.grayscale(image)
        basin = rank.gradient(image, morph.disk(1))
        watershed = morph.watershed(basin, markers)

        result_mask = np.zeros(watershed.shape, dtype=np.uint8)
        result_mask[watershed != watershed[0][0]] = 1

        if self._selection.is_active:
            sel_mask = np.zeros(markers.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            result_mask[~sel_mask] = util.mask.binary(self.canvas)[~sel_mask]

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
