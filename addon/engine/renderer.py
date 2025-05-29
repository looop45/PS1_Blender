import bpy
import gpu
import numpy as np
from gpu_extras.batch import batch_for_shader
from gpu.types import GPUShader, GPUBatch, GPUVertBuf, GPUIndexBuf
from mathutils import Matrix

class PS1RenderEngine(bpy.types.RenderEngine):
    bl_idname = "PS1"
    bl_label = "PS1"
    bl_use_shading_nodes_custom = True
    bl_use_preview = False  # No material previews
    
    display_thread = None
    connected = False

    def __init__(self):
        self.shader = None
        self.objects = {}
        self.initialized = False  # Track first-time setup

    def __del__(self):
        self.objects.clear()

    def render(self, depsgraph):
        self.report({'INFO'}, "Final rendering is not implemented, use viewport render")


    def view_update(self, context, depsgraph):

        if not self.initialized:
            for instance in depsgraph.object_instances:
                obj = instance.object
                if obj.type == 'MESH':
                    self.upload_mesh(obj, depsgraph)
            self.initialized = True

        # Detect changes in scene objects
        for update in depsgraph.updates:
            obj = update.id
            if isinstance(obj, bpy.types.Object) and obj.type == 'MESH':
                self.upload_mesh(obj, depsgraph)

        # Remove deleted objects
        #self.objects = {obj: data for obj, data in self.objects.items() if obj in depsgraph.object_instances}
            

    def upload_mesh(self, obj, depsgraph: bpy.types.Depsgraph):
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        
        mesh.calc_loop_triangles()

        obj.matrix_world.copy()

        verts = [v.co[:] for v in mesh.vertices]
        tris = [loop.vertex_index for tri in mesh.loop_triangles for loop in tri.loops]
        normals = [v.normal[:] for v in mesh.vertices]
        
        # Upload to GPU
        self.objects[obj] = batch_for_shader(self.get_shader(), 'TRIS', {"position": verts}, indices=tris)
        eval_obj.to_mesh_clear()

    # For viewport renders, this method is called whenever Blender redraws
    # the 3D viewport. The renderer is expected to quickly draw the render
    # with OpenGL, and not perform other expensive work.
    # Blender will draw overlays for selection and editing on top of the
    # rendered image automatically.
    def view_draw(self, context, depsgraph):
        region = context.region
        rv3d = context.region_data

        view_matrix = rv3d.view_matrix
        proj_matrix = rv3d.window_matrix

        self.bind_display_space_shader(depsgraph.scene)
        gpu.state.depth_test_set('LESS')
        gpu.state.face_culling_set('BACK')
        gpu.state.front_facing_set(True)

        fb = gpu.state.active_framebuffer_get()
        fb.clear(color=(0, 0, 0, 1))

        for obj, batch in self.objects.items():
            shader = self.get_shader()
            shader.bind()
            matrix = bpy.context.region_data.perspective_matrix
            shader.uniform_float("viewProjectionMatrix", matrix)
            shader.uniform_float("modelMatrix", obj.matrix_world)
            shader.uniform_float("color", (1, 0.2, 0.1, 1))
            batch.draw(shader)
        
        gpu.state.depth_test_set('NONE')
        self.unbind_display_space_shader()

    def get_shader(self):
        if not self.shader:
            shader_info = gpu.types.GPUShaderCreateInfo()
            shader_info.push_constant('MAT4', "viewProjectionMatrix")
            shader_info.push_constant('MAT4', "modelMatrix")
            shader_info.push_constant('VEC4', "color")
            shader_info.vertex_in(0, 'VEC3', "position")
            shader_info.fragment_out(0, 'VEC4', "FragColor")

            shader_info.vertex_source(
                "void main()"
                "{"
                "  gl_Position = viewProjectionMatrix * modelMatrix * vec4(position, 1.0f);"
                "}"
            )

            shader_info.fragment_source(
                "void main()"
                "{"
                "  FragColor = color; "
                "}"
            )

            self.shader = gpu.shader.create_from_info(shader_info)
            del shader_info
        return self.shader


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


def register_engine():
    # Register the RenderEngine
    bpy.utils.register_class(PS1RenderEngine)

    for panel in get_panels():
        panel.COMPAT_ENGINES.add('CUSTOM')


def unregister_engine():
    bpy.utils.unregister_class(PS1RenderEngine)

    for panel in get_panels():
        if 'CUSTOM' in panel.COMPAT_ENGINES:
            panel.COMPAT_ENGINES.remove('CUSTOM')
