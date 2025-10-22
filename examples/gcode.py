#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from berthe import *

# Depth
img = Image('lucy_depth.png')
area_size = [70, 70]

axi = Berthe(area_size)

polygons = ImageThresholdToPolygons(img, 0.5, scale=0.07)
# path = Path()

for polygon in polygons:
    polygon.head_width = 0.5
    polygon.fill = True
    axi.add( polygon )

# axi.path( path )
axi.toGCODE('lucy.gcode', depth=-2., depth_step=-0.3) #, head_width_at_depth=0.5, auto_center=False)
