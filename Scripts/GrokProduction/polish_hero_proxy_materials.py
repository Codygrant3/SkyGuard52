"""Apply governed MaterialInstanceConstant palettes to Hero proxy static meshes."""

from __future__ import annotations

import json
import os
import re
import sys
import traceback
from pathlib import Path

try:
    import unreal
except ModuleNotFoundError:
    unreal = None


ROOT = Path(r"D:\Skyguard52")
HERO_ROOT = "/Game/Skyguard/Meshes/Hero"
MATERIAL_ROOT = f"{HERO_ROOT}/Materials"
ATTEMPT = ROOT / r"Saved\BuildAttempts\HERO_PROXY_MATERIAL_POLISH01\attempt_01"
RECEIPT = ATTEMPT / "material_polish_receipt.json"

PALETTES = {
    "metal_gray": {
        "asset": "MI_HeroProxy_MetalGray",
        "color": (0.23, 0.26, 0.29, 1.0),
        "roughness": 0.42,
        "metallic": 0.82,
        "parents": (
            "/Game/Skyguard/Materials/M_Metal",
            "/Game/Skyguard/Materials/Generated/M_AirframeMetal",
            "/Engine/BasicShapes/BasicShapeMaterial",
        ),
    },
    "olive_drab": {
        "asset": "MI_HeroProxy_OliveDrab",
        "color": (0.16, 0.19, 0.08, 1.0),
        "roughness": 0.68,
        "metallic": 0.18,
        "parents": (
            "/Game/Skyguard/Materials/M_ShahedDrone",
            "/Game/Skyguard/Materials/M_RifleTan",
            "/Game/Skyguard/Materials/M_Metal",
            "/Engine/BasicShapes/BasicShapeMaterial",
        ),
    },
    "rubber_black": {
        "asset": "MI_HeroProxy_RubberBlack",
        "color": (0.012, 0.014, 0.016, 1.0),
        "roughness": 0.84,
        "metallic": 0.0,
        "parents": (
            "/Game/Skyguard/Meshes/WebGame/yak52-detail-kit/yak52-detail-kit-blender/Materials/Canopy_Rail_Rubber_PBR",
            "/Game/Skyguard/Materials/M_CockpitInterior",
            "/Engine/BasicShapes/BasicShapeMaterial",
        ),
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def write_json_atomic(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def run_offline_contract_test() -> int:
    hero_disk = ROOT / r"Content\Skyguard\Meshes\Hero"
    require(hero_disk.is_dir(), f"Hero mesh directory missing: {hero_disk}")
    proxy_files = [path for path in hero_disk.rglob("*.uasset") if "proxy" in path.stem.lower()]
    require(proxy_files, "No case-insensitive Hero proxy asset candidates exist on disk")
    require(set(PALETTES) == {"metal_gray", "olive_drab", "rubber_black"}, "Palette contract changed")
    compile(Path(__file__).read_text(encoding="utf-8"), __file__, "exec")
    print(f"PASS_HERO_PROXY_MATERIAL_POLISH01_OFFLINE_CONTRACT proxy_candidates={len(proxy_files)}")
    return 0


def class_name(asset: object) -> str:
    return asset.get_class().get_name() if asset is not None else ""


def package_path(asset_path: str) -> str:
    return asset_path.split(".", 1)[0]


def asset_name(asset_path: str) -> str:
    return package_path(asset_path).rsplit("/", 1)[-1]


def choose_palette(name: str) -> str:
    lowered = name.lower()
    if any(token in lowered for token in ("rubber", "tire", "wheel", "grip", "hose", "glove")):
        return "rubber_black"
    if any(token in lowered for token in ("rifle", "igla", "shahed", "drone", "radar_truck", "gunner", "flak")):
        return "olive_drab"
    return "metal_gray"


def load_parent(candidates: tuple[str, ...]) -> tuple[object, str]:
    for candidate in candidates:
        parent = unreal.EditorAssetLibrary.load_asset(candidate)
        if parent is not None and isinstance(parent, unreal.MaterialInterface):
            return parent, candidate
    raise RuntimeError(f"No suitable project or engine material parent found: {candidates}")


def ensure_material_instance(palette_name: str, spec: dict[str, object]) -> tuple[object, dict[str, object]]:
    path = f"{MATERIAL_ROOT}/{spec['asset']}"
    material = unreal.EditorAssetLibrary.load_asset(path)
    action = "reused"
    if material is None:
        unreal.EditorAssetLibrary.make_directory(MATERIAL_ROOT)
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            str(spec["asset"]),
            MATERIAL_ROOT,
            unreal.MaterialInstanceConstant,
            unreal.MaterialInstanceConstantFactoryNew(),
        )
        require(material is not None, f"Failed to create {path}")
        action = "created"
    require(
        isinstance(material, unreal.MaterialInstanceConstant),
        f"Wrong material class at {path}: {class_name(material)}",
    )
    parent, parent_path = load_parent(spec["parents"])
    material.set_editor_property("parent", parent)

    color = unreal.LinearColor(*spec["color"])
    applied: list[str] = []
    for parameter in ("BaseColor", "Base Color", "Color", "Tint"):
        try:
            result = unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                material, parameter, color
            )
            if result is not False:
                applied.append(parameter)
        except Exception:
            continue
    for parameter, value in (
        ("Roughness", float(spec["roughness"])),
        ("Metallic", float(spec["metallic"])),
    ):
        try:
            result = unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
                material, parameter, value
            )
            if result is not False:
                applied.append(parameter)
        except Exception:
            continue
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(material, only_if_is_dirty=False)
    except TypeError:
        unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material, {
        "palette": palette_name,
        "asset": path,
        "action": action,
        "parent": parent_path,
        "base_color_linear": list(spec["color"]),
        "roughness": spec["roughness"],
        "metallic": spec["metallic"],
        "parameter_overrides_supported": bool(applied),
        "parameter_overrides": applied,
        "fallback_note": None if applied else "Parent exposes no supported named overrides; selected parent response retained.",
    }


def run_unreal() -> None:
    require(unreal is not None, "This mode must run inside Unreal Editor Python")
    result: dict[str, object] = {
        "schema": "skyguard.hero-proxy-material-polish01.v1",
        "classification": "FAILED_WITH_EVIDENCE",
        "search_root": HERO_ROOT,
        "materials_root": MATERIAL_ROOT,
        "matched_mesh_count": 0,
        "materials": [],
        "assignments": [],
        "error": None,
        "traceback": None,
    }
    try:
        ATTEMPT.mkdir(parents=True, exist_ok=True)
        listed = unreal.EditorAssetLibrary.list_assets(HERO_ROOT, recursive=True, include_folder=False)
        meshes: list[tuple[str, object]] = []
        for listed_path in listed:
            path = package_path(str(listed_path))
            name = asset_name(path)
            if "proxy" not in name.lower():
                continue
            asset = unreal.EditorAssetLibrary.load_asset(path)
            if asset is not None and isinstance(asset, unreal.StaticMesh):
                meshes.append((path, asset))
        require(meshes, f"No StaticMesh proxy assets found beneath {HERO_ROOT}")

        instances: dict[str, object] = {}
        material_rows: list[dict[str, object]] = []
        for palette_name, spec in PALETTES.items():
            instance, row = ensure_material_instance(palette_name, spec)
            instances[palette_name] = instance
            material_rows.append(row)

        assignment_rows: list[dict[str, object]] = []
        for path, mesh in sorted(meshes, key=lambda item: item[0].lower()):
            palette_name = choose_palette(asset_name(path))
            material = instances[palette_name]
            mesh.set_material(0, material)
            try:
                unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False)
            except TypeError:
                unreal.EditorAssetLibrary.save_loaded_asset(mesh)
            assigned = mesh.get_material(0)
            require(assigned is not None, f"Slot 0 remained empty after assignment: {path}")
            require(
                assigned.get_path_name().split(".", 1)[0]
                == material.get_path_name().split(".", 1)[0],
                f"Slot 0 verification failed: {path}",
            )
            assignment_rows.append(
                {
                    "mesh": path,
                    "mesh_name": asset_name(path),
                    "slot": 0,
                    "palette": palette_name,
                    "material": material.get_path_name(),
                }
            )

        result["matched_mesh_count"] = len(meshes)
        result["materials"] = material_rows
        result["assignments"] = assignment_rows
        result["classification"] = "PASSED_HERO_PROXY_MATERIAL_POLISH01_AWAITING_REVIEW"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
    finally:
        write_json_atomic(RECEIPT, result)

    if str(result["classification"]).startswith("PASSED_"):
        unreal.SystemLibrary.quit_editor()
        return
    raise RuntimeError(result["error"] or result["classification"])


if "--offline-contract-test" in sys.argv:
    raise SystemExit(run_offline_contract_test())

run_unreal()
