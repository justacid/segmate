import numpy as np
from PySide2.QtCore import Qt

from .. import util


class RectSelection:

    def __init__(self, item=None):
        self._selecting = False
        self._corner1 = None
        self._corner2 = None

        self.item = item
        if self.item is not None:
            self.item_mouse_pressed = self.item.on_mouse_pressed
            self.item_mouse_moved = self.item.on_mouse_moved
            self.item_mouse_released = self.item.on_mouse_released
            self.item_tablet_pressed = self.item.on_tablet_pressed
            self.item_tablet_moved = self.item.on_tablet_moved
            self.item_tablet_released = self.item.on_tablet_released
            self.item.on_mouse_pressed = self.__mouse_pressed
            self.item.on_mouse_moved = self.__mouse_moved
            self.item.on_mouse_released = self.__mouse_released
            self.item.on_tablet_pressed = self.__tablet_pressed
            self.item.on_tablet_moved = self.__tablet_moved
            self.item.on_tablet_released = self.__tablet_released

    @property
    def is_active(self):
        if self._corner1 and self._corner2:
            return True

    @property
    def rect(self):
        y1, x1 = [int(c) for c in self._corner1]
        y2, x2 = [int(c) for c in self._corner2]

        if x1 > x2 and y1 > y2:
            return [(y2, x2), (y1, x1)]
        elif x1 < x2 and y1 > y2:
            return [(y1, x2), (y2, x1)]
        elif x1 > x2 and y1 < y2:
            return [(y2, x1), (y1, x2)]
        elif x1 < x2 and y1 < y2:
            return [(y1, x1), (y2, x2)]

    @property
    def indices(self):
        if not self.rect:
            return None
        c1, c2 = self.rect
        ys = np.arange(c1[0], c2[0], dtype=np.int32)
        xs = np.arange(c1[1], c2[1], dtype=np.int32)
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
            if not self._min_edge_length(4):
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
        if self._min_edge_length(4) and not self._selecting:
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
        util.draw.rectangle(canvas, self._corner1, self._corner2, color=(47, 79, 79, 255))

    def _min_edge_length(self, gap_size):
        if self._corner1 is None or self._corner2 is None:
            return False
        if self.rect is None:
            return False

        p0, p1 = self.rect
        if p1[0] - p0[0] <= gap_size or p1[1] - p0[1] <= gap_size:
            return False
        return True

    def __mouse_pressed(self, event):
        if event.buttons.left:
            self.start(event.pos)
        elif event.buttons.right:
            self.reset()
        self.item_mouse_pressed(event)

    def __mouse_moved(self, event):
        if event.buttons.left:
            self.move(event.pos)
        self.item_mouse_moved(event)

    def __mouse_released(self, event):
        if event.buttons.left:
            self.release(event.pos)
        self.item_mouse_released(event)

    def __tablet_pressed(self, event):
        if event.buttons.left:
            self.start(event.pos)
        elif event.buttons.middle:
            self.reset()
        self.item_tablet_pressed(event)

    def __tablet_moved(self, event):
        if event.buttons.left:
            self.move(event.pos)
        self.item_tablet_moved(event)

    def __tablet_released(self, event):
        if event.buttons.left:
            self.release(event.pos)
        self.item_tablet_released(event)
