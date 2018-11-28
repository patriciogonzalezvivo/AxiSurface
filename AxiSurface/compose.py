#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite

from AxiSurface.AxiSurface import AxiSurface

STROKE_WIDTH = 0.2

def child(parent, name):
    if isinstance(parent, AxiSurface):
        parent = parent.body
    
    return parent.add( svgwrite.container.Group(id=name, fill='none', stroke='black', stroke_width=STROKE_WIDTH))