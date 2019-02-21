#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement
from .tools import polar2xy, remap

class Circle(AxiElement):
    def __init__( self, center, radius, **kwargs ):
        AxiElement.__init__(self, **kwargs)

        self._center = np.array(center)
        self._radius = radius

        # Optative
        resolution = radius
        if isinstance(radius, list):
            resolution = max(radius[0], radius[1])

        resolution = remap(resolution, 1.0, 300.0, 12.0, 200.0)
        self.open_angle = kwargs.pop('open_angle', 0)
        self.resolution = kwargs.pop('resolution', int(resolution))


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


    def inside( self, pos ):
        dist = math.hypot(pos[0]-self.center[0], pos[1]-self.center[1])
        return dist < self.radius


    def getPoints(self, **kwargs):
        rx, ry = self.radius
        cx, cy = self.center
        resolution = kwargs.pop('resolution', self.resolution)
        
        points = []
        deg = 0.0
        deg = self.open_angle * 0.5
        step = 360.0/resolution
        for i in range(int(resolution)+1):
            if deg > 360 - self.open_angle * 0.5:
                break
            a = math.radians(deg + self.rotate)
            points.append([ cx + math.cos(a) * rx,
                            cy + math.sin(a) * ry ])
            deg += step

        return points


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
                path.append( Circle([cx, cy],[rad_x, rad_y], fill=self.fill, open_angle=self.open_angle, rotate=self.rotate).getPoints() )
                rad_x = max(rad_x - self.head_width, rad_x_target)
                rad_y = max(rad_y - self.head_width, rad_y_target)

        else:
            path.append(self.getPoints())

        return Path(path)


    # def getSVGElementString(self):
    #     path_str = ''

    #     def path_gen(cx, cy, rx, ry):
    #         d = ''
    #         if self.open_angle != 0:
    #             posA = polar2xy([cx, cy], self.rotate + self.open_angle * 0.5, [rx, ry])
    #             posB = polar2xy([cx, cy], self.rotate + 360 - self.open_angle * 0.5, [rx, ry])
    #             args = {
    #                 'x0':posA[0], 
    #                 'y0':posA[1], 
    #                 'xradius': rx, 
    #                 'yradius': ry, 
    #                 'ellipseRotation':0,
    #                 'x1':posB[0], 
    #                 'y1':posB[1]
    #             }

    #             d = "M %(x0)f,%(y0)f A %(xradius)f,%(yradius)f%(ellipseRotation)f 1,1 %(x1)f,%(y1)f"%args
    #         else:
    #             d = 'M' + str(cx - rx) + ',' + str(cy)
    #             d += 'a' + str(rx) + ',' + str(ry) + ' 0 1,0 ' + str(2 * rx) + ',0'
    #             d += 'a' + str(rx) + ',' + str(ry) + ' 0 1,0 ' + str(-2 * rx) + ',0'
    #         return d

    #     cx, cy = self.center
    #     rx, ry = self.radius

    #     path_str = ''
    #     if self.stroke_width > self.head_width or self.fill:
    #         rad_x = rx + (self.stroke_width * self.head_width) * 0.5
    #         rad_y = ry + (self.stroke_width * self.head_width) * 0.5
    #         rad_x_target = rx - (self.stroke_width * self.head_width) * 0.5
    #         rad_y_target = ry - (self.stroke_width * self.head_width) * 0.5

    #         if self.fill:
    #             rad_x_target = 0.0
    #             rad_y_target = 0.0

    #         while rad_x > rad_x_target or rad_y > rad_y_target:
    #             path_str += path_gen(cx, cy, rad_x, rad_y)
    #             rad_x = max(rad_x - self.head_width, rad_x_target)
    #             rad_y = max(rad_y - self.head_width, rad_y_target)

    #     else:
    #         path_str += path_gen(cx, cy, rx, ry)

    #     svg_str = '<path '
    #     if self.id != None:
    #         svg_str += 'id="' + self.id + '" '
    #     svg_str += 'd="' + path_str + '" '
    #     svg_str += 'fill="none" stroke="black" stroke-width="'+str(self.head_width) + '" '
    #     svg_str += '/>\n'
        
    #     return svg_str
