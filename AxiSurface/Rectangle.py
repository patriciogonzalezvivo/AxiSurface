#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement

class Rectangle(AxiElement):
    def __init__( self, center, size, **kwargs ):
        AxiElement.__init__(self, **kwargs);
        self._center = np.array(center)
        self.size = size
        # self.size[0] = float(kwargs.pop('width', size[0]))
        # self.size[1] = float(kwargs.pop('height', size[1]))


    def inside( self, pos ):
        if self.isTransformed:
            return AxiElement.inside(self, pos, self.getPoints() )
        elif (pos[0] > self.center[0] - self.size[0] * 0.5) and (pos[0] < self.center[0] + self.size[0] * 0.5):
            if (pos[1] > self.center[1] - self.size[1] * 0.5) and (pos[1] < self.center[1] + self.size[1] * 0.5):
                return True

        return False


    @property
    def center(self):
        return self._center + self.translate


    @property
    def width(self):
        if isinstance(self.size, tuple) or isinstance(self.size, list):
            return self.size[0]
        else:
            return self.size

    @property
    def height(self):
        if isinstance(self.size, tuple) or isinstance(self.size, list):
            return self.size[1]
        else:
            return self.size


    @property
    def radius(self):
        rx = self.width * 0.5
        ry = self.height * 0.5

        rx = math.sqrt( rx * rx + ry * ry )
        ry = rx

        if isinstance(self.scale, tuple) or isinstance(self.scale, list):
            rx *= self.scale[0]
            ry *= self.scale[1]
        else:
            rx *= self.scale
            ry *= self.scale

        return [rx, ry]


    def getCoorners(self):
        cx, cy = self.center
        rx, ry = self.radius

        x = self.width * 0.5
        y = self.height * 0.5

        coorners = [ [1.0,1.0], [1.0,-1.0], [-1.0,-1.0], [-1.0,1.0] ]

        points = []
        for i in range(0, 4):
            a = math.atan2( y * coorners[i][1], x * coorners[i][0] )
            points.append( [cx + rx * math.cos(a), cy + ry * math.sin(a)] )
        return points


    def getPoints(self):
        points = self.getCoorners()
        points.append(points[0])
        return points


    def getOffset(self, offset):
        return Rectangle( self.center, size=[self.width + offset, self.height + offset], stroke_width=self.stroke_width, head_width=self.head_width )


    def getBuffer(self, offset):
        if offset <= 0:
            import copy
            return copy.copy(self)

        return self.getOffset(offset)


    def getStrokePath(self, **kwargs):
        from .Path import Path
        
        cx, cy = self.center

        path = []
        if self.stroke_width > self.head_width or self.fill:
            width = self.width + (self.stroke_width * self.head_width)
            height = self.height + (self.stroke_width * self.head_width)
            width_target = self.width - (self.stroke_width * self.head_width)
            height_target = self.height - (self.stroke_width * self.head_width)

            while width > width_target or height > height_target:
                path.append( Rectangle([cx, cy], [width, height], fill=self.fill, rotate=self.rotate).getPoints() )
                width = max(width - self.head_width * 2.0, width_target)
                height = max(height - self.head_width * 2.0, height_target)

        else:
            path.append( self.getPoints() )
        return Path(path)

    
    def getFillPath(self, **kwargs):
        from .Path import Path
        
        cx, cy = self.center
        rx, ry = self.radius 

        path = []
        if self.stroke_width > self.head_width or self.fill:
            width = self.width - (self.stroke_width * self.head_width)
            height = self.height - (self.stroke_width * self.head_width)

            width_target = 0.0
            height_target = 0.0

            while width > width_target or height > height_target:
                path.append( Rectangle([cx, cy], [width, height], fill=self.fill, rotate=self.rotate).getPoints() )
                width = max(width - self.head_width * 2.0, width_target)
                height = max(height - self.head_width * 2.0, height_target)

        else:
            path.append( self.getPoints() )
        return Path(path)


    # def getPathString(self):
        
    #     def path_gen(**kwargs):
    #         points = self.getPoints(**kwargs)
    #         return 'M' + 'L'.join('{0} {1}'.format(x,y) for x,y in points)

    #     path_str = ''
    #     if self.stroke_width > self.head_width or self.fill:

    #         if isinstance(self.size, tuple) or isinstance(self.size, list):
    #             rx = self.size[0] * 0.5
    #             ry = self.size[1] * 0.5
    #         else:
    #             rx = self.size * 0.5
    #             ry = self.size * 0.5

    #         if isinstance(self.scale, tuple) or isinstance(self.scale, list):
    #             rx *= self.scale[0]
    #             ry *= self.scale[1]
    #         else:
    #             rx *= self.scale
    #             ry *= self.scale

    #         w = rx + (self.stroke_width * self.head_width) * 0.5
    #         h = ry + (self.stroke_width * self.head_width) * 0.5

    #         w_target = rx - (self.stroke_width * self.head_width) * 0.5
    #         h_target = ry - (self.stroke_width * self.head_width) * 0.5

    #         if self.fill:
    #             w_target = 0
    #             h_target = 0

    #         while w > w_target or h > h_target:
    #             path_str += path_gen( size_offset=[w - rx, h - ry] )
    #             w = max(w - self.head_width, w_target)
    #             h = max(h - self.head_width, h_target)
    #     else:
    #         path_str += path_gen()
    #     return path_str