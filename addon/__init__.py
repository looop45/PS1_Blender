bl_info = {
    "name": "PS1_Renderer",
    "description": "An open-source renderer that mimics the unique style and limitations of the PS1 hardware.",
    "author": "Conner Murray",
    "version": (0, 0, 1),
    "blender": (4, 3, 2), 
    "location": "Info > RenderEngine",
    "warning": "Still under development", # used for warning icon and text in addons panel
    "category": "Render"}

import bpy
import os

from .engine.renderer import register_engine, unregister_engine
from .nodes.basic_nodes import register_nodes, unregister_nodes
from .node_tree.shader_tree import register_node_tree, unregister_node_tree
from .ui.operators import register_operators, unregister_operators
from .ui.panel_material import register_material_panel, unregister_material_panel
from .ui.header import register_header, unregister_header
from .ui.handlers import register_handlers, unregister_handlers
from .nodes.sockets import register_sockets, unregister_sockets

def register():
    register_node_tree()
    register_sockets()
    register_nodes()
    register_engine()
    register_operators()
    register_material_panel()
    register_header()
    register_handlers()

def unregister():
    unregister_handlers()
    unregister_header()
    unregister_material_panel()
    unregister_engine()
    unregister_nodes()
    unregister_sockets()
    unregister_operators()
    unregister_node_tree()