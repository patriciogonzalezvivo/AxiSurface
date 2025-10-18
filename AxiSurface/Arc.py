#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math
import cmath
import numpy as np

from .AxiElement import AxiElement
from .tools import linesIntersection, distance, xy2polar, remap

# From SVG PathTools by Mat Handy
# https://github.com/mathandy/svgpathtools/blob/master/svgpathtools/path.py#L1238

class Arc(AxiElement):
    def __init__( self, start, end, radius, **kwargs):
        AxiElement.__init__(self, **kwargs)

        self._start = np.array(start)
        self._end = np.array(end)
        self._radius = radius

        self.large_arc = kwargs.pop('large_arc', True)
        self.sweep = kwargs.pop('sweep', False)
        self.autoscale_radius = kwargs.pop('autoscale_radius', True)

        self.resolution = max(self.radius[0], self.radius[1])
        self.resolution = int(remap(self.resolution, 0.0, 180.0, 12.0, 180.0))


    @property
    def radius(self):
        if isinstance(self._radius, tuple) or isinstance(self._radius, list):
            rx = self._radius[0]
            ry = self._radius[1]
        else:
            rx = self._radius
            ry = self._radius
        
        if isinstance(self.scale, tuple) or isinstance(self.scale, list):
            rx *= self.scale[0]
            ry *= self.scale[1]
        else:
            rx *= self.scale
            ry *= self.scale

        rx = max(rx, 0.001)
        ry = max(ry, 0.001)

        return np.array([rx, ry])

    
    @property
    def start(self):
        start = self._start
        if self.isTransformed:
            center = self._start + (self._end - self._start) * 0.5
            start = transform(start, translate=self.translate, rotate=self.rotate, scale=self.scale, anchor=center)
        return start


    @property
    def end(self):
        end = self._end
        if self.isTransformed:
            center = self._start + (self._end - self._start) * 0.5
            end = transform(end, translate=self.translate, rotate=self.rotate, scale=self.scale, anchor=center)
        return end


    @property
    def center(self):
        return  self.start + (self.end - self.start) * 0.5


    # @property
    # def bounds(self):
    #     """returns a bounding box for the segment in the form
    #     (xmin, xmax, ymin, ymax)."""
    #     # a(t) = radians(self.theta + self.delta*t)
    #     #      = (2*pi/360)*(self.theta + self.delta*t)
    #     # x'=0: ~~~~~~~~~
    #     # -rx*cos(phi)*sin(a(t)) = ry*sin(phi)*cos(a(t))
    #     # -(rx/ry)*cot(phi)*tan(a(t)) = 1
    #     # a(t) = arctan(-(ry/rx)tan(phi)) + pi*k === atan_x
    #     # y'=0: ~~~~~~~~~~
    #     # rx*sin(phi)*sin(a(t)) = ry*cos(phi)*cos(a(t))
    #     # (rx/ry)*tan(phi)*tan(a(t)) = 1
    #     # a(t) = arctan((ry/rx)*cot(phi))
    #     # atanres = arctan((ry/rx)*cot(phi)) === atan_y
    #     # ~~~~~~~~
    #     # (2*pi/360)*(self.theta + self.delta*t) = atanres + pi*k
    #     # Therfore, for both x' and y', we have...
    #     # t = ((atan_{x/y} + pi*k)*(360/(2*pi)) - self.theta)/self.delta
    #     # for all k s.t. 0 < t < 1

    #     if math.cos(self.phi) == 0:
    #         atan_x = math.pi/2
    #         atan_y = 0
    #     elif math.sin(self.phi) == 0:
    #         atan_x = 0
    #         atan_y = math.pi/2
    #     else:
    #         rx, ry = self.radius
    #         atan_x = math.atan(-(ry/rx)*math.tan(self.phi))
    #         atan_y = math.atan((ry/rx)/math.tan(self.phi))

    #     def angle_inv(ang, k):  # inverse of angle from Arc.derivative()
    #         return ((ang + pi*k)*(360/(2*pi)) - self.theta)/self.delta

    #     xtrema = [self.start[0], self.end[0]]
    #     ytrema = [self.start[1], self.end[1]]

    #     for k in range(-4, 5):
    #         tx = angle_inv(atan_x, k)
    #         ty = angle_inv(atan_y, k)
    #         if 0 <= tx <= 1:
    #             xtrema.append(self.getPointPct(tx)[0])
    #         if 0 <= ty <= 1:
    #             ytrema.append(self.getPointPct(ty)[1])
    #     xmin = max(xtrema)

    #     bbox = Bbox()
    #     bbox.min_x = min(xtrema)
    #     bbox.max_x = max(xtrema)
    #     bbox.min_y = min(ytrema)
    #     bbox.max_x = max(ytrema)
    #     return bbox

    @property
    def length(self):
        return distance(self.start, self.end)


    def intersect(self, line):
        # TODO:
        #    - FIX THIS! Only aplicable for lines
        return linesIntersection(self.start, self.end, line.start, line.end )


    def _getAngles(self, rot_matrix, sx, sy, rx, ry, ex, ey):
        # See http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
        # my notation roughly follows theirs
        rx_sqd = rx*rx
        ry_sqd = ry*ry

        # Transform z-> z' = x' + 1j*y'
        # = rot_matrix**(-1)*(z - (end+start)/2)
        # coordinates.  This translates the ellipse so that the midpoint
        # between self.end and self.start lies on the origin and rotates
        # the ellipse so that the its axes align with the xy-coordinate axes.
        # Note:  This sends self.end to -self.start
        start = complex(sx, sy)
        end = complex(ex, ey)
        zp1 = (1.0/rot_matrix)*(start - end)/2.0
        x1p, y1p = zp1.real, zp1.imag
        x1p_sqd = x1p*x1p
        y1p_sqd = y1p*y1p

        # Correct out of range radii
        # Note: an ellipse going through start and end with radius and phi
        # exists if and only if radius_check is true
        radius_check = (x1p_sqd/rx_sqd) + (y1p_sqd/ry_sqd)
        if radius_check > 1:
            if self.autoscale_radius:
                rx *= cmath.sqrt(radius_check)
                ry *= cmath.sqrt(radius_check)
                radius = rx + 1j*ry
                rx_sqd = rx*rx
                ry_sqd = ry*ry
            else:
                raise ValueError("No such elliptic arc exists.")

        # Compute c'=(c_x', c_y'), the center of the ellipse in (x', y') coords
        # Noting that, in our new coord system, (x_2', y_2') = (-x_1', -x_2')
        # and our ellipse is cut out by of the plane by the algebraic equation
        # (x'-c_x')**2 / r_x**2 + (y'-c_y')**2 / r_y**2 = 1,
        # we can find c' by solving the system of two quadratics given by
        # plugging our transformed endpoints (x_1', y_1') and (x_2', y_2')
        tmp = rx_sqd * y1p_sqd + ry_sqd * x1p_sqd
        radicand = (rx_sqd*ry_sqd - tmp) / tmp
        try:
            radical = cmath.sqrt(radicand)
        except ValueError:
            radical = 0

        if self.large_arc == self.sweep:
            cp = -radical*(rx*y1p/ry - 1j*ry*x1p/rx)
        else:
            cp = radical*(rx*y1p/ry - 1j*ry*x1p/rx)

        # The center in (x,y) coordinates is easy to find knowing c'
        # self.center = exp(1j*self.phi)*cp + (self.start + self.end)/2

        # Now we do a second transformation, from (x', y') to (u_x, u_y)
        # coordinates, which is a translation moving the center of the
        # ellipse to the origin and a dilation stretching the ellipse to be
        # the unit circle
        u1 = (x1p - cp.real)/rx + 1j*(y1p - cp.imag)/ry  # transformed start
        u2 = (-x1p - cp.real)/rx + 1j*(-y1p - cp.imag)/ry  # transformed end

        # clip in case of floating point error
        u1 = np.clip(u1.real, -1, 1) + 1j*np.clip(u1.imag, -1, 1)
        u2 = np.clip(u2.real, -1, 1) + 1j * np.clip(u2.imag, -1, 1)

        # Now compute theta and delta (we'll define them as we go)
        # delta is the angular distance of the arc (w.r.t the circle)
        # theta is the angle between the positive x'-axis and the start point
        # on the circle
        theta = 0.0
        if u1.imag > 0:
            theta = math.degrees(math.acos(u1.real))
        elif u1.imag < 0:
            theta = -math.degrees(math.acos(u1.real))
        else:
            if u1.real > 0:  # start is on pos u_x axis
                theta = 0
            else:  # start is on neg u_x axis
                # Note: This behavior disagrees with behavior documented in
                # http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
                # where theta is set to 0 in this case.
                theta = 180

        det_uv = u1.real*u2.imag - u1.imag*u2.real

        acosand = u1.real*u2.real + u1.imag*u2.imag
        acosand = np.clip(acosand.real, -1, 1) + np.clip(acosand.imag, -1, 1)
        
        delta = 0.0
        if det_uv > 0:
            delta = math.degrees(math.acos(acosand))
        elif det_uv < 0:
            delta = -math.degrees(math.acos(acosand))
        else:
            if u1.real*u2.real + u1.imag*u2.imag > 0:
                # u1 == u2
                delta = 0
            else:
                # u1 == -u2
                # Note: This behavior disagrees with behavior documented in
                # http://www.w3.org/TR/SVG/implnote.html#ArcImplementationNotes
                # where delta is set to 0 in this case.
                delta = 180

        if not self.sweep and delta >= 0:
            delta -= 360
        elif self.large_arc and delta <= 0:
            delta += 360

        return theta, delta


    def getPointPct(self, t):
        if t <= 0.0:
            return self.start
        if t >= 1.0:
            return self.end

        sx, sy = self.start
        cx, cy = self.center
        rx, ry = self.radius
        ex, ey = self.end

        phi = math.radians(self.rotate)
        rot_matrix = cmath.exp(1j*phi)
        theta, delta = self._getAngles( rot_matrix, sx, sy, rx, ry, ex, ey )
        angle = math.radians(theta + t*delta)
        cosphi = rot_matrix.real
        sinphi = rot_matrix.imag
        
        x = rx * cosphi * math.cos(angle) - ry * sinphi * math.sin(angle) + cx
        y = rx * sinphi * math.cos(angle) + ry * cosphi * math.sin(angle) + cy
        return [x, y]


    def getPoints(self, **kwargs):
        resolution = kwargs.pop('resolution', self.resolution)

        points = []
        step = 1.0/float(resolution)
        for i in range(int(resolution+1)):
            points.append(self.getPointPct( float(i) * step ))

        return points


    def _toShapelyGeom(self):
        try:
            from shapely import geometry
        except ImportError:
            geometry = None

        if geometry is None:
            raise Exception('To convert an Arc to a Shapely LineString requires shapely. Try: pip install shapely')

        return geometry.LineString( self.getPoints() )


    def getStrokePath(self, **kwargs):
        from .Polyline import Polyline
        return Polyline(self.getPoints(**kwargs), stroke_width=self.stroke_width, head_width=self.head_width).getStrokePath(**kwargs)

    # def getSVGElementString(self):
    #     rx = self.radius[0]
    #     ry = self.radius[1]
    #     d = ''
    #     args = {
    #         'x0': self.start[0], 
    #         'y0': self.start[1], 
    #         'xradius': rx, 
    #         'yradius': ry, 
    #         'ellipseRotation':0, #has no effect for circles
    #         'x1': self.end[0], 
    #         'y1': self.end[1]
    #     }
    #     d = "M %(x0)f,%(y0)f A %(xradius)f,%(yradius)f%(ellipseRotation)f 1,1 %(x1)f,%(y1)f"%args

    #     svg_str = '<path '
    #     if self.id != None:
    #         svg_str += 'id="' + self.id + '" '
    #     svg_str += 'd="' + d + '" '
    #     svg_str += 'fill="none" stroke="black" stroke-width="'+str(self.head_width) + '" '
    #     svg_str += '/>\n'
        
    #     return svg_str

