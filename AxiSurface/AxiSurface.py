#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite
from svgwrite import cm, mm
from .parser import parseSVG
from .tracer import traceImg
from .shading import shadeHeightmap, shadeNormalmap, shadeGrayscale

STROKE_WIDTH = 0.2

class AxiSurface(object):
    def __init__(self, size='A3', scale=1.0, unit=mm, filename=None):

        if size == 'A4':
            self.width = 210.0
            self.height = 297.0
        elif size == 'A4_landscape':
            self.width = 297.0
            self.height = 210.0
        elif size == 'A3':
            self.width = 297.0
            self.height = 420.0
        elif size == 'A3_landscape':
            self.width = 420.0
            self.height = 297.0
        elif isinstance(size, tuple) or isinstance(size, list):
            if len(size) == 2:
                self.width = size[0]
                self.height = size[1]
        else:
            self.width = float(size)
            self.height = float(size)

        self.scale = scale
        self.filename = filename

        if filename:
            self.dwg = svgwrite.Drawing( filename=filename, debug=False, profile='tiny', size=(self.width * unit, self.height * unit) )
        else:
            self.dwg = svgwrite.Drawing( debug=False, profile='tiny', size=(self.width * unit, self.height * unit) )

        self.dwg.viewbox(width=self.width / self.scale, height=self.height / self.scale)
        self.body = self.dwg.add( svgwrite.container.Group(id='body', fill='none', stroke='black', stroke_width=STROKE_WIDTH) )

    def child( self, name ):
        name = name.replace(" ", "_")
        return self.body.add( svgwrite.container.Group(id=name, fill='none', stroke='black', stroke_width=STROKE_WIDTH) )
        
    def childOf( self, parent, name ):
        name = name.replace(" ", "_")
        return parent.add( svgwrite.container.Group(id=name, fill='none', stroke='black', stroke_width=STROKE_WIDTH) )

    def addRegisters( self ):
        reg = self.child("registration_marks")
        reg.add( svgwrite.shapes.Line(start=(0, 0), end=(10.0, 0.0), stroke_width=STROKE_WIDTH*2.0) )
        reg.add( svgwrite.shapes.Line(start=(0, 0), end=(0.0, 10.0), stroke_width=STROKE_WIDTH*2.0) )

        reg.add( svgwrite.shapes.Line(start=(self.width - 10.0, self.height), end=(self.width, self.height), stroke_width=STROKE_WIDTH*2.0) )
        reg.add( svgwrite.shapes.Line(start=(self.width, self.height - 10.0), end=(self.width, self.height), stroke_width=STROKE_WIDTH*2.0) )

        reg.add( svgwrite.shapes.Line(start=(self.width - 10.0, 0.0), end=(self.width, 0.0), stroke_width=STROKE_WIDTH*2.0) )
        reg.add( svgwrite.shapes.Line(start=(self.width, 0.0), end=(self.width, 10.0), stroke_width=STROKE_WIDTH*2.0) )

        reg.add( svgwrite.shapes.Line(start=(0.0, self.height), end=(10.0, self.height), stroke_width=STROKE_WIDTH*2.0) )
        reg.add( svgwrite.shapes.Line(start=(0.0, self.height - 10.0), end=(0.0, self.height), stroke_width=STROKE_WIDTH*2.0) )

        reg.add( svgwrite.shapes.Line(start=((self.width * 0.5 - 5.0), 0.0), end=((self.width * 0.5 + 5.0), 0.0), stroke_width=STROKE_WIDTH*2.0) )
        reg.add( svgwrite.shapes.Line(start=((self.width * 0.5 - 5.0), self.height), end=((self.width * 0.5 + 5.0), self.height), stroke_width=STROKE_WIDTH*2.0) )
        reg.add( svgwrite.shapes.Line(start=(0.0, (self.height * 0.5 - 5.0)), end=(0.0, (self.height * 0.5 + 5.0)), stroke_width=STROKE_WIDTH*2.0) )
        reg.add( svgwrite.shapes.Line(start=(self.width, (self.height * 0.5 - 5.0)), end=(self.width, (self.height * 0.5 + 5.0)), stroke_width=STROKE_WIDTH*2.0) )


    def fromSVG( self, filename ):
        parseSVG( self, filename )


    def fromThreshold( self, filename, threshold=0.5 ):
        traceImg( self, filename, threshold )

    def fromImage( self, filename, threshold=0.5, invert=False, texture=None, texture_angle=0, texture_resolution=None, texture_presicion=1.0, texture_offset=0, mask=None):
        shadeGrayscale( self, filename, threshold=threshold, invert=invert, texture=texture, texture_resolution=texture_resolution, texture_presicion=texture_presicion, texture_angle=texture_angle,  texture_offset=texture_offset, mask=mask )


    def fromHeightmap( self, filename, camera_angle=1.0, grayscale=None, threshold=0.5, invert=False, texture=None, texture_resolution=None, texture_presicion=1.0, texture_angle=0, texture_offset=0, mask=None):
        shadeHeightmap( self, filename, camera_angle=camera_angle, grayscale=grayscale, threshold=threshold, invert=invert, texture=texture, texture_resolution=texture_resolution, texture_presicion=texture_presicion, texture_angle=texture_angle, texture_offset=texture_offset, mask=mask )


    def fromNormalmap( self, filename, total_faces=18, grayscale=None, threshold=0.5, invert=False, texture=None, texture_resolution=None, texture_presicion=1.0, texture_angle=0, texture_offset=0, mask=None):
        shadeNormalmap( self, filename, total_faces=total_faces, grayscale=grayscale, threshold=threshold, invert=invert, texture=texture, texture_resolution=texture_resolution, texture_presicion=texture_presicion, texture_angle=texture_angle, texture_offset=texture_offset, mask=mask )


    def toSVG( self, filename=None ):
        self.debug = False
        if filename:
            self.dwg.saveas( filename )
        elif self.filename:
            self.dwg.save()

        
