import numpy as np
from skimage.color import rgb2gray
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from segmate.editor.editortool import EditorTool
from segmate.util import to_qimage, from_qimage


class BucketFillTool(EditorTool):

    def __init__(self):
        super().__init__()

    def paint_canvas(self):
        return self.canvas

    def mouse_pressed(self, event):
        if event.button() == Qt.LeftButton:
            self.fill_image(event.pos())

    def tablet_event(self, event):
        if event.type() == QEvent.TabletPress and event.button() == Qt.LeftButton:
            self.fill_image(event.pos())

    def fill_image(self, pos):
        if not self.is_editable:
            self.send_status_message("This layer is not editable...")
            return
        data = from_qimage(self.canvas)
        seed = [pos.y(), pos.x()]
        filled = to_qimage(self.flood_fill(data, seed))
        self.push_undo_snapshot(self.canvas, filled, undo_text="Bucket Fill")
        self.canvas = filled
        self.notify_dirty()

    def flood_fill(self, image, seed):
        h, w = image.shape[:2]
        coords = [[int(c) for c in seed]]

        while coords:
            y, x = coords.pop()
            image[y, x] = (*self.pen_color, 255)

            if y + 1 < h and not any(image[y + 1, x]):
                coords.append([y + 1, x])
            if y - 1 >= 0 and not any(image[y - 1, x]):
                coords.append([y - 1, x])
            if x + 1 < w and not any(image[y, x + 1]):
                coords.append([y, x + 1])
            if x - 1 >= 0 and not any(image[y, x - 1]):
                coords.append([y, x - 1])

        return image

    @property
    def cursor(self):
        return QCursor(QPixmap("icons/cross-cursor.png"))
