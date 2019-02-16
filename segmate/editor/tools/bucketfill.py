import segmate.util as util
from segmate.editor.editortool import EditorTool


class BucketFillTool(EditorTool):

    def on_mouse_pressed(self, event):
        if event.buttons.left:
            self.fill_image(event.pos)

    def on_tablet_pressed(self, event):
        if event.buttons.left:
            self.fill_image(event.pos)

    def fill_image(self, pos):
        if not self.is_editable or not self.is_mask:
            self.send_status_message("This layer is not editable...")
            return

        snapshot = self.canvas.copy()
        util.draw.flood_fill(self.canvas, pos, (*self.color, 255))
        self.push_undo_snapshot(snapshot, self.canvas, undo_text="Bucket Fill")
        self.notify_dirty()

    @property
    def cursor(self):
        return "icons/cross-cursor.png"
