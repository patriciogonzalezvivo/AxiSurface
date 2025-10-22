#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
from Surface import *

axi = Surface()
center = [axi.width*0.5, axi.height*0.5]

radius = axi.width*0.5 - 10.0
while radius > 0:
    axi.circle( center, radius, stroke_width=2.0) 
    radius -= 3.0

axi.toSVG('circles.svg')
# axi.toGCODE('elements.gcode')
# axi.render( debug=True ).write_to_png('elements.png')
# axi.render( sort=True, debug=True ).write_to_png('elements_sorted.png')