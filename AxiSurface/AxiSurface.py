#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from .Group import *
from .Image import *
from .Texture import *
from .Polyline import Polyline

from .parser import parseSVG

STROKE_WIDTH = 0.2

class AxiSurface(Group):
    def __init__(self, size='A3', **kwargs):
        Group.__init__(self, **kwargs)
        self.id = 'Body'

        if size == 'A4':
            self.width = 210.0
            self.height = 297.0
        elif size == 'A4_landscape':
            self.width = 297.0
            self.height = 210.0
        elif size == 'A3':
            self.width = 297.0
            self.height = 420.0
        elif size == 'A3_landscape':
            self.width = 420.0
            self.height = 297.0
        elif isinstance(size, tuple) or isinstance(size, list):
            if len(size) == 2:
                self.width = size[0]
                self.height = size[1]
        else:
            self.width = float(size)
            self.height = float(size)


    def fromSVG( self, filename ):
        parseSVG( self, filename )


    def toSVG( self, filename, sorted=False, **kwargs ):
        scale = kwargs.pop('scale', 1.0)
        unit = kwargs.pop('unit', 'mm')

        svg_str = '<?xml version="1.0" encoding="utf-8" ?>\n<svg '
        svg_str += 'width="'+ str(self.width) + unit + '" '
        svg_str += 'height="' + str(self.height) + unit + '" '
        svg_str += 'viewBox="0,0,'+ str(self.width * scale) + ',' + str(self.height * scale) + '" '
        svg_str += 'baseProfile="tiny" version="1.2" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink" ><defs/>'
        
        if sorted:
            print("Sorting paths")
            svg_str += self.getPath().getSorted().getSVGElementString()
        else:
            svg_str += self.getSVGElementString()

        svg_str += '</svg>'

        with open(filename, "w") as file:
            file.write(svg_str)


    def toGCODE(self, filename, **kwargs ):
        gcode_str = 'M3\n'
        
        gcode_str += self.getPath().getSorted().getGCodeString(**kwargs)

        gcode_str += "G0 Z10\n"
        gcode_str += "G0 X0 Y0\n"
        gcode_str += "M5\n"

        with open(filename, "w") as file:
            file.write(gcode_str)


    def fromThreshold( self, filename, threshold=0.5 ):
        import cv2 as cv

        polylines = []    
        im = cv.imread( filename )
        blur = cv.GaussianBlur(im, (3, 3),0)
        imgray = cv.cvtColor( blur, cv.COLOR_BGR2GRAY )
        ret, thresh = cv.threshold(imgray, int(threshold * 255), 255, cv.THRESH_BINARY)
        image, contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        height, width = im.shape[:2]
        scale = [ (1.0 / width) * surface.width, (1.0 / height) * surface.height ]

        for contour in contours:
            points = []
            for point in contour:
                points.append( (point[0][0] * scale[0], point[0][1] * scale[1]) )

            polylines.append(Polyline(points))

        group = self.group(filename)
        for polyline in polylines:
            group.poly( polyline.points )


    def fromImage( self, filename, **kwargs):
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

        self.texture( texture )


    def fromHeightmap( self, filename, **kwargs):
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

        self.texture( texture )


    def fromNormalmap( self, filename, **kwargs):
        total_faces = int(kwargs.pop('total_faces', 14))
        heightmap = kwargs.pop('heightmap', None)
        camera_angle = float(kwargs.pop('camera_angle', 10.0))

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

        for cut in range(total_faces):
            sub_surface = surface.copy()

            mask_sub = np.isclose(normalmap.data, cut * step)
            # sub_surface = remove_mask(sub_surface, mask_sub)
            sub_surface = sub_surface - mask_sub

            angle_sub = cut * step_angle + 90 + texture_angle
            angle_sub = angle_sub + step_angle * 0.5

            texture_sub = Texture( texture )
            texture_sub.turn(angle_sub)
            texture_sub.project(sub_surface, camera_angle)

            self.texture( texture_sub )