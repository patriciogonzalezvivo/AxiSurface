#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .AxiElement import AxiElement
from .Polyline import Polyline
from .Path import Path
from .Bbox import Bbox
from .hershey_fonts import *
from .tools import transform

class Text(AxiElement):
    def __init__( self, text, center, **kwargs ):
        AxiElement.__init__(self, **kwargs);
        self.text = str(text)
        self._center = center

        self.font =  kwargs.pop('font', FUTURAL)
        self.spacing =  kwargs.pop('spacing', 0)
        self.extra =  kwargs.pop('extra', 0)


    @property
    def center(self):
        return self._center + self.translate


    @property
    def length(self):
        x = 0
        for ch in self.text:
            index = ord(ch) - 32
            if index < 0 or index >= 96:
                x += self.spacing
                continue

            lt, rt, coords = self.font[index]
            x += rt - lt + self.spacing

        if isinstance(self.scale, tuple) or isinstance(self.scale, list):
            x *= self.scale[0]
        else:
            x *= self.scale

        return x


    def getPolylines(self, **kwargs):
        # Based on hershey implementation by Michael Fogleman https://github.com/fogleman/axi/blob/master/axi/hershey.py
        result = []

        bbox = Bbox()

        x = 0
        for ch in self.text:
            index = ord(ch) - 32
            if index < 0 or index >= 96:
                x += self.spacing
                continue

            lt, rt, coords = self.font[index]
            for path in coords:
                path = [ (x + i - lt, j) for i, j in path]
                if path:
                    line = Polyline(path)
                    bbox.join( line.bounds )
                    result.append( line )
            x += rt - lt + self.spacing
            if index == 0:
                x += self.extra

        toCenter = transform(bbox.center, rotate=self.rotate, scale=self.scale)
        stroke_width = kwargs.pop('stroke_width', self.stroke_width )

        translate = [ self.center[0] - toCenter[0], self.center[1] - toCenter[1] ]

        polys = []
        for line in result:
            points = []
            for point in line.points:
                points.append( transform(point, translate=translate, rotate=self.rotate, scale=self.scale) )
            polys.append( Polyline(points, stroke_width=stroke_width) )
            # result[i].translate = translate
            # result[i].scale = self.scale
            # result[i].rotate = self.rotate
            # result[i].origin = bbox.center
            # result[i].stroke_width = stroke_width

        len(polys)
       
        return polys


    def getPoints(self):
        points = []
        polys = self.getPolylines( stroke_width=self.head_width )

        for poly in polys:
            points.extend( poly.getPoints() )
        return points


    def _toShapelyGeom(self):
        try:
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('To convert a Text to a Shapely MultiPolygon requires shapely. Try: pip install shapely')

        polys = self.getPolylines( stroke_width=self.head_width )
        polygons = []
        for poly in polys:
            polygons.append( poly._toShapelyLineString() )

        return geometry.MultiPolygons( polygons )


    def getBuffer(self, offset):
        if offset <= 0.0:
            return copy.copy(self)

        from .Polygon import Polygon

        polys = self.getPolylines( stroke_width=self.head_width )
        polygons = []
        for poly in polys:
            polygons.append( poly._toShapelyLineString().buffer(offset) )

        from shapely.ops import cascaded_union

        buf = cascaded_union(polygons)
        path = Path()
        for ring in buf:
            path.add( Polygon( list(ring.exterior.coords) ) )

        return path
        

    def getStrokePath(self, **kwargs):
        path = Path()
        polys = self.getPolylines(**kwargs)

        for poly in polys:
            path.add( poly.getStrokePath(**kwargs) )

        return path


    