import importlib.util as imp
import importlib
import inspect
import pathlib
import sys

from PySide2.QtCore import QStandardPaths
from segmate.editor.editortool import EditorTool


tools = {}
data_location = QStandardPaths.standardLocations(QStandardPaths.AppDataLocation)[0]
plugins_location = pathlib.Path(data_location) / "segmate" / "plugins"

# adding the plugin location to the path,
# such that the plugin packages can be imported
sys.path.insert(0, str(plugins_location))

for path in plugins_location.iterdir():
    module = importlib.import_module(path.parts[-1])
    plugin_info = [getattr(module, "__plugin_title__", None)]
    found = False
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            if issubclass(obj, EditorTool) and obj != EditorTool:
                plugin_info.append(obj)
                found = True
                break
    if found:
        tools[path.parts[-1]] = plugin_info
