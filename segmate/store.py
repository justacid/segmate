from os import listdir
from pathlib import Path

import imageio as io
import numpy as np
import skimage.color as skcolor


class DataStore:

    def __init__(self, **kwargs):
        self._modified = set()
        self._cache = {}

        self.root = kwargs.get("data_root", None)
        self.folders = kwargs.get("folders", None)
        self.masks = kwargs.get("masks", None)
        self.editable = kwargs.get("editable", None)
        self.colors = kwargs.get("colors", None)
        self.files = None

        if self.root and self.folders:
            self.root = Path(self.root)
            self.files = self._get_filenames(Path(self.root), self.folders[0])

    def _get_filenames(self, data_root, folder):
        files = [f for f in listdir(data_root / folder)]
        files = sorted(files, key=lambda f: int(f.split("-")[1].split(".")[0]))
        return files

    @classmethod
    def from_project(cls, project):
        store = DataStore(
            data_root=project.data_root,
            folders=project.layers,
            masks=project.masks,
            editable=project.editable,
            colors=project.colors
        )
        return store

    @property
    def num_layers(self):
        return len(self.folders)

    def save_to_disk(self):
        for idx in self._modified:
            for i, layer in enumerate(self._cache[idx]):
                if not self.editable[i]:
                    continue
                if self.masks[i]:
                    layer = self._binarize(layer)
                io.imsave(self.root / self.folders[i] / self.files[idx], layer)
        self._modified.clear()

    def _binarize(self, image):
        image = skcolor.rgb2gray(image[:, :, :3])
        output = np.zeros(image.shape, dtype=np.uint8)
        output[image != 0.0] = 255
        return output

    def _load_image(self, idx, folder):
        path = self.root / folder / self.files[idx]
        image = io.imread(path)
        if len(image.shape) == 2:
            image = skcolor.gray2rgb(image, alpha=True)
        return image

    def _load_mask(self, idx, folder, color):
        path = self.root / folder / self.files[idx]
        mask = io.imread(path, as_gray=True)
        return self._make_alpha(mask, color=color)

    def _make_alpha(self, image, color):
        alpha = np.zeros([*image.shape, 4], dtype=np.uint8)
        alpha[image == 0, :] = (0, 0, 0, 0)
        alpha[image == 255, :] = (*color, 255)
        return alpha

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        assert idx >= 0 and idx < len(self.files)
        if idx in self._cache:
            return self._cache[idx]

        data = []
        for i, folder in enumerate(self.folders):
            if not self.masks[i]:
                data.append(self._load_image(idx, self.folders[i]))
            else:
                data.append(self._load_mask(idx, folder, color=self.colors[i]))

        self._cache[idx] = data
        return data

    def __setitem__(self, idx, value):
        self._cache[idx] = value
        self._modified.add(idx)
