#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .Group import *
from .Image import *
from .Texture import *
from .Polyline import Polyline

from .tools import dom2dict

class AxiSurface(Group):
    def __init__(self, size='A3', **kwargs):
        Group.__init__(self, **kwargs)
        self.id = 'Body'

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

    @property
    def size(self):
        return [self.width, self.height]


    @property
    def center(self):
        return [self.width * 0.5, self.height * 0.5]
        

    def fromSVG( self, filename ):
        # TODO:
        #  - Add CubicBezier, QuadraticBezier support
        #  - Resolve nested and element transformations
        #  - Parse correctly the SVG

        from xml.dom.minidom import parse
        doc = parse(filename)
        doc.nodeValue

        svg = doc.getElementsByTagName('svg')[0]
        svg_att = dom2dict(svg) 
        viewBox = svg_att['viewBox'].split()
        width = float(viewBox[2])
        height = float(viewBox[3])

        scale = 'scale(' + str((1.0/width) * self.width) + ',' + str((1.0/height) * self.height) + ')'
        stroke_width = max(width/self.width, height/self.height ) * 0.2

        root_group = self.group( filename, fill=True )
        root_group.parseSVGNode( svg )


    def toSVG( self, filename, **kwargs ):
        scale = kwargs.pop('scale', 1.0)
        unit = kwargs.pop('unit', 'mm')
        optimize = kwargs.pop('optimize', False)
        flip_x = kwargs.pop('flip_x', False)
        flip_y = kwargs.pop('flip_y', False)

        svg_str = '<?xml version="1.0" encoding="utf-8" ?>\n<svg '
        svg_str += 'width="'+ str(self.width) + unit + '" '
        svg_str += 'height="' + str(self.height) + unit + '" '
        svg_str += 'viewBox="0,0,'+ str(self.width * scale) + ',' + str(self.height * scale) + '" '
        svg_str += 'baseProfile="tiny" version="1.2" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink" ><defs/>'
        
        if optimize:
            path = self.getPath()
            path = path.getSimplify().getSorted()

            if flip_x:
                def flip_onX(x, y):
                    return (self.width - x, y)
                path = path.getTransformed(flip_onX)

            if flip_y:
                def flip_onY(x, y):
                    return (x, self.height - y)
                path = path.getTransformed(flip_onY)

            svg_str += path.getSVGElementString()
        else:
            svg_str += self.getSVGElementString()

        svg_str += '</svg>'

        with open(filename, "w") as file:
            file.write(svg_str)


    def getGCODEHeader(self, **kwargs):
        return 'M3\n'


    def getGCODEFooter(self, **kwargs):
        gcode_str = "G0 Z10\n"
        gcode_str += "G0 X0 Y0\n"
        gcode_str += "M5\n"
        return gcode_str


    def toGCODE(self, filename, **kwargs ):
        flip_x = kwargs.pop('flip_x', False)
        flip_y = kwargs.pop('flip_y', True)
        auto_center = kwargs.pop('auto_center', True)
        depth = kwargs.pop('depth', -1.0)
        depth_step = kwargs.pop('depth_step', -0.2)
        head_width = kwargs.pop('head_width', self.head_width)
        # head_width_at_depth = kwargs.pop('head_width_at_depth', head_width)

        gcode_str = self.getGCODEHeader()

        # Initial shallow and precise pass
        path = self.getPath().getSimplify().getSorted()

        if auto_center:
            path = path.getCentered(self.width, self.height)
            path = path.getTranslated(-self.width*0.5, -self.height*0.5)

        if flip_x:
            def flip_onX(x, y):
                return (-x, y)
            path = path.getTransformed(flip_onX)

        if flip_y:
            def flip_onY(x, y):
                return (x, -y)
            path = path.getTransformed(flip_onY)

        z = depth_step
        while z > depth:
            gcode_str += path.getGCodeString(head_down_height=z, **kwargs)
            z += depth_step

        gcode_str += self.getGCODEFooter()

        with open(filename, "w") as file:
            file.write(gcode_str)


    def toPNG(self, filename,  **kwargs):
        try:
            import cairocffi as cairo
        except ImportError:
            cairo = None

        if cairo is None:
            raise Exception('AxiSurface.toPNG() requires cairo')

        sort = kwargs.pop('sort', False)
        scale = kwargs.pop('scale', 20)
        margin = kwargs.pop('margin', 0)
        line_width = kwargs.pop('line_width', 0.5/scale)
        show_bounds = kwargs.pop('show_bounds', False)
        debug = kwargs.pop('debug', False)
        optimize = kwargs.pop('optimize', False)

        margin *= scale
        width = int(scale * self.width + margin * 2)
        height = int(scale * self.height + margin * 2)
        surface = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
        dc = cairo.Context(surface)
        dc.set_line_cap(cairo.LINE_CAP_ROUND)
        dc.set_line_join(cairo.LINE_JOIN_ROUND)
        dc.translate(margin, margin)
        dc.scale(scale, scale)
        dc.set_source_rgb(1, 1, 1)
        dc.paint()
        if show_bounds:
            dc.set_source_rgb(0.5, 0.5, 0.5)
            dc.set_line_width(1 / scale)
            dc.rectangle(0, 0, self.width ,self.height)
            dc.stroke()
        dc.set_source_rgb(0, 0, 0)
        dc.set_line_width(line_width)

        path = self.getPath()
        
        if optimize:
            path = path.getSimplify().getSorted()

        lastPoint = [0.0, 0.0]
        for points in path:
            dc.set_source_rgb(0.5, 0.0, 0.0)
            dc.set_line_width(1 / scale)
            if debug:
                dc.move_to(*lastPoint)
                dc.line_to(*points[0])
                dc.stroke()
            else:
                dc.move_to(*points[0])

            dc.set_source_rgb(0, 0, 0)
            dc.set_line_width(line_width)
            for x, y in points:    
                dc.line_to(x, y)
                lastPoint = [x, y]
            dc.stroke()

        surface.write_to_png(filename)