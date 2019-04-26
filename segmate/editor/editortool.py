from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QUndoCommand


class EditorUndoCommand(QUndoCommand):

    def __init__(self, snapshot, modified, tool):
        super().__init__()

        self._snapshot = snapshot.copy()
        self._modified = modified.copy()
        self._tool = tool

        self.undo_triggered = None
        self.redo_triggered = None

    def undo(self):
        if self.undo_triggered:
            self.undo_triggered(self._snapshot.copy())
            self._tool.notify_dirty()

    def redo(self):
        if self.redo_triggered:
            self.redo_triggered(self._modified.copy())
            self._tool.notify_dirty()


class EditorTool:

    def __init__(self):
        self.is_dirty = False
        self.canvas = None
        self.item = None
        self.color = None
        self.undo_stack = None
        self.status_callback = None
        self.is_editable = False
        self.is_mask = False
        self.on_create()

    def on_paint(self):
        return self.canvas

    def on_finalize(self):
        return self.canvas

    def on_create(self):
        pass

    def on_show(self):
        pass

    def on_hide(self):
        pass

    def on_mouse_pressed(self, event):
        pass

    def on_mouse_moved(self, event):
        pass

    def on_mouse_released(self, event):
        pass

    def on_tablet_pressed(self, event):
        pass

    def on_tablet_moved(self, event):
        pass

    def on_tablet_released(self, event):
        pass

    def on_key_pressed(self, event):
        pass

    def on_key_released(self, event):
        pass

    def on_show_widget(self):
        return None

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
        self.item.image_modified.emit()

    def set_cursor(self, name):
        if name is None:
            self.item.setCursor(QCursor(Qt.ArrowCursor))
            return
        self.item.setCursor(QCursor(name))

    def _on_hide(self):
        self.set_cursor(None)
        self.on_hide()
