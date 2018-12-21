#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite
from .AxiSurface import AxiSurface

from .draw import *

from .Line import Line
from .Rectangle import Rectangle
from .Circle import Circle
from .Polyline import Polyline
from .Path import Path
from .Texture import Texture

STROKE_WIDTH = 0.2

def child(parent, name):
    if isinstance(parent, AxiSurface):
        parent = parent.body
    
    return parent.add( svgwrite.container.Group(id=name, fill='none', stroke='black', stroke_width=STROKE_WIDTH) )

def add(parent, element):
    if isinstance(parent, AxiSurface):
        parent = parent.body

    if isinstance(element, Line):
        line(parent, element.start, element.end)
    elif isinstance(element, Rectangle):
        rect(parent, element.center, element.size)
    elif isinstance(element, Circle):
        circle(parent, element.center, element.radius)
    elif isinstance(element, Polyline):
        polyline(parent, element.points)
    elif isinstance(parent, Texture):
        path(parent, element.toPaths(parent.width, parent.height))
