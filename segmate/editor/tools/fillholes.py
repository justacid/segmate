import numpy as np
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from skimage.color import rgb2gray
from scipy import ndimage as ndi

from segmate.editor.tools.editortool import EditorTool
from segmate.editor.toolwidget import EditorToolWidget
import segmate.util as util


class FillHolesToolInspector(EditorToolWidget):

    def __init__(self, callback):
        super().__init__("Fill Holes Tool")
        button = QPushButton("Fill holes in layer")
        button.pressed.connect(callback)
        self.add_widget(button)


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
