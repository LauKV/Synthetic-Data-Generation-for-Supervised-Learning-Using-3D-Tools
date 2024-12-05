import ssl
import certifi
import bpy
import numpy as np
import sys
import os
import random

#sys.path.append('/home/vazqueza/5A/ProjetRI/PyBlend/PyBlend/scripts')
sys.path.append('/home/opdal/Bureau/5GMM/Synthetic-Data-Generation-for-Supervised-Learning-Using-3D-Tools/PYBLEND')

from object import load_obj, create_plane, enable_shaow_catcher, center
# from PyBlend.pyblend.viztools import plot_corner
from PyBlend.pyblend.find import find_all_objects
from PyBlend.pyblend.lighting import config_world, create_light
from PyBlend.pyblend.camera import get_camera_para
from PyBlend.pyblend.utils import BlenderRemover, ArgumentParserForBlender
from PyBlend.pyblend.transform import look_at, normalize_obj, random_loc, obj_bbox, persp_project, againts_wall
from PyBlend.pyblend.render import (
    config_render,
    render_image,
    enable_segmentation_render,
    enable_depth_render,
    enable_normal_render,
)

from background import set_hdri_background

ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = lambda: ssl_context



def load_and_combine_objects(filepath):
    """
    Load all objects from a Blender file, combine them into a single object,
    and return the combined object.

    Parameters:
    filepath (str): The path to the Blender file.

    Returns:
    bpy.types.Object: The combined object containing all loaded objects with their materials.
    """
    # Load all objects from the file
    with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
        data_to.objects = data_from.objects[:]  # Load all objects

    # Create a list to store the successfully loaded objects
    loaded_objects = []

    # Link all objects to the active collection in the current scene
    for obj in data_to.objects:
        if obj:  # Ensure the object is not None
            bpy.context.collection.objects.link(obj)
            loaded_objects.append(obj)

    # Make all objects local to the current scene
    bpy.ops.object.select_all(action='DESELECT')  # Deselect all objects
    for obj in loaded_objects:
        obj.select_set(True)  # Select each object
    bpy.ops.object.make_local(type='ALL')  # Make them local to the current scene

    # Ensure we have objects to combine
    if not loaded_objects:
        raise RuntimeError("No objects were loaded from the file.")

    # Deselect all objects first
    bpy.ops.object.select_all(action='DESELECT')

    # Select all the newly added objects
    for obj in loaded_objects:
        obj.select_set(True)

    # Set the active object to the first object in the list
    bpy.context.view_layer.objects.active = loaded_objects[0]

    # Switch to Object mode to perform the join operation
    bpy.ops.object.mode_set(mode='OBJECT')

    # Join all selected objects into one
    bpy.ops.object.join()

    print("All objects joined into one.")

    # Return the final joined object
    return bpy.context.view_layer.objects.active


def load_objects(object_paths):
    objects = []
    for i, obj_path in enumerate(object_paths):
        if args.input.endswith(".blend"):
            print("Blend object!")
            obj = load_and_combine_objects(obj_path) # load_mesh_with_materials_original(args.input) # append_and_join_objects(args.input) 
            print(obj)
            center(obj, "object")
            objects.append(obj)
        else: 
            obj = load_obj(obj_path, f"object_{i}", center=True, join=True)
            objects.append(obj)
    return objects

def main(args):
    random.seed(42)
    np.random.seed(42)

    # Set up paths
    object_paths = args.obj_paths.split(",")
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    # Configuring Blender
    config_render(res_x=640, res_y=640, transparent=False)
    remover = BlenderRemover()
    remover.clear_all()
    config_world(0.3)

    # Set HDRI background if provided
    if args.background:
        set_hdri_background(args.background)

    # Create floor plane
    plane = create_plane((0, 0, -1), (0, 0, 0), (20, 20, 20), name="floor")
    enable_shaow_catcher(plane)

    # Load objects
    objects = load_objects(object_paths)

    # Enable render passes
    exr_seg_node, png_seg_node = enable_segmentation_render(f"{output_dir}", max_value=len(objects))
    exr_depth_node, png_depth_node = enable_depth_render(f"{output_dir}", reverse=True)
    png_normal_node = enable_normal_render(f"{output_dir}")
    png_seg_node.file_slots[0].path = f"seg_{args.name}_"
    #exr_seg_node.file_slots[0].path = f"seg_"
    png_depth_node.file_slots[0].path = f"depth_{args.name}_"
    #exr_depth_node.file_slots[0].path = f"depth_"
    png_normal_node.file_slots[0].path = f"normal_{args.name}_"

    # Rendering loop
    camera = bpy.data.objects["Camera"]
    render_counter = 0  # To track unique filenames
    for scene_idx in range(args.num_scenes):
        for obj_idx, obj in enumerate(objects):
            normalize_obj(obj)
            againts_wall(obj, z=-1)
            for obj_part in find_all_objects(obj):
                obj_part.pass_index = obj_idx + 1

        for view_idx in range(args.num_views):
            camera.location = random_loc((0, 0, 0), (8, 8), theta=(-1, 1), phi=(0, 1))
            look_at(camera, (0, 0, 0))
            bpy.context.view_layer.update()

            # Generate unique filenames for each render
            base_filename = f"{output_dir}/render_{args.name}_{render_counter:05d}"
            bpy.context.scene.frame_current = scene_idx * args.num_views + view_idx
            render_image(f"{base_filename}.png")
            render_counter += 1

    remover.clear_all()

if __name__ == "__main__":
    parser = ArgumentParserForBlender()
    parser.add_argument("--obj_paths", type=str, required=True, help="Comma-separated list of paths to object files")
    parser.add_argument("--background", type=str, required=True, help="Path to the HDRI background image")
    parser.add_argument("--output_dir", type=str, default="output", help="Directory to save the output images")
    parser.add_argument("--num_scenes", type=int, default=1, help="Number of scenes to render")
    parser.add_argument("--num_views", type=int, default=2, help="Number of views per scene")
    parser.add_argument("--name", type=str, required=True, help="Name of the object(s)")
    args = parser.parse_args()
    main(args)
