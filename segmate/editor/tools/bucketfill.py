from ..editortool import EditorTool
from ... import util


class BucketFillTool(EditorTool):

    def on_show(self):
        self.set_cursor("icons/cross-cursor.png")

    def on_mouse_pressed(self, event):
        if event.buttons.left:
            self.fill_image(event.pos, (*self.color, 255))
        elif event.buttons.right:
            self.fill_image(event.pos, (0, 0, 0, 0))

    def on_tablet_pressed(self, event):
        if event.buttons.left:
            self.fill_image(event.pos, (*self.color, 255))
        elif event.buttons.left and event.buttons.right:
            self.fill_image(event.pos, (0, 0, 0, 0))

    def fill_image(self, pos, color):
        if not self.is_mask:
            self.send_status_message("The image layer is not editable...")
            return

        snapshot = self.canvas.copy()
        util.draw.flood_fill(self.canvas, pos, color)
        self.push_undo_snapshot(snapshot, self.canvas, undo_text="Bucket Fill")
        self.notify_dirty()
