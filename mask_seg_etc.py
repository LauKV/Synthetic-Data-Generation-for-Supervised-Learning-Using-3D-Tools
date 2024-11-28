import ssl             #####################
import certifi
import bpy
import numpy as np
import sys
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = lambda: ssl_context            ##########""
sys.path.append('/home/vazqueza/5A/ProjetRI/PyBlend/PyBlend/scripts')


import cv2
import bpy
import random
import numpy as np
from pyblend.object import load_obj
from pyblend.viztools import plot_corner
from pyblend.find import find_all_objects
from pyblend.lighting import config_world
from pyblend.camera import get_camera_para
from pyblend.utils import BlenderRemover, ArgumentParserForBlender
from pyblend.transform import look_at, normalize_obj, random_loc, obj_bbox, random_transform, persp_project, againts_wall 
from pyblend.render import (
    config_render,
    render_image,
    enable_segmentation_render,
    enable_depth_render,
    enable_normal_render,
)

from background import set_hdri_background

def place_objects(object_paths, num_objects, scene_center=(0, 0, 0), placement_radius=4):
    objects = []
    angles = np.linspace(0, 2 * np.pi, num_objects, endpoint=False)

    for i, obj_path in enumerate(object_paths[:num_objects]):
        # Load the object
        obj = load_obj(obj_path, f"object_{i}", center=False, join=True)
        normalize_obj(obj)

        # Calculate the bounding box to adjust the position to the floor
        bbox = obj_bbox(obj, mode="box")  # (8, 3) array with min and max coordinates
        min_z = bbox[:, 2].min()  # Find the lowest Z coordinate in the bounding box

        # Position the object on the floor
        x = scene_center[0] + placement_radius * np.cos(angles[i])
        y = scene_center[1] + placement_radius * np.sin(angles[i])
        z = scene_center[2] - min_z  # Shift the object upwards to align with the floor

        obj.location = (x, y, z)
        obj.rotation_euler = (random.uniform(0, np.pi), random.uniform(0, np.pi), random.uniform(0, 2 * np.pi))
        objects.append(obj)

    return objects


def main(args):
    random.seed(42)
    np.random.seed(42)
 
    # Ensure number of objects does not exceed the provided paths
    object_paths = args.obj_paths.split(",")
    num_objects = min(args.num_obj, len(object_paths))

    # ======== Config ========
    config_render(res_x=640, res_y=640, transparent=False)
    remover = BlenderRemover()
    remover.clear_all()
    config_world(0.3)

    # Set the HDRI background if provided
    if args.background:
        set_hdri_background(args.background)
        
    camera = bpy.data.objects["Camera"]
    exr_seg_node, png_seg_node = enable_segmentation_render("tmp/mask_etc3", max_value=num_objects) ###
    exr_depth_node, png_depth_node = enable_depth_render("tmp/mask_etc3", reverse=True)
    png_normal_node = enable_normal_render("tmp/mask_etc3")
    png_seg_node.file_slots[0].path = f"seg_"
    exr_seg_node.file_slots[0].path = f"seg_"
    png_depth_node.file_slots[0].path = f"depth_"
    exr_depth_node.file_slots[0].path = f"depth_"
    png_normal_node.file_slots[0].path = f"normal_"

    # ======== Set up scene ========
    for scene_idx in range(args.num_scene):
        bbox_list = []
        objects = place_objects(object_paths, num_objects, scene_center=(0, 0, 0), placement_radius=3) ####
        #for ii, (uid, path) in enumerate(objects.items()):
        for ii, obj in enumerate(objects): ####enumerate(object_paths[:num_objects]):
            ##obj = load_obj(path, "object", center=False, join=True)
            ##obj.location = (0, 0, 0)
            
            normalize_obj(obj)
            againts_wall(obj, z=-1)
            for obj_part in find_all_objects(obj):
                obj_part.pass_index = ii + 1
            random_transform(obj, offset_scale=2)
            bbox = obj_bbox(obj, mode="box")  # (8, 3)
            bbox_list.append(bbox)
        
        # ======== Render ========
        for camera_idx in range(args.num_views):
            camera.location = random_loc((0, 0, 0), (8, 8), theta=(-1, 1), phi=(0, 1))
            #camera.location = (0, 0, 8)
            look_at(camera, (0, 0, 0))
            bpy.context.view_layer.update()
            camera_para = get_camera_para(camera)
            intr = camera_para["intrinsic"]  # (3, 3)
            extr = camera_para["extrinsic"]  # (4, 4)
            bbox2d_list = []
            for bbox in bbox_list:
                bbox2cam = extr.dot(np.concatenate([bbox, np.ones((8, 1))], axis=1).transpose()).transpose()[
                    :, :3
                ]  # (8, 3)
                bbox2d = persp_project(bbox2cam, intr)  # (8, 2)
                bbox2d_list.append(bbox2d)
            bpy.context.scene.frame_current = scene_idx * args.num_views + camera_idx
            render_image(f"tmp/mask_etc3/out_{scene_idx * args.num_views + camera_idx:04d}.png") ##########
            image = cv2.imread(
                f"tmp/mask_etc3/out_{scene_idx * args.num_views + camera_idx:04d}.png", cv2.IMREAD_UNCHANGED ####""
            )
            for bbox2d in bbox2d_list:
                image = plot_corner(image, bbox2d, linewidth=1)
            cv2.imwrite(f"tmp/mask_etc3/out_bbox_{scene_idx * args.num_views + camera_idx:04d}.png", image) #########
        remover.clear_all()


if __name__ == "__main__":
    parser = ArgumentParserForBlender()
    parser.add_argument("--num_scene", type=int, default=10, help="Number of scenes to render")
    parser.add_argument("--num_obj", type=int, default=1, help="Number of objects to render in each scene")
    parser.add_argument("--num_views", type=int, default=2, help="Number of views per scene")
    parser.add_argument("--obj_paths", type=str, required=True, help="Comma-separated list of paths to object files")
    parser.add_argument("--background", type=str, help="Path to the HDRI background image", default=None)
    args = parser.parse_args()
    main(args)
