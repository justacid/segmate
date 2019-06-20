from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from .layers import LayersGraphicsView


class EditorScene(QGraphicsScene):

    image_loaded = Signal(int)
    opacity_changed = Signal(int, float)
    scene_cleared = Signal()
    image_modified = Signal()
    tool_changed = Signal()

    def __init__(self, data_store):
        super().__init__()
        self.layers = None
        self.data_store = data_store
        self.opacities = [1.0] * len(data_store.folders)
        self.undo_stack = QUndoStack()
        self._active_layer = 0
        self._loaded_idx = -1

    @property
    def image_count(self):
        return 0 if not self.data_store else len(self.data_store)

    @property
    def active_layer(self):
        return self._active_layer

    @active_layer.setter
    def active_layer(self, idx):
        self.layers.set_active(idx)
        self._active_layer = idx

    def save_to_disk(self):
        self.data_store.save_to_disk()

    def load(self, image_idx):
        self._loaded_idx = image_idx
        if self.layers is None:
            self.layers = LayersGraphicsView(self)
            self.layers.image_modified.connect(self._store_dirty)
            self.layers.tool_changed.connect(self.tool_changed.emit)
            self.addItem(self.layers)
        self.layers.load(image_idx)
        self.image_loaded.emit(image_idx)

    def set_layer_opacity(self, layer_idx, value):
        self.layers.set_opacity(layer_idx, value)
        self.opacities[layer_idx] = value
        self.opacity_changed.emit(layer_idx, value)

    def create_undo_action(self):
        return self.undo_stack.createUndoAction(self)

    def create_redo_action(self):
        return self.undo_stack.createRedoAction(self)

    def _store_dirty(self):
        self.data_store[self._loaded_idx] = self.layers.data
        self.image_modified.emit()
