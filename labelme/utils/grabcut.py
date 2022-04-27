import cv2
import numpy as np
from qtpy import QtCore

from labelme.logger import logger
from labelme.shape import Shape

drawing = False
mode = True
ix, iy = -1, -1
r = 4
mask_fore = None
mask_back = None
bgdModel = None
fgdModel = None
poly = np.array([])


def qpixmapToCvMat(qpixmap):
    channels_count = 4
    width, height = qpixmap.width(), qpixmap.height()
    image = qpixmap.toImage()
    s = image.bits().asstring(width * height * channels_count)
    arr = np.fromstring(s, dtype=np.uint8).reshape(
        (height, width, channels_count))
    return arr


def merge(mask_fore, mask_back, img):
    mask = mask_fore[:, :, 1:2] / 255 + mask_back[:, :, 2:3] / 255
    if np.max(np.max(np.max(mask))) > 1:
        return False, img
    mask = mask.astype('uint8')
    return True, mask_fore + mask_back + img * (1 - mask)


def draw_circle(event, x, y, flags, param):
    global ix, iy, drawing, mode, r
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y
    if event == cv2.EVENT_RBUTTONUP:
        mode = not mode

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing is True:
            if mode is True:
                cv2.circle(mask_fore, (x, y), r, (0, 255, 0), -1)
            else:
                cv2.circle(mask_back, (x, y), r, (0, 0, 255), -1)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode is True:
            cv2.circle(mask_fore, (x, y), r, (0, 255, 0), -1)
        else:
            cv2.circle(mask_back, (x, y), r, (0, 0, 255), -1)
    

def processGrabcut(qpixmap, shape, polygon_epsilon=0.001,
                   iteration=5, brush_size=5, convex_hull=True):
    global drawing, mode, ix, iy, r, bgdModel, fgdModel, mask_back
    global mask_fore, poly
    img = qpixmapToCvMat(qpixmap)

    x0 = int(min(shape.points[0].x(), shape.points[1].x()))
    x1 = int(max(shape.points[0].x(), shape.points[1].x()))
    y0 = int(min(shape.points[0].y(), shape.points[1].y()))
    y1 = int(max(shape.points[0].y(), shape.points[1].y()))

    img_roi = cv2.cvtColor(img[y0:y1, x0:x1, :], cv2.COLOR_RGBA2RGB)
    mask_fore = np.zeros_like(img_roi)
    mask_back = np.zeros_like(img_roi)

    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    drawing = False
    mode = True
    ix, iy = -1, -1
    poly = np.array([])
    r = brush_size

    inital_rect = (2, 2, img_roi.shape[0] - 3, img_roi.shape[1] - 3)

    cv2.namedWindow('image', flags=cv2.WINDOW_GUI_NORMAL)
    cv2.imshow('image', img_roi)
    cv2.setMouseCallback('image', draw_circle)
    result_img = img_roi.copy()

    mask_global = np.zeros(img_roi.shape[:2], np.uint8) + 2

    while True:
        valid, masked = merge(mask_fore, mask_back, result_img)
        if not valid:
            logger.error('Foreground has interaction with background! \
                Please restart!')
            mask_fore = np.zeros_like(img_roi)
            mask_back = np.zeros_like(img_roi)
        cv2.imshow('image', masked)
        k = cv2.waitKey(10) & 0xFF
        # change mode
        if k == ord('f'):
            mode = True
        elif k == ord('b'):
            mode = False
        elif k == ord('r'):
            logger.info('Restart')
            mask_fore = np.zeros_like(img_roi)
            mask_back = np.zeros_like(img_roi)
        # clear foreground mask
        elif k == 6:  # ^F
            logger.info('Reselect foreground')
            mask_fore = np.zeros_like(img_roi)
        # clear background mask
        elif k == 2:  # ^B
            logger.info('Reselect background')
            mask_back = np.zeros_like(img_roi)
        # run rect grabcut algorithm
        elif k == ord('i'):
            if mask_fore.any() or mask_back.any():
                logger.error('INIT_WITH_RECT is not working if you already\
                     have any mask')
                continue
            logger.info('Cutting Initial foreground from the picture')

            cv2.grabCut(img_roi, mask_global, inital_rect, bgdModel, fgdModel,
                        iteration, cv2.GC_INIT_WITH_RECT)
            mask_global_2 = np.where(
                (mask_global == 2) | (mask_global == 0), 0, 1).astype('uint8')
            mask_global_reverse = np.where(
                (mask_global == 2) | (mask_global == 0), 1, 0).astype('uint8')

            target = img_roi * mask_global_2[:, :, np.newaxis]
            target_reverse = img_roi * mask_global_reverse[:, :, np.newaxis]
            brightness_subtract = np.full(target_reverse.shape, (75, 75, 75),
                                          dtype=np.uint8)
            target_reverse = cv2.subtract(target_reverse, brightness_subtract)
            
            result_img = target_reverse + target
            _target_grey = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
            contours, hierarchy = cv2.findContours(_target_grey,
                                                   cv2.RETR_CCOMP, 
                                                   cv2.CHAIN_APPROX_NONE)

            cnt = None
            max_area = -1
            for i in range(len(contours)):
                area = cv2.contourArea(contours[i])
                if area > max_area:
                    cnt = contours[i]
                    max_area = area
                    print(area, len(cnt))

            cv2.drawContours(result_img, cnt, -1, (0, 0, 255), 2)
            poly = cv2.approxPolyDP(cnt, polygon_epsilon * cv2.arcLength(cnt, True),
                                    True)
            cv2.drawContours(result_img, poly, -1, (0, 255, 0), 2)
            hull = cv2.convexHull(poly, returnPoints=True)
            cv2.drawContours(result_img, hull, -1, (255, 0, 0), 3)
            cv2.imshow('image', result_img)

        elif k == ord('c'):
            if not mask_fore.any() or not mask_back.any(): 
                logger.error('No Mask is on image')
                continue
            logger.info('Cutting foreground from the picture')

            mask_global[mask_fore[:, :, 1] == 255] = 1
            mask_global[mask_back[:, :, 2] == 255] = 0
            cv2.grabCut(img_roi, mask_global, inital_rect, bgdModel,
                        fgdModel, iteration, cv2.GC_INIT_WITH_MASK)
            mask_global_2 = np.where(
                (mask_global == 2) | (mask_global == 0), 0, 1).astype('uint8')
            mask_global_reverse = np.where(
                (mask_global == 2) | (mask_global == 0), 1, 0).astype('uint8')
            target = img_roi * mask_global_2[:, :, np.newaxis]
            target_reverse = img_roi * mask_global_reverse[:, :, np.newaxis]
            brightness_subtract = np.full(target_reverse.shape, (50, 50, 50),
                                          dtype=np.uint8)
            target_reverse = cv2.subtract(target_reverse, brightness_subtract)

            result_img = target_reverse + target

            _target_grey = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
            contours, hierarchy = cv2.findContours(_target_grey,
                                                   cv2.RETR_CCOMP,
                                                   cv2.CHAIN_APPROX_NONE)

            cnt = None
            max_area = -1
            for i in range(len(contours)):
                area = cv2.contourArea(contours[i])
                if area > max_area:
                    cnt = contours[i]
                    max_area = area
                    print(area, len(cnt))

            cv2.drawContours(result_img, cnt, -1, (0, 0, 255), 2)
            poly = cv2.approxPolyDP(
                cnt, polygon_epsilon * cv2.arcLength(cnt, True), True)
            cv2.drawContours(result_img, poly, -1, (0, 255, 0), 3)
            hull = cv2.convexHull(poly, returnPoints=True)
            cv2.drawContours(result_img, hull, -1, (255, 0, 0), 4)
            cv2.imshow('image', result_img)
        elif k == 27 :
            logger.info('grabcut abort')
            cv2.destroyAllWindows()
            return None
        elif k == 13 :
            cv2.destroyAllWindows()
            res_list = []
            if not poly.any():
                continue
            polygon = Shape(shape_type="polygon")
            for point in poly:
                polygon.addPoint(
                    QtCore.QPointF(x0 + point[0][0], y0 + point[0][1]))
            polygon.close()
            res_list.append(polygon)

            if convex_hull:
                convex_hull = Shape(shape_type="polygon")
                for point in hull:
                    convex_hull.addPoint(
                        QtCore.QPointF(x0 + point[0][0], y0 + point[0][1]))
                convex_hull.close()
                res_list.append(convex_hull)
            return res_list