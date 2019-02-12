#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .AxiElement import AxiElement
from .tools import linesIntersection

class Line(AxiElement):
    def __init__( self, start, end, **kwargs):
        AxiElement.__init__(self, **kwargs);

        self.start = np.array(start)
        self.end = np.array(end)

    def intersect(self, line):
        return linesIntersection(self.start, self.end, line.start, line.end )

    def getPathString(self):
        d = ''
        d += 'M' + self.start[0] + ' ' + self.start[1]
        d += 'L' + self.end[0] + ' ' + elf.end[1]
        return d

