import numpy as np
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import segmate.util as util


class RectSelection:

    def __init__(self, item=None):
        self._selecting = False
        self._corner1 = None
        self._corner2 = None

        self.item = item
        if self.item is not None:
            self.item_mouse_pressed = self.item.mouse_pressed
            self.item_mouse_released = self.item.mouse_released
            self.item_mouse_moved = self.item.mouse_moved

            self.item.mouse_pressed = self.__mouse_pressed
            self.item.mouse_released = self.__mouse_released
            self.item.mouse_moved = self.__mouse_moved

    @property
    def is_active(self):
        if self._corner1 and self._corner2:
            return True

    @property
    def rect(self):
        x1, x2 = int(self._corner1.x()), int(self._corner2.x())
        y1, y2 = int(self._corner1.y()), int(self._corner2.y())
        if x1 > x2 and y1 > y2:
            return [(x2, y2), (x1, y1)]
        elif x1 < x2 and y1 > y2:
            return [(x1, y2), (x2, y1)]
        elif x1 > x2 and y1 < y2:
            return [(x2, y1), (x1, y2)]
        elif x1 < x2 and y1 < y2:
            return [(x1, y1), (x2, y2)]

    @property
    def indices(self):
        if not self.rect:
            return None
        c1, c2 = self.rect
        xs = np.arange(c1[0], c2[0], dtype=np.int32)
        ys = np.arange(c1[1], c2[1], dtype=np.int32)
        return tuple(np.meshgrid(ys, xs, indexing="ij"))

    def start(self, pos):
        self._selecting = True
        self._corner1 = pos
        self._corner2 = None

    def move(self, pos):
        if self._selecting:
            self._corner2 = pos

    def release(self, pos):
        if self._selecting:
            self._selecting = False
            self._corner2 = pos

            if self._corner1 is None or self._corner2 is None:
                self.reset()
                return
            if not self._has_gap_size(4):
                self.reset()

    def reset(self):
        self._selecting = False
        self._corner1 = None
        self._corner2 = None

    def paint(self, canvas):
        if not self.is_active:
            return
        if not self.indices:
            return

        image = util.from_qimage(canvas)
        if self._has_gap_size(4) and not self._selecting:
            try:
                mask = np.zeros(image.shape[:2], dtype=np.bool)
                mask[self.indices] = True

                is_neg = self.indices[0] < 0
                js_neg = self.indices[1] < 0
                if is_neg.any() or js_neg.any():
                    self.reset()
                    return

                image[~mask] = (0, 0, 0, 96)
            except:
                self.reset()
                return
        image = util.to_qimage(image)

        painter = QPainter(canvas)
        painter.drawImage(0, 0, image)
        painter.setPen(QPen(QColor(47, 79, 79)))
        painter.drawRect(QRectF(self._corner1, self._corner2))

    def _has_gap_size(self, gap_size):
        if self._corner1 is None or self._corner2 is None:
            return False
        x1, x2 = self._corner1.x(), self._corner2.x()
        y1, y2 = self._corner1.y(), self._corner2.y()
        if x2 - x1 <= gap_size or y2 - y1 <= gap_size:
            return False
        return True

    def __mouse_pressed(self, event):
        if event.button() == Qt.LeftButton:
            self.start(event.pos())
            return True
        if event.button() == Qt.RightButton:
            self.reset()
            return True
        return self.item_mouse_pressed(event)

    def __mouse_released(self, event):
        if event.button() == Qt.LeftButton:
            self.release(event.pos())
            return True
        return self.item_mouse_released(event)

    def __mouse_moved(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.pos())
            return True
        return self.item_mouse_moved(event)
