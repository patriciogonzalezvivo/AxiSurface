#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np


# This code is adapted from Paul Butler great Surface Projection tutorial
# https://bitaesthetics.com/posts/surface-projection.html and PenKit https://github.com/paulgb/penkit/

def stripes_pattern(num_lines=10, resolution=50, offset=0, zigzag=False):
    x_min = 0.0
    x_max = 1.0
    y_min = 0.0
    y_max = 1.0
    
    resolution = int(resolution)
    resolution_unit = 1.0 / resolution
    resolution_offset = offset * resolution_unit
    x_min = x_min + resolution_offset
    x_max = (x_max-resolution_unit) + resolution_offset

    lines_unit = 1.0 / num_lines
    lines_offset = offset * lines_unit
    y_min = y_min + lines_offset
    y_max = (y_max-lines_unit) + lines_offset

    print(f"stripes_pattern: num_lines={num_lines}, resolution={resolution}, offset={offset} -> x:[{x_min},{x_max}] y:[{y_min},{y_max}]")

    # np.meshgrid is a handy way to generate a grid of points. It
    # returns a pair of matrices, which we will flatten into arrays.
    # For the x-coordinates, we put a nan value at the end so that when
    # we flatten them there is a separater between each horizontal line.
    x, y = np.meshgrid(
        np.hstack( [np.linspace(x_min, x_max, resolution), np.nan] ),
        np.linspace(int(y_min), int(y_max), int(num_lines)),
    )

    if zigzag:
        line = 0
        for each in x:
            if line%2 == 1:
                # each = np.flipud(each)
                x[line] = np.flipud(each)
            line += 1
    
    # For coordinates where the x value is nan, set the y value to nan
    # as well. nan coordinates represent breaks in the path, indicating
    # here that the pen should be raised between each horizontal line.
    y[np.isnan(x)] = np.nan
    return x.flatten(), y.flatten()


def grid_pattern(num_h_lines=10, num_v_lines=10, resolution=50):
    x_h, y_h = stripes_pattern(num_h_lines, resolution)
    y_v, x_v = stripes_pattern(num_v_lines, resolution)
    return np.concatenate([x_h, x_v]), np.concatenate([y_h, y_v])


def dashes_pattern(dash_x, dash_y, num_lines=10, resolution=10):
    x_min = 0.0
    x_max = 1.0
    y_min = 0.0
    y_max = 1.0

    resolution = int(resolution)
    num_lines = int(num_lines)

    offsets_x = np.tile(dash_x, resolution)
    offsets_y = np.tile(dash_y, num_lines)

    x, y = np.meshgrid(
        np.linspace(x_min, x_max, dash_x.size * resolution) + offsets_x,
        np.linspace(y_min, y_max, dash_y.size * num_lines) + offsets_y, 
    )

    return x.flatten(), y.flatten()


def crosses_pattern(resolution=10):
    resolution = int(resolution)
    offset = (1.0/resolution)

    dash_x = np.array([ offset*0.5, 0.0, -offset*0.5, np.nan ])
    dash_y = np.array([ np.nan, 0.0, np.nan, np.nan ])

    x_h, y_h = dashes_pattern(dash_x, dash_y, resolution, resolution)  
    y_v, x_v = dashes_pattern(dash_x, dash_y, resolution, resolution)
    return np.concatenate([x_h, x_v]), np.concatenate([y_h, y_v])


def spiral_pattern(spirals=6.0, ccw=False, offset=0.0, resolution=1000):
    """Makes a pattern consisting of a spiral from the origin.
    Args:
        spirals (float): the number of rotations to make
        ccw (bool): make spirals counter-clockwise (default is clockwise)
        offset (float): if non-zero, spirals start offset by this amount
        resolution (int): number of midpoints along the spiral
    Returns:
        A pattern.
    """
    dist = np.sqrt(np.linspace(0., 1., resolution))
    if ccw:
        direction = 1.
    else:
        direction = -1.
    angle = dist * spirals * np.pi * 2. * direction
    spiral_pattern = (
        (np.cos(angle) * dist / 2.) + 0.5,
        (np.sin(angle) * dist / 2.) + 0.5
    )
    return spiral_pattern


def hex_pattern(grid_size = 10, resolution=50):
    """Makes a pattern consisting on a grid of hexagons.
    Args:
        grid_size (int): the number of hexagons along each dimension of the grid
        resolution (int): the number of midpoints along the line of each hexagon
    
    Returns:
        A pattern.
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

    return x_t.flatten('F'), y_t.flatten('F')