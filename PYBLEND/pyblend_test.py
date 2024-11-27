import bpy
import numpy as np
import sys

sys.path.append('/home/opdal/Bureau/5GMM/Synthetic-Data-Generation-for-Supervised-Learning-Using-3D-Tools/PYBLEND')
from render import config_render, render_image
from lighting import config_world, create_light
# from material import random_mat, load_mat_library
from utils import BlenderRemover, ArgumentParserForBlender
from object import load_obj, create_plane, enable_shaow_catcher, center
from transform import look_at, normalize_obj, againts_wall, random_loc
from background import set_hdri_background

def load_mesh_with_materials(blend_file_path): # for blend files 
    # Load the mesh first
    with bpy.data.libraries.load(blend_file_path, link=False) as (data_from, data_to):
        if data_from.meshes:
            mesh_name = data_from.meshes[0]
            object_name = data_from.objects[0]
            print(mesh_name)
            data_to.meshes.append(mesh_name)
            print(f"Appending mesh: {mesh_name}")
        else:
            print(f"Mesh '{mesh_name}' not found.")

        # Check if materials exist and append them
        if data_from.materials:
            for material_name in data_from.materials:
                data_to.materials.append(material_name)
                print(f"Appending material: {material_name}")
        else:
            print("No materials found in the .blend file.")

    # After appending, create an object from the mesh and link it to the scene
    if mesh_name in bpy.data.meshes:
        mesh = bpy.data.meshes[mesh_name]
        obj = bpy.data.objects.new(object_name, mesh)  # Create an object from the mesh
        bpy.context.collection.objects.link(obj)  # Link the object to the scene
        print(f"Object '{obj.name}' created and linked.")

        # Assign materials to the object if any are available
        if data_from.materials:
            # Check if there are materials to assign
            for i, material_name in enumerate(data_from.materials):
                material = bpy.data.materials.get(material_name)
                if material:
                    # Assign the material to the object
                    if len(obj.data.materials) <= i:
                        obj.data.materials.append(material)
                    else:
                        obj.data.materials[i] = material
                    print(f"Material '{material_name}' assigned to object '{obj.name}'.")
                else:
                    print(f"Material '{material_name}' not found in bpy.data.materials.")
        else:
            print("No materials were appended or assigned.")
        
        return obj
    else:
        print(f"Mesh '{mesh_name}' not found in bpy.data.meshes.")
        return None

def render_teaser(args):
    # ======== Config ========
    config_render(res_x=320, res_y=240, transparent=False)
    remover = BlenderRemover()
    remover.clear_all()
    config_world(0.3)
    """ if args.color is not None:
        # load_mat_library("docs/materials.blend")
        mat = bpy.data.materials["cbrewer medium blue"]
        hex_color = args.color
        color = np.array([int(hex_color[i : i + 2], 16) for i in (0, 2, 4)]) / 255
        mat.node_tree.nodes["Hue Saturation Value"].inputs[4].default_value = np.append(color, 1)
    else:
        mat = None
    """

    # ======== Set up scene ========
    plane = create_plane((0, 0, -1), (0, 0, 0), (20, 20, 20), name="plane")
    enable_shaow_catcher(plane)
    
    # obj = load_obj(args.input, "object", center=True) ---- original
    # -------------------------------------------------------------------------------------
    # load the object
    with bpy.data.libraries.load(args.input) as (data_from, data_to):
        print("Available Objects:", data_from.objects)  
    with bpy.data.libraries.load(args.input, link=False) as (data_from, data_to):
        print("Available Objects:", data_from.objects)
        print("Available Collections:", data_from.collections)
        print("Available Meshes:", data_from.meshes)

    
    if args.input.endswith(".blend"):
        print("Blend object!")
        obj = load_mesh_with_materials(args.input)
        print(obj)
        center(obj, "object")
        #obj = load_obj(args.input, "object", center=True)
    else:
        obj = load_obj(args.input, "object", center=True)

    # -------------------------------------------------------------------------------------
    normalize_obj(obj)
    againts_wall(obj, z=-1)
    spot_light = create_light("SPOT", (3, 3, 10), (np.pi / 2, 0, 0), 400, (1, 1, 1), 5, name="light")
    look_at(spot_light, obj.location)
    camera = bpy.data.objects["Camera"]
    set_hdri_background(args.background)    ###### HDRI Background pathset_hdri_background()

    #bpy.ops.object.mode_set(mode="OBJECT")
    
    # ======== Render ========
    for i in range(args.num):
        camera.location = random_loc((0, 0, 0), (6, 6), theta=(-1, 1), phi=(0, 1))
        look_at(camera, obj.location)
        """ if args.color is None:
            obj.active_material = random_mat(obj.active_material)
        else:
            obj.active_material = mat """
        render_image(f"tmp/multiview/{args.name}_{i:04d}.png")


if __name__ == "__main__":
    parser = ArgumentParserForBlender()
    parser.add_argument("-i", "--input", type=str, default="bunny.obj")
    parser.add_argument("-n", "--num", type=int, default=12)
    parser.add_argument("-c", "--color", type=str, default=None)
    parser.add_argument("--name", type=str, default="out")
    parser.add_argument("-b", "--background", type=str, default="rogland_moonlit_night_4k.exr")
    args = parser.parse_args()
    render_teaser(args)




