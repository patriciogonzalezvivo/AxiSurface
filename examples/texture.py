#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from AxiSurface import *

heightmap = Image('lucy_depth.png')
axi = AxiSurface()
contours = ImageContourToPath(heightmap, 0.1).getScaled(0.1)
contour = Polyline( contours.path[0] )

axi = AxiSurface()

pattern_strip = Pattern( stripes_pattern(num_lines=100, resolution=100) )
axi.pattern( pattern_strip )
pattern_strip.turn(45)
axi.pattern( pattern_strip, translate=[100.0, 0.0], scale=0.70)
pattern_strip.mask( contour, 100, 100)
axi.pattern( pattern_strip, translate=[200.0, 0.0])


pattern_crosses = Pattern(crosses_patterns(resolution=33))
axi.pattern( pattern_crosses, translate=[0.0, 100.0])
pattern_crosses.turn(45)
axi.pattern( pattern_crosses, translate=[100.0, 100.0], scale=0.70 )
pattern_crosses.mask( contour, 100, 100)
axi.pattern( pattern_crosses, translate=[200.0, 100.0])


# pattern_grid = Pattern( grid_pattern(num_h_lines=50, num_v_lines=50 ) )
# axi.pattern( pattern_grid, translate=[0.0, 100.0])
# pattern_grid.turn(45)
# axi.pattern( pattern_grid, translate=[100.0, 100.0], scale=0.70 )
# pattern_grid.mask( contour, 100, 100)
# axi.pattern( pattern_grid, translate=[200.0, 100.0])

# pattern_spiral = Pattern( spiral_pattern(spirals=20) )
# axi.pattern( pattern_spiral, translate=[0.0, 200.0])
# pattern_spiral.mask( contour, 100, 100)
# axi.pattern( pattern_spiral, translate=[0.0, 300.0])

# pattern_hex = Pattern( hex_pattern(), scale=0.01 )
# pattern_hex.mask( contour, 100, 100)
# axi.pattern( pattern_hex, translate=[100.0, 200.0])

axi.toSVG('pattern.svg')