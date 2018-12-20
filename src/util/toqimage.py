import numpy as np
from PySide2.QtGui import QImage


def to_qimage(arr, copy=False):
    """Convert NumPy array to QImage object

    Args:
        arr: A numpy array
        copy: If True, returns a copy of the array

    Returns:
        An QImage object.
    """
    if arr is None:
        return QImage()

    if len(arr.shape) not in (2, 3):
        raise TypeError(f"Unsupported image format.")

    shape = arr.shape[:2][::-1]
    stride = arr.strides[0]
    cdim = 0 if len(arr.shape) != 3 else arr.shape[2]

    formats = {
        0: QImage.Format_Grayscale8,
        3: QImage.Format_RGB888,
        4: QImage.Format_RGBA8888
    }

    if cdim not in formats:
        raise TypeError("Unsupported image format.")

    qimage = QImage(arr.data, *shape, stride, formats[cdim])
    return qimage.copy() if copy else qimage
