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


    def getPathString(self):
        
        def path_gen(A, B):
            d = 'M %(x0)f,%(y0)f L %(x1)f,%(y1)f'%{ 'x0':A[0], 'y0':A[1], 'x1': B[0], 'y1':B[1]}
            return d

        A = self.getStart()
        B = self.getEnd()

        path_str = ''
        if self.stroke_width > 1:
            passes = self.stroke_width / self.head_width
            perp = perpendicular(A, B)
            perp_step = perp * self.head_width

            for i in range(int(-passes/2), int(passes/2) ):
                path_str += path_gen(   [ A[0] + perp_step[0] * i, A[1] + perp_step[1] * i ], 
                                        [ B[0] + perp_step[0] * i, B[1] + perp_step[1] * i ] )
        else:
            path_str = path_gen(A, B)

        return path_str

