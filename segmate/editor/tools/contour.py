import numpy as np

import segmate.util as util
from segmate.editor.editortool import EditorTool


class ContourTool(EditorTool):

    def paint_canvas(self):
        if not self.is_mask:
            return self.canvas

        output = np.zeros(self.canvas.shape, dtype=np.uint8)
        util.draw.contours(output, self.canvas, (*self.color, 255))
        return output
