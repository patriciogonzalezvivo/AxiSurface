#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

class Rectangle(object):
    def __init__( self, center, size ):
        self.center = np.array(center)
        self.size = size

    def inside( self, pos ):
        if (pos[0] > self.center[0] - self.size[0] * 0.5) and (pos[0] < self.center[0] + self.size[0] * 0.5):
            if (pos[1] > self.center[1] - self.size[1] * 0.5) and (pos[1] < self.center[1] + self.size[1] * 0.5):
                return True

        return False