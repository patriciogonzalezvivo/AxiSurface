#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement

def rect_coorner(center, radius, i, angle_offset = 0):
    angle_deg = angle_offset + 90.0 * i - 45.0
    angle_rad = math.pi / 180.0 * angle_deg
    return [center[0] + radius[0] * math.cos(angle_rad), center[1] + radius[1] * math.sin(angle_rad)]


class Rectangle(AxiElement):
    def __init__( self, center, size, **kwargs ):
        AxiElement.__init__(self, **kwargs);
        self.center = np.array(center)
        self.size = size


    def inside( self, pos ):
        if (pos[0] > self.center[0] - self.size[0] * 0.5) and (pos[0] < self.center[0] + self.size[0] * 0.5):
            if (pos[1] > self.center[1] - self.size[1] * 0.5) and (pos[1] < self.center[1] + self.size[1] * 0.5):
                return True

        return False


    def inside( self, pos ):
        points = self.getPoints()
        return pointInside( pos, self.points )


    def getCenter(self):
        return self.center + self.translate

    
    def getRadius(self):
        rx, ry = 1.0, 1.0

        if isinstance(self.size, tuple) or isinstance(self.size, list):
            rx = self.size[0] * 0.5
            ry = self.size[1] * 0.5
        else:
            rx = self.size * 0.5
            ry = self.size * 0.5

        if isinstance(self.scale, tuple) or isinstance(self.scale, list):
            rx *= self.scale[0]
            ry *= self.scale[1]
        else:
            rx *= self.scale
            ry *= self.scale

        return [rx, ry]


    def getCoorners(self, **kwargs):
        cx, cy = self.getCenter()
        rx, ry = self.getRadius()

        size_offset = kwargs.pop('size_offset', [0, 0])
        if isinstance(size_offset, tuple) or isinstance(size_offset, list):
            rx += size_offset[0]
            ry += size_offset[1]
        else:
            rx += size_offset
            ry += size_offset

        points = []
        for i in range(0, 4):
            points.append( rect_coorner([cx, cy], [rx, ry], i, self.rotate) )
        return points


    def getPoints(self, **kwargs ):
        points = self.getCoorners(**kwargs)
        points.append(points[0])
        return points


    def getPathString(self):
        
        def path_gen(**kwargs):
            points = self.getPoints(**kwargs)
            return 'M' + 'L'.join('{0} {1}'.format(x,y) for x,y in points)

        path_str = ''
        if self.stroke_width > 1 or self.fill:

            if isinstance(self.size, tuple) or isinstance(self.size, list):
                rx = self.size[0] * 0.5
                ry = self.size[1] * 0.5
            else:
                rx = self.size * 0.5
                ry = self.size * 0.5

            if isinstance(self.scale, tuple) or isinstance(self.scale, list):
                rx *= self.scale[0]
                ry *= self.scale[1]
            else:
                rx *= self.scale
                ry *= self.scale

            w = rx + (self.stroke_width * self.head_width) * 0.5
            h = ry + (self.stroke_width * self.head_width) * 0.5

            w_target = rx - (self.stroke_width * self.head_width) * 0.5
            h_target = ry - (self.stroke_width * self.head_width) * 0.5

            if self.fill:
                w_target = 0
                h_target = 0

            while w > w_target or h > h_target:
                path_str += path_gen( size_offset=[w - rx, h - ry] )
                w = max(w - self.head_width, w_target)
                h = max(h - self.head_width, h_target)
        else:
            path_str += path_gen()
        return path_str