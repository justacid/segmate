import numpy as np
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from skimage.color import rgb2gray
from scipy import ndimage as ndi

from segmate.editor.tools.editortool import EditorTool
import segmate.util as util


class FillHolesToolInspector(QWidget):

    def __init__(self, callback):
        super().__init__()
        self.setup_ui(callback)

    def setup_ui(self, callback):
        inspector_layout = QVBoxLayout(self)
        inspector_layout.setContentsMargins(0, 0, 0, 0)

        box = QGroupBox("Copy Mask Tool", self)
        box.setStyleSheet("border-radius: 0px;")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(2, 6, 2, 2)

        button = QPushButton("Fill holes in layer")
        button.pressed.connect(callback)
        box_layout.addWidget(button)

        inspector_layout.addWidget(box)


class FillHolesTool(EditorTool):

    def paint_canvas(self):
        return self.canvas

    def paint_result(self):
        return self.canvas

    def _binary_fill_holes(self):
        self.is_dirty = True
        mask = util.extract_binary_mask(self.canvas)
        filled = ndi.binary_fill_holes(mask)
        output = util.color_binary_mask(filled, self.pen_color)
        self.push_undo_snapshot(self.canvas, output, undo_text="Fill Holes")
        self.canvas = output

    @property
    def inspector_widget(self):
        if not self.is_editable:
            return None
        return FillHolesToolInspector(self._binary_fill_holes)
