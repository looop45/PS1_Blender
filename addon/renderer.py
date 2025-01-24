import bpy
import os
import subprocess
import socket
import array
import threading
import time
import sys
import json
import numpy as np

from . import base
from .engine import *
from .client import *


@base.register_class 
class PS1RenderEngine(bpy.types.RenderEngine):
    bl_idname = "PS1"
    bl_label = "PS1 Render Engine"

    display_thread = None
    connected = False

    def __init__(self):
        self.scene_data = None
        self.draw_data = None

        #start Host
        try:
            pass
            p = subprocess.Popen( ["/Users/connermurray/dev/ps1_blender_addon/build/PS1_Render_Engine"], 
                                 stdout=sys.stdout, 
                                 stderr=sys.stderr
                                 )

        except subprocess.CalledProcessError as e:
            print(f"Error running C++ Host: {e}")
            print(e.output)

        time.sleep(1)

        self.engine = Engine()
        self.renderedView = False
        self.connected = True


    def __del__(self):
        self.engine.stop()
        print("Connection closed")
    
     # This is the method called by Blender for both final renders (F12) and
    # small preview for materials, world and lights.
    def render(self, depsgraph):
        scene = depsgraph.scene
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)

        # Fill the render result with a flat color. The framebuffer is
        # defined as a list of pixels, each pixel itself being a list of
        # R,G,B,A values.
        if self.is_preview:
            color = [0.1, 0.2, 0.1, 1.0]
        else:
            color = [0.2, 0.1, 0.1, 1.0]

        pixel_count = self.size_x * self.size_y
        rect = [color] * pixel_count

        # Here we write the pixel values to the RenderResult
        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect = rect
        self.end_result(result)

    # For viewport renders, this method gets called once at the start and
    # whenever the scene or 3D viewport changes. This method is where data
    # should be read from Blender in the same thread. Typically a render
    # thread will be started to do the work while keeping Blender responsive.
    def view_update(self, context, depsgraph):
        # Send scene updates to render server
        #print("sending...")
        pass
        #print(f"Received: {response}")
            

    # For viewport renders, this method is called whenever Blender redraws
    # the 3D viewport. The renderer is expected to quickly draw the render
    # with OpenGL, and not perform other expensive work.
    # Blender will draw overlays for selection and editing on top of the
    # rendered image automatically.
    def view_draw(self, context, depsgraph):
        if (not self.connected):
            print("Connection not started yet")
            return
        #print("Starting Draw Request...")
        self.region = context.region
        self.scene = depsgraph.scene #This is a huge blunder, don't know a way around it yet

        # Set render flag  to false
        self.renderedView = False

        # Get viewport dimensions
        self.width = int(self.region.width)//2
        self.height = int(self.region.height)//2

        #get display info from renderer
        self.engine.draw_request("Camera", self.width, self.height) # camera placeholder
        # Wait until the entire frame has been received

        while not self.renderedView:
            self.engine.client.receive_data( self )


    def processMessage(self, header_sizeBytes, header_messageType, data):
        if header_messageType == ServerMessage.Result:

            # Lazily import GPU module, so that the render engine works in
            # background mode where the GPU module can't be imported by default.
            import gpu

            num_floats = len(data) // struct.calcsize('f')  # 'f' format for 4-byte floats

            # Unpack the byte data into a list of floats
            data = struct.unpack(f'{num_floats}f', data)

            dimensions = (self.width, self.height)

            #print("Actual: ", len(data), " Expected: ", width * height * 4)

            # Bind shader that converts from scene linear to display space,
            gpu.state.blend_set('ALPHA_PREMULT')
            self.bind_display_space_shader(self.scene)
            
            self.draw_data = CustomDrawData(dimensions, data)

            self.draw_data.draw()

            self.unbind_display_space_shader()
            gpu.state.blend_set('NONE')
            self.renderedView = True



class CustomDrawData:
    def __init__(self, dimensions, pixels):
        import gpu

        # Generate dummy float image buffer
        self.dimensions = dimensions
        width, height = dimensions

        pixels = gpu.types.Buffer('FLOAT', width * height * 4, pixels)

        # Generate texture
        self.texture = gpu.types.GPUTexture((width, height), format='RGBA16F', data=pixels)

        # Note: This is just a didactic example.
        # In this case it would be more convenient to fill the texture with:
        # self.texture.clear('FLOAT', value=[0.1, 0.2, 0.1, 1.0])

    def __del__(self):
        del self.texture

    def draw(self):
        from gpu_extras.presets import draw_texture_2d
        draw_texture_2d(self.texture, (0, 0), self.texture.width*2, self.texture.height*2)

def get_panels():
    exclude_panels = {
        'VIEWLAYER_PT_filter',
        'VIEWLAYER_PT_layer_passes',
    }

    panels = []
    for panel in bpy.types.Panel.__subclasses__():
        if hasattr(panel, 'COMPAT_ENGINES') and 'BLENDER_RENDER' in panel.COMPAT_ENGINES:
            if panel.__name__ not in exclude_panels:
                panels.append(panel)

    return panels


def register():
    # Register the RenderEngine
    bpy.utils.register_class(PS1RenderEngine)

    for panel in get_panels():
        panel.COMPAT_ENGINES.add('CUSTOM')


def unregister():
    bpy.utils.unregister_class(PS1RenderEngine)

    for panel in get_panels():
        if 'CUSTOM' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('CUSTOM')
