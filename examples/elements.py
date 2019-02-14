#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from AxiSurface import *

WIDTH = 297.0
# HEIGHT = 420.0
# CENTER = (WIDTH*0.5, HEIGHT*0.5)
MARGIN = WIDTH*0.1

path_str = ""

cols = 20
col_width = (WIDTH-MARGIN * 2.0)/cols
col_height = 20
ang_step = 180.0/cols
scl_step = 1.0/cols

x = MARGIN
y = MARGIN

axi = AxiSurface()

for col in range(cols):
    if col == cols-1:
        axi.rect(center=[x + col * col_width, y], size=[col_width*0.4, col_width*0.4], rotate=col*ang_step, stroke_width=col+0.2, fill=True)
    else:
        axi.rect(center=[x + col * col_width, y], size=[col_width*0.4, col_width*0.4], rotate=col*ang_step, stroke_width=col+0.2)

    axi.rect(center=[x + col * col_width, y + col_height], size=[col_width*0.4, col_width*0.4], rotate=col*ang_step, scale=scl_step+scl_step*col*2.0, fill=True)

y += col_height * 2.0

for col in range(cols):
    if col == cols-1:
        axi.hex(center=[x + col * col_width, y], radius=col_width*0.3, rotate=col*ang_step, stroke_width=col+0.2, fill=True)
    else:
        axi.hex(center=[x + col * col_width, y], radius=col_width*0.3, rotate=col*ang_step, stroke_width=col+0.2)

    axi.hex(center=[x + col * col_width, y + col_height], radius=col_width*0.3, rotate=col*ang_step, scale=scl_step+scl_step*col*2.0, fill=True)

y += col_height * 2.0

for col in range(cols):
    axi.circle(center=[x + col * col_width, y], radius=col_width*0.25, rotate=col*ang_step, scale=scl_step+scl_step*col*2.0, fill=True)

    if col == cols-1:
        axi.circle(center=[x + col * col_width, y + col_height], radius=col_width*0.25, rotate=col*ang_step, stroke_width=col+0.2, fill=True)
    else:
        axi.circle(center=[x + col * col_width, y + col_height], radius=col_width*0.25, rotate=col*ang_step, stroke_width=col+0.2)

    if col == cols-1:
        axi.circle(center=[x + col * col_width, y + col_height * 2.0], radius=col_width*0.25, open_angle=90, rotate=col*ang_step, stroke_width=col+0.2, fill=True)
    else:
        axi.circle(center=[x + col * col_width, y + col_height * 2.0], radius=col_width*0.25, open_angle=90, rotate=col*ang_step, stroke_width=col+0.2)

y += col_height * 2.0


for col in range(cols):
    axi.line([-col_width*0.5, 0.0], [col_width*0.5,0.0], translate=[x + col * col_width, y + col_height], rotate=col*ang_step, stroke_width=col*0.25+0.2)

y += col_height
poly = Polyline( [ [-col_width*0.5, 0.0], [col_width*0.5, 0.0], [0.0, col_width*0.5], [0.0, -col_width*0.5] ] )
for col in range(cols):
    poly.translate = [x + col * col_width, y + col_height]
    poly.rotate = col*ang_step
    axi.poly( poly.getPoints(), stroke_width=col*0.25+0.2 )

y += col_height
for col in range(cols):
    axi.text( "Hi", translate=[x + col * col_width, y + col_height], scale=0.2, rotate=col*ang_step, stroke_width=col*0.25+0.2)

axi.toSVG('elements.svg')