#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
    
import math
import numpy as np

from .AxiElement import AxiElement
from .tools import lerp, distance, remap, transform, normalize, perpendicular, clamp, dot, linesIntersection


class Polyline(AxiElement):
    def __init__( self, points=None, **kwargs):
        AxiElement.__init__(self, **kwargs);
        self.points = []
        self.normals = []
        self.tangents = []
        self.lengths = []
        self.holes = None
        self.dirty = True
        self.anchor = kwargs.pop('anchor', [0.0, 0.0])
        self.close = kwargs.pop('close', False)

        if points != None:            
            if isinstance(points, Polyline):
                self.points = points.points
                self.dirty = points.dirty
                self.close = kwargs.pop('close', points.close)

                self.translate = kwargs.pop('translate', points.translate)
                self.scale = kwargs.pop('scale', points.scale)
                self.rotate = kwargs.pop('rotate', points.rotate)
                self.stroke_width = kwargs.pop('stroke_width', points.stroke_width)
                self.head_width = kwargs.pop('head_width', points.head_width)
                self.fill = kwargs.pop('fill', points.fill)
                self.anchor = kwargs.pop('anchor', points.anchor) 

            elif isinstance(points, str):
                self.setFromString(points)
                
            else:
                self.points = points


    def __len__(self):
        return len(self.points)


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
            try:
                normal = perpendicular(self.points[0], self.points[1])
            except TypeError:
                print(">> perp p0 and p1 ", self.points[0], self.points[1], 'from', self.points)
        elif index == self.size():
            try:
                normal = perpendicular(self.points[-2], self.points[-1])
            except TypeError:
                print(">> perp p-2 and p-1", self.points[-2], self.points[-1], 'from', self.points)
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

        self.dirty = False


    def size(self):
        return len(self.points)


    def setFromString(self, data):
        data = data.split(' ')
        for x, y in zip(data[0::2], data[1::2]):
            self.points.append( [float(x), float(y)] )


    def lineTo( self, pos ):
        self.points.append( pos )
        self.dirty = True

        
    def arcTo( self, pos, radius, **kwargs ):
        if self.size > 0:
            from .Arc import Arc
            self.points.extend( Arc(self.points[-1], pos, radius, **kwargs ).getPoints()[1:] )
            self.dirty = True
        else:
            print('Arc needs a starting point')


    def cubicBezierTo( self, control1, control2, end, **kwargs ):
        if self.size > 0:
            from .CubicBezier import CubicBezier
            self.points.extend( CubicBezier(self.points[-1], control1, control2, end, **kwargs ).getPoints()[1:] )
            self.dirty = True
        else:
            print('cubicBezier needs a starting point')


    def setClose(self, close):
        if self.points[0][0] == self.points[-1][0] and self.points[0][1] == self.points[-1][1]:
            if not close:
                # If it's closed and shouldn't be delete the last one
                del self.points[-1]
                self.dirty = True
        else:
            if close:
                # If it's not closed and need to be close
                self.points.append( self.points[0] )
                self.dirty = True
        self.close = close 


    def getPerimeter(self):
        if self.dirty:
            self._updateCache()

        if len(self.lengths) < 1:
            return 0
        return self.lengths[-1]


    def getIndexAtLength(self, length):
        totalLength = self.getPerimeter()
        length = max(min(length, totalLength), 0)
    
        # lastPointIndex = (len(self.points) - 1, len(self.points))[self.isClosed]
        lastPointIndex = len(self.points) - 1

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
            return  (0, int(index + len(self.points)) % int(len(self.points) - 1) )[self.close]

        if index > len(self.points)-1:
            return  (len(self.points) - 1, int(index) % len(self.points))[self.close]

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

        if self.dirty:
            self._updateCache()

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

        poly = Polyline( stroke_width=self.stroke_width, fill=self.fill, head_width=self.head_width, close=self.close )
        totalLength = self.getPerimeter()
        f = 0.0
        while f < totalLength:
            poly.lineTo( self.getPointAtLength(f) )
            f += spacing

        # if not self.isClosed:
        #     if poly.size() > 0:
        #         poly.points[-1] = self.points[-1]
        #         self.isClosed = False
        #     else:
        #         self.isClosed = True
        
        return poly


    def getResampledByCount(self, count):
        if count < 2:
            return None

        perimeter = self.getPerimeter()
        return self.getResampledBySpacing( perimeter / (count-1) )


    def getOffset(self, offset):
        if offset == 0 or len(self.points) <= 2:
            return self

        if self.dirty:
            self._updateCache()

        points = []

        if self.size() < 2:
            return Polyline(points, stroke_width=self.stroke_width, fill=self.fill, head_width=self.head_width, close=self.close)

        for i in range(self.size()):
            width = offset

            norm = normalize(self.normals[i])

            # TODO:
            #       FIX MITER
            #       Refs: https://github.com/tangrams/tangram/blob/master/src/builders/polylines.js
            if i != 0:
                prevN = normalize(self.normals[i-1])
                mitter = 2.0 / (1.0 + dot(norm, prevN) )
                try:
                    scale = math.sqrt(mitter)
                except ValueError:
                    raise Exception("SQRT out of domain", norm, prevN, mitter)
                width *= scale

            p = [self.points[i][0] + norm[0] * width, self.points[i][1] + norm[1] * width]
            points.append( transform(p, rotate=self.rotate, scale=self.scale, translate=self.translate, anchor=self.anchor) )
        return Polyline(points, stroke_width=self.stroke_width, fill=self.fill, head_width=self.head_width, close=self.close)


    def _toShapelyGeom(self):
        if self.close:
            return self._toShapelyPolygon()
        else:
            return self._toShapelyLineString()


    def _toShapelyPolygon(self):
        try:
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('To convert a Polyline to a Shapely Polygon requires shapely. Try: pip install shapely')

        holes=[]
        if self.holes != None:            
            for hole in self.holes:
                holes.append( Polyline(hole, close=True) )
        return geometry.Polygon( self.getPoints(), holes=holes )


    def _toShapelyLineString(self):
        try:
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('To convert a Polyline to a Shapely LineString requires shapely. Try: pip install shapely')

        return geometry.LineString(self.getPoints())


    def getBuffer(self, offset):
        if offset <= 0:
            return self

        if len(self.points) < 2:
            return self

        poly = self._toShapelyLineString().buffer(offset)
        return Polyline( list(poly.exterior.coords), stroke_width=self.stroke_width, head_width=self.head_width, close=self.close )


    def getSimplify(self, tolerance = None):
        if len(self.points) < 2:
            return self

        if tolerance is None:
            tolerance = self.head_width * 0.1

        line = self._toShapelyLineString().simplify(tolerance, preserve_topology=False)
        if line.length > 0:
            return Polyline( list(line.coords), stroke_width=self.stroke_width, fill=self.fill, head_width=self.head_width)
        else:
            return Polyline()


    def getConvexHull(self):
        if len(self.points) < 3:
            return Polyline()

        polygon = self._toShapelyPolygon()
        return Polyline( list(polygon.convex_hull.exterior.coords) )


    def getStrokePath(self, **kwargs):
        from .Path import Path

        simplify = kwargs.pop('simplify', True )

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

        return Path(path)


    def getFillPath(self, **kwargs):
        from .Path import Path

        # From FlatCam
        # https://bitbucket.org/jpcgt/flatcam/src/46454c293a9b390c931b52eb6217ca47e13b0231/camlib.py?at=master&fileviewer=file-view-default#camlib.py-478
        head_width = kwargs.pop('head_width', self.head_width)
        overlap = kwargs.pop('overlap', 0.15 )
        offset = kwargs.pop('offset', 0.0 )
        simplify = kwargs.pop('simplify', True )
        sort_them = kwargs.pop('sort', True )
        join_them = kwargs.pop('join', True )
        optimize_lifts = kwargs.pop('optimize_lifts', False )

        if len(self.points) < 3:
            return self

        polygon = self._toShapelyPolygon()
        
        # Can only result in a Polygon or MultiPolygon
        # NOTE: The resulting polygon can be "empty".
        current = polygon.buffer(-head_width / 2.0 - offset)
        if current.area == 0:
            # Otherwise, trying to to insert current.exterior == None
            # into the FlatCAMStorage will fail.
            return Path()

        path = Path(head_width=head_width)
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
            current = current.buffer(-head_width * (1 - overlap))
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

        if simplify:
            path = path.getSimplify()
        
        if sort_them:
            path = path.getSorted()

        if join_them:
            if optimize_lifts:
                path = path.getJoined(boundary=polygon)
            else:
                path = path.getJoined()
        
        return path


    def getIntersections(self, other):
        indices = []

        from .Line import Line

        if isinstance(other, Line):
            points = self.getPoints()
            prev_point = points[0]
            index = 0
            for point in points[1:]:
                intersection = linesIntersection(prev_point, point, other.start, other.end)
                if intersection:
                    pct = distance(prev_point, intersection) / distance(prev_point, point)
                    indices.append( index + pct )
                prev_point = point
                index += 1.0

        elif isinstance(other, Polyline):
            points = other.getPoints()
            other_prev_point = points[0]
            for other_point in points[1:]:
                indices.extend( self.getIntersections(Line(other_prev_point, other_point)) )
                other_prev_point = other_point

        # TODO:
        #      - Intersections w Arcs, Circles, Rects, Hexagons and Polygons w Holes

        return indices


    def getCroppedPath(self, bounds=None, **kwargs ):
        from .Path import Path

        x1 = kwargs.pop('x', 0.0)
        y1 = kwargs.pop('y', 0.0)
        x2 = x1 + kwargs.pop('width', 297.0)
        y2 = y1 + kwargs.pop('height', 420.0)

        if bounds != None:
            from .Bbox import Bbox
            if isinstance(bounds, Bbox):
                x1 = bounds.min_x
                y1 = bounds.min_y
                x2 = bounds.max_x
                y2 = bounds.max_y

        def crop_interpolate(x1, y1, x2, y2, ax, ay, bx, by):
            dx = bx - ax
            dy = by - ay
            t1 = (x1 - ax) / dx if dx else -1
            t2 = (y1 - ay) / dy if dy else -1
            t3 = (x2 - ax) / dx if dx else -1
            t4 = (y2 - ay) / dy if dy else -1
            ts = [t1, t2, t3, t4]
            ts = [t for t in ts if t >= 0 and t <= 1]
            t = min(ts)
            x = ax + (bx - ax) * t
            y = ay + (by - ay) * t
            return (x, y)

        points = self.getPoints()
        e = 1e-9
        result = []
        buf = []
        previous_point = None
        previous_inside = False
        for x, y in points:
            inside = x >= x1 - e and y >= y1 - e and x <= x2 + e and y <= y2 + e
            if inside:
                if not previous_inside and previous_point:
                    px, py = previous_point
                    ix, iy = crop_interpolate(x1, y1, x2, y2, x, y, px, py)
                    buf.append([ix, iy])
                buf.append([x, y])
            else:
                if previous_inside and previous_point:
                    px, py = previous_point
                    ix, iy = crop_interpolate(x1, y1, x2, y2, x, y, px, py)
                    buf.append([ix, iy])
                    result.append(buf)
                    buf = []
            previous_point = [x, y]
            previous_inside = inside
        if buf:
            result.append(buf)
        return Path(result, head_width=self.head_width, stroke_width=self.stroke_width)


    def getTransformed(self, func):
        return Polyline([func(x, y) for x, y in self.getPoints()])


    def getPoints(self):
        points = []

        if self.isTranformed:
            for p in self.points:
                points.append( transform(p, rotate=self.rotate, scale=self.scale, translate=self.translate, anchor=self.anchor) )
        else:
            points = self.points

        if len(points) > 2 and self.close:
            if points[0][0] != points[-1][0] and points[0][1] != points[-1][1]:
                points.append( points[0] )

        return points


    def getPath(self, **kwargs):
        path = AxiElement.getPath(self, **kwargs)

        if self.holes != None:
            for poly in self.holes:
                path.add( poly.getPath(**kwargs) )

        return path
