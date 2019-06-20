import warnings

import numpy as np
import skimage
import skimage.color as skcolor


def binary(array):
    """Retrieve binary mask from a RGB(A) numpy array, where array != 0.

    Args:
        image: A numpy array with shape [H, W], [H, W, C] or [H, W, C, A]

    Returns:
        Binary mask, where everything not equal to zero is set to True
    """
    if array is None:
        raise ValueError("The argument 'array' can not be 'None'.")
    if len(array.shape) not in (2, 3, 4):
        raise ValueError("Unsupported array type.")

    if len(array.shape) > 2:
        array = skcolor.rgb2gray(array[:,:,:3])
    return array != 0.0


def color(array, color=(255, 255, 255)):
    """Returns a colored numpy array from a binary mask with given color.

    Args:
        image: A binary numpy array

    Returns:
        Numpy array with corresponding colors.
    """
    if array is None:
        raise ValueError("The argument 'arr' can not be 'None'.")
    if len(array.shape) != 2:
        raise TypeError(f"Only binary masks are supported.")

    output = np.zeros((*array.shape, 4), dtype=np.uint8)
    output[array == True] = (*color, 255)
    return output


def grayscale(array):
    """ Convert numpy array to grayscale.

    Args:
        image: A numpy array with shape [H, W, C] or [H, W, C, A]

    Returns:
        Grayscale numpy array
    """
    if array is None:
        raise ValueError("The argument 'array' can not be 'None'.")
    if len(array.shape) not in (2, 3, 4):
        raise ValueError("Unsupported array type.")

    if len(array.shape) == 2:
        return array

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return skimage.img_as_ubyte(skcolor.rgb2gray(array[:,:,:3]))


def selection(array, rect):
    """ Returns a selection mask given by a rectangle.

    Args:
        array: image from which to get the dimensions
        rect: 2-tuple containing the coordinates [(y1, x1), (y2, x2)]

    Returns:
        A mask with the selected area.
    """
    if array is None or rect is None:
        raise ValueError("The arguments 'array' and rect' must not be 'None'.")
    if len(rect) != 2:
        raise ValueError("Rectangle must contain two coordinates.")
    if len(rect[0]) != 2 or len(rect[1]) != 2:
        raise ValueError("Invalid rectangle coordinates.")

    h, w = array.shape[:2]
    y1, y2 = np.clip([rect[0][0], rect[1][0]], 0, h+1)
    x1, x2 = np.clip([rect[0][1], rect[1][1]], 0, w+1)

    mask = np.zeros(array.shape, dtype=np.bool)
    mask[int(y1):int(y2), int(x1):int(x2)] = True
    return mask
