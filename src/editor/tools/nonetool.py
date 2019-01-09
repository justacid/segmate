from PySide2.QtCore import Qt

from util import to_qimage
from .editortool import EditorTool


class NoneTool(EditorTool):

    def paint_canvas(self):
        return self.canvas

    def paint_result(self):
        return self.canvas
