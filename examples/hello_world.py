#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from berthe import Berthe

paper = Berthe()

paper.circle(center=(paper.width*0.5, paper.height*0.5), radius=paper.width*0.5 )
paper.rect(center=(paper.width*0.5, paper.height*0.5), size=(paper.width, paper.height) )
paper.text(text='hello world', center=(paper.width*0.5, paper.height*0.5) )

paper.toSVG('hello_world.svg')