#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from AxiSurface import *

# Depth
img = Image('pixelspirit.png')

axi = AxiSurface()

polygons = ImageThresholdToPolygons(img, 0.5, scale=0.5)
path = Path()

for polygon in polygons:
    polygon.head_width = 0.5
    polygon.fill = True
    path.add( polygon.getPath() )

axi.path(path)
axi.toSVG('polygons.svg')
# axi.render( debug=True ).write_to_png('polygons.png')
# axi.render( sort=True, debug=True ).write_to_png('polygons_sorted.png')