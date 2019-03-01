#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from AxiSurface import *

# Depth
area_size = [70, 70]

axi = AxiSurface(area_size)

axi.line( [-int(area_size[0]/2), 0.0], [int(area_size[0]/2), 0.0] )
axi.line( [0.0, -int(area_size[1]/2)], [0.0, int(area_size[1]/2)] )

for x in range( -int(area_size[0]/2), int(area_size[0]/2) + 1 ):
    if x == 0:
        continue

    if x % 10 == 0:
        axi.line( [x, -1.0], [x, 1.0], stroke_width=0.5 )
        axi.text( str(x*0.1), center=[x, 4], scale=0.1)
    else:
        axi.line( [x, -0.5], [x, 0.5] )

for y in range( -int(area_size[1]/2), int(area_size[1]/2) + 1):
    if y == 0:
        continue

    if y % 10 == 0:
        axi.line( [-1.0, y], [1.0, y], stroke_width=0.5 )
        center = [4.0, y]
        if y < 0:
            center[0] = -center[0] - 1
        axi.text( str(y*0.1), center=center, scale=0.1)
    else:
        axi.line( [-0.5, y], [0.5, y] )

# # Grid
# for y in range( -int(area_size[1]/2), int(area_size[1]/2) + 1 ):
#     if y % 10 == 0:
#         for x in range( -int(area_size[0]/2), int(area_size[0]/2) + 1):
#             if x % 10 == 0:
#                 axi.line( [x - 1.0, y], [x + 1.0, y] )
#                 axi.line( [x, y - 1.0], [x, y + 1.0] )


axi.toSVG('ruler.svg')
axi.toGCODE('ruler.cnc', auto_center=False)
