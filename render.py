
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
import os, subprocess
import time
import multiprocessing, threading
from shutil import copyfile
from extensions_framework import util as efutil
from . import util
from . import project_file_writer
from locale import getdefaultlocale

sep = os.sep

def update_start( engine, data, scene):
    if engine.is_preview:
        update_preview( engine, data, scene)
    else:
        update_scene( engine, data, scene)
        
def render_start( engine, scene):
    if engine.is_preview:
        render_preview( engine, scene)
    else:
        if engine.animation:
            print("Animation: ", engine.animation)
            frame_start = scene.frame_start
            frame_current = frame_start
            scene.frame_set(frame_start)
            frame_end = scene.frame_end
            step = scene.frame_step
            while frame_current <= frame_end:
                render_scene( engine, scene)
                frame_current += frame_step
                scene.frame_set(frame_current)
        else:
            render_scene( engine, scene)
        
def render_init( engine):
    pass

def update_preview( engine, data, scene):
    pass

def render_preview( engine, scene):
    # Iterate through the preview scene, finding objects with materials attached
    objects_materials = {}
    (width, height) = util.resolution(scene)

    if (width, height) == (96, 96):
        return
    for object in [ob for ob in scene.objects if ob.is_visible(scene) and not ob.hide_render]:
        for mat in util.get_instance_materials(object):
	        if mat is not None:
		        if not object.name in objects_materials.keys(): objects_materials[object] = []
		        objects_materials[object].append(mat)
    
    # find objects that are likely to be the preview objects
    preview_objects = [o for o in objects_materials.keys() if o.name.startswith('preview')]
    if len(preview_objects) < 1:
        return

    # find the materials attached to the likely preview object
    likely_materials = objects_materials[preview_objects[0]]
    if len(likely_materials) < 1:
        return

    as_bin_path = util.realpath(bpy.context.user_preferences.addons['render_appleseed'].preferences.appleseed_bin_path)
    appleseed_exe = os.path.join( as_bin_path, "appleseed.cli")

    # Get the addon path so we can use the files in the material preview directory
    addon_prev_path = os.path.join(sep.join(util.realpath(__file__).split(sep)[:-1]), "mat_preview")
    tempdir = efutil.temp_directory()
    img_file = os.path.join(os.path.join(tempdir, "mat_preview"), "mat_preview.png")
    scene_file = os.path.join(os.path.join(tempdir,"mat_preview"), "mat_preview.appleseed")
    output_path = os.path.join(tempdir, "mat_preview")
    
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    temp_files = os.listdir(output_path)
    for item in os.listdir(addon_prev_path):
        if item not in temp_files:
            copyfile(os.path.join(addon_prev_path, item), os.path.join(output_path, item)) 
        
    prev_mat = likely_materials[0]
    exporter = project_file_writer.write_project_file()
    file_written = exporter.export_preview(scene, scene_file, addon_prev_path, prev_mat, width, height)
    if not file_written:
        print('Error while exporting -- check the console for details.')
        return;
    else:
        if not bpy.app.background:
            with open(scene_file,'r') as inf:
                threads = multiprocessing.cpu_count()
                # Check if version of appleseed.cli allows silencing of console: > 1.1.0-alpha-20
                encoding = getdefaultlocale()[1]
                if "alpha-21" in subprocess.Popen((appleseed_exe, "-v"), 
                                stdout = subprocess.PIPE, 
                                stderr = subprocess.STDOUT).communicate()[0].decode(encoding):
                    cmd = ( appleseed_exe, 
                    scene_file, 
                    '-o', img_file, 
                    '--threads', str( threads),
                    '--continuous-saving',
                    '--message-verbosity fatal')
                else:
                    cmd = ( appleseed_exe, 
                    scene_file, 
                    '-o', img_file, 
                    '--threads', str( threads),
                    '--continuous-saving')
                appleseed_proc = subprocess.Popen( cmd, stdout=subprocess.PIPE)
                returncode = appleseed_proc.communicate()
            if returncode[0] == b'':
                if os.path.exists(img_file):
                    try:
                        result = engine.begin_result( 0, 0, width, height)
                        lay = result.layers[0]
                        lay.load_from_file( img_file)
                        engine.end_result( result)
                    except:
                        pass
                else:
                    err_msg = 'Error: Could not load render result from %s' % img_file
                    print( err_msg)


def update_scene( engine, data, scene):
    if os.path.isdir( scene.appleseed.project_path):
        proj_name = None
    else:
        proj_name = scene.appleseed.project_path.split( os.path.sep)[-1]

def render_scene( engine, scene):
    # Export the scene
    bpy.ops.appleseed.export()
    
    DELAY = scene.appleseed.refresh_time

    if scene.appleseed.project_path == '':
        engine.report( {'INFO'}, "No project path has been specified!")
        return 
        
    project_dir = util.realpath( scene.appleseed.project_path)
    
    # Make the output directory, if it doesn't exist yet
    if not os.path.exists( project_dir):
        try:
            os.mkdir( project_dir)
        except:
            engine.report( {"INFO"}, "The project directory cannot be created. Check directory permissions.")
            return
            
    render_output = os.path.join( project_dir, "render")
    width = scene.render.resolution_x
    height = scene.render.resolution_y
    img_file = os.path.join( render_output,  ( scene.name + '_' + str( scene.frame_current) + scene.appleseed.img_extension))
    
    # Make the render directory, if it doesn't exist yet
    if not os.path.exists( render_output):
        try:
            os.mkdir( render_output)
        except:
            engine.report( {"INFO"}, "The project render directory cannot be created. Check directory permissions.")
            return
    
    # Set filename to render
    filename = scene.name
    if not filename.endswith( ".appleseed"):
        filename += ".appleseed"
    filename = os.path.join( project_dir, filename)
    
    # Get the absolute path to the executable dir
    # Test the path is specified and the executable exists
    as_bin_path = util.realpath( bpy.context.user_preferences.addons['render_appleseed'].preferences.appleseed_bin_path)
    if as_bin_path == '':
        engine.report({'INFO'}, "The path to appleseed executable has not been specified. Set the path in the addon user preferences.")
        return
    appleseed_exe = os.path.join( as_bin_path, ("appleseed.studio" if scene.appleseed.display_mode == 'STUDIO' else "appleseed.cli"))
    
    # Start the appleseed executable 
    if scene.appleseed.display_mode != "STUDIO":      
        scene.render.display_mode = scene.appleseed.display_mode  
        #If rendering with command line
        # Check if version of appleseed.cli allows silencing of console: > 1.1.0-alpha-20
        encoding = getdefaultlocale()[1]
        if "alpha-21" in subprocess.Popen((appleseed_exe, "-v"), 
                        stdout = subprocess.PIPE, 
                        stderr = subprocess.STDOUT).communicate()[0].decode(encoding):

            cmd = (appleseed_exe, 
                    filename, 
                    '-o', img_file, 
                    '--threads', str(threads),
                    '--continuous-saving',
                    '--message-verbosity fatal')
        else:
            cmd = ( appleseed_exe, 
                    filename, 
                    '-o', img_file, 
                    '--threads', str( scene.appleseed.threads), 
                    '--continuous-saving')

    else:
        # If rendering with GUI, we have two options
        if scene.appleseed.studio_rendering_mode == "PROGRESSIVE":
            cmd = os.path.join( as_bin_path, appleseed_exe) + ' ' + filename + " --render interactive"
        else:
            cmd = os.path.join( as_bin_path, appleseed_exe) + ' ' + filename + " --render final"
    
    process = subprocess.Popen( cmd, cwd = render_output, stdout=subprocess.PIPE)
    
    # Wait for the rendered image file to be created
    while not os.path.exists( img_file):
        if engine.test_break():
            try:
                process.kill()
            except:
                pass
            break

        if process.poll() != None:
            engine.update_stats( "", "Appleseed: Error")
            break

        time.sleep( DELAY)

    if os.path.exists( img_file):
        engine.update_stats( "", "Appleseed: Rendering")

        prev_size = -1

        def update_image():
            result = engine.begin_result( 0, 0, width, height)
            lay = result.layers[0]
            # it's possible the image wont load early on.
            try:
                lay.load_from_file( img_file)
            except:
                pass

            engine.end_result( result)

        # Update while rendering
        while True:
            if process.poll() != None:
                update_image()
                break

            # user exit
            if engine.test_break():
                try:
                    process.kill()
                except:
                    pass
                break

            # check if the file updated
            new_size = os.path.getsize( img_file)

            #if new_size != prev_size:
            update_image()
            #    prev_size = new_size

            time.sleep( DELAY)

class RenderAppleseed( bpy.types.RenderEngine):
    bl_idname = 'APPLESEED_RENDER'
    bl_label = 'appleseed'
    bl_use_preview = True

    lock = threading.Lock()
    
    animation = False
    
    def __init__( self):
        render_init( self)

    # final rendering
    def update( self, data, scene):
        update_start( self, data, scene)

    def render( self, scene):
        with self.lock:
            render_start( self, scene)
        
    #Need a function for rendering animation
#    frame_current = scene.frame_current
#    frame_start = scene.frame_start
#    frame_end = scene.frame_end
#    step = scene.frame_step
#    
#    frame_current = frame_start
#    
#    while frame_current <= frame_end:
#        render_start(self, scene)
#        frame_current += frame_step