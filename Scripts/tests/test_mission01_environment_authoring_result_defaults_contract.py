from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission01EnvironmentAuthoringLibrary.h"
LOCKED = {
    "SkyguardMission01EnvironmentAuthoringLibrary.h",
    "SkyguardMission01EnvironmentAuthoringLibrary.cpp",
    "SkyguardMission01EnvironmentAuthoringTests.cpp",
    "SkyguardRadarNode.cpp",
    "SkyguardRadarNode.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardGuidedLockRules.h",
    "SkyguardCpgHud.cpp",
    "SkyguardCpgHud.h",
    "SkyguardCpgHudTests.cpp",
    "SkyguardCpgSightHud.cpp",
    "SkyguardCpgSightHud.h",
    "SkyguardGunner.cpp",
    "SkyguardGunner.h",
    "SkyguardGunnerCampaign.cpp",
    "SkyguardProtectAsset.cpp",
    "SkyguardProtectAsset.h",
    "SkyguardHarborProofTests.cpp",
    "SkyguardCampaignTheaterKitTests.cpp",
}
# Isolated-test drafts stay off this lane. Visible-audit, capture-config,
# and material-compilation defaults are pending siblings, not this PR.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_phase4_m01_landscape_repair_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_landscape_capture_config_defaults_contract.py",
    "Scripts/tests/test_landscape_material_compilation_defaults_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_mission01_environment_readiness_defaults_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "bool bSuccess = false;",
    "TObjectPtr<ALandscape> Landscape;",
    "TObjectPtr<UPCGGraph> Graph;",
    "int32 LandscapeComponentCount = 0;",
    "FSkyguardLandscapeVisibleAudit VisibleAudit;",
    "int32 GraphNodeCount = 0;",
    "int32 GraphEdgeCount = 0;",
    "TArray<FString> GraphNodeSettingClasses;",
    "bool bLandscapeGuidValid = false;",
    "bool bLandscapeTransformExact = false;",
    "bool bGraphContractValid = false;",
    "bool bAuthoredStructureReady = false;",
    "bool bLicensedMeshSlotsEmpty = true;",
    "bool bGenerationLocked = true;",
    "int32 GeneratedPCGComponentCount = 0;",
    "int32 GeneratedPCGInstanceCount = 0;",
    "bool bRouteAndBeachGeneratedInstancesZero = true;",
    "FString Error;",
)
IN_CLASS_DEFAULTS = {
    "bSuccess": "false",
    "LandscapeComponentCount": "0",
    "GraphNodeCount": "0",
    "GraphEdgeCount": "0",
    "bLandscapeGuidValid": "false",
    "bLandscapeTransformExact": "false",
    "bGraphContractValid": "false",
    "bAuthoredStructureReady": "false",
    "bLicensedMeshSlotsEmpty": "true",
    "bGenerationLocked": "true",
    "GeneratedPCGComponentCount": "0",
    "GeneratedPCGInstanceCount": "0",
    "bRouteAndBeachGeneratedInstancesZero": "true",
}
PRESENCE_ONLY_FIELDS = (
    "TObjectPtr<ALandscape> Landscape;",
    "TObjectPtr<UPCGGraph> Graph;",
    "FSkyguardLandscapeVisibleAudit VisibleAudit;",
    "TArray<FString> GraphNodeSettingClasses;",
    "FString Error;",
)
# FSkyguardLandscapeVisibleAudit nested numerics stay on #207.
VISIBLE_AUDIT_NESTED_FIELDS_NOT_LOCKED = (
    "int32 VisibleComponentCount = 0;",
    "int32 RegisteredComponentCount = 0;",
    "int32 RenderStateCreatedComponentCount = 0;",
    "int32 HiddenInGameComponentCount = 0;",
    "int32 GeneratedMaterialInstanceReadyComponentCount = 0;",
    "int32 GovernedMaterialParentMatchComponentCount = 0;",
    "int32 ContractCameraFrustumIntersectionCount = 0;",
    "bool bActorHiddenInGame = true;",
    "bool bActorTemporarilyHiddenInEditor = true;",
    "bool bBoundsFiniteAndNonzero = false;",
    "FVector BoundsMinimum = FVector::ZeroVector;",
    "FVector BoundsMaximum = FVector::ZeroVector;",
)
# FSkyguardLandscapeMaterialCompilationResult stays on #209.
MATERIAL_COMPILATION_FIELDS_NOT_LOCKED = (
    "struct FSkyguardLandscapeMaterialCompilationResult",
    "int32 GeneratedMaterialInstanceCount = 0;",
    "int32 MaterialResourceCount = 0;",
    "int32 CompilationFinishedResourceCount = 0;",
    "int32 ValidShaderMapResourceCount = 0;",
    "bool bAssetCompilationQueueEmpty = false;",
    "bool bShaderCompilationQueueEmpty = false;",
)
# FSkyguardLandscapeCaptureConfigurationResult stays on #208.
CAPTURE_CONFIG_FIELDS_NOT_LOCKED = (
    "struct FSkyguardLandscapeCaptureConfigurationResult",
    "ESkyguardLandscapeCaptureDiagnosticMode Mode",
    "bool bUsesShowOnlyLandscape = false;",
    "int32 ShowOnlyLandscapeComponentCount = 0;",
    "int32 DiagnosticMaterialParentMatchComponentCount = 0;",
    "bool bRenderThreadSynchronized = false;",
    "FString CaptureSource;",
    "FString ViewMode;",
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Landscape =",
    "Graph =",
    "VisibleAudit =",
    "GraphNodeSettingClasses =",
    "Error =",
    "nullptr",
    "TEXT(",
    "FString()",
    "TArray()",
    'TEXT("")',
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def authoring_result_body(header: str) -> str:
    start = header.index("struct FSkyguardMission01EnvironmentAuthoringResult")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:bool|int32)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class Mission01EnvironmentAuthoringResultDefaultsContractTests(unittest.TestCase):
    def test_authoring_result_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(
            "struct FSkyguardMission01EnvironmentAuthoringResult",
            header,
        )
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", authoring_result_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = authoring_result_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 18)
        self.assertEqual(
            body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"),
            18,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = authoring_result_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn("bool bSuccess = false;", body)
        self.assertIn("int32 LandscapeComponentCount = 0;", body)
        self.assertIn("int32 GraphNodeCount = 0;", body)
        self.assertIn("int32 GraphEdgeCount = 0;", body)
        self.assertIn("bool bLandscapeGuidValid = false;", body)
        self.assertIn("bool bLandscapeTransformExact = false;", body)
        self.assertIn("bool bGraphContractValid = false;", body)
        self.assertIn("bool bAuthoredStructureReady = false;", body)
        self.assertIn("bool bLicensedMeshSlotsEmpty = true;", body)
        self.assertIn("bool bGenerationLocked = true;", body)
        self.assertIn("int32 GeneratedPCGComponentCount = 0;", body)
        self.assertIn("int32 GeneratedPCGInstanceCount = 0;", body)
        self.assertIn(
            "bool bRouteAndBeachGeneratedInstancesZero = true;",
            body,
        )
        self.assertNotIn("bSuccess = true", body)
        self.assertNotIn("bLandscapeGuidValid = true", body)
        self.assertNotIn("bLandscapeTransformExact = true", body)
        self.assertNotIn("bGraphContractValid = true", body)
        self.assertNotIn("bAuthoredStructureReady = true", body)
        self.assertNotIn("bLicensedMeshSlotsEmpty = false", body)
        self.assertNotIn("bGenerationLocked = false", body)
        self.assertNotIn("bRouteAndBeachGeneratedInstancesZero = false", body)
        self.assertEqual(len(defaults), 13, defaults)
        self.assertNotIn("Landscape", defaults)
        self.assertNotIn("Graph", defaults)
        self.assertNotIn("VisibleAudit", defaults)
        self.assertNotIn("GraphNodeSettingClasses", defaults)
        self.assertNotIn("Error", defaults)

    def test_pointer_audit_array_and_error_are_presence_only(self) -> None:
        body = authoring_result_body(origin_main_header())
        for field in PRESENCE_ONLY_FIELDS:
            self.assertIn(field, body)
        self.assertNotIn("Landscape =", body)
        self.assertNotIn("Graph =", body)
        self.assertNotIn("VisibleAudit =", body)
        self.assertNotIn("GraphNodeSettingClasses =", body)
        self.assertNotIn("Error =", body)
        self.assertNotIn("nullptr", body)
        self.assertNotIn("TEXT(", body)
        self.assertNotIn("FString()", body)
        self.assertNotIn("TArray()", body)
        defaults = in_class_defaults(body)
        self.assertNotIn("Landscape", defaults)
        self.assertNotIn("Graph", defaults)
        self.assertNotIn("VisibleAudit", defaults)
        self.assertNotIn("GraphNodeSettingClasses", defaults)
        self.assertNotIn("Error", defaults)
        pointer_defaults = dict(
            re.findall(r"TObjectPtr<[^>]+>\s+(\w+)\s*=\s*([^;]+);", body)
        )
        array_defaults = dict(
            re.findall(r"TArray<[^>]+>\s+(\w+)\s*=\s*([^;]+);", body)
        )
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        audit_defaults = dict(
            re.findall(
                r"FSkyguardLandscapeVisibleAudit\s+(\w+)\s*=\s*([^;]+);",
                body,
            )
        )
        self.assertEqual(pointer_defaults, {})
        self.assertEqual(array_defaults, {})
        self.assertEqual(string_defaults, {})
        self.assertEqual(audit_defaults, {})
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)

    def test_contract_does_not_re_lock_visible_audit_nested_defaults(self) -> None:
        body = authoring_result_body(origin_main_header())
        self.assertIn("FSkyguardLandscapeVisibleAudit VisibleAudit;", body)
        self.assertNotIn("struct FSkyguardLandscapeVisibleAudit", body)
        for field in VISIBLE_AUDIT_NESTED_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, body)
        self.assertNotIn("VisibleComponentCount", body)
        self.assertNotIn("RegisteredComponentCount", body)
        self.assertNotIn("RenderStateCreatedComponentCount", body)
        self.assertNotIn("HiddenInGameComponentCount", body)
        self.assertNotIn("GeneratedMaterialInstanceReadyComponentCount", body)
        self.assertNotIn("GovernedMaterialParentMatchComponentCount", body)
        self.assertNotIn("ContractCameraFrustumIntersectionCount", body)
        self.assertNotIn("bActorHiddenInGame", body)
        self.assertNotIn("bActorTemporarilyHiddenInEditor", body)
        self.assertNotIn("bBoundsFiniteAndNonzero", body)
        self.assertNotIn("BoundsMinimum", body)
        self.assertNotIn("BoundsMaximum", body)
        self.assertNotIn("FVector::ZeroVector", body)

    def test_contract_does_not_lock_material_or_capture_siblings(self) -> None:
        body = authoring_result_body(origin_main_header())
        for field in MATERIAL_COMPILATION_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, body)
        for field in CAPTURE_CONFIG_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, body)
        self.assertNotIn(
            "FSkyguardLandscapeMaterialCompilationResult",
            body,
        )
        self.assertNotIn(
            "FSkyguardLandscapeCaptureConfigurationResult",
            body,
        )
        self.assertNotIn("ESkyguardLandscapeCaptureDiagnosticMode", body)
        self.assertNotIn("GeneratedMaterialInstanceCount", body)
        self.assertNotIn("MaterialResourceCount", body)
        self.assertNotIn("CompilationFinishedResourceCount", body)
        self.assertNotIn("ValidShaderMapResourceCount", body)
        self.assertNotIn("bAssetCompilationQueueEmpty", body)
        self.assertNotIn("bShaderCompilationQueueEmpty", body)
        self.assertNotIn("bUsesShowOnlyLandscape", body)
        self.assertNotIn("ShowOnlyLandscapeComponentCount", body)
        self.assertNotIn("DiagnosticMaterialParentMatchComponentCount", body)
        self.assertNotIn("bRenderThreadSynchronized", body)
        self.assertNotIn("CaptureSource", body)
        self.assertNotIn("ViewMode", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = authoring_result_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = authoring_result_body(origin_main_header()).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                "FSkyguardMission01EnvironmentAuthoringResult contains "
                + banned,
            )

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in LOCKED_SCRIPTS:
            if (ROOT / sibling).exists():
                existing.append(sibling)
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", *existing],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
