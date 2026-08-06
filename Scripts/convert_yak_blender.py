import bpy
import sys
src = r"D:\Skyguard52\Content\Skyguard\Meshes\Source\webgame\yak52-detail-kit.glb"
dst = r"D:\Skyguard52\Content\Skyguard\Meshes\Source\webgame\yak52-detail-kit-blender.glb"
# reset scene
bpy.ops.wm.read_factory_settings(use_empty=True)
print("IMPORT", src)
bpy.ops.import_scene.gltf(filepath=src)
print("objects", len(bpy.data.objects))
print("meshes", len(bpy.data.meshes))
bpy.ops.export_scene.gltf(filepath=dst, export_format='GLB', export_apply=True)
print("EXPORTED", dst)
