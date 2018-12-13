# outer __init__.py

from svgwrite import cm, mm

# Surface Class
from .AxiSurface import AxiSurface

# Elements Class
from .Line import Line
from .Rectangle import Rectangle
from .Circle import Circle
from .Polyline import Polyline
from .Path import Path
from .Texture import *

# drawing primitives
from .text import text
from .primitives import dot, line, arc, circle, rect, polyline, path
from .tools import normalize, perpendicular, polar2xy
from .compose import child, add