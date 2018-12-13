#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
import cv2 as cv

from .Polyline import Polyline

def traceImg(surface, filename, threshold):

    polylines = []
    
    im = cv.imread( filename )
    blur = cv.GaussianBlur(im, (3, 3),0)
    imgray = cv.cvtColor( blur, cv.COLOR_BGR2GRAY )
    ret, thresh = cv.threshold(imgray, int(threshold * 255), 255, cv.THRESH_BINARY)
    image, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    height, width = im.shape[:2]
    scale = [ (1.0 / width) * surface.width, (1.0 / height) * surface.height ]

    for contour in contours:
        points = []
        for point in contour:
            points.append( (point[0][0] * scale[0], point[0][1] * scale[1]) )

        polylines.append(Polyline(points))

    return polylines

