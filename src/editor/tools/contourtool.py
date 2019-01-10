from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import numpy as np
from skimage.measure import find_contours
from skimage.color import rgb2gray

from .editortool import EditorTool
import util


class ContourTool(EditorTool):

    def __init__(self, image, parent):
        super().__init__(image, parent)
        self._snapshot = QImage(image)

    def paint_canvas(self):
        image = util.from_qimage(self.canvas)
        image = util.to_qimage(self.draw_contours(image))
        return image

    def paint_result(self):
        return self._snapshot

    def draw_contours(self, image):
        if len(image.shape) == 2:
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
                output[int(r), int(c)] = (255, 0, 0, 255)

        return output
