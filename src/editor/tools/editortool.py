from abc import ABC, abstractmethod

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QUndoStack
from PySide2.QtGui import QImage
from util import to_qimage


class EditorTool(ABC):

    def __init__(self, image):
        self._canvas = QImage(image)
        self._pen_color = None
        self._undo_stack = None
        self._status_callback = None

    @abstractmethod
    def paint_canvas(self):
        pass

    @abstractmethod
    def paint_result(self):
        pass

    def push_undo_command(self, command):
        if self._undo_stack:
            self._undo_stack.push(command)

    def send_status_message(self, message):
        if self._status_callback:
            self._status_callback(message)

    def mouse_pressed(self, event):
        return False

    def mouse_released(self, event):
        return False

    def mouse_moved(self, event):
        return False

    @property
    def canvas(self):
        return self._canvas

    @canvas.setter
    def canvas(self, canvas_):
        self._canvas = canvas_

    @property
    def cursor(self):
        return Qt.ArrowCursor

    @property
    def pen_color(self):
        return self._pen_color

    @pen_color.setter
    def pen_color(self, color):
        self._pen_color = color

    @property
    def undo_stack(self):
        return self._undo_stack

    @undo_stack.setter
    def undo_stack(self, stack):
        if not isinstance(stack, QUndoStack):
            raise TypeError("Stack argument must be 'QUndoStack'.")
        self._undo_stack = stack

    @property
    def status_callback(self):
        return self._status_callback

    @status_callback.setter
    def status_callback(self, func):
        self._status_callback = func
