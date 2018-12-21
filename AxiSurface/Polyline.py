#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np
from .tools import pointInside, linesIntersection, lerp, distance, remap

class Polyline(object):
    def __init__( self, parent=None ):
        if isinstance(parent, Polyline):
            parent = parent.points

        if parent == None:
            parent = []

        self.points = parent
        self.lengths = []
        self._updateCache()


    def lineTo( self, pos ):
        self.points.append( pos )
        self._updateCache()


    def __getitem__(self, index):
        if type(index) is int:
            return self.points[ index ]
        else:
            return None


    def __getitem__(self, index):
        if type(index) is int:
            return self.points[ index ]
        else:
            return None


    def __setitem__(self, index, value):
        if type(index) is int:
            self.points[index] = value


    def size(self):
        return len(self.points)


    def inside( self, pos ):
        return pointInside( pos, self.points )


    def _updateCache(self):
        # Clean
        self.lengths = []
        N = len(self.points)

        # Check
        if N == 0:
            return 

        # Process
        length = 0
        for i in range( N - 1 ):
            self.lengths.append(length)
            p1 = self.points[i]
            p2 = self.points[i+1]
            length += distance(p1, p2)


    def getPerimeter(self):
        if len(self.lengths) < 1:
            return 0
        return self.lengths[-1]


    def getPointAtLength(self, length):
        return self.getPointAtIndexInterpolated( self.getIndexAtLength( length ) )


    def getIndexAtLength(self, length):
        totalLength = self.getPerimeter()
        length = max(min(length, totalLength), 0)
    
        lastPointIndex = len(self.points)

        i1 = max(min(int(math.floor(length / totalLength * lastPointIndex)), len(self.lengths)-2), 0) # start approximation here
        leftLimit = 0
        rightLimit = lastPointIndex
        
        distAt1 = 0.0
        distAt2 = 0.0
        for iterations in range(32):
            i1 = max(min(int(i1), len(self.lengths)-1), 0)
            distAt1 = self.lengths[i1]

            if distAt1 <= length:         # if Length at i1 is less than desired Length (this is good)
                distAt2 = self.lengths[i1+1]
                if distAt2 >= length:
                    t = remap(length, distAt1, distAt2, 0.0, 1.0)
                    return i1 + t
                else:
                    leftLimit = i1
            else:
                rightLimit = i1
            i1 = (leftLimit + rightLimit) / 2

        return 0


    def getPointAtIndexInterpolated(self, findex):
        i1, i2, t = self.getInterpolationParams(findex)
        return lerp(self.points[i1], self.points[i2], t)


    def getInterpolationParams(self, findex):
        i1 = math.floor(findex)
        t = findex - i1
        i1 = self.getWrappedIndex(i1)
        i2 = self.getWrappedIndex(i1 + 1)
        return i1, i2, t


    def getWrappedIndex(self, index):
        if len(self.points) == 0:
            return 0
    
        if index < 0: 
            return int(index + len(self.points)) % int(len(self.points) - 1)

        if index > len(self.points)-1:
            return int(index) % len(self.points)

        return int(index)


    def getResampledBySpacing(self, spacing):
        if spacing==0 or (self.points) == 0:
            return self

        poly = Polyline()
        totalLength = self.getPerimeter()
        f = 0.0
        while f < totalLength:
            poly.lineTo( self.getPointAtLength(f) )
            f += spacing
        
        return poly


    def getResampledByCount(self, count):
        if count < 2:
            return None

        perimeter = self.getPerimeter()
        return self.getResampledBySpacing( perimeter / (count-1) )


    def toTexture(self, width, height, resolution=1000):
        x = np.zeros(resolution+1)
        y = np.zeros(resolution+1)
        x.fill(np.nan)
        y.fill(np.nan)

        poly = self.getResampledByCount(resolution)

        for i in range(poly.size()):
            p = poly[i]

            x[i] = p[0] / float(width)
            y[i] = p[1] / float(height)

        x[resolution] = np.nan
        y[resolution] = np.nan

        from .Texture import Texture
        return Texture( (x.flatten('F'), y.flatten('F')) )


