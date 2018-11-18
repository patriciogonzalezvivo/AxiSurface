#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite
import hersheydata  # data file w/ Hershey font data

# FONT_DEFAULT = 'EMSOsmotron'
# FONT_DEFAULT = 'EMSHerculean'
FONT_DEFAULT = 'futural'
# FONT_DEFAULT = 'futuram'

def text_char(parent, char, face, offset, vertoffset):
    path_string = face[char]

    split_string = path_string.split()
    midpoint = offset - float(split_string[0])
    splitpoint = path_string.find("M")

    # Space glyphs have just widths with no moves, so their splitpoint is 0
    # We only want to generate paths for visible glyphs where splitpoint > 0
    if splitpoint > 0:
        path_string = path_string[splitpoint:]  # portion after first move
        trans = 'translate({0},{1})'.format(midpoint, vertoffset)
        parent.add( svgwrite.path.Path(d=path_string,transform=trans) )

    return midpoint + float(split_string[1])

def text(parent, text, view_center=(0.0, 0.0), scale=1.0, rotate=0, font_name=FONT_DEFAULT):
    font = getattr(hersheydata, font_name)
    g = parent.add( svgwrite.container.Group(id="text"))
    w = 0  # Initial spacing offset
    v = 0  # Initial vertical offset
    spacing = 3  # spacing between letters

    # evaluate text string
    letter_vals = (ord(q) - 32 for q in str(text))
    for q in letter_vals:
        if q <= 0 or q > 95:
            w += 2 * spacing
        else:
            w = text_char(g, q, font, w, 0)

    g.translate(   view_center[0] - scale * w * 0.5, 
                ty=view_center[1] - scale * v * 0.5 )

    if scale != 1:
        g.scale( scale ) 
        # Compaensate the scale so we have a consisten stroke width
        if 'stroke-width' in parent.attribs:
            g.attribs['stroke-width'] = parent.attribs['stroke-width'] / scale

    if rotate != 0:
        g.rotate( rotate , (w * 0.5, v * 0.5))

    return [w * scale, v * scale]
