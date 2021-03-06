
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
from bpy_extras.io_utils import ExportHelper
import os
from . import project_file_writer
from . import util

class ExportAppleseedScene( bpy.types.Operator, ExportHelper):
    """Saves an appleseed scene"""
    bl_idname = "appleseed.export_scene"
    bl_label = "Export Appleseed Scene"

    filename_ext = ".appleseed"
    filter_glob = bpy.props.StringProperty( default = "*.appleseed", options = {'HIDDEN'},)
    
    @classmethod
    def poll( cls, context):
        renderer = context.scene.render
        return renderer.engine == 'APPLESEED_RENDER'
        
    def execute( self, context):
        scene = context.scene
        appleseed_proj = project_file_writer.write_project_file( None)
        appleseed_proj.export( scene, util.realpath( self.filepath))
        return {'FINISHED'}

def menu_func_export_scene( self, context):
    self.layout.operator( ExportAppleseedScene.bl_idname, text = "Appleseed (.appleseed)")

def register():
    bpy.utils.register_class( ExportAppleseedScene)
    bpy.types.INFO_MT_file_export.append( menu_func_export_scene)


def unregister():
    bpy.utils.unregister_class( ExportAppleseedScene)
    bpy.types.INFO_MT_file_export.remove( menu_func_export_scene)
