from os import listdir
from pathlib import Path

import imageio as io
import numpy as np
from skimage import img_as_ubyte
from skimage.color import rgb2gray

from segmate.util import to_qimage, from_qimage


class DataLoader:

    def __init__(self, folder):
        self.root = Path(folder)
        self.folders = ["images", "masks", "spores"]
        self.editable = [False, True, True]
        self.cache = {}
        self.modified = set()
        self.files = [f for f in listdir(self.root / self.folders[0])]
        self.files = sorted(self.files, key=lambda f: int(f.split("-")[1].split(".")[0]))

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        assert idx >= 0 and idx < len(self.files)

        if idx in self.cache:
            return self.cache[idx]

        data = [
            self._load_image(idx),
            self._load_mask(idx, self.folders[1], color=self.pen_colors[1]),
            self._load_mask(idx, self.folders[2], color=self.pen_colors[2]),
        ]

        self.cache[idx] = data
        return data

    def __setitem__(self, idx, value):
        self.cache[idx] = value
        self.modified.add(idx)

    def save_to_disk(self):
        for idx in self.modified:
            _, mask1, mask2 = self.cache[idx]
            mask1 = self._binarize(mask1)
            mask2 = self._binarize(mask2)
            io.imsave(self.root / self.folders[1] / self.files[idx], mask1)
            io.imsave(self.root / self.folders[2] / self.files[idx], mask2)

    @property
    def pen_colors(self):
        return [(255, 255, 255), (38, 190, 33), (239, 56, 176)]

    def _binarize(self, image):
        image = rgb2gray(from_qimage(image)[:, :, :3])
        buffer = np.zeros(image.shape, dtype=np.uint8)
        buffer[image != 0.0] = 255
        return buffer

    def _load_image(self, idx):
        path = self.root / self.folders[0] / self.files[idx]
        return to_qimage(io.imread(path))

    def _load_mask(self, idx, folder, color):
        path = self.root / folder / self.files[idx]
        mask = io.imread(path, as_gray=True)
        return to_qimage(self._make_alpha(mask, color=color))

    def _make_alpha(self, image, color):
        alpha = np.zeros([*image.shape, 4], dtype=np.uint8)
        alpha[image == 0, :] = (0, 0, 0, 0)
        alpha[image == 255, :] = (*color, 255)
        return alpha
