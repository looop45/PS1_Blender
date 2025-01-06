import bpy

# a global container is used to keep all lambda function to register classes
REGISTRARS = []
def registrar(register, unregister, name=None):
    global REGISTRARS
    if name is None or not [True for _, _, n in REGISTRARS if n == name]:
        REGISTRARS.append((register, unregister, name))

# register a class in blender system
def register_class(cls):
    registrar(lambda: bpy.utils.register_class(cls), lambda: bpy.utils.unregister_class(cls), cls.__name__)
    return cls

# register registrars
def register():
    for r, _, _ in REGISTRARS:
        r()


# unregister registrars
def unregister():
    for _, u, _ in reversed(REGISTRARS):
        u()