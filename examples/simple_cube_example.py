
import numpy as np
from pflacs import Premise, Calc



def rectangle_area(w, b=None):
    """Calculate the area of a rectange with side lengths «w» and «b».

    https://en.wikipedia.org/wiki/Rectangle
    """
    if b is None:
        b = w
    return w * b


def box_volume(h, w=None, b=None, base_area=None):
    """Calculate the volume of a box (rectangular cuboid) with 
    side lengths «h», «w» and «b».

    https://en.wikipedia.org/wiki/Cuboid
    """
    if base_area:
        return h * base_area
    if b is None:
        b = h
    if w is None:
        w = h
    base_area = rectangle_area(w, b)
    return h * base_area


def box_surface_area(h=None, w=None, b=None, area_hw=None, 
      area_wb=None, area_bh=None):
    """Calculate the surface area of a box (rectangular cuboid) with 
    side lengths «h», «w» and «b».

    https://en.wikipedia.org/wiki/Cuboid
    https://mathworld.wolfram.com/Cube.html
    https://mathworld.wolfram.com/Cuboid.html
    """
    # if [h, w, b].count(None) == 2:
    #     if h is not None: w = b = h
    #     if w is not None: h = b = w
    #     if b is not None: h = w = b
    # elif h:
    #     if b is None:
    #         b = h
    #     if w is None:
    #         w = h
    # if [area_hw, area_wb, area_bh].count(None) == 1:
    #     if area_hw is None: w = b = h
    if h and w is None and b is None:
        w = b = h
        area_hw = area_wb = area_bh = rectangle_area(h,w)
    else:
        if area_hw is None:
            area_hw = rectangle_area(h,w)
        if area_wb is None:
            area_wb = rectangle_area(w,b)
        if area_bh is None:
            area_bh = rectangle_area(b,h)
    area = 2.0*(area_hw + area_wb + area_bh)
    return area


basecase = Premise("Study base-case",
                parameters={
                    "w": 4,
                    "b": 5,
                    "h": 3.5,
                } )


basecase.plugin_func(rectangle_area)
basecase.plugin_func(box_volume)

print(f"Base-case rectange area = {basecase.rectangle_area()}")
print(f"Base-case cube volume = {basecase.box_volume()}")

parastudy = Premise("Parameter study", parent=basecase,
                parameters={
                    "w": np.array([1.0, 1.35, 2.0, 4.5]),
                    "b": np.linspace(2.2, 5.5, 4),
                    "h": 10.0,
                } )

rect =  Calc("Study rectangle area", parent=parastudy, 
                        funcname="rectangle_area" )

Calc("Study cube volume", parent=rect, funcname="box_volume" )

rect()
rect.df

box = rect.get_child_by_name("Study cube volume")
box()
box.df

