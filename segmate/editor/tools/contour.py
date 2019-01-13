from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import numpy as np
from skimage.measure import find_contours
from skimage.color import rgb2gray

from segmate.editor.tools.editortool import EditorTool
from segmate.util import to_qimage, from_qimage


class ContourTool(EditorTool):

    def __init__(self, image, parent):
        super().__init__(image, parent)
        self._snapshot = QImage(image)

    def paint_canvas(self):
        image = from_qimage(self.canvas)
        image = to_qimage(self.draw_contours(image))
        return image

    def paint_result(self):
        return self._snapshot

    def draw_contours(self, image):
        if not self.is_editable:
            return image

        segmentation = rgb2gray(image[:,:,:3])
        if np.max(segmentation) == 0.0:
            return image


        mask = np.ones(segmentation.shape, dtype=np.uint8)
        mask[segmentation != 0.0] = 0

        contours = find_contours(mask, 0.25)
        output = np.zeros((*mask.shape, 4), dtype=np.uint8)

        for contour in contours:
            for r, c in contour:
                output[int(r), int(c)] = (*self.pen_color, 255)

        return output
