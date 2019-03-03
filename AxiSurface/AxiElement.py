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
        self.id = kwargs.pop('id', None)

        self.stroke_width = kwargs.pop('stroke_width', self.head_width)
        self.fill = kwargs.pop('fill', False)

        self.translate = kwargs.pop('translate', np.array([0, 0]) )
        self.rotate = kwargs.pop('rotate', 0.0)
        self.scale = kwargs.pop('scale', 1.0)
        
        self.parent = None

    @property
    def isTranformed(self):
        return self.translate[0] != 0.0 or self.translate[1] != 0.0 or self.scale != 1.0 or self.rotate != 0.0


    def inside( self, pos ):
        return pointInside( pos, self.getPoints() )

    
    def getPoints(self):
        print('getPoints(): Function not declare')
        return []


    def _toShapelyGeom(self):
        try:
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('To convert an Element to a Shapely geometry requires shapely. Try: pip install shapely')

        return geometry.Polygon( self.getPoints() )


    def getBuffer(self, offset):
        if offset <= 0:
            import copy
            return copy.copy(self)
            
        return Polyline( self.getPoints(), stroke_width=self.stroke_width, head_width=self.head_width ).getBuffer(offset)


    def getStrokePath(self, **kwargs ):
        # raise Exception('getPath(): Function not declare. Going with a simple convertion of the getPoints() to a Path')
        from .Path import Path
        return Path([ self.getPoints() ])


    def getFillPath(self, **kwargs ):
        return Path()


    def getPath(self, **kwargs):
        # raise Exception('getPath(): Function not declare. Going with a simple convertion of the getPoints() to a Path')
        from .Path import Path
        path = self.getStrokePath(**kwargs)

        if self.fill:
            path.add( self.getFillPath(**kwargs) )

        return path


    @property
    def bounds(self):
        return Bbox( points=self.getPoints() )


    def getSVGElementString(self):
        return self.getPath().getSVGElementString()


