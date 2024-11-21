import bpy
import math


#### render functions

def config_cycle_gpu(verbose=False):
    devices = []
    bpy.data.scenes[0].render.engine = "CYCLES"
    bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"
    bpy.context.scene.cycles.device = "GPU"
    bpy.context.preferences.addons["cycles"].preferences.get_devices()

    if verbose:
        print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)

    for d in bpy.context.preferences.addons["cycles"].preferences.devices:
        if d["name"][0] == "N":  # enable NVIDIA devices
            d["use"] = 1
            devices.append(d["name"])

    return devices


def config_cycles(pre_sample=1024, sample=4096):
    """
    Config cycles render engine for preview_samples and samples
    """
    bpy.data.scenes["Scene"].cycles.preview_samples = pre_sample
    bpy.data.scenes["Scene"].cycles.samples = sample


def config_render(
    path="tmp/output.png", engine="CYCLES", res_x=640, res_y=480, file_format="PNG", transparent=True, enable_gpu=True
):
    """
    Config render engine for path, engine, res_x, res_y, file_format, transparent
    """

    bpy.context.preferences.edit.undo_steps = 0  # disable undo

    render = bpy.context.scene.render
    render.filepath = path
    render.image_settings.file_format = file_format
    render.film_transparent = transparent
    render.resolution_x = res_x
    render.resolution_y = res_y
    if engine.startswith("C"):
        render.engine = "CYCLES"
        config_cycles()
        bpy.data.scenes["Scene"].cycles.use_denoising = True
        if enable_gpu:
            config_cycle_gpu()
    else:
        render.engine = "BLENDER_EEVEE"


def render_image(path=None):
    if path is not None:
        bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)

