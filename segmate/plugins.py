import importlib
import inspect
import json
import pathlib
import sys

from pkg_resources import Requirement
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *

from . import pipapi
from .editor.editortool import EditorTool


# When a dynamically imported plugin itself tries to import torch (> 1.0.1) it crashes
# when it is initialized after QApplication. Therefore try to import it here and swallow
# an import error for systems were torch is not installed. This is obviously a band-aid,
# and to be removed as as soon as possible.
# Also see: https://github.com/pytorch/pytorch/issues/11326
try:
    import torch
except ImportError:
    pass


_plugins = {}


def get_plugins():
    return _plugins


def _plugin_info(plugin_dir):
    if not plugin_dir.is_dir():
        return None
    plugin_info_path = plugin_dir / "plugin.json"
    if not plugin_info_path.exists():
        return None
    with open(plugin_info_path, "r") as f:
        try:
            plugin_info = json.load(f)
        except json.decoder.JSONDecodeError as e:
            print("'{0}/plugin.json': {1}.".format(plugin_dir.stem, e))
            return None
    return plugin_info


def initialize_plugins():
    global _plugins

    app_data = QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)[0]
    location = pathlib.Path(app_data) / "plugins"

    if not location.exists():
        return
    sys.path.insert(0, str(location))

    for plugin_dir in location.iterdir():
        plugin_info = _plugin_info(plugin_dir)
        if plugin_info is None:
            continue

        # If there is any error we do not want the application to crash, therefore
        # catch all errors unconditionally, report an error and continue
        try:
            plugin_name = plugin_info["name"]
            module_name = plugin_info["module"]
            class_name = plugin_info["class"]

            module = importlib.import_module("{0}.{1}".format(plugin_dir.name, module_name))
            class_ = getattr(module, class_name)

            if not (inspect.isclass(class_) and issubclass(class_, EditorTool)):
                print("'{0}' is not a subclass of 'EditorTool', skipping...".format(class_))
                continue

            _plugins[plugin_dir.name] = [plugin_name, class_]
        except:
            print("There was an error loading the plugin '{0}', skipping..." \
                .format(plugin_dir.name))
            continue


def missing_dependencies():
    app_data = QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)[0]
    location = pathlib.Path(app_data) / "plugins"

    if not location.exists():
        return

    collected_dependencies = []
    for plugin_dir in location.iterdir():
        plugin_info = _plugin_info(plugin_dir)
        if plugin_info is None:
            continue

        plugin_dependencies = plugin_info.get("dependencies", [])
        collected_dependencies.extend(
            [Requirement.parse(p).name.lower() for p in plugin_dependencies])

    installed_dependencies = pipapi.installed(user=False)
    return [d for d in collected_dependencies if d not in installed_dependencies]


class DependencyInstaller(QDialog):

    def __init__(self, missing_deps, parent=None):
        super().__init__(parent)
        self.dependencies = missing_deps

        self._setup_ui()
        self.add_line("Missing dependencies:")
        for dependency in self.dependencies:
            self.add_line("    - {0}".format(dependency))
        self.add_line("\nInstall dependencies?\n\n")

    def _setup_ui(self):
        self.setFixedSize(400, 500)
        self.setWindowTitle("Plugin Dependency Installer")
        text_label = QLabel("Log:")
        self.text = QPlainTextEdit()
        self.text.setReadOnly(True)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self._run)
        self.buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.addWidget(text_label)
        layout.addWidget(self.text)
        layout.addWidget(self.buttons)

    def add_line(self, text):
        self.text.appendPlainText(text)
        self.text.verticalScrollBar().setValue(self.text.verticalScrollBar().maximum())
        self.repaint()

    def _run(self):
        self.buttons.setEnabled(False)

        for dependency in self.dependencies:
            for out_line in pipapi.install(dependency, user=not pipapi.is_venv()):
                self.add_line(out_line)
        self.add_line("\n")
        self.add_line("Please restart the application!")

        self.buttons.accepted.disconnect(self._run)
        self.buttons.accepted.connect(self.accept)
        self.buttons.setEnabled(True)
        self.buttons.button(QDialogButtonBox.Cancel).setEnabled(False)
