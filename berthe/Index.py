#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Mostly rom Axi by Michael Fogleman
# https://github.com/fogleman/axi/blob/master/axi/spatial.py

from math import hypot
from collections import defaultdict

from .Bbox import Bbox

class Index(Bbox):
    def __init__( self, chain, **kwargs):
        Bbox.__init__(self, **kwargs);
        self.n = kwargs.pop('n', 100)
        self.min_x = min(p[0] for p in chain)
        self.max_x = max(p[0] for p in chain)
        self.min_y = min(p[1] for p in chain)
        self.max_y = max(p[1] for p in chain)
        self.bins = defaultdict(list)
        self.size = 0
        for point in chain:
            self.insert(point)
    

    def normalize(self, x, y):
        if self.width == 0.0:
            px = 0.0
        else:
            px = (x - self.min_x) / self.width

        if self.height == 0.0:
            py = 0.0
        else:
            py = (y - self.min_y) / self.height
            
        i = int(px * self.n)
        j = int(py * self.n)
        return (i, j)


    def insert(self, point):
        x, y = point[:2]
        i, j = self.normalize(x, y)
        self.bins[(i, j)].append(point)
        self.size += 1


    def remove(self, point):
        x, y = point[:2]
        i, j = self.normalize(x, y)
        self.bins[(i, j)].remove(point)
        self.size -= 1


    def nearest(self, point):
        x, y = point[:2]
        i, j = self.normalize(x, y)
        points = []
        r = 0
        while not points:
            points.extend(self.ring(i, j, r))
            r += 1
        points.extend(self.ring(i, j, r))
        return min(points, key=lambda p: (hypot(x - p[0], y - p[1]), p[1], p[0]))


    def ring(self, i, j, r):
        if r == 0:
            return self.bins[(i, j)]
        result = []
        for p in range(i - r, i + r + 1):
            result.extend(self.bins[(p, j - r)])
            result.extend(self.bins[(p, j + r)])
        for q in range(j - r + 1, j + r):
            result.extend(self.bins[(i - r, q)])
            result.extend(self.bins[(i + r, q)])
        return result