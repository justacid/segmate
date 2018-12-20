from PySide2.QtCore import Signal
from PySide2.QtWidgets import QGraphicsScene


class ImageScene(QGraphicsScene):

    image_loaded = Signal(int)
    opacity_changed = Signal(int, float)
    scene_cleared = Signal()

    def __init__(self, data_loader):
        super().__init__()
        self.layers = []
        self.loader = data_loader
        self.opacities = [1.0] * len(data_loader)

    def numImages(self):
        return 0 if not self.loader else len(self.loader)

    def numLayers(self):
        return len(layers)

    def getOpacity(self, idx):
        return self.opacities[idx]

    def setOpacity(self, idx, value):
        self.layers[idx].setOpacity(value)
        self.opacities[idx] = value
        self.opacity_changed.emit(idx, value)

    def clear(self):
        for layer in self.layers:
            self.removeItem(layer)
        self.layers.clear()
        self.scene_cleared.emit()

    def load(self, idx):
        self.clear()
        self.layers = [self.addPixmap(i) for i in self.loader[idx]]
        for layer, opacity in zip(self.layers, self.opacities):
            layer.setOpacity(opacity)
        self.image_loaded.emit(idx)
