from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from .editoritem import EditorItem


class EditorScene(QGraphicsScene):

    image_loaded = Signal(int)
    opacity_changed = Signal(int, float)
    scene_cleared = Signal()
    image_modified = Signal()

    def __init__(self, data_loader):
        super().__init__()
        self.layers = []
        self.loader = data_loader
        self.opacities = [1.0] * len(data_loader.folders)
        self._undo_stack = QUndoStack()
        self._active_layer = len(data_loader.folders) - 1
        self._loaded_idx = -1

    @property
    def image_count(self):
        return 0 if not self.loader else len(self.loader)

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
            self._cache_if_dirty()
            for layer in self.layers:
                layer.is_dirty = False
        self.loader.save_to_disk()

    def clear(self):
        for layer in self.layers:
            self.removeItem(layer)
        self.layers.clear()
        self.scene_cleared.emit()

    def _cache_if_dirty(self):
        data = [l.data for l in self.layers]
        dirty = any(l.is_dirty for l in self.layers)

        if not dirty:
            return

        self.loader[self._loaded_idx] = data
        self.image_modified.emit()

    def load(self, image_idx):
        if self._loaded_idx >= 0:
            self._cache_if_dirty()
        self._loaded_idx = image_idx

        self.clear()
        self._undo_stack.clear()

        self.layers = []
        for i, layer in enumerate(self.loader[image_idx]):
            pen_colors = self.loader.pen_colors
            is_editable = self.loader.editable[i]
            item = EditorItem(layer, self._undo_stack, pen_colors[i], is_editable)
            item.image_modified.connect(self._cache_if_dirty)
            self.addItem(item)
            self.layers.append(item)

        for layer, opacity in zip(self.layers, self.opacities):
            layer.setOpacity(opacity)
        self.image_loaded.emit(image_idx)

    def change_layer_opacity(self, layer_idx, value):
        self.layers[layer_idx].setOpacity(value)
        self.opacities[layer_idx] = value
        self.opacity_changed.emit(layer_idx, value)

    def create_undo_action(self):
        return self._undo_stack.createUndoAction(self)

    def create_redo_action(self):
        return self._undo_stack.createRedoAction(self)
