import numpy as np
from PySide2.QtGui import QImage
from skimage.color import rgb2gray


def to_qimage(arr, copy=True):
    """Convert NumPy array to QImage object

    Args:
        arr: A numpy array
        copy: If True, returns a copy of the array

    Returns:
        An QImage object.
    """
    if arr is None:
        raise ValueError("The argument 'arr' can not be 'None'.")

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


def from_qimage(image):
    """Convert QImage object to a numpy array. Always copies.

    Args:
        image: A valid QImage

    Returns:
        Numpy array with RGBA image data.
    """
    if image is None:
        raise ValueError("The argument 'image' can not be 'None'.")

    width, height = image.width(), image.height()

    dims = {
        QImage.Format_Grayscale8: [height, width],
        QImage.Format_RGB888: [height, width, 3],
        QImage.Format_RGBA8888: [height, width, 4]
    }

    if image.format() not in dims:
        raise TypeError("Unsupported image format.")

    return np.array(image.constBits(), dtype=np.uint8).reshape(dims[image.format()])


def extract_binary_mask(image):
    """Retrieve the binary mask from a QImage object with alpha channel.

    Args:
        image: A QImage in the RGBA888 or RGBA8888format

    Returns:
        Binary mask, where everything not equal to zero is set to 1
    """
    if image is None:
        raise ValueError("The argument 'image' can not be 'None'.")

    image = from_qimage(image)
    noalpha = rgb2gray(image[:,:,:3])
    mask = np.zeros(noalpha.shape, dtype=np.uint8)
    mask[noalpha != 0.0] = 1
    return mask


def color_binary_mask(arr, color=(255, 255, 255)):
    """Returns a colored QImage from a binary mask with given color.

    Args:
        image: A binary numpy array

    Returns:
        A QImage from the corresponding binary image.
    """
    if arr is None:
        raise ValueError("The argument 'arr' can not be 'None'.")
    if len(arr.shape) != 2:
        raise TypeError(f"Only binary masks are supported.")

    output = np.zeros((*arr.shape, 4), dtype=np.uint8)
    output[arr == 1] = (*color, 255)
    return to_qimage(output, copy=True)

def invert_binary_mask(arr):
    """Inverts a binary numpy array.

    Args:
        image: A binary numpy array

    Returns:
        A numpy array where 1 and 0 are switched.
    """
    output = np.ones(arr.shape, dtype=np.uint8)
    output[arr == 1] = 0
    return output
