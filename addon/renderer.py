import bpy
import os
import subprocess
import socket
import array
import threading
import time
import sys
import queue

from . import base
from .host import server_host


@base.register_class
class PS1RenderEngine(bpy.types.RenderEngine):
    bl_idname = "PS1"
    bl_label = "PS1 Render Engine"

    host_addr = "127.0.0.1"
    port = 6969
    host = None

    connection = None

    def __init__(self):
        self.scene_data = None
        self.draw_data = None

        #start host
        self.host = server_host(self.host_addr, self.port)

        time.sleep(1)

        #start client
        try:
            '''result = subprocess.run(
                ["/Users/connermurray/dev/ps1_blender_addon/build/PS1_Render_Engine"],  # Replace with the actual path to your C++ client executable
                check=True,
                text=True,
                stdout=sys.stdout
            )'''
            p = subprocess.Popen( ["/Users/connermurray/dev/ps1_blender_addon/build/PS1_Render_Engine"], stdout=sys.stdout, stderr=sys.stderr)
            #p.communicate()

        except subprocess.CalledProcessError as e:
            print(f"Error running C++ client: {e}")
            print(e.output)

        self.host.connect()

        #server_thread = threading.Thread(target=update_thread, daemon=True, args=(self.host, self))
        #server_thread.start()

        print(self.host.conn)



    def __del__(self):
        pass
    
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
        # send info to client
        # Send a test string to the client
        test_string = "Hello from Python Server!"
        self.host.conn.sendall(test_string.encode('utf-8'))
        print(f"Sent: {test_string}")
            


    # For viewport renders, this method is called whenever Blender redraws
    # the 3D viewport. The renderer is expected to quickly draw the render
    # with OpenGL, and not perform other expensive work.
    # Blender will draw overlays for selection and editing on top of the
    # rendered image automatically.
    def view_draw(self, context, depsgraph):
        # Recv pixel data

        self.host.conn.recv()

        # Lazily import GPU module, so that the render engine works in
        # background mode where the GPU module can't be imported by default.
        import gpu

        region = context.region
        scene = depsgraph.scene

        # Get viewport dimensions
        dimensions = region.width, region.height

        # Bind shader that converts from scene linear to display space,
        gpu.state.blend_set('ALPHA_PREMULT')
        self.bind_display_space_shader(scene)

        if not self.draw_data or self.draw_data.dimensions != dimensions:
            self.draw_data = CustomDrawData(dimensions)

        self.draw_data.draw()

        self.unbind_display_space_shader()
        gpu.state.blend_set('NONE')

class CustomDrawData:
    def __init__(self, dimensions):
        import gpu

        # Generate dummy float image buffer
        self.dimensions = dimensions
        width, height = dimensions

        pixels = width * height * array.array('f', [0.1, 0.2, 0.1, 1.0])
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
        draw_texture_2d(self.texture, (0, 0), self.texture.width, self.texture.height)

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
