from ..editortool import EditorTool


class CursorTool(EditorTool):

    def on_show(self):
        self.enable_selection(True)
