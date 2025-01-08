import bpy

def get_mesh(depsgraph):
   for bl_mesh in 

def get_meshes(depsgraph):
    pass

def get_camera(depsgraph):
    pass

def get_materials(depsgraph):
    pass

def get_material(depsgraph):
    pass

def get_active_scene():
    return bpy.context.scene()

def get_active_scene_name():
    return get_active_scene.name