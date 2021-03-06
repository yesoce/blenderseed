'''
The MIT License (MIT)

Copyright (c) 2014 appleseedhq

Contributors: Franz Beaune, Joel Daniels, Esteban Tovagliari.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

bl_info = {
    "name": "appleseed",
    "author": "Franz Beaune, Joel Daniels, Esteban Tovagliari, Jasper van Nieuwenhuizen",
    "version": (0, 3, 6),
    "blender": (2, 7, 1),
    "location": "Info Header (engine dropdown)",
    "description": "appleseed integration",
    "warning": "",
    "wiki_url": "https://github.com/appleseedhq/blenderseed/wiki",
    "tracker_url": "https://github.com/appleseedhq/blenderseed/issues",
    "category": "Render"}

if "bpy" in locals():
    import imp
    imp.reload( properties)
    imp.reload( operators)
    imp.reload( export)
    imp.reload( ui)
    imp.reload( render)
    imp.reload( util)
    imp.reload( preferences)
    imp.reload( project_file_writer)
    
else:
    import bpy
    from . import properties
    from . import operators
    from . import export
    from . import ui
    from . import render
    from . import util
    from . import preferences
    from . import project_file_writer

import bpy, bl_ui, bl_operators
import math, mathutils
from shutil import copyfile
from datetime import datetime
import os, subprocess, time


def register():
    properties.register()
    operators.register()
    export.register()
    ui.register()
    preferences.register()
    bpy.utils.register_module( __name__)

def unregister():
    properties.unregister()
    operators.unregister()
    export.unregister()
    ui.unregister()
    preferences.unregister()
    bpy.utils.unregister_module( __name__)
