import bpy


def find_parent(obj: bpy.types.Object):
    while obj.parent:
        obj = obj.parent
    return obj


def find_all_meshes(obj: bpy.types.Object, parent=True):
    """
    Find all meshes in the given object and its children.

    Args:
        obj (bpy.types.Object): The object.

    Returns:
        List[bpy.types.Object]: The list of meshes.
    """
    if parent:
        obj = find_parent(obj)
    meshes = []
    if isinstance(obj.data, bpy.types.Mesh):
        meshes.append(obj)
    for child in obj.children:
        meshes.extend(find_all_meshes(child, parent=False))
    return meshes

def find_all_objects(obj: bpy.types.Object):
    """
    Find all objects in the given object and its children.

    Args:
        obj (bpy.types.Object): The object.

    Returns:
        List[bpy.types.Object]: The list of objects.
    """
    objs = []
    objs.append(obj)
    for child in obj.children:
        objs.extend(find_all_objects(child))
    return objs

