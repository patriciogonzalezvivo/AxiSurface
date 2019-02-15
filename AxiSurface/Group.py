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
from .Texture import Texture

class Group(AxiElement):
    def __init__( self, id="Untitle", **kwargs ):
        AxiElement.__init__(self, **kwargs);

        self.id = id
        self.elements = []
        self.subgroup = { } 


    def add(self, element ):
        self.elements.append(element)
        return element


    def line(self, start_pos, end_pos, **kwargs):
        return self.add( Line(start_pos, end_pos, **kwargs) )


    def arc(self, start_pos, end_pos, radius, **kwargs):
        return self.add( Arc(start_pos, end_pos, radius, **kwargs) )


    def circle(self, center, radius, **kwargs):
        return self.add( Circle(center, radius, **kwargs) )


    def rect(self, center, size, **kwargs):
        return self.add( Rectangle(center, size, **kwargs) )


    def hex(self, center, radius, **kwargs):
        return self.add( Hexagon( center, radius, **kwargs) )


    def poly(self, points, **kwargs):
        return self.add( Polyline(points, **kwargs) )


    def text(self, text, center, **kwargs):
        return self.add( Text(text, center, **kwargs) )

    def texture(self, texture, **kwargs):
        return self.add( Texture(texture, **kwargs) )


    def group(self, group_id):
        g = Group(group_id)
        self.subgroup[group_id] = g
        return self.add( g )


    def getPathString(self):
        d = ''
        for el in self.elements:
            d += el.getPathString()
        return d


    def getElementString(self):
        svg_str = '<g fill="none" id="' + self.id + '" stroke="black" stroke-width="0.2">'

        for el in self.elements:
            if isinstance(el, Group):
                svg_str += el.getElementString()
            else:
                svg_str += '<path d="' + el.getPathString() + '" />\n'

        svg_str += '</g>'
        
        return svg_str
        

