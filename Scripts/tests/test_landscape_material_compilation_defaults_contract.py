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
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_phase4_m01_landscape_repair_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_landscape_capture_config_defaults_contract.py",
    "Scripts/tests/test_landscape_capture_configuration_defaults_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "bool bSuccess = false;",
    "int32 LandscapeComponentCount = 0;",
    "int32 GeneratedMaterialInstanceCount = 0;",
    "int32 MaterialResourceCount = 0;",
    "int32 CompilationFinishedResourceCount = 0;",
    "int32 ValidShaderMapResourceCount = 0;",
    "bool bAssetCompilationQueueEmpty = false;",
    "bool bShaderCompilationQueueEmpty = false;",
    "FString Error;",
)
IN_CLASS_DEFAULTS = {
    "bSuccess": "false",
    "LandscapeComponentCount": "0",
    "GeneratedMaterialInstanceCount": "0",
    "MaterialResourceCount": "0",
    "CompilationFinishedResourceCount": "0",
    "ValidShaderMapResourceCount": "0",
    "bAssetCompilationQueueEmpty": "false",
    "bShaderCompilationQueueEmpty": "false",
}
PRESENCE_ONLY_FIELDS = ("FString Error;",)
# FSkyguardLandscapeVisibleAudit stays on a sibling worker.
VISIBLE_AUDIT_FIELDS_NOT_LOCKED = (
    "struct FSkyguardLandscapeVisibleAudit",
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
# FSkyguardLandscapeCaptureConfigurationResult stays on a sibling worker.
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
# FSkyguardMission01EnvironmentAuthoringResult stays on a later worker.
AUTHORING_RESULT_FIELDS_NOT_LOCKED = (
    "struct FSkyguardMission01EnvironmentAuthoringResult",
    "TObjectPtr<ALandscape> Landscape;",
    "TObjectPtr<UPCGGraph> Graph;",
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
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Error =",
    "TEXT(",
    "FString()",
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


def compilation_body(header: str) -> str:
    start = header.index("struct FSkyguardLandscapeMaterialCompilationResult")
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


class LandscapeMaterialCompilationDefaultsContractTests(unittest.TestCase):
    def test_compilation_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn("struct FSkyguardLandscapeMaterialCompilationResult", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", compilation_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = compilation_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 9)
        self.assertEqual(
            body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"),
            9,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = compilation_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn("bool bSuccess = false;", body)
        self.assertIn("int32 LandscapeComponentCount = 0;", body)
        self.assertIn("int32 GeneratedMaterialInstanceCount = 0;", body)
        self.assertIn("int32 MaterialResourceCount = 0;", body)
        self.assertIn("int32 CompilationFinishedResourceCount = 0;", body)
        self.assertIn("int32 ValidShaderMapResourceCount = 0;", body)
        self.assertIn("bool bAssetCompilationQueueEmpty = false;", body)
        self.assertIn("bool bShaderCompilationQueueEmpty = false;", body)
        self.assertNotIn("bSuccess = true", body)
        self.assertNotIn("bAssetCompilationQueueEmpty = true", body)
        self.assertNotIn("bShaderCompilationQueueEmpty = true", body)
        self.assertEqual(len(defaults), 8, defaults)
        self.assertNotIn("Error", defaults)

    def test_error_is_presence_only_without_invented_defaults(self) -> None:
        body = compilation_body(origin_main_header())
        for field in PRESENCE_ONLY_FIELDS:
            self.assertIn(field, body)
        self.assertNotIn("Error =", body)
        self.assertNotIn("TEXT(", body)
        self.assertNotIn("FString()", body)
        defaults = in_class_defaults(body)
        self.assertNotIn("Error", defaults)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)

    def test_contract_does_not_lock_visible_audit_or_capture_or_authoring(self) -> None:
        body = compilation_body(origin_main_header())
        for field in VISIBLE_AUDIT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, body)
        for field in CAPTURE_CONFIG_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, body)
        for field in AUTHORING_RESULT_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, body)
        self.assertNotIn("ESkyguardLandscapeCaptureDiagnosticMode", body)
        self.assertNotIn("CaptureSource", body)
        self.assertNotIn("ViewMode", body)
        self.assertNotIn("VisibleAudit", body)
        self.assertNotIn("GraphNodeCount", body)
        self.assertNotIn("GeneratedPCGComponentCount", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = compilation_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = compilation_body(origin_main_header()).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardLandscapeMaterialCompilationResult contains {banned}",
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
