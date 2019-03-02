#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement
from .Index import Index
from .tools import path_length, transform

# Mostly rom Axi by Michael Fogleman
# https://github.com/fogleman/axi/blob/master/axi/spatial.py

class Path(AxiElement):
    def __init__(self, path=None, **kwargs):
        AxiElement.__init__(self, **kwargs);

        if path is None:
            self.path = []
        elif isinstance(path, Path):
            self.path = path.path

        elif isinstance(path, AxiElement):
            self.path = path.getPath()
        else:
            self.path = path

        self._length = None
        self._down_length = None


    def __len__(self):
        return len(self.path)


    def __iter__(self):
        self._index = 0
        return self


    def __next__(self):
        if self._index < len(self.path):
            result = self[ self._index ]
            self._index += 1
            return result
        else:
            raise StopIteration


    def next(self):
        return self.__next__()


    def __getitem__(self, index):
        from .Polyline import Polyline
        if type(index) is int:
            return Polyline( self.path[index], translate=self.translate, scale=self.scale, rotate=self.rotate, stroke_width=self.stroke_width, head_width=self.head_width )
        else:
            return None


    @property
    def length(self):
        if self._length is None:
            length = self.down_length
            for p0, p1 in zip(self.path, self.path[1:]):
                x0, y0 = p0[-1]
                x1, y1 = p1[0]
                length += math.hypot(x1 - x0, y1 - y0)
            self._length = length
        return self._length


    @property
    def up_length(self):
        return self.length - self.down_length


    @property
    def down_length(self):
        if self._down_length is None:
            self._down_length = path_length(self.path)
        return self._down_length


    @property
    def width(self):
        return self.bounds.width


    @property
    def height(self):
        return self.bounds.height


    def add(self, other):
        from .Polyline import Polyline

        if isinstance(other, Path):
            self.path.extend( other.path )
        elif isinstance(other, Polyline):
            points  = other.getPoints() 
            if len(points) > 1: 
                self.path.append( points )
        elif isinstance(other, AxiElement):
            self.path.extend( other.getPath() )
        elif isinstance(other, list):
            self.path.append( other )
        else:
            raise Exception("Error, don't know what to do with: ", other)

    # def substract(self, other):
    #     from .Polyline import Polyline
    #     from .Polygon import Polygon

    #     # if isinstance(other, Polygon):


    def getPoints(self):
        return [(x, y) for points in self.path for x, y in points]


    def getConvexHull(self):
        try:
            from .Polyline import Polyline
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('Polyline.getConvexHull() requires Shapely')

        polygon = geometry.Polygon( self.getPoints() )
        return Polyline( polygon.convex_hull.exterior.coords, head_width=self.head_width, stroke_width=self.stroke_width )


    def getTexture(self, width, height, **kwargs):
        resolution = kwargs.pop('resolution', None)

        from .Texture import Texture
        from .Polyline import Polyline
        texture = Texture(width=width, height=height, **kwargs)

        for points in self.path:
        
            if resolution:
                poly = Polyline(points)
                poly = poly.getResampledBySpacing(resolution)
                points = poly.getPoints()

            N = len(points)
            x = np.zeros(int(N)+1)
            y = np.zeros(int(N)+1)
            x.fill(np.nan)
            y.fill(np.nan)

            for i in range(N):
                X, Y = points[i]
                x[i] = X / float(texture.width)
                y[i] = Y / float(texture.height)

            x[N] = np.nan
            y[N] = np.nan

            texture.add( (x.flatten('F'), y.flatten('F')) )

        return texture


    def getSorted(self, reversable=True):
        if len(self.path) < 2:
            return self

        path = self.path[:]

        first = path[0]
        path.remove(first)
        result = [first]
        points = []

        for path in path:
            x1, y1 = path[0]
            x2, y2 = path[-1]
            points.append((x1, y1, path, False))

            if reversable:
                points.append((x2, y2, path, True))

        if len(points) <= 2:
            return self

        index = Index( chain=points )

        while index.size > 0:
            x, y, path, reverse = index.nearest(result[-1][-1])
            x1, y1 = path[0]
            x2, y2 = path[-1]
            index.remove((x1, y1, path, False))

            if reversable:
                index.remove((x2, y2, path, True))

            if reverse:
                result.append(list(reversed(path)))
            else:
                result.append(path)

        return Path( result, head_width=self.head_width, stroke_width=self.stroke_width )


    def getJoined(self, tolerance = None, boundary = None):
        try:
            from shapely import geometry
        except ImportError:
            geometry = None

        if boundary != None and geometry is None:
            print('Path.joined() will not work with boundary bacause needs Shapely')
            boundary = None

        if len(self.path) < 2:
            return self

        if tolerance is None:
            tolerance = self.head_width

        result = [list(self.path[0])]
        for path in self.path[1:]:
            x1, y1 = result[-1][-1]
            x2, y2 = path[0]

            join = False

            if boundary != None:
                walk_path = geometry.LineString( [result[-1][-1], path[0]] )
                walk_cut = walk_path.buffer( self.head_width * 0.5 )
                join = walk_cut.within(boundary) # and walk_path.length < max_walk
            else:
                join = math.hypot(x2 - x1, y2 - y1) <= tolerance

            if join:
                result[-1].extend(path)
            else:
                result.append(list(path))
                
        return Path(result, head_width=self.head_width, stroke_width=self.stroke_width )


    def getSimplify(self, tolerance = None):
        from .Polyline import Polyline

        result = Path( head_width=self.head_width, stroke_width=self.stroke_width )
        for points in self.path:
            if len(points) > 1:
                result.add( Polyline( points, head_width=self.head_width, stroke_width=self.stroke_width).getSimplify(tolerance) )
        return result


    def getTransformed(self, func):
        return Path([[func(x, y) for x, y in points] for points in self.path], head_width=self.head_width, stroke_width=self.stroke_width )


    def getTranslated(self, dx, dy):
        def func(x, y):
            return (x + dx, y + dy)
        return self.getTransformed(func)


    def getScaled(self, sx, sy=None):
        if sy is None:
            sy = sx
        def func(x, y):
            return (x * sx, y * sy)
        return self.getTransformed(func)


    def getRotated(self, angle):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        def func(x, y):
            return (x * c - y * s, y * c + x * s)
        return self.getTransformed(func)


    def getMoved(self, x, y, ax, ay):
        bbox = self.bounds
        x1, y1, x2, y2 = bbox.limits
        dx = x1 + (x2 - x1) * ax - x
        dy = y1 + (y2 - y1) * ay - y
        return self.getTranslated(-dx, -dy)


    def getCentered(self, width, height):
        return self.getMoved(width / 2, height / 2, 0.5, 0.5)


    def getRotatedToFit(self, width, height, step=5):
        for angle in range(0, 180, step):
            path = self.getRotated(angle)
            if path.width <= width and path.height <= height:
                return path.getCentered(width, height)
        return None


    def getScaledToFit(self, width, height, padding=0):
        width -= padding * 2
        height -= padding * 2
        scale = min(width / self.width, height / self.height)
        return self.getScaled(scale, scale).getCentered(width, height)


    def getRotateAndScaleToFit(self, width, height, padding=0, step=1):
        values = []
        width -= padding * 2
        height -= padding * 2
        hull = self.getConvexHull()
        for angle in range(0, 180, step):
            d = hull.getRotated(angle)
            scale = min(width / d.bounds.width, height / d.bounds.height)
            values.append((scale, angle))
        scale, angle = max(values)
        return self.getRotated(angle).getScaled(scale, scale).getCentered(width, height)


    def getSVGElementString(self):
        path_str = ''

        if self.isTranformed:
            for points in self.path:
                first = True
                for point in points:
                    p = transform(point, translate=self.translate, scale=self.scale, rotate=self.rotate)
                    if first:
                        first = False
                        path_str += 'M%0.1f %0.1f' % (p[0], p[1])
                    else:
                        path_str += 'L%0.1f %0.1f' % (p[0], p[1])
        else:
            for points in self.path:
                path_str += 'M' + ' L'.join('{0} {1}'.format(x,y) for x,y in points)

        svg_str = '<path '
        if self.id != None:
            svg_str += 'id="' + self.id + '" '
        svg_str += 'd="' + path_str + '" '
        svg_str += 'fill="none" stroke="black" stroke-width="'+str(self.head_width) + '" '
        svg_str += '/>\n'
        
        return svg_str


    def getGCodeString(self, **kwargs):
        head_up_height = kwargs.pop('head_up_height', 3)
        head_down_height = kwargs.pop('head_down_height', -0.5)
        head_up_speed = kwargs.pop('head_up_speed', 800)
        head_down_speed = kwargs.pop('head_down_speed', 500)
        move_speed = kwargs.pop('move_speed', 300)
        # bed_max_x = kwargs.pop('bed_max_x', 200)
        # bed_max_y = kwargs.pop('bed_max_y', 200)


        transformed = self.isTranformed
        gcode_str = ''
        for points in self.path:
            gcode_str += "G0 Z%0.1f F" % (head_up_height) + str(head_up_speed) + "\n"
            
            p = points[0][:]
            if transformed:
                p = transform(points[0], translate=self.translate, scale=self.scale, rotate=self.rotate)
                gcode_str += "G0 X%0.1f Y%0.1f\n" % (p[0], p[1])
            else:
                gcode_str += "G0 X%0.1f Y%0.1f\n" % (p[0], p[1])

            gcode_str += "G1 Z%0.1f F" % (head_down_height) + str(head_down_speed) +"\n"

            first = True
            for point in points[1:]:
                # if x > 0 and x < bed_max_x and y > 0 and y < bed_max_y:  
                p = point[:]
                if transformed:
                    p = transform(p, translate=self.translate, scale=self.scale, rotate=self.rotate)
                gcode_str += "G1 X%0.1f Y%0.1f" % (p[0], p[1])

                if first:
                    gcode_str += " F" + str(move_speed)
                    first = False
                gcode_str += '\n'

        gcode_str += "G0 Z%0.1f\n" % (head_up_height)
        return  gcode_str
            
