import json
from os import makedirs
from pathlib import Path
import shutil
import tempfile
import zipfile

import imageio as io
import numpy as np
from segmate import __version__


class Project:

    def __init__(self, temp_dir, archive_path, data_root, version, layers, masks, colors):
        self.temp_dir = temp_dir
        self.archive_path = archive_path
        self.data_root = data_root
        self.version = version
        self.layers = layers
        self.masks = masks
        self.colors = colors


def new_project(archive_path, layers, masks, files, colors):
    # Copy all files from data_root to a temp directory, patch up
    # data_root and create the corresponding meta file - the callee is
    # responsible for actually creating the archive via save_project
    temp_dir = tempfile.TemporaryDirectory(prefix="segmate-")
    temp_path = Path(temp_dir.name)

    for folder, fpaths in zip(layers, files):
        makedirs(temp_path / "data" / folder)
        for path in fpaths:
            path = Path(path)
            if not path.is_file():
                raise AttributeError(f"'{path}' is not a file!")
            target = temp_path / "data" / folder / path.name
            shutil.copy(path, target)

    # Create missing masks
    for image in files[0]:
        for i, folder in enumerate(files[1:]):
            folder = [Path(f).name for f in folder]
            if Path(image).name in folder:
                continue
            data = io.imread(path, as_gray=True)
            mask = np.zeros(data.shape, dtype=np.uint8)
            target = temp_path / "data" / layers[i+1] / Path(image).name
            io.imwrite(target, mask)

    with open(temp_path / "meta", "w+") as jf:
        json_data = {"version": __version__, "layers": layers,
                     "masks": masks, "colors": colors}
        json.dump(json_data, jf)

    return Project(temp_dir, Path(archive_path), temp_path / "data", __version__,
        layers, masks, colors)


def open_project(archive_path):
    # Extract all files to a temp dir, which is used as root directory
    temp_dir = tempfile.TemporaryDirectory(prefix="segmate-")
    with zipfile.ZipFile(archive_path, mode="r") as zipf:
        zipf.extractall(path=temp_dir.name)
    with open(Path(temp_dir.name) / "meta") as jf:
        json_data = json.load(jf)
    return Project(temp_dir, Path(archive_path), Path(temp_dir.name) / "data",
        json_data["version"], json_data["layers"], json_data["masks"], json_data["colors"])


def write_project(project):
    # Add all files in temp dir to a new zip archive
    temp_path = Path(project.temp_dir.name)
    files = [f for f in temp_path.rglob("*") if f.is_file()]
    modified_path = temp_path / project.archive_path.name
    with zipfile.ZipFile(modified_path, mode="w", compression=zipfile.ZIP_STORED) as zipf:
        for path in files:
            zipf.write(path, arcname=path.relative_to(temp_path))

    # Unconditionally overwrite the original archive. The replace method on a path
    # object crashes with an 'OSError: [Errno 18] Invalid cross-device link:', when
    # source and target filesystems are different, hence use shutil instead
    shutil.move(modified_path, project.archive_path)


def export_project(project, path):
    # Create new folder at path with the archive name and copy the whole temporary
    # directory to this new folder. If the target already exists it is overwritten.
    source = Path(project.temp_dir.name) / "data"
    target = Path(path) / project.archive_path.stem
    try:
        shutil.copytree(source, target)
    except FileExistsError:
        shutil.rmtree(target)
        shutil.copytree(source, target)
