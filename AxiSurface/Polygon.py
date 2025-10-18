#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
from .Polyline import Polyline
from .tools import pointInside

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

            elif isinstance(points, str):
                self.setFromString(points)
                
            else:
                self.points = points
                self.anchor = kwargs.pop('anchor', [0.0, 0.0]) 

            if holes != None:
                for hole in holes:
                    self.addHole(hole)
                
            # Close it manually 
            self.setClosed(True)


    def addHole(self, points):
        if len(points) > 2:
            if isinstance(points, Polyline):
                points.setClosed(True)
                self.holes.append( points )
            else:
                self.holes.append( Polyline(points, close=True) )
        else:
            print("Polygon.addHole(): Not enough points for a hole", points)

    
    def inside( self, pos ):
        if pointInside( pos, self.getPoints() ):
            in_hole = 0
            for hole in self.holes:
                if hole.inside(pos):
                    in_hole += 1
            if in_hole == 0:
                return True

        return False

