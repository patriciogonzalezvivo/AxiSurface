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

        self.holes = holes

        if points is None:
            self.points = []
        elif isinstance(points, Polyline):
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

        # Close it manually 
        if self.points[0][0] != self.points[-1][0] or self.points[0][1] != self.points[-1][1]:
            self.points.append(self.points[0])
        self.isClosed = False

        if self.holes == None:
            self.holes = []

        self._updateCache()


    def addHole(self, points):
        if isinstance(points, Polyline):
            self.holes.append( points )
        else:
            self.holes.append( Polyline(points) )
        
        # Must be close
        if self.holes[-1][0][0] != self.holes[-1][-1][0] or self.holes[-1][0][1] != self.holes[-1][-1][1]:
            self.holes[-1].points.append( self.holes[-1].points[0] )
        self.holes[-1].isClosed=False


    def getFillPath(self, **kwargs ):
        # From FlatCam
        # https://bitbucket.org/jpcgt/flatcam/src/46454c293a9b390c931b52eb6217ca47e13b0231/camlib.py?at=master&fileviewer=file-view-default#camlib.py-478
        tooldia = kwargs.pop('tooldia', self.head_width * 2.0 )
        overlap = kwargs.pop('overlap', 0.15 )

        try:
            from .Path import Path
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('Polygon.getFillPath() requires Shapely')

        if len(self.points) < 3:
            return self

        holes=[]
        for hole in self.holes:
            holes.append( Polyline(hole) )
        polygon = geometry.Polygon( self.getPoints(), holes=holes )

         # Can only result in a Polygon or MultiPolygon
        # NOTE: The resulting polygon can be "empty".
        current = polygon.buffer(-tooldia / 2.0)
        if current.area == 0:
            # Otherwise, trying to to insert current.exterior == None
            # into the FlatCAMStorage will fail.
            return None

        path = Path()
        # current can be a MultiPolygon
        try:
            for p in current:
                path.add( Polyline( p.exterior.coords ) )
                for i in p.interiors:
                    path.add( Polyline( i.coords ) )

        # Not a Multipolygon. Must be a Polygon
        except TypeError:
            path.add( Polyline( current.exterior.coords ) )
            for i in current.interiors:
                path.add( Polyline( i.coords ) )

        while True:

            # Can only result in a Polygon or MultiPolygon
            current = current.buffer(-tooldia * (1 - overlap))
            if current.area > 0:

                # current can be a MultiPolygon
                try:
                    for p in current:
                        path.add( Polyline( p.exterior.coords ) )
                        for i in p.interiors:
                            path.add( Polyline( i.coords ) )

                # Not a Multipolygon. Must be a Polygon
                except TypeError:
                    path.add( Polyline( current.exterior.coords ) )
                    for i in current.interiors:
                        path.add( Polyline( i.coords ) )
            else:
                break

        return path


    def getPath(self):
        from .Path import Path

        # TODO:
        #      - Fix stroke_width and head_width on scale

        path = []
        if self.stroke_width > self.head_width:
            r = (self.stroke_width * self.head_width) * 0.5
            r_target = -(self.stroke_width * self.head_width) * 0.5
            while r > r_target:
                path.append( self.getOffset(r).getPoints() )
                r = max(r - self.head_width, r_target)
        else:
            path.append( self.getPoints() )

        path = Path(path)
        if self.fill:
            path.add( self.getFillPath() )

        for poly in self.holes:
            path.add( poly.getPath() )

        return path