from os import listdir
from pathlib import Path

import imageio as io
import numpy as np
from PySide2.QtGui import *

import util


class DataLoader:

    def __init__(self, folder):
        self.root = Path(folder)
        self.folders = ["images", "masks", "spores"]

        self.files = [f for f in listdir(self.root / self.folders[0])]
        self.files = sorted(self.files, key=lambda f: int(f.split("-")[1].split(".")[0]))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        assert idx >= 0 and idx < len(self.files)

        data = [
            self.loadImage(idx),
            self.loadMask(idx, self.folders[1], color=(255, 255, 0)),
            self.loadMask(idx, self.folders[2], color=(0, 255, 255)),
        ]

        return data

    def penColors(self):
        return [(255, 255, 255), (255, 255, 0), (0, 255, 255)]

    def loadImage(self, idx):
        path = self.root / self.folders[0] / self.files[idx]
        return util.to_qimage(io.imread(path))

    def loadMask(self, idx, folder, color=(255, 255, 255)):
        path = self.root / folder / self.files[idx]
        mask = io.imread(path, as_gray=True)
        image = self.makeAlpha(mask, color=color)
        return util.to_qimage(image)

    def makeAlpha(self, image, color=(255, 255, 255)):
        alpha = np.zeros([*image.shape, 4], dtype=np.uint8)
        alpha[image == 0, :] = (0, 0, 0, 0)
        alpha[image == 255, :] = (*color, 255)
        return alpha
