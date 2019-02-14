#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

class AxiElement(object):
    def __init__(self, **kwargs):
        self.head_width = kwargs.pop('head_width', 0.2)
        self.stroke_width = kwargs.pop('stroke_width', self.head_width)
        self.fill = kwargs.pop('fill', False)

        self.translate = kwargs.pop('translate', np.array([0, 0]) )
        self.rotate = kwargs.pop('rotate', 0.0)
        self.scale = kwargs.pop('scale', 1.0)


