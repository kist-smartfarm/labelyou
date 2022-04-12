from qtpy import QtCore
from labelme.shape import Shape
from functools import reduce

def processGrid(box, xnum, ynum, margin=0): 
    assert xnum > 0 and ynum > 0 
    shapes = [] 

    x0 = min(box.points[0].x(), box.points[1].x())
    x1 = max(box.points[0].x(), box.points[1].x())
    y0 = min(box.points[0].y(), box.points[1].y())
    y1 = max(box.points[0].y(), box.points[1].y())
    
    xGridSize = (x1 - x0) / xnum
    yGridSize = (y1 - y0) / ynum

    for i in range(ynum): 
        for j in range(xnum): 
            _y0 = y0 + i * yGridSize + (margin // 2)
            _x0 = x0 + j * xGridSize + (margin // 2)
            _y1 = _y0 + yGridSize - (margin // 2)
            _x1 = _x0 + xGridSize - (margin // 2)
            shape_cell = Shape(shape_type="rectangle")
            shape_cell.addPoint(QtCore.QPointF(_x0, _y0))
            shape_cell.addPoint(QtCore.QPointF(_x1, _y1))

            shape_cell.other_data['grid_y'] = i
            shape_cell.other_data['grid_x'] = j

            shapes.append(shape_cell)
    return shapes  

def divmod_excel(n):
    a, b = divmod(n, 26)
    if b == 0:
        return a - 1, b + 26
    return a, b

import string
def to_excel(num):
    chars = []
    while num > 0:
        num, d = divmod_excel(num)
        chars.append(string.ascii_uppercase[d - 1])
    return ''.join(reversed(chars))
