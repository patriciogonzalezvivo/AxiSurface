#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
from .Polyline import Polyline

class Polygon(Polyline):
    def __init__( self, points=None, holes=None, **kwargs):
        Polyline.__init__(self, **kwargs);
        self.holes = []
        self.points = []

        if points != None:
            
            if isinstance(points, Polyline):
                self.points = points.points

                self.translate = kwargs.pop('translate',points.translate)
                self.scale = kwargs.pop('scale', points.scale)
                self.rotate = kwargs.pop('rotate', points.rotate)
                self.stroke_width = kwargs.pop('stroke_width', points.stroke_width)
                self.head_width = kwargs.pop('head_width', points.head_width)
                self.fill = kwargs.pop('fill', points.fill)

                self.anchor = kwargs.pop('anchor', points.anchor) 
            elif isinstance(points, Polygon):
                self.points = points.points
                self.holes = points.holes

                self.translate = kwargs.pop('translate',points.translate)
                self.scale = kwargs.pop('scale', points.scale)
                self.rotate = kwargs.pop('rotate', points.rotate)
                self.stroke_width = kwargs.pop('stroke_width', points.stroke_width)
                self.head_width = kwargs.pop('head_width', points.head_width)
                self.fill = kwargs.pop('fill', points.fill)

                self.anchor = kwargs.pop('anchor', points.anchor) 
            else:
                self.points = points

                self.anchor = kwargs.pop('anchor', [0.0, 0.0]) 

            if holes != None:
                for hole in holes:
                    self.addHole(hole)
                
            # Close it manually 
            if self.points[0][0] != self.points[-1][0] or self.points[0][1] != self.points[-1][1]:
                self.points.append(self.points[0])
            self.isClosed = False

            self._updateCache()


    def addHole(self, points):
        if len(points) > 2:
            if isinstance(points, Polyline):
                self.holes.append( points )
            else:
                self.holes.append( Polyline(points) )
            
            # Must be close
            if self.holes[-1][0][0] != self.holes[-1][-1][0] or self.holes[-1][0][1] != self.holes[-1][-1][1]:
                self.holes[-1].points.append( self.holes[-1].points[0] )
            self.holes[-1].isClosed = False
        else:
            print("Polygon.addHole(): Not enough points for a hole", points)

