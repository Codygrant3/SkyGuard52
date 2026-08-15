"""Import Apache silhouette GLB into Candidates (not accepted runtime)."""
import os

import unreal

SRC = r"D:\Skyguard52\Blender\APACHE_AIRFRAME_SILHOUETTE01\exports\apache_airframe_open_cpg.glb"
DEST = "/Game/Skyguard/Candidates/Apache/Airframe_Silhouette01"
NAME = "SM_ApacheAirframe_Silhouette"
REPORT = r"D:\Skyguard52\Saved\Reports\APACHE_AIRFRAME_SILHOUETTE_IMPORT.txt"


def main() -> None:
    if not os.path.isfile(SRC):
        raise RuntimeError("missing " + SRC)
    if not unreal.EditorAssetLibrary.does_directory_exist(DEST):
        unreal.EditorAssetLibrary.make_directory(DEST)

    task = unreal.AssetImportTask()
    task.filename = SRC
    task.destination_path = DEST
    task.destination_name = NAME
    task.automated = True
    task.replace_existing = True
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

    meshes = []
    for path in unreal.EditorAssetLibrary.list_assets(DEST, True, False):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if isinstance(asset, unreal.StaticMesh):
            meshes.append(path)
    unreal.EditorAssetLibrary.save_directory("/Game/Skyguard/Candidates/Apache", False, True)

    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as handle:
        handle.write("src=" + SRC + "\n")
        handle.write("dest=" + DEST + "\n")
        handle.write("meshes=" + ",".join(meshes) + "\n")
    unreal.log("[ApacheAirframe] done meshes=" + str(len(meshes)))
    unreal.SystemLibrary.quit_editor()


if __name__ == "__main__":
    main()
