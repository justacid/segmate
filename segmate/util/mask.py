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
