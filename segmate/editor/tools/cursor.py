from PySide2.QtCore import Qt

from segmate.editor.tools.editortool import EditorTool
from segmate.util import to_qimage


class CursorTool(EditorTool):

    def paint_canvas(self):
        return self.canvas

    def paint_result(self):
        return self.canvas
