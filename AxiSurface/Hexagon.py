#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement

class Hexagon(AxiElement):
    def __init__( self, center, radius, **kwargs):
        AxiElement.__init__(self, **kwargs)
        self._center = np.array(center)
        self._radius = radius


    @property
    def center(self):
        return self._center + self.translate
        

    @property
    def radius(self):
        if isinstance(self._radius, tuple) or isinstance(self._radius, list):
            rx = self._radius[0]
            ry = self._radius[1]
        else:
            rx = self._radius
            ry = self._radius
        
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

        points = []
        for i in range(0, 6):
            a = math.radians( self.rotate + 60.0 * i - 30.0 )
            points.append( [cx + rx * math.cos(a), cy + ry * math.sin(a)] )
        return points


    def getPoints(self):
        points = self.getCoorners()
        points.append(points[0])
        return points


    def getBuffer(self, offset):
        if offset <= 0:
            import copy
            return copy.copy(self)
            
        return Hexagon( self.center, [self.radius[0] + offset, self.radius[1] + offset], stroke_width=self.stroke_width, head_width=self.head_width )


    def getPath(self):
        from .Path import Path

        cx, cy = self.center
        rx, ry = self.radius

        path = []
        if self.stroke_width > self.head_width or self.fill:
            rad_x = rx + (self.stroke_width * self.head_width) * 0.5
            rad_y = ry + (self.stroke_width * self.head_width) * 0.5
            rad_x_target = rx - (self.stroke_width * self.head_width) * 0.5
            rad_y_target = ry - (self.stroke_width * self.head_width) * 0.5

            if self.fill:
                rad_x_target = 0.0
                rad_y_target = 0.0

            while rad_x > rad_x_target or rad_y > rad_y_target:
                path.append( Hexagon([cx, cy], [rad_x, rad_y], fill=self.fill, rotate=self.rotate).getPoints() )
                rad_x = max(rad_x - self.head_width, rad_x_target)
                rad_y = max(rad_y - self.head_width, rad_y_target)

        else:
            path.append(self.getPoints())
        return Path(path)


    # def getPathString(self):

    #     def path_gen(**kwargs):
    #         points = self.getPoints(**kwargs)
    #         return 'M' + 'L'.join('{0} {1}'.format(x,y) for x,y in points)

        
    #     rx, ry = self.radius

    #     path_str = ''
    #     if self.stroke_width > self.head_width or self.fill:
    #         rx, ry = self.radius

    #         rx_delta = rx + (self.stroke_width * self.head_width) * 0.5
    #         rx_target = rx - (self.stroke_width * self.head_width) * 0.5
    #         ry_delta = ry + (self.stroke_width * self.head_width) * 0.5
    #         ry_target = ry - (self.stroke_width * self.head_width) * 0.5
            
    #         if self.fill:
    #             ry_target = 0.0
    #             rx_target = 0.0

    #         while rx_delta > rx_target or ry_delta > ry_target:
    #             path_str += path_gen(radius_offset=[rx_delta - rx , ry_delta - ry])
    #             rx_delta = max(rx_delta - self.head_width, rx_target)
    #             ry_delta = max(ry_delta - self.head_width, ry_target)
    #     else:
    #         path_str += path_gen()
    #     return path_str