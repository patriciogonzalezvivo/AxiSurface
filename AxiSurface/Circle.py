#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import numpy as np

class Circle(object):
    def __init__( self, center, radius ):
        self.center = np.array(center)
        self.radius = radius

    def inside( self, pos ):
        dist = math.hypot(pos[0]-self.center[0], pos[1]-self.center[1])
        return dist < self.radius