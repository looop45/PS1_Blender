import bpy
import gpu
import numpy as np
from gpu_extras.batch import batch_for_shader
from gpu.types import GPUShader, GPUBatch, GPUVertBuf, GPUIndexBuf
from mathutils import Matrix
from ..engine.compile import compile_tree

class PS1RenderEngine(bpy.types.RenderEngine):
    bl_idname = "PS1"
    bl_label = "PS1"
    bl_use_shading_nodes_custom = True
    bl_use_preview = False  # No material previews
    
    display_thread = None
    connected = False

    shaders = {}

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

        #obj.matrix_world.copy()

        vertices = np.empty((len(mesh.vertices), 3), 'f')
        indices = np.empty((len(mesh.loop_triangles), 3), 'i')

        mesh.vertices.foreach_get("co", np.reshape(vertices, len(mesh.vertices) * 3))
        mesh.loop_triangles.foreach_get("vertices", np.reshape(indices, len(mesh.loop_triangles) * 3))
        
        # Upload to GPU
        shader = self.get_shader(obj)
        self.objects[obj] = batch_for_shader(self.get_shader(obj), 'TRIS', {"pos": vertices}, indices=indices)
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
            if obj.type == 'MESH':
                shader = self.get_shader(obj)
                shader.bind()
                matrix = bpy.context.region_data.perspective_matrix
                shader.uniform_float("viewProjectionMatrix", matrix)
                shader.uniform_float("modelMatrix", obj.matrix_world)
                batch.draw(shader)
        
        gpu.state.depth_test_set('NONE')
        self.unbind_display_space_shader()

    def create_shader(self, obj):
        print("COMPILING SHADER")
            shader_info = gpu.types.GPUShaderCreateInfo()
            shader_info.push_constant('MAT4', "viewProjectionMatrix")
            shader_info.push_constant('MAT4', "modelMatrix")

            tree = obj.ps1_settings.node_tree
            if tree == None:
                return gpu.shader.from_builtin('POLYLINE_UNIFORM_COLOR')
            compile_result = compile_tree(tree)

            #loop through and declare all uniforms TODO

            shader_info.vertex_in(0, 'VEC3', "position")
            #Need to bring in normals here
            shader_info.fragment_out(0, 'VEC4', "fragColor")

            shader_info.vertex_source(
                "void main()"
                "{"
                "  gl_Position = viewProjectionMatrix * modelMatrix * vec4(position, 1.0f);"
                "}"
            )

            shader_info.fragment_source(compile_result.as_glsl())

            self.shaders[obj.name] = gpu.shader.create_from_info(shader_info)
            del shader_info

    def get_shader(self, obj):
        if obj.name not in self.shaders:
            
        return self.shaders[obj.name]


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
