import bpy
from bpy.types import NodeTree

'''Node Tree Class'''
class PS1ShaderTree(NodeTree):
    bl_idname = 'ps1ShaderTree'
    bl_label = "PS1 Material"
    bl_icon = 'MATSHADERBALL'


    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PS1'

'''Add custom node tree as property of objects'''
class PS1ObjectSettings(bpy.types.PropertyGroup):
    pass

def register_node_tree():
    bpy.utils.register_class(PS1ObjectSettings)
    PS1ObjectSettings.node_tree = bpy.props.PointerProperty(
    name="PS1 Node Tree",
    type=bpy.types.NodeTree,
    poll=lambda self, tree: tree.bl_idname == "ps1ShaderTree"
)
    bpy.types.Object.ps1_settings = bpy.props.PointerProperty(type=PS1ObjectSettings)
    bpy.utils.register_class(PS1ShaderTree) 

def unregister_node_tree():
    del bpy.types.Object.ps1_settings
    bpy.utils.unregister_class(PS1ObjectSettings)
    bpy.utils.unregister_class(PS1ShaderTree)
