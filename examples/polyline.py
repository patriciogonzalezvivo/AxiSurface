#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from AxiSurface import *
import math

WIDTH = 297.0
# HEIGHT = 420.0
# CENTER = (WIDTH*0.5, HEIGHT*0.5)
MARGIN = WIDTH*0.1

path_str = ""

cols = 10
col_width = (WIDTH-MARGIN * 2.0)/ (cols-1)
col_height = 20
ang_step = 180.0/cols
scl_step = 1.0/cols

x = MARGIN
y = MARGIN

axi = AxiSurface()

poly = Polyline( [ [-col_width*0.5, 0.0], [col_width*0.5, 0.0], [0.0, col_width*0.5], [0.0, -col_width*0.5] ] )
for col in range(cols):
    poly.translate = [x + col * col_width, y + col_height]
    poly.rotate = col*ang_step
    axi.poly( poly.getPoints(), stroke_width=col*0.5+0.2 )

y += col_height * 2.0

points = []
for t in range(int(MARGIN), int(WIDTH-MARGIN)):
    t = float(t)
    points.append( [t, math.sin(t * 0.1) * col_height*0.5] )

poly = axi.poly(points, translate=[0.0, y + col_height])
axi.poly( poly.getPolygonOffset(10.0) )

y += col_height * 2.0

for col in range(cols):
    axi.text( "Hi", [x + col * col_width, y + col_height], scale=0.2, rotate=col*ang_step, stroke_width=col*0.25+0.2)

axi.toSVG('polyline.svg')