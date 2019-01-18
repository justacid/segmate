import numpy as np
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from skimage.measure import find_contours
from skimage.color import rgb2gray
from scipy.interpolate import CubicSpline

from segmate.editor.tools.editortool import EditorTool
import segmate.util as util


class ContourTool(EditorTool):

    def __init__(self, image, parent):
        super().__init__(image, parent)
        self._snapshot = QImage(image)

    def paint_canvas(self):
        if not self.is_editable:
            return self.canvas
        return self.draw_contours(self.canvas)

    def paint_result(self):
        return self._snapshot

    def draw_contours(self, image):
        mask = util.extract_binary_mask(image)
        if np.max(mask) == 0:
            return image

        mask = util.invert_binary_mask(mask)
        contours = find_contours(mask, 0.25)
        output = np.zeros(mask.shape, dtype=np.uint8)

        for contour in contours:
            contour = np.round(contour).astype(np.int32)
            output[contour[:, 0], contour[:, 1]] = 1

        return util.color_binary_mask(output, self.pen_color)
