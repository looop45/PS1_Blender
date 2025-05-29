import bpy

_original_node_header_draw = None

def PS1_node_editor_header_draw(self, context):
    layout = self.layout
    space = context.space_data
    snode = space
    tree_type = space.tree_type
    id = space.node_tree

    # 1. Workspace / context selector
    layout.template_header()

    # 4. Add menu (shows if the node tree is valid)

    layout.menu("NODE_MT_add", text="Add")

    layout.separator()

    # 2. ID block (shows tree selector + "New" + Unlink)
    if tree_type == "ps1ShaderTree":
        layout.template_ID(snode, "node_tree", new="ps1.new_material", unlink="ps1.unlink_material")
    else:
        layout.template_ID(snode, "node_tree", new="node.new_node_tree", unlink="node.unlink_node_tree")

    # 3. Fake user icon
    if id:
        layout.prop(id, "use_fake_user", text="", emboss=False)

    layout.separator()

    # 5. Standard utility toggles
    #layout.prop(snode, "use_auto_render", text="Auto", toggle=True)
    #layout.prop(snode, "show_annotation", text="", icon='ANNOTATE')
    #layout.prop(snode, "pin", text="", icon='PINNED' if snode.pin else 'UNPINNED')

def register_header():
    global _original_node_header_draw

    _original_node_header_draw = bpy.types.NODE_HT_header.draw
    bpy.types.NODE_HT_header.draw = PS1_node_editor_header_draw


def unregister_header():
    global _original_node_header_draw

    if _original_node_header_draw:
        bpy.types.NODE_HT_header.draw = _original_node_header_draw
        _original_node_header_draw = None