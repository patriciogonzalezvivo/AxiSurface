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
from .Polygon import Polygon
from .Text import Text
from .Path import Path
from .Texture import Texture

from .tools import dom2dict

class Group(AxiElement):
    def __init__( self, id="Untitle", **kwargs ):
        AxiElement.__init__(self, **kwargs);

        self.id = id
        self.elements = []
        self.subgroup = { } 

    def __iter__(self):
        self._index = 0
        return self


    def __next__(self):
        if self._index < len(self.elements):
            result = self[ self._index ]
            self._index += 1
            return result
        else:
            raise StopIteration


    def next(self):
        return self.__next__()


    def __getitem__(self, index):
        if type(index) is int:
            return self.elements[index]
        else:
            return None


    def add(self, element ):
        element.parent = self
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


    def polyline(self, points, **kwargs):
        return self.add( Polyline(points, **kwargs) )


    def polygon(self, points, **kwargs):
        return self.add( Polygon(points, **kwargs) )


    def path(self, path, **kwargs):
        return self.add( Path(path, **kwargs) )


    def text(self, text, center, **kwargs):
        return self.add( Text(text, center, **kwargs) )


    def texture(self, texture, **kwargs):
        return self.add( Texture(texture, **kwargs) )


    def group(self, group_id, **kwargs):
        g = Group(group_id, **kwargs)
        self.subgroup[group_id] = g
        return self.add( g )


    def getPoints(self):
        points = []
        for el in self.elements:
            points.extend( el.getPoints() )
        return points


    def getPath(self, **kwargs):
        import copy

        path = Path()
        for el in self.elements:
            if isinstance(el, Path ):
                path.add( el )
            else:
                if len(kwargs.items()) > 0:
                    tmp = copy.copy(el)
                    for key in kwargs:
                        tmp.__dict__[key] = kwargs[key]
                        print(key, tmp.__dict__[key])
                    path.add( tmp.getPath() )
                else:
                    path.add( el.getPath() )
        return path


    def parseSVGNode(self, node):
        att = dom2dict(node)

        # if 'transform' in att:
        #     matrix = parse_transform(att['transform'])
    
        self.id = att.pop('id', self.id)
        self.fill = att.pop('fill', self.fill)
        self.stroke_width = att.pop('stroke_width', self.stroke_width)
            
        for el in node.childNodes:
            if el.nodeName == "metadata":
                continue

            elif el.nodeName == "#text":
                continue

            elif el.nodeName == "g":
                sub_group = self.group("sub_group")
                sub_group.parseSVGNode( el )

            elif el.nodeName == "path":
                el_att = dom2dict(el)
                # print(el_att)

                id = el_att.pop('id', self.id + "_sub")
                fill = el_att.pop('fill', self.fill )
                stroke_width = el_att.pop('stroke-width', self.stroke_width)
                self.path( el_att['d'], id=id, fill=fill, stroke_width=stroke_width)

            else:
                print(el.nodeName + " is no to be implemented")


    def getSVGElementString(self):
        svg_str = '<g '
        if self.id != None:
            svg_str += 'id="' + self.id + '" '
        svg_str += 'fill="none" stroke="black" stroke-width="'+str(self.head_width)+'">'

        for el in self.elements:
            svg_str += el.getSVGElementString()

        svg_str += '</g>'
        
        return svg_str
        

