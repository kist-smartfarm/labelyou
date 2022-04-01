
from turtle import shape
from qtpy import QtCore
from labelme.shape import Shape

def processGrid(box, xcols, ycols, margin=0): 
    assert xcols > 0 and ycols > 0 
    shapes = [] 

    x0 = min(box.points[0].x(), box.points[1].x())
    x1 = max(box.points[0].x(), box.points[1].x())
    y0 = min(box.points[0].y(), box.points[1].y())
    y1 = max(box.points[0].y(), box.points[1].y())
    
    xGridSize = (x1 - x0) / xcols
    yGridSize = (y1 - y0) / ycols

    for i in range(ycols): 
        for j in range(xcols): 
            _y0 = y0 + i * yGridSize + (margin // 2)
            _x0 = x0 + j * xGridSize + (margin // 2)
            _y1 = _y0 + yGridSize - (margin // 2)
            _x1 = _x0 + xGridSize - (margin // 2)
            rectangle = Shape(shape_type="rectangle")
            rectangle.addPoint(QtCore.QPointF(_x0, _y0))
            rectangle.addPoint(QtCore.QPointF(_x1, _y1))
            shapes.append(rectangle)
    return shapes  
    