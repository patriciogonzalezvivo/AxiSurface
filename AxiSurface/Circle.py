#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement
from .tools import polar2xy

class Circle(AxiElement):
    def __init__( self, center, radius, **kwargs ):
        AxiElement.__init__(self, **kwargs)

        self.center = np.array(center)
        self.radius = radius

        # Optative
        self.open_angle =  kwargs.pop('open_angle', None)

    def inside( self, pos ):
        dist = math.hypot(pos[0]-self.center[0], pos[1]-self.center[1])
        return dist < self.radius

    
    def getCenter(self):
        return self.center + self.translate
        
    
    def getRadius(self):
        if isinstance(self.radius, tuple) or isinstance(self.radius, list):
            rx = self.radius[0]
            ry = self.radius[1]
        else:
            rx = self.radius
            ry = self.radius
        if isinstance(self.scale, tuple) or isinstance(self.scale, list):
            rx *= self.scale[0]
            ry *= self.scale[1]
        else:
            rx *= self.scale
            ry *= self.scale
        return [rx, ry]


    def getPathString(self):

        def path_gen(cx, cy, rx, ry):
            d = ''
            if self.open_angle != None:
                posA = polar2xy([cx, cy], self.rotate + self.open_angle, [rx, ry])
                posB = polar2xy([cx, cy], self.rotate + 360 - self.open_angle, [rx, ry])
                args = {
                    'x0':posA[0], 
                    'y0':posA[1], 
                    'xradius': rx, 
                    'yradius': ry, 
                    'ellipseRotation':0,
                    'x1':posB[0], 
                    'y1':posB[1]
                }

                d = "M %(x0)f,%(y0)f A %(xradius)f,%(yradius)f%(ellipseRotation)f 1,1 %(x1)f,%(y1)f"%args
            else:
                d = 'M' + str(cx - rx) + ',' + str(cy)
                d += 'a' + str(rx) + ',' + str(ry) + ' 0 1,0 ' + str(2 * rx) + ',0'
                d += 'a' + str(rx) + ',' + str(ry) + ' 0 1,0 ' + str(-2 * rx) + ',0'
            return d

        cx, cy = self.getCenter()
        rx, ry = self.getRadius()

        path_str = ''
        if self.stroke_width > self.head_width or self.fill:
            rad_x = rx + (self.stroke_width * self.head_width) * 0.5
            rad_y = ry + (self.stroke_width * self.head_width) * 0.5
            rad_x_target = rx - (self.stroke_width * self.head_width) * 0.5
            rad_y_target = ry - (self.stroke_width * self.head_width) * 0.5

            if self.fill:
                rad_x_target = 0.0
                rad_y_target = 0.0

            while rad_x > rad_x_target or rad_y > rad_y_target:
                path_str += path_gen(cx, cy, rad_x, rad_y)
                rad_x = max(rad_x - self.head_width, rad_x_target)
                rad_y = max(rad_y - self.head_width, rad_y_target)

        else:
            path_str += path_gen(cx, cy, rx, ry)
        return path_str

        

