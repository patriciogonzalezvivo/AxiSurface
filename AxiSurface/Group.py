#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .AxiElement import AxiElement

from .Line import Line
from .Arc import Arc
from .Circle import Circle
from .Rectangle import Rectangle
from .Hexagon import Hexagon
from .Polyline import Polyline
from .Text import Text

class Group(AxiElement):
    def __init__( self, id="None", **kwargs ):
        AxiElement.__init__(self, **kwargs);

        self.id = id
        self.elements = []
        self.subgroup = { } 

    def line(self, start_pos, end_pos, **kwargs):
        self.elements.append( Line(start_pos, end_pos, **kwargs) )

    def arc(self, start_pos, end_pos, radius, **kwargs):
        self.elements.append( Arc(start_pos, end_pos, radius, **kwargs) )

    def circle(self, center, radius, **kwargs):
        self.elements.append( Circle(center, radius, **kwargs) )

    def rect(self, center, size, **kwargs):
        self.elements.append( Rectangle(center, size, **kwargs) )

    def hex(self, center, radius, **kwargs):
        self.elements.append( Hexagon( center, radius, **kwargs) )

    def poly(self, points, **kwargs):
        self.elements.append( Polyline(points, **kwargs) )

    def text(self, text, **kwargs):
        self.elements.append( Text(text, **kwargs) )

    def group(self, group_id):
        g = Group(group_id)
        self.elements.append( g )
        self.subgroup[group_id] = g

    def getPathString(self):
        d = ''
        for el in self.elements:
            d += el.getPathString()
        return d

