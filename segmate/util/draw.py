import numpy as np
import skimage.draw as draw
import skimage.measure as measure
import skimage.color as skcolor

import segmate.util as util


def line(image, p0, p1, color, *, width=1):
    """Draw a line between two points.

    Args:
        image: The canvas to draw on
        p0: Start point
        p1: End point
        color: Color of the drawn line
        width: The thickness of the line
    """
    r0, c0 = int(p0[0]), int(p0[1])
    r1, c1 = int(p1[0]), int(p1[1])

    rows, cols = draw.line(r0, c0, r1, c1)
    rows = np.clip(rows, 0, image.shape[0]-1)
    cols = np.clip(cols, 0, image.shape[1]-1)
    image[rows, cols] = color
    radius = width / 2

    for row, col in zip(rows, cols):
        if width % 2 != 0:
            rr, cc = draw.circle(row, col, radius)
        else:
            rr, cc = draw.circle(row + 0.5, col + 0.5, radius)
        rr = np.clip(rr, 0, image.shape[0]-1)
        cc = np.clip(cc, 0, image.shape[1]-1)
        image[rr, cc] = color


def rectangle(image, top_left, bot_right, color):
    """Draw a rectangle defined by two corners.

    Args:
        image: The canvas to draw on
        top_left: Top left corner of the rectangle
        bot_right: Bottom right corner of the rectangle
        color: Color of the drawn rectangle
    """
    rows = [top_left[0]-1, top_left[0]-1, bot_right[0]-1, bot_right[0]-1]
    cols = [top_left[1]-1, bot_right[1]-1, bot_right[1]-1, top_left[1]-1]
    rr, cc = draw.polygon_perimeter(rows, cols, shape=image.shape, clip=True)
    image[rr, cc] = color


def flood_fill(image, seed, fill_color, *, border_color=None):
    """Flood fill with color, starting at seed. The flood fill will zerod
    pixels, and stop whenever a 4-connected neighbor is greater than zero.

    Args:
        image: The canvas to draw on
        seed: Seed point for the flood fill
        color: Color of the filled region
    """

    if border_color is None:
        border_color = fill_color

    h, w = image.shape[:2]
    coords = [[int(c) for c in seed]]

    while coords:
        y, x = coords.pop()
        image[y, x] = fill_color

        if y + 1 < h and not np.array_equal(image[y + 1, x], border_color):
            coords.append([y + 1, x])
        if y - 1 >= 0 and not np.array_equal(image[y - 1, x], border_color):
            coords.append([y - 1, x])
        if x + 1 < w and not np.array_equal(image[y, x + 1], border_color):
            coords.append([y, x + 1])
        if x - 1 >= 0 and not np.array_equal(image[y, x - 1], border_color):
            coords.append([y, x - 1])


def contours(dest, source, color):
    """Draw contours of regions with a given color to some destination.
    This method uses Marching Squares internally.

    Args:
        dest: The canvas to draw on
        source: The array from which the contours shall be extracted
        color: Color of the contours
    """
    mask = util.mask.binary(source)
    if (mask == False).all():
        return

    contours = measure.find_contours(~mask, 0.25)
    for contour in contours:
        contour = np.round(contour).astype(np.int32)
        dest[contour[:, 0], contour[:, 1]] = color
