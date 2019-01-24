import numpy as np
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from scipy import ndimage as ndi
from skimage.color import rgb2gray
from skimage.filters import rank
import skimage.morphology as morph

from segmate.editor.editortool import EditorTool
from segmate.editor.widgets import EditorToolWidget
from segmate.editor.selection import RectSelection
import segmate.util as util


class MorphologyToolInspector(EditorToolWidget):

    def __init__(self, cb_fill, cb_dilate, cb_erode, cb_skel, cb_wshed):
        super().__init__("Morphology")
        btn_fill = QPushButton("Fill Holes")
        btn_fill.pressed.connect(cb_fill)
        btn_dilate = QPushButton("Dilate")
        btn_dilate.pressed.connect(cb_dilate)
        btn_erode = QPushButton("Erode")
        btn_erode.pressed.connect(cb_erode)
        btn_skel = QPushButton("Skeletonize")
        btn_skel.pressed.connect(cb_skel)
        btn_wshed = QPushButton("Watershed")
        btn_wshed.pressed.connect(cb_wshed)

        self.add_widget(btn_fill)
        self.add_separator()
        self.add_widget(btn_dilate)
        self.add_widget(btn_erode)
        self.add_separator()
        self.add_widget(btn_skel)
        self.add_widget(btn_wshed)


class MorphologyTool(EditorTool):

    def __init__(self, image, item):
        super().__init__(image, item)
        self._selection = RectSelection(self)

    def paint_canvas(self):
        image = QImage(self.canvas)
        self._selection.paint(image)
        return image

    def _fill_holes(self):
        mask = util.extract_binary_mask(self.canvas)
        filled = ndi.binary_fill_holes(mask)

        if self._selection.is_active:
            sel_mask = np.zeros(mask.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            filled[~sel_mask] = mask[~sel_mask]

        output = util.color_binary_mask(filled, self.pen_color)

        self.push_undo_snapshot(self.canvas, output, undo_text="Fill Holes")
        self.canvas = output
        self.notify_dirty()

    def _dilate(self):
        mask = util.extract_binary_mask(self.canvas)
        dilated = morph.binary_dilation(mask)

        if self._selection.is_active:
            sel_mask = np.zeros(mask.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            dilated[~sel_mask] = mask[~sel_mask]

        output = util.color_binary_mask(dilated, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Dilate")
        self.canvas = output
        self.notify_dirty()

    def _erode(self):
        mask = util.extract_binary_mask(self.canvas)
        eroded = morph.binary_erosion(mask)

        if self._selection.is_active:
            sel_mask = np.zeros(mask.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            eroded[~sel_mask] = mask[~sel_mask]

        output = util.color_binary_mask(eroded, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Erode")
        self.canvas = output
        self.notify_dirty()

    def _skeletonize(self):
        mask = util.extract_binary_mask(self.canvas)
        skeletonized = morph.skeletonize(mask)

        if self._selection.is_active:
            sel_mask = np.zeros(mask.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            skeletonized[~sel_mask] = mask[~sel_mask]

        output = util.color_binary_mask(skeletonized, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Skeletonize")
        self.canvas = output
        self.notify_dirty()

    def _watershed(self):
        image = self.item.scene.data_store[self.item.image_idx][0]
        image = util.to_grayscale(image)

        markers = util.extract_binary_mask(self.canvas)
        markers = morph.label(markers, background=0)
        markers[0, markers.shape[1] - 1] = np.max(markers) + 1

        basin = rank.gradient(image, morph.disk(1))
        watershed = morph.watershed(basin, markers)

        result_mask = np.zeros(watershed.shape, dtype=np.uint8)
        result_mask[watershed != watershed[0][0]] = 1

        if self._selection.is_active:
            sel_mask = np.zeros(markers.shape, dtype=np.bool)
            sel_mask[self._selection.indices] = True
            result_mask[~sel_mask] = util.extract_binary_mask(self.canvas)[~sel_mask]

        output = util.color_binary_mask(result_mask, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Watershed")
        self.canvas = output
        self.notify_dirty()

    @property
    def inspector_widget(self):
        if not self.is_editable:
            return None
        return MorphologyToolInspector(
            self._fill_holes, self._dilate, self._erode,
            self._skeletonize, self._watershed)
