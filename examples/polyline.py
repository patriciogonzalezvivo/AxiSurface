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

axi.polyline( contour )

contour_simpler = contour.getSimplify(0.5)
axi.polyline( contour_simpler, translate=[100.0, 0.0])


contour_convexHull = contour.getConvexHull()
axi.polyline( contour_convexHull, translate=[200.0, 0.0])


contour_offset = contour.getOffset(5)
axi.polyline( contour_offset, translate=[0.0, 100.0])


contour_buffer = contour.getBuffer(5)
axi.polyline( contour_buffer, translate=[100.0, 100.0])


# contour.
contour.head_width = 0.5
contour.fill = True
axi.path( contour, translate=[200.0, 100.0] )


axi.toSVG('polyline.svg')
# axi.render( debug=True ).write_to_png('lucy.png')
# axi.render( sort=True, debug=True ).write_to_png('lucy_sorted.png')