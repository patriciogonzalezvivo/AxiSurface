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
axi.texture( stripes_texture(num_lines=75) )

texture = Texture(stripes_texture(num_lines=100, resolution=100), rotate=45, scale=0.70)
axi.texture( texture, translate=[100.0, 0.0])
texture.mask( contour, 100, 100)
axi.texture( texture, translate=[200.0, 0.0])




axi.texture( grid_texture(num_h_lines=50, num_v_lines=50 ), translate=[0.0, 100.0])
axi.texture( grid_texture(num_h_lines=50, num_v_lines=50 ), translate=[100.0, 100.0], rotate=45, scale=0.70 )
axi.texture( spiral_texture(), translate=[0.0, 200.0])
axi.texture( spiral_texture(spirals=20), translate=[100.0, 200.0])
axi.texture( hex_texture(), scale=0.1, translate=[-50.0, 270.0]) 




axi.toSVG('texture.svg')