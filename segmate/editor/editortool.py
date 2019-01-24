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

    def __init__(self, image, item):
        self.is_dirty = False

        self._canvas = QImage(image)
        self._item = item
        self._pen_color = None
        self._undo_stack = None
        self._status_callback = None
        self._is_editable = True

    @abstractmethod
    def paint_canvas(self):
        pass

    def paint_result(self):
        return self.canvas

    @property
    def inspector_widget(self):
        return None

    def push_undo_snapshot(self, snapshot, modified, *, undo_text=""):
        if self._undo_stack:
            command = EditorUndoCommand(snapshot, modified)
            command.setText(undo_text)
            # a undo-command push triggers a redo - so push first, then
            # register callbacks; this suppresses the signal on initial redo
            self._undo_stack.push(command)
            command.undo_triggered = self._item.undo_tool_command
            command.redo_triggered = self._item.redo_tool_command

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

    def notify_dirty(self):
        self.is_dirty = True
        self.item.image_modified.emit()

    @property
    def is_editable(self):
        return self._editable

    @is_editable.setter
    def is_editable(self, value):
        self._editable = value

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, item_):
        self._item = item_

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
