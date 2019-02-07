from abc import ABC, abstractmethod

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from segmate.util import to_qimage


class EditorUndoCommand(QUndoCommand):

    def __init__(self, snapshot, modified, tool):
        super().__init__()

        self._snapshot = QImage(snapshot)
        self._modified = QImage(modified)
        self._tool = tool

        self.undo_triggered = None
        self.redo_triggered = None

    def undo(self):
        if self.undo_triggered:
            self.undo_triggered(QImage(self._snapshot))
            self._tool.notify_dirty()

    def redo(self):
        if self.redo_triggered:
            self.redo_triggered(QImage(self._modified))
            self._tool.notify_dirty()


class EditorTool(ABC):

    def __init__(self):
        self.is_dirty = False
        self.canvas = None
        self.item = None
        self.color = None
        self.undo_stack = None
        self.status_callback = None
        self.is_editable = False
        self.is_mask = False

    @property
    def inspector_widget(self):
        return None

    @property
    def cursor(self):
        return QCursor(Qt.ArrowCursor)

    @abstractmethod
    def paint_canvas(self):
        return self.canvas

    def paint_result(self):
        return self.canvas

    def push_undo_snapshot(self, snapshot, modified, *, undo_text=""):
        if self.undo_stack:
            command = EditorUndoCommand(snapshot, modified, self)
            command.setText(undo_text)
            # a undo-command push triggers a redo - so push first, then
            # register callbacks; this suppresses the signal on initial redo
            self.undo_stack.push(command)
            command.undo_triggered = self.item.undo_tool_command
            command.redo_triggered = self.item.redo_tool_command

    def send_status_message(self, message):
        if self.status_callback:
            self.status_callback(message)

    def notify_dirty(self):
        self.is_dirty = True
        self.item.image_modified.emit()

    def mouse_pressed(self, event):
        return False

    def mouse_released(self, event):
        return False

    def mouse_moved(self, event):
        return False

    def tablet_event(self, event):
        pass
