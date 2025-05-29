import bpy
from bpy.app.handlers import persistent

_last_seen_tree = None
_draw_handler = None

def update_node_editor_tree(context):
    obj = context.object

    area = next((a for a in context.screen.areas if a.type == 'NODE_EDITOR'), None)
    if not area:
        return

    space = area.spaces.active
    if space.tree_type != "ps1ShaderTree":
        return

    if obj and obj.ps1_settings and obj.ps1_settings.node_tree:
        space.node_tree = obj.ps1_settings.node_tree
    else:
        space.node_tree = None

def sync_from_editor_to_object():
    global _last_seen_tree

    context = bpy.context
    obj = context.object

    for area in context.screen.areas:
        if area.type != 'NODE_EDITOR':
            continue
        for space in area.spaces:
            if space.type == 'NODE_EDITOR' and space.tree_type == "ps1ShaderTree":
                current_tree = space.node_tree
                if current_tree != _last_seen_tree:
                    if obj and hasattr(obj, "ps1_settings"):
                        obj.ps1_settings.node_tree = current_tree
                    _last_seen_tree = current_tree

@persistent
def depsgraph_update_handler(scene):
    context = bpy.context
    update_node_editor_tree(context)

def node_editor_draw_handler():
    sync_from_editor_to_object()

def register_handlers():
    #Register depsgraph handler
    if depsgraph_update_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(depsgraph_update_handler)

    #Register UI draw handler
    global _draw_handler
    if _draw_handler is None:
        _draw_handler = bpy.types.SpaceNodeEditor.draw_handler_add(
            node_editor_draw_handler, (), 'WINDOW', 'POST_PIXEL')


def unregister_handlers():
    if depsgraph_update_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(depsgraph_update_handler)

    global _draw_handler
    if _draw_handler is not None:
        bpy.types.SpaceNodeEditor.draw_handler_remove(_draw_handler, 'WINDOW')
        _draw_handler = None
