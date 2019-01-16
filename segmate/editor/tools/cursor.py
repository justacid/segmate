from segmate.editor.tools.editortool import EditorTool


class CursorTool(EditorTool):

    def paint_canvas(self):
        return self.canvas

    def paint_result(self):
        return self.canvas
