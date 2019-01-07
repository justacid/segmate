from PySide2.QtCore import Qt

from .editortool import EditorTool


class NoneTool(EditorTool):

    def paint(self):
        return self.canvas

    def cursor(self):
        return Qt.ArrowCursor
