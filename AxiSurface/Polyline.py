#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement
from .tools import lerp, distance, remap, transform, normalize, perpendicular, clamp, dot

class Polyline(AxiElement):
    def __init__( self, points=None, **kwargs):
        AxiElement.__init__(self, **kwargs);
        self.points = []
        self.normals = []
        self.tangents = []
        self.lengths = []
        self.holes = None
        self.isClosed = kwargs.pop('isClosed', False) 
        self.anchor = kwargs.pop('anchor', [0.0, 0.0])

        if points != None:            
            if isinstance(points, Polyline):
                self.points = points.points
                self.translate = kwargs.pop('translate', points.translate)
                self.scale = kwargs.pop('scale', points.scale)
                self.rotate = kwargs.pop('rotate', points.rotate)
                self.stroke_width = kwargs.pop('stroke_width', points.stroke_width)
                self.head_width = kwargs.pop('head_width', points.head_width)
                self.fill = kwargs.pop('fill', points.fill)

                self.isClosed = kwargs.pop('isClosed', points.isClosed) 
                self.anchor = kwargs.pop('anchor', points.anchor) 
            else:
                self.points = points
        
            self._updateCache()


    def __iter__(self):
        self._index = 0
        return self


    def __next__(self):
        if self._index < len(self.points):
            result = self[ self._index ]
            self._index += 1
            return result
        else:
            raise StopIteration


    def next(self):
        return self.__next__()


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

        poly = Polyline( stroke_width=self.stroke_width, fill=self.fill, head_width=self.head_width )
        totalLength = self.getPerimeter()
        f = 0.0
        while f < totalLength:
            poly.lineTo( self.getPointAtLength(f) )
            f += spacing

        if not self.isClosed:
            if poly.size() > 0:
                poly.points[-1] = self.points[-1]
                self.isClosed = False
            else:
                self.isClosed = True
        
        return poly


    def getResampledByCount(self, count):
        if count < 2:
            return None

        perimeter = self.getPerimeter()
        return self.getResampledBySpacing( perimeter / (count-1) )


    def getOffset(self, offset):
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
        return Polyline(points, stroke_width=self.stroke_width, fill=self.fill, head_width=self.head_width)

        
    def getBuffer(self, offset):
        if offset <= 0:
            return self

        try:
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('Polyline.getBuffer() requires Shapely')

        if len(self.points) < 2:
            return self

        line = geometry.LineString( self.getPoints() )
        poly = line.buffer(offset)

        return Polyline( list(poly.exterior.coords), stroke_width=self.stroke_width, head_width=self.head_width )


    def _toShapelyPolygon(self):
        try:
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('This requires Shapely module')

        holes=[]
        if self.holes != None:            
            for hole in self.holes:
                holes.append( Polyline(hole) )
        return geometry.Polygon( self.getPoints(), holes=holes )


    def getFillPath(self, **kwargs ):
        # From FlatCam
        # https://bitbucket.org/jpcgt/flatcam/src/46454c293a9b390c931b52eb6217ca47e13b0231/camlib.py?at=master&fileviewer=file-view-default#camlib.py-478
        tooldia = kwargs.pop('tooldia', self.head_width)
        overlap = kwargs.pop('overlap', 0.15 )

        try:
            from .Path import Path
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('Polyline.getFillPath() requires Shapely')

        if len(self.points) < 3:
            return self

        polygon = self._toShapelyPolygon()
        
         # Can only result in a Polygon or MultiPolygon
        # NOTE: The resulting polygon can be "empty".
        current = polygon.buffer(-tooldia / 2.0)
        if current.area == 0:
            # Otherwise, trying to to insert current.exterior == None
            # into the FlatCAMStorage will fail.
            return Path()

        path = Path(stroke_width=self.stroke_width, head_width=self.head_width)
        # current can be a MultiPolygon
        try:
            for p in current:
                path.add( Polyline( list(p.exterior.coords) ) )
                for i in p.interiors:
                    path.add( Polyline( i.coords ) )

        # Not a Multipolygon. Must be a Polygon
        except TypeError:
            path.add( Polyline( list(current.exterior.coords) ) )
            for i in current.interiors:
                path.add( Polyline( list(i.coords) ) )

        while True:

            # Can only result in a Polygon or MultiPolygon
            current = current.buffer(-tooldia * (1 - overlap))
            if current.area > 0:

                # current can be a MultiPolygon
                try:
                    for p in current:
                        path.add( Polyline( list(p.exterior.coords) ) )
                        for i in p.interiors:
                            path.add( Polyline( list(i.coords) ) )

                # Not a Multipolygon. Must be a Polygon
                except TypeError:
                    path.add( Polyline( list(current.exterior.coords) ) )
                    for i in current.interiors:
                        path.add( Polyline( list(i.coords) ) )
            else:
                break

        return path.getSimplify().getSorted().getJoined(boundary=polygon)
        

    def getSimplify(self, tolerance = None):
        try:
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('Polyline.getSimplify() requires Shapely')

        if len(self.points) < 2:
            return self

        if tolerance is None:
            tolerance = self.head_width * 0.1

        line = geometry.LineString(self.getPoints())
        line = line.simplify(tolerance, preserve_topology=False)
        if line.length > 0:
            return Polyline( list(line.coords), stroke_width=self.stroke_width, fill=self.fill, head_width=self.head_width)
        else:
            return Polyline()


    def getConvexHull(self):
        try:
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('Polyline.getConvexHull() requires Shapely')

        polygon = self._toShapelyPolygon()
        # points = [z.tolist() for z in polygon.convex_hull.exterior.coords.xy]
        return Polyline( list(polygon.convex_hull.exterior.coords) )


    def getPoints(self):
        if self.isTranformed:
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


    def getPath(self):
        from .Path import Path

        # TODO:
        #      - Fix stroke_width and head_width on scale

        path = []
        if self.stroke_width > self.head_width:
            r = (self.stroke_width * self.head_width) * 0.5
            r_target = -(self.stroke_width * self.head_width) * 0.5
            while r > r_target:
                path.append( self.getOffset(r).getPoints() )
                r = max(r - self.head_width, r_target)
        else:
            path.append( self.getPoints() )

        path = Path(path)
        if self.fill:
            path.add( self.getFillPath() )

        if self.holes != None:
            for poly in self.holes:
                path.add( poly.getPath() )

        return path

