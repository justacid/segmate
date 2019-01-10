import numpy as np
from skimage.color import rgb2gray
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from .editortool import EditorTool
from util import to_qimage, from_qimage


class BucketFillUndoCommand(QUndoCommand):

    def __init__(self, before, after):
        super().__init__("Bucket fill")
        self.triggered_undo = None
        self.triggered_redo = None
        self.before_image = QImage(before)
        self.after_image = QImage(after)

    def undo(self):
        if self.triggered_undo:
            self.triggered_undo(QImage(self.before_image))

    def redo(self):
        if self.triggered_redo:
            self.triggered_redo(QImage(self.after_image))


class BucketFillTool(EditorTool):

    def __init__(self, image):
        super().__init__(image)

    def paint_canvas(self):
        return self.canvas

    def paint_result(self):
        return self.canvas

    def mouse_pressed(self, event):
        if event.button() == Qt.LeftButton:
            mouse_pos = event.pos()
            data = from_qimage(self.canvas)
            seed = [mouse_pos.y(), mouse_pos.x()]
            filled = to_qimage(self.flood_fill(data, seed))
            fill_command = BucketFillUndoCommand(self.canvas, filled)
            fill_command.triggered_undo = self.undo_command
            fill_command.triggered_redo = self.redo_command
            self.push_undo_command(fill_command)
            self.canvas = filled

    def flood_fill(self, image, seed):
        if len(image.shape) == 2:
            return image

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

    def undo_command(self, image):
        self.send_status_message("Undo...")
        self.canvas = image

    def redo_command(self, image):
        self.canvas = image
