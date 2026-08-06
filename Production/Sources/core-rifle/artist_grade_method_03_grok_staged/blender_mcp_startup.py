import bpy

if "blender_mcp" not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module="blender_mcp")

scene = bpy.context.scene
for prop in (
    "blendermcp_use_polyhaven",
    "blendermcp_use_hyper3d",
    "blendermcp_use_hunyuan3d",
):
    if hasattr(scene, prop):
        setattr(scene, prop, False)

if not getattr(scene, "blendermcp_server_running", False):
    bpy.ops.blendermcp.start_server()
