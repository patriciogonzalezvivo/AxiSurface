#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite
from xml.dom.minidom import parse

STROKE_WIDTH = 0.2

def dom2dict(element):
    """Converts DOM elements to dictionaries of attributes."""
    keys = list(element.attributes.keys())
    values = [val.value for val in list(element.attributes.values())]
    return dict(list(zip(keys, values)))

def calcStrokeWidth(transform_str):
    transform_substrs = transform_str.split(')')[:-1]

    def getMult(transform_substr):
        type_str, value_str = transform_substr.split('(')
        value_str = value_str.replace(',', ' ')
        values = list(map(float, filter(None, value_str.split(' '))))

        if 'scale' in transform_substr:
            x_scale = values[0]
            y_scale = values[1] if (len(values) > 1) else x_scale

            return max(abs(x_scale), abs(y_scale))

        return 1.0

    width = 1.0
    for substr in transform_substrs:
        width *= getMult(substr)
    
    return 1.0/width

def parseGroup(parent, group):
    att = dom2dict(group)
    # print(att)
    
    if 'transform' in att:
        transform_str = att['transform']
        parent.attribs['transform'] = transform_str
        
    for el in group.childNodes:
        if el.nodeName == "metadata":
            continue
        elif el.nodeName == "#text":
            continue
        elif el.nodeName == "g":
            g = parent.add( svgwrite.container.Group() )
            parseGroup(g, el)
        elif el.nodeName == "path":
            el_att = dom2dict(el)
            parent.add( svgwrite.path.Path( d=el_att['d'], stroke_width=calcStrokeWidth(transform_str)) )
        else:
            print(el.nodeName + " is no to be implemented")
        


def parseSVG( surface, filename ):
    doc = parse(filename)
    doc.nodeValue

    svg = doc.getElementsByTagName('svg')[0]
    svg_att = dom2dict(svg) 
    viewBox = svg_att['viewBox'].split()
    width = float(viewBox[2])
    height = float(viewBox[3])
    transform = 'scale(' + str((1.0/width) * surface.width) + ',' + str((1.0/height) * surface.height) + ')'
    stroke_width = max(width/surface.width, height/surface.height ) * 0.2

    root = surface.body.add( svgwrite.container.Group(id=filename, fill='none', stroke='black', stroke_width=stroke_width, transform=transform ) )
    parseGroup( root, svg )
