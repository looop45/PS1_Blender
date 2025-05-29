import bpy
from bpy.types import Node

#Mix in class for polling
class PS1TreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ps1ShaderTree'

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
        self.inputs.new("NodeSocketColor", "Color")

    def draw_buttons(self, context, layout):
        layout.label(text="Normal Shading Mode")
        layout.prop(self, "normal_mode", text="")

    def draw_label(self):
        return "Output"

'''Image Texture Node'''
class PS1TextureNode(PS1TreeNode, Node):
    '''Image texture node for PS1 renderer.'''

    bl_idname = "ps1_texture"
    bl_label = "Image Texture"
    bl_icon = 'TEXTURE'

    image: bpy.props.PointerProperty(name="Image", type=bpy.types.Image) # type: ignore

    def init(self, context):
        
        self.outputs.new("NodeSocketColor", "Color")

    def draw_buttons(self, context, layout):
        layout.template_ID(self, "image", open="image.open")

    def draw_label(self):
        return "Image Texture"
    
    def copy(self, node):
        self.image = node.image


'''RGB Color Node'''
class PS1ColorNode(PS1TextureNode, Node):
    '''RGB color output node.'''

    bl_idname = "ps1_color"
    bl_label = "Color"
    bl_icon = "COLOR"

    color: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0,
        max=1.0
    ) # type: ignore

    def init(self, context):
        self.outputs.new("NodeSocketColor", "Color")

    def draw_buttons(self, context, layout):
        layout.prop(self, "color")

    def draw_label(self):
        return "Color"
    
class PS1MixRGBNode(PS1TreeNode, Node):
    '''Mix RGB Node for PS1 Materials.'''

    bl_idname = "ps1_mix_rgb"
    bl_label = "Mix RGB"
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

    factor: bpy.props.FloatProperty( # type: ignore
        name="Factor",
        default=1.0,
        min=0.0,
        max=1.0
    )

    def init(self, context):
        self.inputs.new("NodeSocketFloat", "Factor")
        self.inputs.new("NodeSocketColor", "Color1")
        self.inputs.new("NodeSocketColor", "Color2")
        self.outputs.new("NodeSocketColor", "Color")

    def draw_buttons(self, context, layout):
        layout.prop(self, "blend_mode", text="")
        layout.prop(self, "fac", text="Fac")

    def draw_label(self):
        return "Mix RGB"    


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
        NodeItem("ps1_texture"),
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