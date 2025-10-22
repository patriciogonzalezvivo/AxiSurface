#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from berthe import *

axi = Berthe()
text = Text(text='Hello World !!', center=[axi.width*0.5, axi.height*0.5] )
axi.add( text )
axi.add( text.getBuffer(5) )

axi.toSVG('text.svg')