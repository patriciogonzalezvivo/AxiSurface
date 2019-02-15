#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .AxiElement import AxiElement
from .Bbox import Bbox
from .tools import linesIntersection, perpendicular, transform

class Line(AxiElement):
    def __init__( self, start, end, **kwargs):
        AxiElement.__init__(self, **kwargs);
        self._start = np.array(start)
        self._end = np.array(end)


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


    def intersect(self, line):
        return linesIntersection(self.getStart(), self.getEnd(), line._start, line._end )


    def getPoints(self):
        return [self.getStart(), self.getEnd()]

    
    def getBbox(self):
        return Bbox( points=self.getPoints() )


    def getPath(self):
        path = []
        A = self.start
        B = self.end
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

