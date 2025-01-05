bl_info = {
    "name": "PS1_Renderer",
    "description": "An open-source renderer that mimicks the unique style and limitations of the PS1 hardware.",
    "author": "Conner Murray",
    "version": (0, 0, 1),
    "blender": (4, 3, 2), 
    "location": "Info > RenderEngine",
    "warning": "Still under development", # used for warning icon and text in addons panel
    "category": "Render"}

import bpy
import os

from . import base
from . import renderer


def register():
    base.register()

def unregister():
   base.unregister()
