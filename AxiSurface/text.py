#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .AxiElement import AxiElement
from .Polyline import Polyline
from .hershey_fonts import *

# import svgwrite
# from AxiSurface.AxiSurface import AxiSurface
# import AxiSurface.hersheydata as hersheydata

# FONT_DEFAULT = 'EMSOsmotron'
# FONT_DEFAULT = 'EMSHerculean'
# FONT_DEFAULT = 'futural'
# FONT_DEFAULT = 'futuram'

# def text_char(parent, char, face, offset, vertoffset):
#     path_string = face[char]

#     split_string = path_string.split()
#     midpoint = offset - float(split_string[0])
#     splitpoint = path_string.find("M")

#     # Space glyphs have just widths with no moves, so their splitpoint is 0
#     # We only want to generate paths for visible glyphs where splitpoint > 0
#     if splitpoint > 0:
#         path_string = path_string[splitpoint:]  # portion after first move
#         trans = 'translate({0},{1})'.format(midpoint, vertoffset)
#         parent.add( svgwrite.path.Path(d=path_string,transform=trans) )

#     return midpoint + float(split_string[1])

# def text(parent, text, center=(0.0, 0.0), scale=1.0, rotate=0, font_name=FONT_DEFAULT):
#     if isinstance(parent, AxiSurface):
#         parent = parent.body

#     font = getattr(hersheydata, font_name)
#     g = parent.add( svgwrite.container.Group(id="text") )
#     w = 0  # Initial spacing offset
#     v = 0  # Initial vertical offset
#     spacing = 3  # spacing between letters

#     # evaluate text string
#     letter_vals = (ord(q) - 32 for q in str(text))
#     for q in letter_vals:
#         if q <= 0 or q > 95:
#             w += 2 * spacing
#         else:
#             w = text_char(g, q, font, w, 0)

#     g.translate(   center[0] - scale * w * 0.5, 
#                 ty=center[1] - scale * v * 0.5 )

#     if scale != 1:
#         g.scale( scale ) 
#         # Compaensate the scale so we have a consisten stroke width
#         if 'stroke-width' in parent.attribs:
#             g.attribs['stroke-width'] = parent.attribs['stroke-width'] / scale

#     if rotate != 0:
#         g.rotate( rotate , (w * 0.5, v * 0.5))

#     return [w * scale, v * scale]

class Text(AxiElement):
    def __init__( self, text, **kwargs ):
        AxiElement.__init__(self, **kwargs);
        self.text = text

        self.font =  kwargs.pop('font', FUTURAL)
        self.spacing =  kwargs.pop('spacing', 0)
        self.extra =  kwargs.pop('extra', 0)


    def getPolylines(self, **kwargs ):
        # Based on hershey implementation by Michael Fogleman https://github.com/fogleman/axi/blob/master/axi/hershey.py
        result = []

        x = 0
        for ch in self.text:
            index = ord(ch) - 32
            if index < 0 or index >= 96:
                x += self.spacing
                continue

            lt, rt, coords = self.font[index]
            for path in coords:
                path = [(x + i - lt + self.translate[0], j + self.translate[1]) for i, j in path]
                if path:
                    result.append( Polyline(path) )
            x += rt - lt + self.spacing
            if index == 0:
                x += self.extra

        return result


    def getPoints(self, **kwargs ):


    def getPathString(self):
        lines = self.getPolylines()

        path_str = ''
        for line in lines:
            path_str += line.getPathString()

        return path_str

    