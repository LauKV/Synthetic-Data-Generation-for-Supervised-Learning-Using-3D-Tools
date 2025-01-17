import bpy
import math
import numpy as np
from mathutils import Matrix, Vector
from numpy.random import uniform
from tools.find import find_all_meshes


def get_vertices(obj_or_mesh: bpy.types.Object or bpy.types.Mesh, mode="obj"):
    """
    Get the vertices of the given object or mesh.

    Args:
        obj_or_mesh (bpy.types.Object or bpy.types.Mesh): The object or mesh.
        mode (str, optional): "obj" or "world". Object space or world space. Defaults to "obj".
    """
    meshes = find_all_meshes(obj_or_mesh)
    assert len(meshes) > 0, "No mesh found"
    mesh_list = []
    vertices_list = []
    for mesh in meshes:
        vertices = np.ones(len(mesh.data.vertices) * 3)
        mesh.data.vertices.foreach_get("co", vertices)
        vertices = vertices.reshape(-1, 3)  # (N, 3)
        vertices_list.append(vertices)
        mesh_list.append(mesh)

    if mode == "world":
        for i, (obj, vertices) in enumerate(zip(mesh_list, vertices_list)):
            vertices = np.concatenate([vertices, np.ones((len(vertices), 1))], axis=1)  # (N, 4)
            vertices = vertices @ np.array(obj.matrix_world).T  # (N, 4) @ (4, 4) -> (N, 4)
            vertices = vertices[:, :3]
            vertices_list[i] = vertices
    vertices = np.concatenate(vertices_list, axis=0)
    return vertices



def transform(obj_or_mesh: bpy.types.Object or bpy.types.Mesh, matrix: Matrix or np.ndarray):
    mesh = obj_or_mesh.data if isinstance(obj_or_mesh, bpy.types.Object) else obj_or_mesh
    mesh.transform(Matrix(matrix))
    mesh.update()


def center_vert_bbox(vertices, bbox_center=None, bbox_scale=None, scale=False):
    if bbox_center is None:
        bbox_center = (vertices.min(0) + vertices.max(0)) / 2
    vertices = vertices - bbox_center
    if scale:
        if bbox_scale is None:
            bbox_scale = np.linalg.norm(vertices, 2, 1).max()
        vertices = vertices / bbox_scale
    else:
        bbox_scale = 1
    return vertices, bbox_center, bbox_scale




def obj_bbox(obj: bpy.types.Object, ignore_matrix=False, mode="minmax"):
    """
    Compute the bounding box of the given object.

    Args:
        obj (bpy.types.Object): The object
        ignore_matrix (bool, optional): If True, ignore the matrix_world of the object. Defaults to False.
        mode (str, optional): "minmax" or "box". Defaults to "minmax".

    Returns:
        Tuple[Vector, Vector]: The minimum and maximum coordinates of the bounding box.
    """
    if mode == "minmax":
        bbox_min = (math.inf,) * 3
        bbox_max = (-math.inf,) * 3
        for obj in find_all_meshes(obj):
            for coord in obj.bound_box:
                coord = Vector(coord)
                if not ignore_matrix:
                    coord = obj.matrix_world @ coord
                bbox_min = tuple(min(x, y) for x, y in zip(bbox_min, coord))
                bbox_max = tuple(max(x, y) for x, y in zip(bbox_max, coord))
        return Vector(bbox_min), Vector(bbox_max)
    elif mode == "box":
        # return a 8 * 3 array
        bbox_min = (math.inf,) * 3
        bbox_max = (-math.inf,) * 3
        for obj in find_all_meshes(obj):
            for coord in obj.bound_box:
                coord = Vector(coord)
                bbox_min = tuple(min(x, y) for x, y in zip(bbox_min, coord))
                bbox_max = tuple(max(x, y) for x, y in zip(bbox_max, coord))
        # canonical box
        box = np.array(
            [
                [bbox_min[0], bbox_min[1], bbox_min[2]],
                [bbox_min[0], bbox_min[1], bbox_max[2]],
                [bbox_min[0], bbox_max[1], bbox_max[2]],
                [bbox_min[0], bbox_max[1], bbox_min[2]],
                [bbox_max[0], bbox_min[1], bbox_min[2]],
                [bbox_max[0], bbox_min[1], bbox_max[2]],
                [bbox_max[0], bbox_max[1], bbox_max[2]],
                [bbox_max[0], bbox_max[1], bbox_min[2]],
            ]
        )
        if not ignore_matrix:
            box = np.concatenate([box, np.ones((8, 1))], axis=1)
            box = box @ np.array(obj.matrix_world).T
            box = box[:, :3]
        return box
    else:
        raise ValueError(f"Unknown mode {mode}")
    

def normalize_obj(obj: bpy.types.Object):
    """
    Normalize the object to have unit bounding box and center at the world origin.
    """
    bbox_min, bbox_max = obj_bbox(obj)
    scale = 1 / max(bbox_max - bbox_min)
    obj.scale = obj.scale * scale
    # Apply scale to matrix_world.
    bpy.context.view_layer.update()
    bbox_min, bbox_max = obj_bbox(obj)
    offset = -(bbox_min + bbox_max) / 2
    obj.matrix_world = Matrix.Translation(offset) @ obj.matrix_world
    bpy.context.view_layer.update()



def look_at(obj: bpy.types.Object, target):
    """
    Point the given object at the target.
    """
    loc = np.array(obj.location)
    target = np.array(target)
    direction = target - loc
    direction = Vector(direction)
    rot_quat = direction.to_track_quat("-Z", "Y")
    obj.rotation_euler = rot_quat.to_euler()



def againts_wall(obj: bpy.types.Object, z=0):
    """
    Move the object to the wall. The wall is defined as the z coordinate of the lowest vertex.

    Args:
        obj (bpy.types.Object): The object.
        z (float, optional): The z coordinate of the wall. Defaults to 0.
    """
    vertices = get_vertices(obj, mode="world")
    obj.location[2] = -vertices[:, 2].min() + z


def random_loc(loc, radius=[0, 1], theta=[-0.5, 0.5], phi=[-1, 1]):
    radius = uniform(radius[0], radius[1])
    theta = uniform(theta[0], theta[1]) * np.pi
    phi = uniform(phi[0], phi[1]) * np.pi
    loc += (
        np.array(
            [
                np.cos(phi) * np.cos(theta),
                np.cos(phi) * np.sin(theta),
                np.sin(phi),
            ]
        )
        * radius
    )
    return loc


def persp_project(points3d, cam_intr):
    hom_2d = np.array(cam_intr).dot(points3d.transpose()).transpose()
    points2d = (hom_2d / (hom_2d[:, 2:] + 1e-6))[:, :2]
    return points2d.astype(np.float32)

