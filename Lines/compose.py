#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite

from Lines.Surface import Surface

STROKE_WIDTH = 0.2

def child(parent, name):
    if isinstance(parent, Surface):
        parent = parent.body
    
    return parent.add( svgwrite.container.Group(id=name, fill='none', stroke='black', stroke_width=STROKE_WIDTH))