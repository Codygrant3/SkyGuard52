"""Import CPG cockpit GLB into Candidates (not accepted runtime)."""
import os

import unreal

SRC = r"D:\Skyguard52\Blender\APACHE_CPG_COCKPIT_BLOCKOUT01\exports\apache_cpg_cockpit_unreal.glb"
DEST = "/Game/Skyguard/Candidates/Apache/CPG_Cockpit_Blockout01"
NAME = "SM_ApacheCPG_Cockpit"
REPORT = r"D:\Skyguard52\Saved\Reports\APACHE_CPG_COCKPIT_IMPORT.txt"


def log(msg: str) -> None:
    unreal.log("[CPGImport] " + msg)


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

    imported = list(task.imported_object_paths or [])
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
        handle.write("imported=" + ",".join(imported) + "\n")
        handle.write("meshes=" + ",".join(meshes) + "\n")
    log("done meshes=" + str(len(meshes)))
    # Request exit after import so this stays a one-shot.
    unreal.SystemLibrary.quit_editor()


if __name__ == "__main__":
    main()
