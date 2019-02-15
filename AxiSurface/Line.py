#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .AxiElement import AxiElement
from .tools import linesIntersection, perpendicular, transform

class Line(AxiElement):
    def __init__( self, start, end, **kwargs):
        AxiElement.__init__(self, **kwargs);
        self.start = np.array(start)
        self.end = np.array(end)


    def getCenter(self):
        return  self.translate + self.start + (self.end - self.start) * 0.5
        

    def getLength(self):
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
        

    def getStart(self):
        start = self.start

        if self.rotate != 0 or self.scale != 1:
            center = self.start + (self.end - self.start) * 0.5
            start = transform(start, rotate=self.rotate, scale=self.scale, anchor=center)

        return [start[0] + self.translate[0], start[1] + self.translate[1]] 


    def getEnd(self):
        end = self.end

        if self.rotate != 0 or self.scale != 1:
            center = self.start + (self.end - self.start) * 0.5
            end = transform(end, rotate=self.rotate, scale=self.scale, anchor=center)

        return [end[0] + self.translate[0], end[1] + self.translate[1]]


    def intersect(self, line):
        return linesIntersection(self.getStart(), self.getEnd(), line.start, line.end )


    def getPath(self):
        path = []

        A = self.getStart()
        B = self.getEnd()

        if self.stroke_width > self.head_width:
            passes = self.stroke_width / self.head_width
            perp = perpendicular(A, B)
            perp_step = perp * self.head_width
            for i in range(int(-passes/2), int(passes/2) ):
                path.append([ [ A[0] + perp_step[0] * i, A[1] + perp_step[1] * i ], 
                              [ B[0] + perp_step[0] * i, B[1] + perp_step[1] * i ] ])
        else:
            path.append([A, B])

        return path


    def getPathString(self):
    
        def path_gen(points):
            return 'M' + 'L'.join('{0} {1}'.format(x,y) for x,y in points)

        path = self.getPath()
        path_str = ''

        for poly in path:
            path_str += path_gen( poly )

        return path_str
        

