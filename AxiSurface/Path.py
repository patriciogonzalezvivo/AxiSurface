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
from .tools import path_length

# Mostly rom Axi by Michael Fogleman
# https://github.com/fogleman/axi/blob/master/axi/spatial.py

class Path(AxiElement):
    def __init__(self, path=None, **kwargs):
        AxiElement.__init__(self, **kwargs);

        if path is None:
            self.path = []
        elif isinstance(path, Path):
            self.path = path.points
        elif isinstance(path, AxiElement):
            self.path = path.getPath()
        else:
            self.path = path


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
        if isinstance(other, Path):
            self.path.extend( other.path )
        else:
            self.path.extend( other.getPath() )


    def getPoints(self):
        return [(x, y) for points in self.path for x, y in points]


    def getSorted(self, reversable=True):
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
        return Path(result)


    def getTransform(self, func):
        return Path([[func(x, y) for x, y in path] for path in self.path])


    def getTranslated(self, dx, dy):
        def func(x, y):
            return (x + dx, y + dy)
        return self.getTransform(func)


    def getScaled(self, sx, sy=None):
        if sy is None:
            sy = sx
        def func(x, y):
            return (x * sx, y * sy)
        return self.getTransform(func)


    def getRotated(self, angle):
        c = cos(radians(angle))
        s = sin(radians(angle))
        def func(x, y):
            return (x * c - y * s, y * c + x * s)
        return self.getTransform(func)


    def getSVGElementString(self):
        path_str = ''
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
        head_down_height = kwargs.pop('head_down_height', 1)
        head_up_speed = kwargs.pop('head_up_speed', 800)
        head_down_speed = kwargs.pop('head_down_speed', 500)
        move_speed = kwargs.pop('move_speed', 300)
        # bed_max_x = kwargs.pop('bed_max_x', 200)
        # bed_max_y = kwargs.pop('bed_max_y', 200)

        for points in self.path:
            gcode_str += "G0 Z%0.1f F" % (head_up_height) + str(head_up_speed) + "\n"
            gcode_str += "G0 X%0.1f Y%0.1f\n" % (points[0][0], points[0][1]) 
            gcode_str += "G1 Z%0.1f F" % (head_down_height) + str(head_down_speed) +"\n"

            first = True
            for x,y in points[1:]:
                # if x > 0 and x < bed_max_x and y > 0 and y < bed_max_y:  
                gcode_str += "G1 X%0.1f Y%0.1f" % (x, y)
                if first:
                    gcode_str += " F" + str(move_speed)
                    first = False
                gcode_str += '\n'

        gcode_str += "G0 Z%0.1f\n" % (head_up_height)
        return  gcode_str
            
