
#
# This source file is part of appleseed.
# Visit http://appleseedhq.net/ for additional information and resources.
#
# This software is released under the MIT license.
#
# Copyright (c) 2013 Franz Beaune, Joel Daniels, Esteban Tovagliari.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import bpy
from bpy.types   import NodeSocket, Node
from ...util     import strip_spaces, realpath, join_names_underscore, filter_params, debug, asUpdate, sep
from ..materials import AppleseedMatProps
from .           import AppleseedNode, AppleseedSocket

#--------------------------------
# Image texture node.
#--------------------------------
class AppleseedTexNode( Node, AppleseedNode):
    '''Appleseed Image Texture Node'''
    bl_idname = "AppleseedTexNode"
    bl_label = "Image Texture"
    bl_icon = 'TEXTURE'

    node_type = 'texture'
    
    tex_path = bpy.props.StringProperty( name = "Texture", 
                                         description = "Path to the image texture", 
                                         default = '', 
                                         subtype = 'FILE_PATH')
                                         
    color_space = bpy.props.EnumProperty( name = "",
                                         description = "Image color space",
                                         items = [
                                         ( 'linear_rgb', 'Linear', ''),
                                         ( 'srgb', 'sRGB', ''),
                                         ( 'ciexyz', 'CIE-XYZ', '')],
                                         default = 'srgb')

    mode = bpy.props.EnumProperty( name = "",
                                         description = "Tiling mode",
                                         items = [
                                         ( 'wrap', 'Wrap / Tiling', ''),
                                         ( 'clamp', 'Clamp', '')],
                                         default = 'wrap')

    def init( self, context):
        self.outputs.new( 'NodeSocketColor', "Color")
        
    def draw_buttons( self, context, layout):
        layout.label("Image:")    
        layout.prop( self, "tex_path", text = "")
        layout.prop( self, "color_space")
        layout.prop( self, "mode")
    
    def draw_buttons_ext(self, context, layout):
        pass
    
    def copy( self, node):
        pass
    
    def free( self):
        asUpdate( "Removing node ", self)
    
    def draw_label( self):
        return self.bl_label


def register():
    bpy.utils.register_class( AppleseedTexNode)

def unregister():
    bpy.utils.unregister_class( AppleseedTexNode)
