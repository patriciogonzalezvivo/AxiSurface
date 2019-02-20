#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from AxiSurface import *

# Depth
heightmap = Image('lucy_depth.png')
axi = AxiSurface()

contours = ImageContourToPath(heightmap, 0.1).getScaled(0.1)
contour = Polyline( contours.path[0] )

axi.poly( contour )

contour_simpler = contour.getSimplify(0.5)
axi.poly( contour_simpler, translate=[100.0, 0.0])


contour_convexHull = contour.getConvexHull()
axi.poly( contour_convexHull, translate=[200.0, 0.0])


contour_offset = contour.getOffset(5)
axi.poly( contour_offset, translate=[0.0, 100.0])


contour_buffer = contour.getBuffer(5)
axi.poly( contour_buffer, translate=[100.0, 100.0])


contour_fill = contour.getFillPath()
axi.path( contour_fill, translate=[0.0, 200.0])


axi.toSVG('polyline.svg')
# axi.render( debug=True ).write_to_png('lucy.png')
# axi.render( sort=True, debug=True ).write_to_png('lucy_sorted.png')