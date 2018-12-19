from pathlib import Path
from os import listdir

import numpy as np
import imageio as io
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QGraphicsScene
from PySide2.QtGui import QImage, QPixmap

import util


class ImageScene(QGraphicsScene):

    changed = Signal()

    def __init__(self, loader=None, opacities=None):
        super().__init__()
        self.layers = []
        self.loader = loader

        if loader is None:
            self.opacities = None
        else:
            self.opacities = opacities or np.linspace(1.0, 0.2, len(loader[0]), endpoint=False)

    def set_opacity(self, idx, value):
        self.layers[idx].setOpacity(value)

    def set_loader(self, loader):
        self.loader = loader
        self.opacities = np.linspace(1.0, 0.2, len(loader[0]), endpoint=False)

    def set_image(self, idx):
        for layer in self.layers:
            self.removeItem(layer)
        self.layers.clear()

        for image, opacity in zip(self.loader[idx], self.opacities):
            item = self.addPixmap(image)
            item.setOpacity(opacity)
            self.layers.append(item)

        self.changed.emit()


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
