from abc import ABC, abstractmethod

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from segmate.util import to_qimage


class EditorUndoCommand(QUndoCommand):

    def __init__(self, snapshot, modified):
        super().__init__()

        self._snapshot = QImage(snapshot)
        self._modified = QImage(modified)

        self.undo_triggered = None
        self.redo_triggered = None

    def undo(self):
        if self.undo_triggered:
            self.undo_triggered(QImage(self._snapshot))

    def redo(self):
        if self.redo_triggered:
            self.redo_triggered(QImage(self._modified))


class EditorTool(ABC):

    def __init__(self, image, parent):
        self._canvas = QImage(image)
        self._parent = parent
        self._pen_color = None
        self._undo_stack = None
        self._status_callback = None
        self._is_dirty = False

    @abstractmethod
    def paint_canvas(self):
        pass

    @abstractmethod
    def paint_result(self):
        pass

    def push_undo_snapshot(self, snapshot, modified, *, undo_text=""):
        if self._undo_stack:
            command = EditorUndoCommand(snapshot, modified)
            command.setText(undo_text)
            # a undo-command push triggers a redo - so push first, then
            # register callbacks; this suppresses the signal on initial redo
            self._undo_stack.push(command)
            command.undo_triggered = self._parent.undo_tool_command
            command.redo_triggered = self._parent.redo_tool_command

    def send_status_message(self, message):
        if self._status_callback:
            self._status_callback(message)

    def mouse_pressed(self, event):
        return False

    def mouse_released(self, event):
        return False

    def mouse_moved(self, event):
        return False

    def tablet_event(self, event, pos):
        pass

    @property
    def is_dirty(self):
        return self._is_dirty

    @is_dirty.setter
    def is_dirty(self, value):
        self._is_dirty = value
        if value:
            self.parent.image_modified.emit()

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent_):
        self._parent = parent_

    @property
    def canvas(self):
        return self._canvas

    @canvas.setter
    def canvas(self, canvas_):
        self._canvas = canvas_

    @property
    def cursor(self):
        return QCursor(Qt.ArrowCursor)

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
