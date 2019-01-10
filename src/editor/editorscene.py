from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from .editoritem import EditorItem


class EditorScene(QGraphicsScene):

    image_loaded = Signal(int)
    opacity_changed = Signal(int, float)
    scene_cleared = Signal()

    def __init__(self, data_loader):
        super().__init__()
        self.layers = []
        self.loader = data_loader
        self.undo_stack = QUndoStack()
        self.opacities = [1.0] * len(data_loader.folders)
        self.active_layer = len(data_loader.folders) - 1

    def numImages(self):
        return 0 if not self.loader else len(self.loader)

    def numLayers(self):
        return len(layers)

    def getOpacity(self, layer_idx):
        return self.opacities[layer_idx]

    def setOpacity(self, layer_idx, value):
        self.layers[layer_idx].setOpacity(value)
        self.opacities[layer_idx] = value
        self.opacity_changed.emit(layer_idx, value)

    def createUndoAction(self):
        return self.undo_stack.createUndoAction(self)

    def createRedoAction(self):
        return self.undo_stack.createRedoAction(self)

    def setActive(self, layer_idx):
        self.active_layer = layer_idx
        for i, layer in enumerate(self.layers):
            if i == layer_idx:
                layer.setActive(True)
            else:
                layer.setActive(False)

    def clear(self):
        for layer in self.layers:
            self.removeItem(layer)
        self.layers.clear()
        self.scene_cleared.emit()

    def load(self, image_idx):
        self.clear()
        self.undo_stack.clear()

        self.layers = []
        for i, layer in enumerate(self.loader[image_idx]):
            pen_colors = self.loader.pen_colors
            item = EditorItem(layer, self.undo_stack, pen_colors[i])
            self.addItem(item)
            self.layers.append(item)

        for layer, opacity in zip(self.layers, self.opacities):
            layer.setOpacity(opacity)
        self.image_loaded.emit(image_idx)
