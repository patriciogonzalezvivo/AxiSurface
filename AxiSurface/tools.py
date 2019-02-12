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


def distance(A, B):
    ab = np.array(B) - np.array(A)
    return np.sqrt( ab[0] * ab[0] + ab[1] * ab[1] )


def perpendicular(A, B):
    ab = np.array(B) - np.array(A)
    dir_ab = normalize(ab)
    return np.array([-dir_ab[1], dir_ab[0]])


def remap(value, in_min, in_max, out_min, out_max):
    in_span = in_max - in_min
    out_span = out_max - out_min

    value = float(value - in_min)
    if value != 0:
        value /= float(in_span)
    return out_min + (value * out_span)

def lerp(A, B, t):
    A = np.array(A)
    B = np.array(B)
    return A * (1.0 - t) + B * t

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

# Collisions

#  https://github.com/openframeworks/openFrameworks/blob/patch-release/libs/openFrameworks/graphics/ofPolyline.inl#L622
def pointInside( pos, points ):
    counter = 0

    # double xinters;
    p1 = [0.0, 0.0]
    p2 = [0.0, 0.0]

    N = len(points)

    p1 = points[0]

    for i in range(1, N + 1):
        p2 = points[i % N]

        if pos[1] > min(p1[1], p2[1]):
            if pos[1] <= max(p1[1], p2[1]):
                if pos[0] <= max(p1[0], p2[0]):
                    if p1[1] != p2[1]:
                        xinters = (pos[1] - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
                        if p1[0] == p2[0] or pos[0] <= xinters:
                            counter += 1
        p1 = p2
        
    return counter % 2 != 0

# https://github.com/openframeworks/openFrameworks/blob/master/libs/openFrameworks/math/ofMath.h#L435
def linesIntersection(line1Start, line1End, line2Start, line2End):
    diffLA = np.array(line1End) - np.array(line1Start)
    compareA = diffLA[0] * line1Start[1] - diffLA[1] * line1Start[0]
    if ( ( diffLA[0]*line2Start[1] - diffLA[1]*line2Start[0] ) < compareA ) ^ ( ( diffLA[0]*line2End[1] - diffLA[1]*line2End[0] ) < compareA ):

        diffLB = np.array(line2End) - np.array(line2Start)
        compareB = diffLB[0] * line2Start[1] - diffLB[1] * line2Start[0]
        if ( ( diffLB[0]*line1Start[1] - diffLB[1]*line1Start[0] ) < compareB ) ^ ( ( diffLB[0]*line1End[1] - diffLB[1]*line1End[0]) < compareB ):
            lDetDivInv = 1 / ((diffLA[0] * diffLB[1]) - (diffLA[1] * diffLB[0]))
            intersection[0] =  -((diffLA[0] * compareB) - (compareA * diffLB[0])) * lDetDivInv
            intersection[1] =  -((diffLA[1] * compareB) - (compareA * diffLB[1])) * lDetDivInv
            return intersection

    return None
