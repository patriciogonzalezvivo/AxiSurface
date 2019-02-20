#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

from .AxiElement import AxiElement
from .tools import linesIntersection, distance, xy2polar

class Arc(AxiElement):
    def __init__( self, start, end, radius, **kwargs):
        AxiElement.__init__(self, **kwargs)

        self._start = np.array(start)
        self._end = np.array(end)
        self.resolution = kwargs.pop('resolution', 18)
        self.radius = radius

        # TODO:
        #  -- add getPoints(), getBbox(), getPath()

    @property
    def center(self):
        return  self.start + (self.end - self.start) * 0.5

    
    @property
    def start(self):
        start = self._start
        if self.isTranformed:
            center = self._start + (self._end - self._start) * 0.5
            start = transform(start, translate=self.translate, rotate=self.rotate, scale=self.scale, anchor=center)
        return start


    @property
    def end(self):
        end = self._end
        if self.isTranformed:
            center = self._start + (self._end - self._start) * 0.5
            end = transform(end, translate=self.translate, rotate=self.rotate, scale=self.scale, anchor=center)
        return end


    @property
    def length(self):
        return distance(self.start, self.end)


    def intersect(self, line):
        # TODO:
        #    - FIX THIS! Only aplicable for lines
        return linesIntersection(self.start, self.end, line.start, line.end )


    def getPoints(self):
        rx, ry = self.radius

        cx, cy = self.center
        a0, r0 = xy2polar(self.center, self.start)
        a1, r1 = xy2polar(self.center, self.end)
        
        points = []
        deg = min(a0, a1)
        step = 360.0/self.resolution
        for i in range(int(self.resolution+1)):
            if deg > max(a0, a1):
                break
            a = math.radians(deg + self.rotate)
            points.append([ cx + math.cos(a) * rx,
                            cy + math.sin(a) * ry ])
            deg += step

        return points


    def getSVGElementString(self):
        rx = self.radius[0]
        ry = self.radius[1]
        d = ''
        args = {
            'x0': self.start[0], 
            'y0': self.start[1], 
            'xradius': rx, 
            'yradius': ry, 
            'ellipseRotation':0, #has no effect for circles
            'x1': self.end[0], 
            'y1': self.end[1]
        }
        d = "M %(x0)f,%(y0)f A %(xradius)f,%(yradius)f%(ellipseRotation)f 1,1 %(x1)f,%(y1)f"%args

        svg_str = '<path '
        if self.id != None:
            svg_str += 'id="' + self.id + '" '
        svg_str += 'd="' + d + '" '
        svg_str += 'fill="none" stroke="black" stroke-width="'+str(self.head_width) + '" '
        svg_str += '/>\n'
        
        return svg_str

