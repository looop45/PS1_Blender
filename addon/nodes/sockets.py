import bpy
from bpy.types import NodeSocket

class PS1SocketFloat(NodeSocket):
    bl_idname = "PS1SocketFloat"
    bl_label = "Float Socket"

    default_value: bpy.props.FloatProperty( # type: ignore
        name="Float",
        default=1.0,
        min=0.0,
        max=1.0
    )

    def draw(self, context, layout, node, text):
        layout.prop(self, "default_value", text=text, slider=True)

    def draw_color(self, context, node):
        return (0.7, 0.7, 0.7, 1.0)
    
class PS1SocketColor(NodeSocket):
    bl_idname = "PS1SocketColor"
    bl_label = "Color Socket"

    default_value: bpy.props.FloatVectorProperty( # type: ignore
        name="Color",
        subtype='COLOR',
        size=4,
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0,
        max=1.0
    )

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        return (0.1, 0.95, 0.25, 1.0)
    
classes = (
    PS1SocketFloat,
    PS1SocketColor
)

def register_sockets():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister_sockets():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)