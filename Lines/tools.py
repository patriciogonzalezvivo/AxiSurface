#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

# Basic trigonometry
# -----------------------------------------------------------------

def normalize(v, tolerance=0.00001):
    mag2 = sum(n * n for n in v)
    if abs(mag2 - 1.0) > tolerance:
        mag = math.sqrt(mag2)
        v = tuple(n / mag for n in v)
    return np.array(v)


def perpendicular(A, B):
    ab = np.array(B) - np.array(A)
    dir_ab = normalize(ab)
    return np.array([-dir_ab[1], dir_ab[0]])


# Convertions
# -----------------------------------------------------------------

def polar2xy(center, angle, radius):
    a = math.radians(angle)
    return [center[0] + radius * math.cos(a), 
            center[1] + radius * math.sin(a) ]


# Bezier controls
# -----------------------------------------------------------------

def lineProp( pointA, pointB ):
    lengthX = pointB[0] - pointA[0]
    lengthY = pointB[1] - pointA[1]
    return math.sqrt( math.pow(lengthX, 2) + math.pow(lengthY, 2)), math.atan2(lengthY, lengthX)


def controlPoint( current, _previous, _next, reverse ):
    p = _previous
    n = _next

    if _previous == None:
        p = current
    if _next == None:
        n = current

    smoothing = 0.2
    o = lineProp(p, n) 

    angle = o[1]
    if reverse: 
        angle += math.pi
    length = o[0] * smoothing

    x = current[0] + math.cos(angle) * length
    y = current[1] + math.sin(angle) * length

    return [x, y]


def bezierCommand( point, i, a ):
    #  start control point
    cpsX, cpsY = controlPoint(a[i - 1], a[i - 2], point, False) 

    #  end control point
    if i + 1 >= len(a):
        cpeX, cpeY = controlPoint(point, a[i - 1], None, True)
    else:
        cpeX, cpeY = controlPoint(point, a[i - 1], a[i + 1], True)

    return ' C ' + str(cpsX) + ',' + str(cpsY) + " " + str(cpeX) + "," + str(cpeY) + " " + str(point[0]) + "," + str(point[1])
