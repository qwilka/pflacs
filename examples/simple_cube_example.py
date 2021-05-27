

from pflacs import Premise


def rectangle_area(w, b=None):
    """Calculate the area of a rectange with side lengths «w» and «b».
    """
    if b is None:
        b = w
    return w * b


def box_volume(h, w=None, b=None, base_area=None):
    """Calculate the volume of a box with side lengths
    «h», «w» and «b».
    """
    if base_area:
        return h * base_area
    if b is None:
        b = h
    if w is None:
        w = h
    base_area = rectangle_area(w, b)
    return h * base_area

