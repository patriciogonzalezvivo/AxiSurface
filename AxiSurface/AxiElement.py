#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .Bbox import Bbox
from .tools import pointInside

class AxiElement(object):
    def __init__(self, **kwargs):
        self.head_width = kwargs.pop('head_width', 0.2)
        self.stroke_width = kwargs.pop('stroke_width', self.head_width)
        self.fill = kwargs.pop('fill', False)

        self.translate = kwargs.pop('translate', np.array([0, 0]) )
        self.rotate = kwargs.pop('rotate', 0.0)
        self.scale = kwargs.pop('scale', 1.0)
        self.id = kwargs.pop('id', None)

    @property
    def isTranformed(self):
        return self.translate[0] != 0.0 or self.translate[1] != 0.0 or self.scale != 1.0 or self.rotate != 0.0


    def inside( self, pos ):
        return pointInside( pos, self.getPoints() )

    
    def getPoints(self):
        print('getPoints(): Function not declare')
        return []


    def getPath(self):
        print('getPath(): Function not declare')
        return []

    @property
    def bounds(self):
        return Bbox( points=self.getPoints() )


    def getSVGElementString(self):
        return self.getPath().getSVGElementString()


