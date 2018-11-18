#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

# Basic trigonometry

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

def remap(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def polar2xy(center_x, center_y, angle, radius):
    a = math.radians(angle)
    return [center_x + radius * math.cos(a), 
            center_y + radius * math.sin(a) ]