#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import svgwrite

import numpy as np

# This code is adapted from Paul Butler great Surface Projection tutorial
# https://bitaesthetics.com/posts/surface-projection.html and PenKit https://github.com/paulgb/penkit/

def stripes_texture(num_lines=10, resolution=50, offset=0):
    x_min = 0.0
    x_max = 1.0
    y_min = 0.0
    y_max = 1.0
    
    resolution_unit = 1.0 / resolution
    resolution_offset = offset * resolution_unit
    x_min = x_min + resolution_offset
    x_max = (x_max-resolution_unit) + resolution_offset

    lines_unit = 1.0 / num_lines
    lines_offset = offset * lines_unit
    y_min = y_min + lines_offset
    y_max = (y_max-lines_unit) + lines_offset

    # np.meshgrid is a handy way to generate a grid of points. It
    # returns a pair of matrices, which we will flatten into arrays.
    # For the x-coordinates, we put a nan value at the end so that when
    # we flatten them there is a separater between each horizontal line.
    x, y = np.meshgrid(
        np.hstack( [np.linspace(x_min, x_max, resolution), np.nan] ),
        np.linspace(y_min, y_max, num_lines),
    )
    
    # For coordinates where the x value is nan, set the y value to nan
    # as well. nan coordinates represent breaks in the path, indicating
    # here that the pen should be raised between each horizontal line.
    y[np.isnan(x)] = np.nan
    return x.flatten(), y.flatten()


def grid_texture(num_h_lines=10, num_v_lines=10, resolution=50):
    x_h, y_h = make_stripes_texture(num_h_lines, resolution)
    y_v, x_v = make_stripes_texture(num_v_lines, resolution)
    return np.concatenate([x_h, x_v]), np.concatenate([y_h, y_v])


def spiral_texture(spirals=6.0, ccw=False, offset=0.0, resolution=1000):
    """Makes a texture consisting of a spiral from the origin.
    Args:
        spirals (float): the number of rotations to make
        ccw (bool): make spirals counter-clockwise (default is clockwise)
        offset (float): if non-zero, spirals start offset by this amount
        resolution (int): number of midpoints along the spiral
    Returns:
        A texture.
    """
    dist = np.sqrt(np.linspace(0., 1., resolution))
    if ccw:
        direction = 1.
    else:
        direction = -1.
    angle = dist * spirals * np.pi * 2. * direction
    spiral_texture = (
        (np.cos(angle) * dist / 2.) + 0.5,
        (np.sin(angle) * dist / 2.) + 0.5
    )
    return spiral_texture


def hex_texture(grid_size = 2, resolution=1):
    """Makes a texture consisting on a grid of hexagons.
    Args:
        grid_size (int): the number of hexagons along each dimension of the grid
        resolution (int): the number of midpoints along the line of each hexagon
    
    Returns:
        A texture.
    """
    grid_x, grid_y = np.meshgrid(
        np.arange(grid_size),
        np.arange(grid_size)
    )
    ROOT_3_OVER_2 = np.sqrt(3) / 2
    ONE_HALF = 0.5
    
    grid_x = (grid_x * np.sqrt(3) + (grid_y % 2) * ROOT_3_OVER_2).flatten()
    grid_y = grid_y.flatten() * 1.5
    
    grid_points = grid_x.shape[0]
    
    x_offsets = np.interp(np.arange(4 * resolution),
        np.arange(4) * resolution, [
            ROOT_3_OVER_2,
            0.,
            -ROOT_3_OVER_2,
            -ROOT_3_OVER_2,
        ])
    y_offsets = np.interp(np.arange(4 * resolution),
        np.arange(4) * resolution, [
            -ONE_HALF,
            -1.,
            -ONE_HALF,
            ONE_HALF
        ])
    
    tmx = 4 * resolution
    x_t = np.tile(grid_x, (tmx, 1)) + x_offsets.reshape((tmx, 1))
    y_t = np.tile(grid_y, (tmx, 1)) + y_offsets.reshape((tmx, 1))
    
    x_t = np.vstack([x_t, np.tile(np.nan, (1, grid_x.size))])
    y_t = np.vstack([y_t, np.tile(np.nan, (1, grid_y.size))])
    
    return fit_texture((x_t.flatten('F'), y_t.flatten('F')))


def layer_to_path_gen(layer):
    """Generates an SVG path from a given layer.
    Args:
        layer (layer): the layer to convert
    Yields:
        str: the next component of the path
    """
    draw = False
    for x, y in zip(*layer):
        if np.isnan(x) or np.isnan(y):
            draw = False
        elif not draw:
            yield 'M {} {}'.format(x, y)
            draw = True
        else:
            yield 'L {} {}'.format(x, y)


class Texture(object):
    def __init__( self, texture ):
        
        if isinstance(texture, Texture):
            x, y = texture.data
            self.data = (x.copy(), y.copy())
        else:
            x, y = texture
            self.data = (x.copy(), y.copy())


    def rotate(self, rotation, x_offset=0.5, y_offset=0.5):
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

    def plot(self, surface, angle=0, **kwargs):

        # TODO:
        #       - if it's surface
        #       - if it's just z values
        #  https://github.com/paulgb/penkit/blob/master/penkit/projection.py#L36

        # Extract the Xs and Ys from the texture
        x, y = self.data
        
        # Map the texture to get the Zs
        z = self._map(surface.T)

        if angle > 0:        
            # The projection is as simple as linearly blending the Z and Y
            # dimensions. The multiples are calculated from the given
            # angle with standard trig.
            z_coef = np.sin(np.radians(angle))
            y_coef = np.cos(np.radians(angle))

            self.data = (x, y * y_coef + z * z_coef)
        else:
            self.data = (x, y + z * 0.0)

    def mask(self, element, width, height):
        x, y = self.data
        print(x.shape[0], y.shape[0])

        N = x.shape[0]

        z = np.zeros(N)
        for i in range(N):
            if np.isnan(x[i]) or np.isnan(y[i]):
                continue
            pos = [x[i] * width, y[i] * height]
            if not element.inside(pos):
                z[i] = np.nan

        self.data = (x, y + z)


    def toPaths(self, width, height):
        x, y = self.data
        return ' '.join( layer_to_path_gen( (x * width, y * height) ) )
