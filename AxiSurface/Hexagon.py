#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement

def hex_coorner(center, radius, i, angle_offset = 0):
    angle_deg = angle_offset + 60.0 * i - 30.0
    angle_rad = math.pi / 180.0 * angle_deg
    return [center[0] + radius[0] * math.cos(angle_rad), center[1] + radius[1] * math.sin(angle_rad)]


class Hexagon(AxiElement):
    def __init__( self, center, radius, **kwargs):
        AxiElement.__init__(self, **kwargs)
        self.center = center
        self.radius = radius


    def getCenter(self):
        return self.center + self.translate

    
    def getRadius(self):
        rx = self.radius
        ry = self.radius
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

        radius_offset = kwargs.pop('radius_offset', [0, 0])
        if isinstance(radius_offset, tuple) or isinstance(radius_offset, list):
            rx += radius_offset[0]
            ry += radius_offset[1]
        else:
            rx += radius_offset
            ry += radius_offset

        points = []
        for i in range(0, 6):
            points.append( hex_coorner([cx, cy], [rx, ry], i, self.rotate) )
        return points


    def getPoints(self, **kwargs):
        points = self.getCoorners(**kwargs)
        points.append(points[0])
        return points


    def getPathString(self):

        def path_gen(**kwargs):
            points = self.getPoints(**kwargs)
            return 'M' + 'L'.join('{0} {1}'.format(x,y) for x,y in points)

        
        rx, ry = self.getRadius()

        path_str = ''
        if self.stroke_width > 1 or self.fill:
            rx, ry = self.getRadius()

            rx_delta = rx + (self.stroke_width * self.head_width) * 0.5
            rx_target = rx - (self.stroke_width * self.head_width) * 0.5
            ry_delta = ry + (self.stroke_width * self.head_width) * 0.5
            ry_target = ry - (self.stroke_width * self.head_width) * 0.5
            
            if self.fill:
                ry_target = 0.0
                rx_target = 0.0

            while rx_delta > rx_target or ry_delta > ry_target:
                path_str += path_gen(radius_offset=[rx_delta - rx , ry_delta - ry])
                rx_delta = max(rx_delta - self.head_width, rx_target)
                ry_delta = max(ry_delta - self.head_width, ry_target)
        else:
            path_str += path_gen()
        return path_str