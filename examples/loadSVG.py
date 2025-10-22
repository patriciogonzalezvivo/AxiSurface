
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from Surface import *

axi = Surface()

axi.fromSVG('tiger.svg')

axi.toSVG('out.svg')