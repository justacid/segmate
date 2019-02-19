import segmate.util as util
from segmate.editor.editortool import EditorTool
from segmate.editor.widgets import EditorToolWidget, LabeledSlider


class DrawTool(EditorTool):

    def on_create(self):
        self._brush_size = 2
        self._eraser_size = 4

    def on_show(self):
        self._last_point = None
        self._draw = False
        self._have_undo_copy = False
        self._undo_copy = None
        self.set_cursor("icons/dot-cursor.png")

    def on_mouse_pressed(self, event):
        if event.buttons.left or event.buttons.right:
            self._pressed(event.pos, event.buttons.right)

    def on_mouse_moved(self, event):
        if (event.buttons.left or event.buttons.right) and self._draw:
            self._moved(event.pos, event.buttons.right)

    def on_mouse_released(self, event):
        if (event.buttons.left or event.buttons.right) and self._draw:
            self._released(event.pos, event.buttons.right)

    def on_tablet_pressed(self, event):
        if event.buttons.left:
            self._pressed(event.pos, event.buttons.middle)

    def on_tablet_moved(self, event):
        if event.buttons.left and self._draw:
            self._moved(event.pos, event.buttons.middle)

    def on_tablet_released(self, event):
        if event.buttons.left and self._draw:
            self._released(event.pos, event.buttons.middle)

    def on_show_widget(self):
        def brush_cb(value):
            self._brush_size = value
        def eraser_cb(value):
            self._eraser_size = value
        return DrawToolInspector(self._brush_size, brush_cb, self._eraser_size, eraser_cb)

    def _pressed(self, pos, erase):
        if not self.is_editable:
            self.send_status_message("This layer is not editable...")
            return
        if not self._have_undo_copy:
            self._undo_copy = self.canvas.copy()
            self._have_undo_copy = True
        self._last_point = pos
        self._draw_line(pos, erase)
        self._draw = True

    def _released(self, pos, erase):
        if not self.is_editable:
            return
        self._draw_line(pos, erase)
        self._draw = False
        if self._have_undo_copy:
            self.push_undo_snapshot(self._undo_copy, self.canvas, undo_text="Draw")
            self._have_undo_copy = False

    def _moved(self, pos, erase):
        if not self.is_editable:
            return
        self._draw_line(pos, erase)

    def _draw_line(self, end_point, erase):
        color = (*self.color, 255) if not erase else (0, 0, 0, 0)
        width = self._brush_size if not erase else self._eraser_size
        util.draw.line(self.canvas, self._last_point, end_point, color, width=width)
        self._last_point = end_point
        self.notify_dirty()


class DrawToolInspector(EditorToolWidget):

    def __init__(self, brush_size, brush_cb, eraser_size, eraser_cb):
        super().__init__("Brush Settings")
        brush = LabeledSlider(
            "Brush Size", callback=brush_cb, value=brush_size, maximum=50)
        eraser = LabeledSlider(
            "Eraser Size", callback=eraser_cb, value=eraser_size, maximum=50)
        self.add_widget(brush)
        self.add_widget(eraser)
