from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from .item import EditorItem


class EditorScene(QGraphicsScene):

    image_loaded = Signal(int)
    opacity_changed = Signal(int, float)
    scene_cleared = Signal()
    image_modified = Signal()

    def __init__(self, data_store):
        super().__init__()
        self.layers = []
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
        self.layers[self._active_layer].is_active = False
        self.layers[idx].is_active = True
        self._active_layer = idx

    def save_to_disk(self):
        if self._loaded_idx >= 0:
            for layer in self.layers:
                layer.is_dirty = False
        self.data_store.save_to_disk()

    def load(self, image_idx):
        self._loaded_idx = image_idx
        if not self.layers:
            for layer_idx in range(self.data_store.num_layers):
                item = EditorItem(self)
                item.image_modified.connect(self._store_dirty)
                self.addItem(item)
                self.layers.append(item)

        for layer_idx, (layer, opacity) in enumerate(zip(self.layers, self.opacities)):
            layer.load(image_idx, layer_idx)
            layer.setOpacity(opacity)

        self.image_loaded.emit(image_idx)

    def change_layer_opacity(self, layer_idx, value):
        self.layers[layer_idx].setOpacity(value)
        self.opacities[layer_idx] = value
        self.opacity_changed.emit(layer_idx, value)

    def create_undo_action(self):
        return self.undo_stack.createUndoAction(self)

    def create_redo_action(self):
        return self.undo_stack.createRedoAction(self)

    def _store_dirty(self):
        dirty = any(layer.is_dirty for layer in self.layers)
        if not dirty:
            return
        self.data_store[self._loaded_idx] = [layer.data for layer in self.layers]
        self.image_modified.emit()
