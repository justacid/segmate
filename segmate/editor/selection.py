import numpy as np
from PySide2.QtCore import Qt

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
            self.item_tablet_event = self.item.tablet_event

            self.item.mouse_pressed = self.__mouse_pressed
            self.item.mouse_released = self.__mouse_released
            self.item.mouse_moved = self.__mouse_moved
            self.item.tablet_event = self.__tablet_event

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

        image = canvas.copy()
        if self._has_gap_size(4) and not self._selecting:
            try:
                mask = np.zeros(image.shape[:2], dtype=np.bool)
                mask[self.indices] = True

                is_neg = self.indices[0] < 0
                js_neg = self.indices[1] < 0
                if is_neg.any() or js_neg.any():
                    self.reset()
                    return

                alpha = np.ones(image.shape[:2]) * 255
                alpha[image[:,:,1] == 0] = 96
                colors = np.dstack((image[:,:,:3] * 0.25, alpha))
                image[~mask] = colors[~mask]
            except:
                self.reset()
                return

        canvas[:] = image
        p0 = (self._corner1.y(), self._corner1.x())
        p1 = (self._corner2.y(), self._corner2.x())
        util.draw.rectangle(canvas, p0, p1, color=(47, 79, 79, 255))

    def _has_gap_size(self, gap_size):
        if self._corner1 is None or self._corner2 is None:
            return False
        if self.rect is None:
            return False
        p0, p1 = self.rect
        if p1[0] - p0[0] <= gap_size or p1[1] - p0[1] <= gap_size:
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

    def __tablet_event(self, event):
        if event.type() == QEvent.TabletPress and event.button() == Qt.LeftButton:
            self.start(event.pos())
        elif event.type() == QEvent.TabletMove and event.buttons() & Qt.LeftButton:
            self.move(event.pos())
        elif event.type() == QEvent.TabletRelease and event.button() == Qt.LeftButton:
            self.release(event.pos())
