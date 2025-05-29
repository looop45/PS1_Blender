import bpy
from bpy.types import Operator

'''New material'''
class PS1ENGINE_OT_new_material(Operator):
    bl_idname = "ps1.new_material"
    bl_label = "New PS1 Material"

    def execute(self, context):

        bpy.ops.node.new_node_tree(type="ps1ShaderTree")

        tree = bpy.data.node_groups[-1]

        obj = context.object
        if obj:
            obj.ps1_settings.node_tree = tree
            context.space_data.node_tree = tree
            self.report({'INFO'}, f"Assigned new ps1ShaderTree '{tree.name}' to {obj.name}")
        else:
            self.report({'WARNING'}, "No active object to assign node tree to!!!")
            
        return {'FINISHED'}
    
'''Unlink Material'''
class PS1ENGINE_OT_unlink_material(Operator):
    bl_idname = 'ps1.unlink_material'
    bl_label = "Unlink PS1 Material"

    def execute(self, context):
        obj = bpy.context.object
        if obj and obj.ps1_settings:
            obj.ps1_settings.node_tree = None

        return {'FINISHED'}

    
def register_operators():
    bpy.utils.register_class(PS1ENGINE_OT_new_material)

def unregister_operators():
    bpy.utils.unregister_class(PS1ENGINE_OT_new_material)
