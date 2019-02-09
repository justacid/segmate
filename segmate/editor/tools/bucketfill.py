from skimage.color import rgb2gray
from PySide2.QtCore import Qt

import segmate.util as util
from segmate.editor.editortool import EditorTool


class BucketFillTool(EditorTool):

    def mouse_pressed(self, event):
        if event.button() == Qt.LeftButton:
            self.fill_image(event.pos())

    def tablet_event(self, event):
        if event.type() == QEvent.TabletPress and event.button() == Qt.LeftButton:
            self.fill_image(event.pos())

    def fill_image(self, pos):
        if not self.is_editable:
            self.send_status_message("This layer is not editable...")
            return

        snapshot = self.canvas.copy()
        seed = [pos.y(), pos.x()]
        util.draw.flood_fill(self.canvas, seed, (*self.color, 255))
        self.push_undo_snapshot(snapshot, self.canvas, undo_text="Bucket Fill")
        self.notify_dirty()

    @property
    def cursor(self):
        return "icons/cross-cursor.png"
