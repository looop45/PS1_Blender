import bpy
from bpy.types import Panel

class PS1ENGINE_PT_material_panel(Panel):
    bl_label = "PS1 Shader Panel"
    bl_idname = "PS1_ENGINE_PT_material_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'PS1'

    def draw(self, context):
        layout = self.layout
        material = context.material
        row = layout.row()
        row.template_ID(material, "node_tree", new="node.new_node_tree")


def register_material_panel():
    pass
    #bpy.utils.register_class(PS1ENGINE_PT_material_panel)

def unregister_material_panel():
    pass
    #bpy.utils.unregister_class(PS1ENGINE_PT_material_panel)