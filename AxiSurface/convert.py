#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict


from .Path import Path
from .Polygon import Polygon
from .Image import Image
from .Texture import *
from .tools import transform

def ImageContourToPath(filename, threshold=0.5, scale=1.0):
    try:
        import cv2 as cv
    except ImportError:
        cv = None

    if cv is None:
        raise Exception('AxiSurface.fromThreshold() requires OpenCV')

    path = []    

    if isinstance(filename, Image):
        filename = filename.filename
    im = cv.imread( filename )
    blur = cv.GaussianBlur(im, (3, 3),0)
    imgray = cv.cvtColor( blur, cv.COLOR_BGR2GRAY )
    ret, thresh = cv.threshold(imgray, int(threshold * 255), 255, cv.THRESH_BINARY)
    image, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # height, width = im.shape[:2]
    # scale = [ (1.0 / width) * size[0], (1.0 / height) * size[1] ]

    for contour in contours:
        points = []
        for point in contour:
            # points.append( (point[0][0] * scale[0], point[0][1] * scale[1]) )
            points.append( (point[0][0] * scale, point[0][1] * scale) )
        path.append( points )

    return Path( path )


def ImageThresholdToPolygons(filename, threshold=0.5, min_area=10.0, scale=1.0):
    try:
        import cv2 as cv
    except ImportError:
        cv = None

    if cv is None:
        raise Exception('AxiSurface.fromThreshold() requires OpenCV')

    polygons = []    

    if isinstance(filename, Image):
        filename = filename.filename
    im = cv.imread( filename )
    blur = cv.GaussianBlur(im, (3, 3),0)
    imgray = cv.cvtColor( blur, cv.COLOR_BGR2GRAY )
    ret, thresh = cv.threshold(imgray, int(threshold * 255), 255, cv.THRESH_BINARY)
    image, contours, hierarchy = cv.findContours(thresh, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)

    if not contours:
        return polygons

    # now messy stuff to associate parent and child contours
    cnt_children = defaultdict(list)
    child_contours = set()
    assert hierarchy.shape[0] == 1
    # http://docs.opencv.org/3.1.0/d9/d8b/tutorial_py_contours_hierarchy.html
    for idx, (_, _, _, parent_idx) in enumerate(hierarchy[0]):
        if parent_idx != -1:
            child_contours.add(idx)
            cnt_children[parent_idx].append(contours[idx])
    # create actual polygons filtering by area (removes artifacts)

    def scaled(points):
        result = []
        for point in points:
            result.append( [point[0] * scale, point[1] * scale] )
        return result

    for idx, cnt in enumerate(contours):
        if idx not in child_contours and cv.contourArea(cnt) >= min_area:
            assert cnt.shape[1] == 1
            poly = Polygon( scaled(cnt[:, 0, :]) )

            for c in cnt_children.get(idx, []):
                if cv.contourArea(c) >= min_area:
                    poly.addHole( scaled(c[:, 0, :]) )
            polygons.append(poly)

    return polygons


def GrayscaleToTexture(filename, **kwargs):
    grayscale = Image( filename )

    threshold = float(kwargs.pop('threshold', 0.5))
    invert = kwargs.pop('invert', False)
    texture = kwargs.pop('texture', None)
    texture_angle = float(kwargs.pop('texture_angle', 0.0))
    mask = kwargs.pop('mask', None)

    # Make surface to carve from (copy from gradient to get same dinesions)
    surface = grayscale.copy()
    surface.fill(1.0)

    # Make gradient into dither mask
    grayscale.dither(threshold=threshold, invert=invert)
    surface = surface - grayscale

    # Load and remove Mask
    if isinstance(mask, basestring) or isinstance(mask, str):
        mask = Image(mask)
        mask = mask.threshold()
    surface = surface - mask

    # Create texture
    if texture is None:
        texture_resolution = kwargs.pop('texture_resolution', min(grayscale.width, grayscale.height) * 0.5)
        texture_presicion = float(kwargs.pop('texture_presicion', 1.0))
        texture_offset = float(kwargs.pop('texture_offset', 0.0)) 
        texture = Texture( stripes_texture(texture_resolution, min(grayscale.width, grayscale.height) * texture_presicion, texture_offset), **kwargs)
    elif not isinstance(texture, Texture):
        texture = Texture( texture, **kwargs  )

    if texture_angle > 0:
        texture.turn(texture_angle)

    # Project texture on surface 
    texture.project(surface)

    return texture


def HeightmapToTexture(filename, **kwargs):
    grayscale = kwargs.pop('grayscale', None)
    camera_angle = float(kwargs.pop('camera_angle', 10.0))

    threshold = float(kwargs.pop('threshold', 0.5))
    invert = kwargs.pop('invert', False)
    texture = kwargs.pop('texture', None)
    texture_angle = float(kwargs.pop('texture_angle', 0.0))
    mask = kwargs.pop('mask', None)

    # Load heightmap
    heightmap = Image(filename)
    heightmap.occlude(camera_angle)

    # load and remove mask
    if isinstance(mask, basestring) or isinstance(mask, str):
        mask = Image(mask)
        mask = mask.threshold()
    heightmap = heightmap - mask

    # Load gradient into dither mask
    if grayscale != None:
        gradientmap = Image( grayscale )
        heightmap = heightmap - gradientmap.dither(threshold=threshold, invert=invert)

    # Create texture
    if texture is None:
        texture_resolution = kwargs.pop('texture_resolution', min(gradientmap.width, gradientmap.height) * 0.5)
        texture_presicion = float(kwargs.pop('texture_presicion', 1.0))
        texture_offset = float(kwargs.pop('texture_offset', 0.0)) 
        texture = Texture( stripes_texture(num_lines=texture_resolution, resolution=min(heightmap.width, heightmap.height) * texture_presicion, offset=texture_offset), **kwargs )
    elif not isinstance(texture, Texture):
        texture = Texture( texture, **kwargs )

    if texture_angle > 0:
        texture.turn(texture_angle)

    texture.project(heightmap, camera_angle)

    return texture


def NormalmapToTexture(filename, **kwargs):
    total_faces = int(kwargs.pop('total_faces', 14))
    heightmap = kwargs.pop('heightmap', None)
    camera_angle = float(kwargs.pop('camera_angle', 0.0))

    grayscale = kwargs.pop('grayscale', None)
    threshold = float(kwargs.pop('threshold', 0.5))
    invert = kwargs.pop('invert', False)
    texture = kwargs.pop('texture', None)
    texture_angle = float(kwargs.pop('texture_angle', 0.0))
    mask = kwargs.pop('mask', None)

    normalmap = Image(filename, type='2D_angle')

    # create a surface to carve from
    if heightmap is None:
        surface = normalmap.copy()
        surface.fill(0.0)
    else:
        surface = heightmap.copy()

    # Decimate normalmap into the N faces
    def decimate(array, dec):
        return (np.floor(array * dec)) / dec
        
    step = 1.0/total_faces
    step_angle = 360.0/total_faces
    normalmap.data = decimate(normalmap.data, float(total_faces))

    # Mask
    if isinstance(mask, basestring) or isinstance(mask, str):
        mask = Image(mask)
        mask = mask.threshold()
    surface = surface - mask
        
    # Load gradient into dither mask
    if grayscale != None:
        gradientmap = Image( grayscale )
        surface = surface - gradientmap.dither(threshold=threshold, invert=invert)

    # Create texture
    if texture is None:
        texture_resolution = kwargs.pop('texture_resolution', min(gradientmap.width, gradientmap.height) * 0.5)
        texture_presicion = float(kwargs.pop('texture_presicion', 1.0))
        texture_offset = float(kwargs.pop('texture_offset', 0.0)) 
        texture = Texture( stripes_texture(texture_resolution, min(surface.width, surface.height) * texture_presicion, texture_offset), **kwargs)
    elif not isinstance(texture, Texture):
        texture = Texture( texture, **kwargs )
        
    if texture_angle > 0:
        texture.turn(texture_angle)

    result = Texture(**kwargs)
    for cut in range(total_faces):
        sub_surface = surface.copy()

        mask_sub = np.isclose(normalmap.data, cut * step)
        # sub_surface = remove_mask(sub_surface, mask_sub)
        sub_surface = sub_surface - mask_sub

        angle_sub = cut * step_angle + 90 + texture_angle
        angle_sub = angle_sub + step_angle * 0.5

        texture_sub = Texture( texture, **kwargs )
        texture_sub.turn(angle_sub)

        if camera_angle != 0.0:
            texture_sub.project(sub_surface, camera_angle)

        result.add( texture_sub )

    return result