import bpy
from bpy.types import Node
from .sockets import *
from ..engine.compile import get_variable_name

import string 

#Mix in class for polling
class PS1TreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ps1ShaderTree'
    
    def update(self):
        # Notify the tree that something has changed
        if self.id_data:
            self.id_data.update()


class PS1ShaderOutputNode(PS1TreeNode, Node):
    '''Final output node for PS1 materials.'''

    bl_idname = "ps1_output"
    bl_label = "Output Node"
    bl_icon = 'OUTPUT'

    normal_mode: bpy.props.EnumProperty( # type: ignore
        name = "Normal Mode",
        items=[
            ('FLA', "Flat", ""),
            ('GOU', "Gouraud", ""),
        ],
        default = 'FLA'
    )

    def init(self, context):
        self.inputs.new("PS1SocketColor", "Color")

    def draw_buttons(self, context, layout):
        layout.label(text="Normal Shading Mode")
        layout.prop(self, "normal_mode", text="")

    def draw_label(self):
        return "Output"
    
    def compile(self, inputs):
        color = inputs.get("Color", "vec3(0.0)")
        return f"vec3 out_col = {color};", "out_col"

'''Image Texture Node'''
class PS1TextureNode(PS1TreeNode, Node):
    '''Image texture node for PS1 renderer.'''
    bl_idname = "ps1TextureNode"
    bl_label = "Image Texture"
    bl_icon = 'TEXTURE'

    image: bpy.props.PointerProperty(name="Image", type=bpy.types.Image) # type: ignore

    def init(self, context):
        self.outputs.new("PS1SocketColor", "Color")

    def draw_buttons(self, context, layout):
        layout.template_ID(self, "image", open="image.open")

    def draw_label(self):
        return "Image Texture"
    
    def copy(self, node):
        self.image = node.image

    def required_uniforms(self):
        return {f"{self.name}_tex": self.image}
    
    def compile(self, inputs):
        out_var = f"{get_variable_name(self)}_out"
        tex_uniform = f"{get_variable_name(self)}_tex"
        code = f"vec3 {out_var} = texture({tex_uniform}, uv).rgb;" #for now, there is only one static uv set
        return code, out_var


'''RGB Color Node'''
class PS1ColorNode(PS1TreeNode, Node):
    '''RGB color output node.'''

    bl_idname = "ps1_color"
    bl_label = "Color"
    bl_icon = "COLOR"

    color: bpy.props.FloatVectorProperty( # type: ignore
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        update=update_callback
    )

    def init(self, context):
        self.outputs.new("PS1SocketColor", "Color")

    def draw_buttons(self, context, layout):
        pass
        layout.prop(self, "color")

    def draw_label(self):
        return "Color"
    
    def compile(self, inputs):
        r, g, b, _ = self.color
        out_var = f"{get_variable_name(self)}_color"
        code = f"vec3 {out_var} = vec3({r:.4f}, {g:.4f}, {b:.4f});" #vec3 for now
        return code, out_var
    
class PS1MixRGBNode(PS1TreeNode, Node):
    '''Mix RGB Node for PS1 Materials.'''

    bl_idname = "ps1_mix_rgb"
    bl_label = "MixRGB"
    bl_icon = 'NODE_COMPOSITING'

    blend_mode: bpy.props.EnumProperty( # type: ignore
        name = "Blend Mode",
        items=[
            ('NOR', "Normal", ""),
            ('MUL', "Multiply", ""),
            ('ADD', "Add", ""),
            ('SUB', "Subtract", ""),
            ('DIV', "Divide", ""),
            ('SCR', "Screen", ""),
        ],
        default = 'NOR'
    )

    def init(self, context): 
        self.inputs.new("PS1SocketFloat", "Factor")
        self.inputs.new("PS1SocketColor", "Color1")
        self.inputs.new("PS1SocketColor", "Color2")
        self.outputs.new("PS1SocketColor", "Color")

    def draw_buttons(self, context, layout):
        layout.prop(self, "blend_mode", text="")        

    def draw_label(self):
        return "Mix RGB"    
    
    def compile(self, inputs):
        fac = inputs.get("Factor", "0.5")
        color1 = inputs.get("Color1", "vec3(0.0)")
        color2 = inputs.get("Color2", "vec3(0.0)")
        out_var = f"{self.name}_mix"

        if self.blend_mode == 'NOR':
            expr = f"mix({color1}, {color2}, {fac})"
        elif self.blend_mode == 'MUL':
            expr = f"mix({color1}, {color1} * {color2}, {fac})"
        elif self.blend_mode == 'ADD':
            expr = f"mix({color1}, {color1} + {color2}, {fac})"
        elif self.blend_mode == 'SUB':
            expr = f"mix({color1}, {color1} - {color2}, {fac})"
        elif self.blend_mode == 'DIV':
            expr = f"mix({color1}, {color1} / max({color2}, vec3(0.0001)), {fac})"
        elif self.blend_mode == 'SCR':
            expr = f"mix({color1}, 1.0 - (1.0 - {color1}) * (1.0 - {color2}), {fac})"
        else:
            expr = f"mix({color1}, {color2}, {fac})"  # fallback to normal

        code = f"vec3 {out_var} = {expr};"
        return code, out_var


#######################
### Node Categories ###
#######################

import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class PS1NodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ps1ShaderTree'
    
node_categories = [
    PS1NodeCategory('PS1NODES', "PS1 Nodes", items =[
        NodeItem("ps1_output"),
        NodeItem("ps1TextureNode"),
        NodeItem("ps1_color"),
        NodeItem("ps1_mix_rgb"),
    ])
]

classes = (
    PS1ShaderOutputNode,
    PS1TextureNode,
    PS1ColorNode,
    PS1MixRGBNode,
)
    
#TODO::Change register list of node types
def register_nodes():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    nodeitems_utils.register_node_categories('PS1NODES', node_categories)

def unregister_nodes():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)