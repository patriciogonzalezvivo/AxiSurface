#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite
from svgwrite import cm, mm

STROKE_WIDTH = 0.2

class Surface(object):
    def __init__(self, size='A3', scale=1.0):

        if isinstance(size, str):
            if size == 'A4':
                self.width = 210.0
                self.height = 297.0
            elif if size == 'A3':
                self.width = 297.0
                self.height = 420.0
        elif isinstance(size, tuple) or isinstance(size, list):
            if len(size) == 2:
                self.width = size[0]
                self.height = size[1]
        else:
            self.width = float(size)
            self.height = float(size)

        self.scale = scale
        
    self.dwg = svgwrite.Drawing(size=(self.width*mm, self.height*mm))
    self.dwg.viewbox(width=self.width*self.scale, height=self.height*self.scale)
    self.body = dwg.add( svgwrite.container.Group(id='body', fill='none', stroke='black', stroke_width=STROKE_WIDTH) )

    def addGroup( self, name ):
        name = name.replace(" ", "_")
        return self.body.add( svgwrite.container.Group(id=name, fill='none', stroke='black', stroke_width=STROKE_WIDTH) )
        
    def addGroupTo( self, parent, name ):
        name = name.replace(" ", "_")
        return parent.add( svgwrite.container.Group(id=name, fill='none', stroke='black', stroke_width=STROKE_WIDTH) )

    def toSVG( self, filename ):
        self.dwg.saveas(filename)