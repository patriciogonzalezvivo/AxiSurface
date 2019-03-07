#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .AxiElement import AxiElement
from .Image import Image
from .tools import distance, remap, transform


class Texture(AxiElement):
    def __init__( self, parent=None, **kwargs ):
        AxiElement.__init__(self, **kwargs)
        self.width = float(kwargs.pop('width', 100))
        self.height = float(kwargs.pop('height', 100))
        self.anchor = kwargs.pop('anchor', [0.5, 0.5])

        if parent is None:
            x = np.zeros(1)
            x.fill(np.nan)
            y = np.zeros(1)
            y.fill(np.nan)
            self.data = (x, y)
        
        elif isinstance(parent, Texture):
            x, y = parent.data
            self.data = (x.copy(), y.copy())
            self.width = parent.width
            self.height = parent.height
            self.translate = kwargs.pop('translate', parent.translate)
            self.scale = kwargs.pop('scale', parent.scale) 
            self.rotate = kwargs.pop('rotate', parent.rotate)
            self.anchor = kwargs.pop('rotate', parent.anchor)

        else:
            x, y = parent
            self.data = (x.copy(), y.copy())

    def __add__(self, other):
        return self.add(other)


    def __iadd__(self, other):
        return self.add(other)


    def add(self, other):
        if isinstance(other, Texture):
            x1, y1 = self.data
            x2, y2 = other.data
            self.data = (np.concatenate([x1, x2]), np.concatenate([y1, y2]))
            return self

        else:
            x1, y1 = self.data
            x2, y2 = other
            self.data = (np.concatenate([x1, x2]), np.concatenate([y1, y2]))
            return self


    @property
    def center(self):
        return [self.width * self.anchor[0], self.height * self.anchor[1]]


    def turn(self, rotation, x_offset=0.5, y_offset=0.5):
        """Rotates the given texture by a given angle.
        Args:
            rotation (float): the angle of rotation in degrees
            x_offset (float): the x component of the center of rotation (optional)
            y_offset (float): the y component of the center of rotation (optional)
        """
        x, y = self.data
        x = x.copy() - x_offset
        y = y.copy() - y_offset
        angle = np.radians(rotation)
        x_rot = x * np.cos(angle) + y * np.sin(angle)
        y_rot = x * -np.sin(angle) + y * np.cos(angle)

        self.data = (x_rot + x_offset, y_rot + y_offset)


    def _map(self, surface):
        """Returns values on a surface for points on a texture.
        Args:
            surface (surface): the surface to trace along
        Returns:
            an array of surface heights for each point in the
            texture. Line separators (i.e. values that are ``nan`` in
            the texture) will be ``nan`` in the output, so the output
            will have the same dimensions as the x/y axes in the
            input texture.
        """
        x, y = self.data
        surface_h, surface_w = surface.shape

        # First, we convert the points along the texture into integers within
        # the bounds of the surface's index. The clipping here will also convert
        # the nan values to 0.
        surface_x = np.clip( np.int32(surface_w * x - 1e-9), 0, surface_w - 1)
        surface_y = np.clip( np.int32(surface_h * y - 1e-9), 0, surface_h - 1)

        # Grab z-values along the texture path. Note that this will include values
        # for every point, even if it is nan or had to be clipped to within the
        # bounds of the surface, so we have to fix that next.
        surface_z = surface[surface_x, surface_y]

        # # Set z-values that are either out of bounds or nan in the texture to nan
        # # in the output.
        # # Numpy wants to warn about the fact that there are nan values in the
        # # textures, so we silence warnings about this.
        # with np.errstate(invalid='ignore'):
        #     surface_z[  (x < 0) | (x >= 1) |
        #                 (y < 0) | (y >= 1)] = np.nan
        
        return surface_z


    def project(self, surface, angle=0, **kwargs):

        # Map the texture to get the Zs
        if isinstance(surface, Image):
            if surface.type == "grayscale":
                z = self._map(surface.data.T)
            elif surface.type == "mask":
                return self.mask(surface)
        else:
            z = self._map(surface.T)

        # Extract the Xs and Ys from the texture
        x, y = self.data

        if angle != 0:        
            # The projection is as simple as linearly blending the Z and Y
            # dimensions. The multiples are calculated from the given
            # angle with standard trig.
            z_coef = np.sin(np.radians( (angle) ))
            y_coef = np.cos(np.radians( (angle) ))

            self.data = (x, y * y_coef - z * z_coef)
        else:
            self.data = (x, y + z * 0.0)

        return self


    def mask(self, element, width=None, height=None):
        x, y = self.data

        if width == None:
            width = self.width
        if height == None:
            height = self.height

        if isinstance(element, AxiElement):
            N = x.shape[0]
            z = np.zeros(N)
            for i in range(N):
                if np.isnan(x[i]) or np.isnan(y[i]):
                    continue
                pos = [x[i] * width, y[i] * height]
                if not element.inside(pos):
                    z[i] = np.nan
            self.data = (x, y + z)

        elif isinstance(element, Image):
            if element.type == "mask":
                self.data = (x, y + Image.data * 0.0)
            else:
                raise Exception("Texture: Masking Image is not a mask but a", element.type)


    def carve(self, element, width=None, height=None):
        x, y = self.data

        if width == None:
            width = self.width
        if height == None:
            height = self.height

        if isinstance(element, AxiElement):
            N = x.shape[0]
            z = np.zeros(N)
            for i in range(N):
                if np.isnan(x[i]) or np.isnan(y[i]):
                    continue
                pos = [x[i] * width, y[i] * height]
                if element.inside(pos):
                    z[i] = np.nan
            self.data = (x, y + z)

        # elif isinstance(element, Image):
        #     if element.type == "mask":
        #         self.data = (x, y + Image.data * 0.0)

        #     else:
        #         raise Exception("Texture: Masking Image is not a mask but a", element.type)


    def getPoints(self):
        X, Y = self.data
        W, H = self.width, self.height

        pts = []
        for x, y in zip( *(X * W, Y * H) ):
            if not np.isnan(x) and not np.isnan(y):
                pts.append( transform( [x,y], rotate=self.rotate, scale=self.scale, translate=self.translate, anchor=self.center) )

        return pts


    def getPath(self):
        from .Path import Path

        X, Y = self.data
        W, H = self.width, self.height

        pts = []
        path = []
        draw = False
        for x, y in zip( *(X * W, Y * H) ):
            if np.isnan(x) or np.isnan(y):
                if draw and len(pts) > 0:
                    path.append( pts[:] )
                draw = False
            else:
                if not draw:
                    pts = [] 
                    draw = True
                pts.append( transform( [x,y], rotate=self.rotate, scale=self.scale, translate=self.translate, anchor=self.center) )

        if draw and len(pts) > 0:
            path.append( pts[:] )

        return Path(path)

