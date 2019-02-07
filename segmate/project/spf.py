import json
from os import makedirs
from pathlib import Path

from segmate import __version__


class ProjectFile:

    def __init__(self):
        self.version = ""
        self.data_root = ""
        self.folders = []
        self.masks = []
        self.editable = []
        self.colors = []

    @classmethod
    def parse(cls, spf_path):
        with open(spf_path, "r") as jf:
            json_data = json.load(jf)

        project = ProjectFile()
        project.version = json_data["version"]
        project.data_root = json_data["data_root"]
        project.folders = json_data["folders"]
        project.masks = json_data["masks"]
        project.editable = json_data["editable"]
        project.colors = [(c["r"], c["g"], c["b"]) for c in json_data["colors"]]
        return project

    @classmethod
    def save(cls, spf_path, project):
        makedirs(Path(spf_path).parent, exist_ok=True)
        with open(spf_path, "w") as jf:
            json_data = {
                "version": __version__,
                "data_root": project.data_root,
                "folders": project.folders,
                "masks": project.masks,
                "editable": project.editable,
                "colors": [{"r": c[0], "g": c[1], "b": c[2]} for c in project.colors]
            }
            json.dump(json_data, jf)
