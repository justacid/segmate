from pathlib import Path
from os import listdir

import numpy as np
import imageio as io
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QGraphicsScene
from PySide2.QtGui import QImage, QPixmap

import util


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
        self.image_loaded.emit(idx)


class DataLoader:

    def __init__(self, folder, subfolders=None):
        self.folder = Path(folder)
        if subfolders is None:
            self.subfolders = listdir(self.folder)
        else:
            self.subfolders = [Path(s) for s in subfolders]

        self.files = [f for f in listdir(self.folder / self.subfolders[0])]
        self.files = sorted(self.files, key=lambda f: int(f.split("-")[1].split(".")[0]))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        assert idx >= 0 and idx < len(self.files)
        paths = [self.folder / s / self.files[idx] for s in self.subfolders]
        data = [QPixmap(util.np_to_qimage(io.imread(p))) for p in paths]
        return data
