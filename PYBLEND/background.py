import bpy

def set_colored_background(color: tuple[float, float, float, float]) -> None:
    """Sets a solid color background in the Blender scene.

    Args:
        color (tuple): A tuple with RGBA values (range 0-1) for the background color.
    """
    # Ensure the world environment is set up
    #if bpy.context.scene.world is None:
    #    bpy.context.scene.world = bpy.data.worlds.new(name="NewWorld")

    # Use nodes for the world to adjust color settings
    
    if not bpy.context.scene.world.node_tree:
        bpy.context.scene.world.use_nodes = True
    world_nodes = bpy.context.scene.world.node_tree.nodes
    world_links = bpy.context.scene.world.node_tree.links

    # Clear existing nodes in the world to prevent conflicts
    world_nodes.clear()

    # Add background shader and world output nodes
    background_node = world_nodes.new(type="ShaderNodeBackground")
    world_output_node = world_nodes.new(type="ShaderNodeOutputWorld")

    # Connect background shader to world output
    world_links.new(background_node.outputs["Background"], world_output_node.inputs["Surface"])

    # Set the background color with RGBA values
    background_node.inputs["Color"].default_value = color


def set_hdri_background(hdri_path: str) -> None:
    """Sets a HDRI background in the Blender scene.

    Args:
        color (tuple): A tuple with RGBA values (range 0-1) for the background color.
    """
    # Get the world settings
    world = bpy.context.scene.world

    # Create a new node tree if it doesn't exist
    if not world.node_tree:
        world.use_nodes = True

    # Set up world node tree
    world_node_tree = bpy.context.scene.world.node_tree
    world_node_tree.nodes.clear()

    location_x = 0

    # Path to HDRI image
    path_to_image = hdri_path
    image_obj = bpy.data.images.load(path_to_image)

    # Environment texture node
    environment_texture_node = world_node_tree.nodes.new(type="ShaderNodeTexEnvironment")
    environment_texture_node.image = image_obj
    environment_texture_node.location = location_x, 0
    location_x += 300

    # Background node
    background_node = world_node_tree.nodes.new(type="ShaderNodeBackground")
    background_node.inputs["Strength"].default_value = 1.0
    background_node.location.x = location_x
    location_x += 300

    # World output node
    world_output_node = world_node_tree.nodes.new(type="ShaderNodeOutputWorld")
    world_output_node.location.x = location_x

    # Connect nodes
    world_node_tree.links.new(environment_texture_node.outputs["Color"], background_node.inputs["Color"])
    world_node_tree.links.new(background_node.outputs["Background"], world_output_node.inputs["Surface"])



