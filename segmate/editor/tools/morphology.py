import numpy as np
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from scipy import ndimage as ndi
from skimage.color import rgb2gray
from skimage.filters import rank
import skimage.morphology as morph

from segmate.editor.tools.editortool import EditorTool
from segmate.editor.toolwidget import EditorToolWidget
import segmate.util as util


class MorphologyToolInspector(EditorToolWidget):

    def __init__(self, cb_fill, cb_dilate, cb_erode, cb_skel, cb_wshed):
        super().__init__("Morphology Tool")
        btn_fill = QPushButton("Fill Holes")
        btn_fill.pressed.connect(cb_fill)
        btn_dilate = QPushButton("Dilate")
        btn_dilate.pressed.connect(cb_dilate)
        btn_erode = QPushButton("Erode")
        btn_erode.pressed.connect(cb_erode)

        self.add_widget(btn_fill)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.add_widget(line)

        self.add_widget(btn_dilate)
        self.add_widget(btn_erode)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.add_widget(line)

        btn_skel = QPushButton("Skeletonize")
        btn_skel.pressed.connect(cb_skel)
        btn_wshed = QPushButton("Watershed")
        btn_wshed.pressed.connect(cb_wshed)
        self.add_widget(btn_skel)
        self.add_widget(btn_wshed)


class MorphologyTool(EditorTool):

    def paint_canvas(self):
        return self.canvas

    def paint_result(self):
        return self.canvas

    def _fill_holes(self):
        self.is_dirty = True
        mask = util.extract_binary_mask(self.canvas)
        filled = ndi.binary_fill_holes(mask)
        output = util.color_binary_mask(filled, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Fill Holes")
        self.canvas = output

    def _dilate(self):
        self.is_dirty = True
        mask = util.extract_binary_mask(self.canvas)
        mask = morph.binary_dilation(mask)
        output = util.color_binary_mask(mask, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Dilate")
        self.canvas = output

    def _erode(self):
        self.is_dirty = True
        mask = util.extract_binary_mask(self.canvas)
        mask = morph.binary_erosion(mask)
        output = util.color_binary_mask(mask, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Erode")
        self.canvas = output

    def _skeletonize(self):
        self.is_dirty = True
        mask = util.extract_binary_mask(self.canvas)
        mask = morph.skeletonize(mask)
        output = util.color_binary_mask(mask, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Skeletonize")
        self.canvas = output

    def _watershed(self):
        self.is_dirty = True

        image = self.item.scene.data_loader[self.item.image_idx][0]
        image = util.to_grayscale(image)

        markers = util.extract_binary_mask(self.canvas)
        markers = morph.label(markers, background=0)
        markers[0, markers.shape[1] - 1] = np.max(markers) + 1

        basin = rank.gradient(image, morph.disk(1))
        watershed = morph.watershed(basin, markers)

        result_mask = np.zeros(watershed.shape, dtype=np.uint8)
        result_mask[watershed != watershed[0][0]] = 1

        output = util.color_binary_mask(result_mask, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Watershed")
        self.canvas = output

    @property
    def inspector_widget(self):
        if not self.is_editable:
            return None
        return MorphologyToolInspector(
            self._fill_holes, self._dilate, self._erode,
            self._skeletonize, self._watershed)
