#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .Element import Element

# From SVG PathTools by Mat Handy
# https://github.com/mathandy/svgpathtools/blob/master/svgpathtools/path.py#L1238

class CubicBezier(Element):
    def __init__( self, start, control1, control2, end, **kwargs):
        Element.__init__(self, **kwargs)

        self._start = np.array(start)
        self._control1 = np.array(control1)
        self._control2 = np.array(control2)
        self._end = np.array(end)

        self.resolution = kwargs.pop('resolution', 100)

    
    @property
    def start(self):
        start = self._start
        if self.isTransformed:
            center = self._start + (self._end - self._start) * 0.5
            start = transform(start, translate=self.translate, rotate=self.rotate, scale=self.scale, anchor=center)
        return start


    @property
    def control1(self):
        control1 = self._control1
        if self.isTransformed:
            center = self._start + (self._control1 - self._start) * 0.5
            control1 = transform(control1, translate=self.translate, rotate=self.rotate, scale=self.scale, anchor=center)
        return control1


    @property
    def control2(self):
        control2 = self._control2
        if self.isTransformed:
            center = self._control2 + (self._end - self._control2) * 0.5
            control2 = transform(control2, translate=self.translate, rotate=self.rotate, scale=self.scale, anchor=center)
        return control2


    @property
    def end(self):
        end = self._end
        if self.isTransformed:
            center = self._start + (self._end - self._start) * 0.5
            end = transform(end, translate=self.translate, rotate=self.rotate, scale=self.scale, anchor=center)
        return end


    def getPointPct(self, t):
        """Evaluate the cubic Bezier curve at t using Horner's rule."""
        # algebraically equivalent to
        # P0*(1-t)**3 + 3*P1*t*(1-t)**2 + 3*P2*(1-t)*t**2 + P3*t**3
        # for (P0, P1, P2, P3) = self.bpoints()
        return self.start + t*(
            3*(self.control1 - self.start) + t*(
                3*(self.start + self.control2) - 6*self.control1 + t*(
                    -self.start + 3*(self.control1 - self.control2) + self.end
                )))


    def getPoints(self, **kwargs):

        # resolution = max(rx, ry)
        # resolution = int(remap(resolution, 0.0, 180.0, 12.0, 180.0))
        resolution = kwargs.pop('resolution', self.resolution)

        points = []
        step = 1.0/float(resolution)
        for i in range(int(resolution+1)):
            points.append(self.getPointPct( float(i) * step ))

        return points