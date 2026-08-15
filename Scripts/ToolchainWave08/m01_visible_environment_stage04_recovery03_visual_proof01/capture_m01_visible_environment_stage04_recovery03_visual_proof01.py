"""Bind the proven Stage03 D3D12 proof to the accepted Stage04 Recovery03 map."""

from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_visible_environment_stage03_visual_proof01\capture_m01_visible_environment_stage03_visual_proof01.py"
)
EXPECTED_BYTES = 8_314
EXPECTED_SHA256 = "8ea62b4e57f947f1274467f1762d0bad9b5def0c6bf1e7a15ea132124d16dfda"

OLD_PREFIX = "M01_VISIBLE_ENVIRONMENT_STAGE03_VISUAL_PROOF01"
NEW_PREFIX = "M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_VISUAL_PROOF01"
OLD_ID = "M01-VISIBLE-ENVIRONMENT-STAGE03-VISUAL-PROOF01"
NEW_ID = "M01-VISIBLE-ENVIRONMENT-STAGE04-RECOVERY03-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_VisibleEnvironmentStage03"
NEW_MAP = "Lvl_M01_VisibleEnvironmentStage04Recovery03"
OLD_CSV = "M01VisibleEnvironmentStage03VisualProof01.csv"
NEW_CSV = "M01VisibleEnvironmentStage04Recovery03VisualProof01.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transform_source() -> str:
    if (
        not SOURCE.is_file()
        or SOURCE.stat().st_size != EXPECTED_BYTES
        or sha256(SOURCE) != EXPECTED_SHA256
    ):
        raise RuntimeError("Frozen Stage03 proof binder changed")

    namespace = {"__name__": "stage03_proof_binder_authority", "__file__": str(SOURCE)}
    exec(
        compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"),
        namespace,
        namespace,
    )
    transformed = namespace["transform_source"]()
    optional_tokens = {
        "m01_visible_environment_stage03_visual_proof01",
        "visible-environment-stage03-visual-proof01",
    }
    for old, new in (
        (OLD_PREFIX, NEW_PREFIX),
        (OLD_ID, NEW_ID),
        (OLD_MAP, NEW_MAP),
        (OLD_CSV, NEW_CSV),
        ("m01_visible_environment_stage03_visual_proof01", "m01_visible_environment_stage04_recovery03_visual_proof01"),
        ("visible-environment-stage03-visual-proof01", "visible-environment-stage04-recovery03-visual-proof01"),
    ):
        if old not in transformed and old not in optional_tokens:
            raise RuntimeError(f"Stage04 Recovery03 proof token absent: {old}")
        if old in transformed:
            transformed = transformed.replace(old, new)

    old_fingerprint = (
        '"M01_HSSC01R01_", "M01_HSSC02_", "M01_HSSC03_", "M01_PHV02_", '
        '"M01_STAGE03_"))'
    )
    new_fingerprint = (
        '"M01_HSSC01R01_", "M01_HSSC02_", "M01_HSSC03_", "M01_PHV02_", '
        '"M01_STAGE03_", "M01_STAGE04R03_"))'
    )
    if transformed.count(old_fingerprint) != 1:
        raise RuntimeError("Stage04 governed-transform fingerprint anchor changed")
    transformed = transformed.replace(old_fingerprint, new_fingerprint)

    authority_start = '''        stage_freeze_path = ROOT / "Docs/AAA_Review/M01_VISIBLE_ENVIRONMENT_STAGE03_AUTHORING01_ATTEMPT01_ACCEPTANCE_FREEZE.json"'''
    authority_end = '''        map_file = ISOLATED_ROOT / (
            "Content/M01/"
            "Lvl_M01_VisibleEnvironmentStage04Recovery03.umap"
        )'''
    start = transformed.find(authority_start)
    end = transformed.find(authority_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Stage04 postflight-authority block anchor changed")
    new_authority = '''        postflight_path = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_POSTFLIGHT01/attempt_01/postflight_receipt.json"
        verify_record({"absolute_path": str(postflight_path), "bytes": 20520, "sha256": "e585b5d4d5f08018cae6263364428bbeee6f7509e0202bf114853372d7b14b1a"})
        postflight = read_json(postflight_path)
        expected_ready = "PASSED_STAGE04_RECOVERY03_SAVED_MAP_READY_FOR_GOVERNED_D3D12_VISUAL_PROOF"
        if postflight.get("classification") != expected_ready:
            raise RuntimeError("Stage04 Recovery03 postflight classification changed")
        if int(postflight.get("actor_count", 0)) != 230:
            raise RuntimeError("Stage04 Recovery03 actor count changed")
        if int(postflight.get("facade_actor_count", 0)) != 32 or int(postflight.get("lighthouse_actor_count", 0)) != 3:
            raise RuntimeError("Stage04 Recovery03 accepted-asset counts changed")
        if int(postflight.get("hidden_legacy_count", 0)) != 75 or int(postflight.get("vegetation_count", 0)) != 28:
            raise RuntimeError("Stage04 Recovery03 bounded-remediation counts changed")
        if postflight.get("errors") != [] or postflight.get("world_saved") is not False:
            raise RuntimeError("Stage04 Recovery03 postflight safety state changed")
        terminal_path = ROOT / "Saved/Reports/M01_VISIBLE_ENVIRONMENT_STAGE04_RECOVERY03_POSTFLIGHT01_TERMINAL.json"
        verify_record({"absolute_path": str(terminal_path), "bytes": 676, "sha256": "89a405c75f0b6618aa6262d4eb9c4cfeaecae1d95ffd9400824a7e3df559312c"})
        terminal = read_json(terminal_path)
        if terminal.get("classification") != expected_ready or terminal.get("exit_code") != 0:
            raise RuntimeError("Stage04 Recovery03 terminal postflight changed")
        authoring_path = ROOT / "Saved/BuildAttempts/M01_VISIBLE_ENVIRONMENT_STAGE04_AUTHORING01_RECOVERY03/attempt_01/authoring_receipt.json"
        verify_record({"absolute_path": str(authoring_path), "bytes": 63288, "sha256": "30b2a0a90cf88811990a27aeb49c5e554093bbe65f6089d106650e351db58c2f"})
        authoring = read_json(authoring_path)
        if authoring.get("classification") != "PASSED_STAGE04_RECOVERY03_AUTHORING_AWAITING_GOVERNED_D3D12_VISUAL_PROOF":
            raise RuntimeError("Stage04 Recovery03 authoring receipt changed")
        if int(authoring.get("actor_count_after", 0)) != 230:
            raise RuntimeError("Stage04 Recovery03 authoring actor count changed")
'''
    transformed = transformed[:start] + new_authority + transformed[end:]

    old_assertions_start = '''        for hidden_label in ("M01_HSSC02_CoastalA_TERRAIN", "M01_HSSC02_CoastalA_HARDSCAPE"):'''
    assertions_end = '''        for forbidden_prefix in ("M01_VEK02_City_", "M01_VEK02_Lighthouse_", "M01_RS01_Tree_"):'''
    start = transformed.find(old_assertions_start)
    end = transformed.find(assertions_end, start)
    if start < 0 or end < 0:
        raise RuntimeError("Stage04 world-assertion block anchor changed")
    stage04_assertions = '''        hidden_exact = (
            "M01_HSSC02_CoastalA_TERRAIN", "M01_HSSC02_CoastalA_HARDSCAPE",
            "M01_STAGE03_Lighthouse_Hero_STRUCTURAL", "M01_STAGE03_Lighthouse_Hero_GLAZING",
            "M01_STAGE03_Lighthouse_Hero_DETAILS",
        )
        hidden_window_prefixes = ("M01_HSSC01R01_Window_", "M01_HSSC03_RearWindow_")
        hidden_count = 0
        for hidden_label in hidden_exact:
            hidden_component = by_label[hidden_label][0].get_component_by_class(unreal.StaticMeshComponent)
            if hidden_component is None or bool(hidden_component.get_editor_property("visible")) or not bool(hidden_component.get_editor_property("hidden_in_game")):
                raise RuntimeError(f"Stage04 legacy actor is not hidden: {hidden_label}")
            if hidden_label.startswith("M01_STAGE03_"):
                hidden_count += 1
        for hidden_actor in actors:
            if hidden_actor.get_actor_label().startswith(hidden_window_prefixes):
                hidden_component = hidden_actor.get_component_by_class(unreal.StaticMeshComponent)
                if hidden_component is None or bool(hidden_component.get_editor_property("visible")) or not bool(hidden_component.get_editor_property("hidden_in_game")):
                    raise RuntimeError(f"Stage04 legacy window is not hidden: {hidden_actor.get_actor_label()}")
                hidden_count += 1
        if hidden_count != 75:
            raise RuntimeError(f"Stage04 expected 75 hidden legacy art actors; found {hidden_count}")

        facade_meshes = {
            "CoastalFacadeBay_A_BalconyDetails": "/Game/M01/VisibleEnvironmentStage04Recovery03/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_BalconyDetails.SM_M01_CoastalFacadeBay_A_BalconyDetails",
            "CoastalFacadeBay_A_Glass": "/Game/M01/VisibleEnvironmentStage04Recovery03/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_Glass.SM_M01_CoastalFacadeBay_A_Glass",
            "CoastalFacadeBay_A_Interior": "/Game/M01/VisibleEnvironmentStage04Recovery03/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_Interior.SM_M01_CoastalFacadeBay_A_Interior",
            "CoastalFacadeBay_A_StructureFrame": "/Game/M01/VisibleEnvironmentStage04Recovery03/FacadeBayR02/StaticMeshes/SM_M01_CoastalFacadeBay_A_StructureFrame.SM_M01_CoastalFacadeBay_A_StructureFrame",
        }
        expected_materials = {
            "CoastalFacadeBay_A_BalconyDetails": ["M_ENV_Plaster_Warm_2K", "M_ENV_Metal_Plate_2K", "M_M01_CoastalFacadeBay_R02_AgedBrass"],
            "CoastalFacadeBay_A_Glass": ["M_M01_PrewarWindowR03_Glass_CandidateB"],
            "CoastalFacadeBay_A_Interior": ["M_M01_PrewarWindowR03_BookRed", "M_M01_PrewarWindowR03_BookGreen", "M_M01_PrewarWindowR03_Furniture", "M_M01_PrewarWindowR03_AgedBronzeHardware", "M_M01_PrewarWindow_CurtainCloth", "M_M01_PrewarWindow_WarmLamp", "M_M01_PrewarWindowR03_Radiator", "M_M01_PrewarWindowR03_InteriorWall", "M_M01_PrewarWindow_InteriorWood"],
            "CoastalFacadeBay_A_StructureFrame": ["M_M01_PrewarWindow_PaintedTimber", "M_M01_PrewarWindowR03_AgedBronzeHardware", "M_M01_PrewarWindowR03_FastenerSlot", "M_M01_PrewarWindow_RevealPlaster", "M_M01_PrewarWindow_WeatheredPlaster", "M_M01_CoastalFacadeBay_R02_WarmGreyStucco", "M_M01_C06_WeatheredConcrete", "M_ENV_Plaster_Warm_2K"],
        }
        facade_count = 0
        for label, matched in by_label.items():
            if not label.startswith("M01_STAGE04R03_Facade_"):
                continue
            facade_count += len(matched)
            suffix = next((name for name in facade_meshes if label.endswith(name)), None)
            if suffix is None or len(matched) != 1:
                raise RuntimeError(f"Stage04 facade identity changed: {label}")
            component = matched[0].get_component_by_class(unreal.StaticMeshComponent)
            expected_mesh = unreal.load_asset(facade_meshes[suffix])
            if component is None or expected_mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(expected_mesh):
                raise RuntimeError(f"Stage04 facade mesh changed: {label}")
            if not bool(component.get_editor_property("visible")) or bool(component.get_editor_property("hidden_in_game")):
                raise RuntimeError(f"Stage04 facade is not visible: {label}")
            observed_materials = [slot.get_editor_property("material_interface").get_name() for slot in expected_mesh.get_editor_property("static_materials")]
            if observed_materials != expected_materials[suffix]:
                raise RuntimeError(f"Stage04 facade material contract changed: {suffix}: {observed_materials}")
        if facade_count != 32:
            raise RuntimeError(f"Stage04 expected 32 facade actors; found {facade_count}")

        lighthouse_meshes = {
            "M01_STAGE04R03_LighthouseHero_Lighthouse_Details_A": "/Game/M01/VisibleEnvironmentStage04Recovery03/LighthouseR04/StaticMeshes/SM_M01_Lighthouse_Details_A.SM_M01_Lighthouse_Details_A",
            "M01_STAGE04R03_LighthouseHero_Lighthouse_Lantern_A": "/Game/M01/VisibleEnvironmentStage04Recovery03/LighthouseR04/StaticMeshes/SM_M01_Lighthouse_Lantern_A.SM_M01_Lighthouse_Lantern_A",
            "M01_STAGE04R03_LighthouseHero_Lighthouse_Tower_A": "/Game/M01/VisibleEnvironmentStage04Recovery03/LighthouseR04/StaticMeshes/SM_M01_Lighthouse_Tower_A.SM_M01_Lighthouse_Tower_A",
        }
        for lighthouse_label, mesh_path in lighthouse_meshes.items():
            if len(by_label.get(lighthouse_label, [])) != 1:
                raise RuntimeError(f"Stage04 lighthouse group missing: {lighthouse_label}")
            component = by_label[lighthouse_label][0].get_component_by_class(unreal.StaticMeshComponent)
            expected_mesh = unreal.load_asset(mesh_path)
            if component is None or expected_mesh is None or asset_identity(component.get_editor_property("static_mesh")) != asset_identity(expected_mesh):
                raise RuntimeError(f"Stage04 lighthouse mesh changed: {lighthouse_label}")
            if not bool(component.get_editor_property("visible")) or bool(component.get_editor_property("hidden_in_game")):
                raise RuntimeError(f"Stage04 lighthouse is not visible: {lighthouse_label}")
        tower = by_label["M01_STAGE04R03_LighthouseHero_Lighthouse_Tower_A"][0]
        tower_origin, tower_extent = tower.get_actor_bounds(False)
        tower_bottom = float(tower_origin.z - tower_extent.z)
        if tower_bottom < 0.0 or tower_bottom > 100.0:
            raise RuntimeError(f"Stage04 lighthouse ground contact changed: {tower_bottom}")
'''
    transformed = transformed[:start] + stage04_assertions + transformed[end:]
    return transformed


if __name__ == "__main__":
    exec(
        compile(transform_source(), str(SOURCE) + "::stage04-recovery03-visual-proof01", "exec"),
        globals(),
        globals(),
    )
