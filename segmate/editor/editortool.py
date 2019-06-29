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
        self._item = None
        self.is_dirty = False
        self.canvas = None
        self.color = None
        self.undo_stack = None
        self.status_callback = None
        self.is_mask = False

    @property
    def image_index(self):
        return self._item.image_index

    @property
    def layer_index(self):
        return self._item.active

    @property
    def layer_name(self):
        return self._item.layer_names[self._item.active]

    @property
    def selection_rect(self):
        return self._item.selection_rect

    @property
    def panes(self):
        return self._item.panes

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
            command.undo_triggered = self._item.undo_tool_command
            command.redo_triggered = self._item.redo_tool_command

    def send_status_message(self, message):
        if self.status_callback:
            self.status_callback(message)

    def notify_dirty(self):
        self._item.image_modified.emit()

    def set_cursor(self, name):
        if name is None:
            self._item.setCursor(QCursor(Qt.ArrowCursor))
            return
        self._item.setCursor(QCursor(name))

    def enable_selection(self, enabled):
        self._item.show_selection = enabled

    def set_layer(self, layer_index, image):
        self._item._layer_data[layer_index] = image

    def get_layers(self, layer_index=None, image_index=None):
        if image_index is not None:
            assert isinstance(image_index, int)
        if layer_index is not None:
            assert isinstance(layer_index, int)

        if image_index is None:
            if layer_index is None:
                return self._item._layer_data.copy()
            return self._item._layer_data[layer_index].copy()

        if layer_index is None:
            return self._item.scene.data_store[image_index].copy()
        return self._item.scene.data_store[image_index][layer_index].copy()

    def get_color(self, layer_index):
        return self._item._colors[layer_index]

    def get_is_mask(self, layer_index):
        return self._item._masks[layer_index]

    def update(self):
        self._item.update()

    def _on_hide(self):
        self.set_cursor(None)
        self.on_hide()
        self._item.show_selection = False
