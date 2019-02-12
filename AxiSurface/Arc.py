#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .AxiElement import AxiElement
from .tools import linesIntersection

class Arc(AxiElement):
    def __init__( self, start, end, radius, **kwargs):
        AxiElement.__init__(self, **kwargs);

        self.start = np.array(start)
        self.end = np.array(end)
        self.radius = radius

    def intersect(self, line):
        # TODO:
        #    - FIX THIS! Only aplicable for lines
        return linesIntersection(self.start, self.end, line.start, line.end )


    def getPathString(self):
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
        return d

