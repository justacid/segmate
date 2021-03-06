import numpy as np

from ..editortool import EditorTool
from ... import util


class ContourTool(EditorTool):

    def on_paint(self):
        if not self.is_mask:
            return self.canvas

        output = np.zeros(self.canvas.shape, dtype=np.uint8)
        util.draw.contours(output, self.canvas, (*self.color, 255))
        return output
