from abc import ABC, abstractmethod

import util


class EditorTool(ABC):

    def __init__(self, image):
        self.image = image
        self.canvas = util.to_qimage(self.image)
        self._pen_color = None
        self._undo_stack = None
        self.status_callback = None

    @abstractmethod
    def paint(self):
        pass

    @abstractmethod
    def cursor(self):
        pass

    @property
    def penColor(self):
        return self._pen_color

    @penColor.setter
    def penColor(self, color):
        self._pen_color = color

    def addUndoCommand(self, command):
        if self._undo_stack:
            self._undo_stack.push(command)

    def setUndoStack(self, undo_stack):
        self._undo_stack = undo_stack

    def setStatusCallback(self, func):
        self.status_callback = func

    def sendStatusMessage(self, message):
        if self.status_callback:
            self.status_callback(message)

    def mousePressEvent(self, event):
        return False

    def mouseReleaseEvent(self, event):
        return False

    def mouseMoveEvent(self, event):
        return False
