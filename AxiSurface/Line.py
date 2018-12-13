#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
from .tools import linesIntersection

class Line(object):
    def __init__( self, start, end ):
        self.start = np.array(start)
        self.end = np.array(end)

    def intersect(self, line):
        return linesIntersection(self.start, self.end, line.start, line.end )
