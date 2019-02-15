#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement
from .Bbox import Bbox
from .tools import pointInside, linesIntersection, lerp, distance, remap, transform, normalize, clamp, perpendicular, dot

class Polyline(AxiElement):
    def __init__( self, points=None, **kwargs):
        AxiElement.__init__(self, **kwargs);

        # TODO:
        #   Polyline < > Polygon
        #   Resolve width
        #   resolve fill

        if isinstance(points, Polyline):
            points = points.points

        if points == None:
            points = []

        self.points = points
        self.normals = []
        self.tangents = []
        self.lengths = []
        self.isClosed = kwargs.pop('isClosed', False) 
        self.anchor = kwargs.pop('anchor', [0.0, 0.0]) 
        self._updateCache()


    def __getitem__(self, index):
        if type(index) is int:
            # return self.points[ index ]
            if self.isTranformed:
                return transform(self.points[ index ], rotate=self.rotate, scale=self.scale, translate=self.translate, anchor=self.anchor)
            else:
                return self.points[ index ]
        else:
            return None

    
    def _calcData(self, index): #, angle, rotation):
        normal = [0.0, 0.0]
        tangent = [0.0, 0.0]

        if self.size() < 2:
            return normal, tangent

        if index == 0:
            normal = perpendicular(self.points[0], self.points[1])
        elif index == self.size():
            normal = perpendicular(self.points[-2], self.points[-1])
        else:
            i1 = self.getWrappedIndex( index - 1 )
            i2 = self.getWrappedIndex( index     )
            i3 = self.getWrappedIndex( index + 1 )

            p1 = self.points[i1]
            p2 = self.points[i2]
            p3 = self.points[i3]

            v1 = [p1[0] - p2[0], p1[1] - p2[1]] # vector to previous point
            v2 = [p3[0] - p2[0], p3[1] - p2[1]]  # vector to next point

            v1 = normalize(v1);
            v2 = normalize(v2);

            # If just one of p1, p2, or p3 was identical, further calculations 
            # are (almost literally) pointless, as v1 or v2 will then contain 
            # NaN values instead of floats.
            segmentHasZeroLength = v1 is None or v2 is None

            if not segmentHasZeroLength:
                if distance(v2, v1) > 0.0:
                    tangent  = normalize(v2 - v1)
                else:
                    tangent = -v1

                normal = normalize( [-tangent[1], tangent[0]] )
                # rotation = np.cross( v1, v2 )
                # angle    = math.pi - math.acos( clamp( np.dot( v1, v2 ), -1.0, 1.0 ) )

        return normal, tangent


    def _updateCache(self):
        # Clean
        self.lengths = []
        self.tangents = []
        self.normals = []
        N = len(self.points)

        # Check
        if N < 2:
            return self

        # Process
        length = 0
        for i in range( N - 1 ):
            self.lengths.append(length)
            p1 = self.points[i]
            p2 = self.points[i+1]
            length += distance(p1, p2)

            normal, tangent = self._calcData(i)
            self.normals.append(normal)
            self.tangents.append(tangent)

        normal, tangent = self._calcData(N)
        self.normals.append(normal)
        self.tangents.append(tangent)

        if self.isClosed:
            self.lengths.append(length)


    def size(self):
        return len(self.points)


    def lineTo( self, pos ):
        self.points.append( pos )
        self._updateCache()


    def setClose(self, close):
        self.isClosed = close
        self._updateCache()


    def inside( self, pos ):
        return pointInside( pos, self.points )


    def isTranformed(self):
        return self.translate[0] != 0.0 or self.translate[1] != 0.0 or self.scale != 1.0 or self.rotate != 0.0


    def getPerimeter(self):
        if len(self.lengths) < 1:
            return 0
        return self.lengths[-1]


    def getIndexAtLength(self, length):
        totalLength = self.getPerimeter()
        length = max(min(length, totalLength), 0)
    
        lastPointIndex =  (len(self.points) - 1, len(self.points))[self.isClosed]

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
            return  (0, int(index + len(self.points)) % int(len(self.points) - 1) )[self.isClosed]

        if index > len(self.points)-1:
            return  (len(self.points) - 1, int(index) % len(self.points))[self.isClosed]

        return int(index)


    def getPointAtLength(self, length):
        return self.getPointAtIndexInterpolated( self.getIndexAtLength( length ) )


    def getPointAtIndexInterpolated(self, findex):
        i1, i2, t = self.getInterpolationParams(findex)
        p = lerp(self.points[i1], self.points[i2], t)

        if self.isTranformed:
            return transform(p, rotate=self.rotate, scale=self.scale, translate=self.translate, anchor=self.anchor)
        else:
            return p


    def getNormalAtIndex(self, index):
        if self.points.size() < 2:
            return self

        if self.isTranformed:
            return transform(p, self.normals[ self.getWrappedIndex(index) ], rotate=self.rotate )
        else:
            return self.normals[ self.getWrappedIndex(index) ]


    def getNormalAtIndexInterpolated(self, findex):
        if self.points.size() < 2:
            return self

        i1, i2, t = self.getInterpolationParams(findex)
        return lerp(self.getNormalAtIndex(i1), self.getNormalAtIndex[i2], t)


    def getTangentAtIndex(self, index):
        if self.points.size() < 2:
            return self

        if self.isTranformed:
            return transform(p, self.tangents[ self.getWrappedIndex(index) ], rotate=self.rotate )
        else:
            return self.tangents[ self.getWrappedIndex(index) ]


    def getTangentAtIndexInterpolated(self, findex):
        # if(points.size() < 2) return T();
        i1, i2, t = self.getInterpolationParams(findex)
        return lerp(self.getTangentAtIndex(i1), self.getTangentAtIndex[i2], t)


    def getResampledBySpacing(self, spacing):
        if spacing==0 or (self.points) == 0:
            return self

        poly = Polyline()
        totalLength = self.getPerimeter()
        f = 0.0
        while f < totalLength:
            poly.lineTo( self.getPointAtLength(f) )
            f += spacing

        if not self.isClosed:
            if poly.size() > 0:
                poly.points[-1] = self.points[-1];
                self.isClosed = False
            else:
                self.isClosed = True
        
        return poly


    def getResampledByCount(self, count):
        if count < 2:
            return None

        perimeter = self.getPerimeter()
        return self.getResampledBySpacing( perimeter / (count-1) )


    def getPolygonOffset(self, offset):
        if offset == 0 or (self.points) <= 2:
            return self

        points = []

        if self.size() < 2:
            return Polyline(points)

        for i in range(self.size()):
            width = offset

            miter = self.normals[i]

            # TODO:
            #       FIX MITER
            #       Refs: https://github.com/tangrams/tangram/blob/master/src/builders/polylines.js
            if i != 0:
                prevN = self.normals[i-1]
                scale = math.sqrt(2.0 / (1.0 + dot(miter, prevN) ))
                width *= scale

            p = [self.points[i][0] + miter[0] * width,
                 self.points[i][1] + miter[1] * width]
            points.append( transform(p, rotate=self.rotate, scale=self.scale, translate=self.translate, anchor=self.anchor) )
        
        return Polyline(points)


    def getPoints(self):
        if self.isTranformed():
            points = []
            for p in self.points:
                points.append( transform(p, rotate=self.rotate, scale=self.scale, translate=self.translate, anchor=self.anchor) )

            if self.isClosed:
                points.append( transform(self.points[0], rotate=self.rotate, scale=self.scale, translate=self.translate, anchor=self.anchor) )
            return points
        else:
            if self.isClosed:
                points = self.points[:]
                points.append( self.points[0] )
                return points
            else:
                return self.points


    def getBbox(self):
        return Bbox( points=self.getPoints() )


    def getPath(self):
        path = []

        if self.stroke_width > self.head_width:
            r = (self.stroke_width * self.head_width) * 0.5
            r_target = -(self.stroke_width * self.head_width) * 0.5
            while r > r_target:
                path.append( self.getPolygonOffset(r).getPoints() )
                r = max(r - self.head_width, r_target)
        else:
            path.append( self.getPoints() )

        return path


    def getTexture(self, **kwargs):
        size = kwargs.pop('size', None)
        resolution = kwargs.pop('resolution', None)

        if size == None:
            bbox = self.getBbox()
        
        path = self.getPath()

        from .Texture import Texture
        texture = Texture()

        for points in path:
            poly = Polyline(points)

            if resolution:
                poly = poly.getResampledBySpacing(resolution)

            N = poly.size()
            x = np.zeros(int(N)+1)
            y = np.zeros(int(N)+1)
            x.fill(np.nan)
            y.fill(np.nan)

            for i in range(N):
                p = poly[i]
                x[i] = p[0] / float(size[0])
                y[i] = p[1] / float(size[1])

            x[N] = np.nan
            y[N] = np.nan

            texture = texture + Texture( (x.flatten('F'), y.flatten('F')) )

        return texture


    def getPathString(self):

        def path_gen(points):
            return 'M' + 'L'.join('{0} {1}'.format(x,y) for x,y in points)
        
        path = self.getPath()
        path_str = ''

        for poly in path:
            path_str += path_gen( poly )

        return path_str



