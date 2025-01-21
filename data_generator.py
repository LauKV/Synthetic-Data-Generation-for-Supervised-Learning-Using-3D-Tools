import os
import random
import subprocess

def run_blender_commands(obj_dir, hdri_dir, output_base_dir, blender_app, script_path, num_scenes, num_views):
    """
    Run Blender commands for each object in the specified directory with a randomly selected HDRI.

    :param obj_dir: Path to the directory containing .obj files
    :param hdri_dir: Path to the directory containing .exr HDRI files
    :param output_base_dir: Base directory where output directories will be created
    :param blender_app: Path to the Blender executable
    :param script_path: Path to the Python script to execute in Blender
    :param num_scenes: Number of scenes to render per object
    :param num_views: Number of views to render per scene
    """
    # Get list of .obj files
    obj_files = [f for f in os.listdir(obj_dir) if f.endswith('.obj') or f.endswith('.blend') or f.endswith('.glb')]
    hdri_files = [f for f in os.listdir(hdri_dir) if f.endswith('.exr')]

    if not obj_files:
        print("No .obj files found in the directory.")
        return

    if not hdri_files:
        print("No .exr HDRI files found in the directory.")
        return

    for obj_file in obj_files:
        for hdri in hdri_files:
            # Select a random HDRI file
            # hdri_file = random.choice(hdri_files)
            hdri_path = os.path.join(hdri_dir, hdri)
            print(f"HDRI: {hdri}")
            
            obj_path = os.path.join(obj_dir, obj_file)
            obj_name = os.path.splitext(obj_file)[0]

            # Create output directory for the current object
            output_dir = os.path.join(output_base_dir, obj_name)
            os.makedirs(output_dir, exist_ok=True)

            # Construct the Blender command
            command = [
                blender_app, '-b', '-P', script_path, '--',
                '--obj_paths', obj_path,
                '--background', hdri_path,
                '--output_dir', output_dir,
                '--num_scenes', str(num_scenes),
                '--num_views', str(num_views),
                '--name', obj_name
            ]
            print(command)
            print(f"Running command for object '{obj_name}'...")
            try:
                subprocess.run(command, check=True)
                print(f"Completed rendering for object '{obj_name}'.")
            except subprocess.CalledProcessError as e:
                print(f"Error occurred while rendering object '{obj_name}': {e}")
            except Exception as e:
                print(f"Skipping object '{obj_name}' due to an error: {e}")

# Example usage
obj_directory = "./objects"
hdri_directory = "./hdris"
output_directory = "./renders10"
blender_executable = "/home/opdal/Bureau/5GMM/Synthetic-Data-Generation-for-Supervised-Learning-Using-3D-Tools/PYBLEND/blender-3.2.2-linux-x64/blender"
#"blender_app"
blender_script = "super_main.py"
num_scenes = 1
num_views = 10

run_blender_commands(obj_directory, hdri_directory, output_directory, blender_executable, blender_script, num_scenes, num_views)
