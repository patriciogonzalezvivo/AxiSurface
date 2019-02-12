# outer __init__.py

from svgwrite import cm, mm

# Surface Class
from .AxiSurface import AxiSurface
from .AxiElement import AxiElement

# Composing
from .Group import Group

# Elements Class
from .Line import Line
from .Rectangle import Rectangle
from .Circle import Circle
from .Polyline import Polyline
from .Texture import *

# drawing primitives
# from .text import text
from .draw import dot, line, arc, circle, rect, hexagon, polyline, path
from .tools import normalize, perpendicular, polar2xy
from .compose import child, add