from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardMission01EnvironmentAuthoringLibrary.h"
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
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_landscape_capture_config_defaults_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_landscape_height_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_footprint_sample_defaults_contract.py",
    "Scripts/tests/test_landscape_material_compilation_defaults_contract.py",
)
LIVE_MODES = [
    "Lit",
    "LandscapeCoverage",
    "ShaderComplexity",
    "ComponentBoundary",
]
SIBLING_TYPES = (
    "FSkyguardLandscapeCaptureConfigurationResult",
    "FSkyguardLandscapeVisibleAudit",
    "FSkyguardMission01EnvironmentAuthoringResult",
    "FSkyguardLandscapeMaterialCompilationResult",
)
SIBLING_DEFAULT_TOKENS = (
    "ESkyguardLandscapeCaptureDiagnosticMode Mode =",
    "ESkyguardLandscapeCaptureDiagnosticMode::Lit",
    "bUsesShowOnlyLandscape",
    "ShowOnlyLandscapeComponentCount",
    "DiagnosticMaterialParentMatchComponentCount",
    "bRenderThreadSynchronized",
    "VisibleComponentCount",
    "RegisteredComponentCount",
    "RenderStateCreatedComponentCount",
    "HiddenInGameComponentCount",
    "GovernedMaterialParentMatchComponentCount",
    "ContractCameraFrustumIntersectionCount",
    "bActorHiddenInGame",
    "bActorTemporarilyHiddenInEditor",
    "bBoundsFiniteAndNonzero",
    "BoundsMinimum",
    "BoundsMaximum",
    "GraphNodeCount",
    "GraphEdgeCount",
    "GraphNodeSettingClasses",
    "bLandscapeGuidValid",
    "bLandscapeTransformExact",
    "bGraphContractValid",
    "bAuthoredStructureReady",
    "bLicensedMeshSlotsEmpty",
    "bGenerationLocked",
    "GeneratedPCGComponentCount",
    "GeneratedPCGInstanceCount",
    "bRouteAndBeachGeneratedInstancesZero",
    "GeneratedMaterialInstanceCount",
    "MaterialResourceCount",
    "CompilationFinishedResourceCount",
    "ValidShaderMapResourceCount",
    "bAssetCompilationQueueEmpty",
    "bShaderCompilationQueueEmpty",
)
HARBOR_TUNING = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
    "40.f",
    "80.f",
)


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def enum_body(header: str, enum_name: str) -> str:
    start = header.index(f"enum class {enum_name}")
    brace = header.index("{", start)
    finish = header.index("}", brace)
    return header[brace : finish + 1]


def enum_enumerators(header: str, enum_name: str) -> list[str]:
    return re.findall(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\b",
        enum_body(header, enum_name),
        re.M,
    )


class LandscapeCaptureDiagnosticEnumContractTests(unittest.TestCase):
    def test_landscape_capture_diagnostic_enum_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "enum class ESkyguardLandscapeCaptureDiagnosticMode : uint8",
            header,
        )
        self.assertIn("UENUM(BlueprintType)", header)

    def test_enumerators_match_live_order(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardLandscapeCaptureDiagnosticMode",
        )
        self.assertEqual(enumerators, LIVE_MODES)
        self.assertEqual(
            enumerators,
            [
                "Lit",
                "LandscapeCoverage",
                "ShaderComplexity",
                "ComponentBoundary",
            ],
        )
        self.assertEqual(len(enumerators), 4, enumerators)
        body = enum_body(header, "ESkyguardLandscapeCaptureDiagnosticMode")
        for name in LIVE_MODES:
            self.assertIn(name, body)
            self.assertIn(name, enumerators)

    def test_diagnostic_enum_does_not_invent_index_none(self) -> None:
        header = origin_main(HEADER_NAME)
        enumerators = enum_enumerators(
            header,
            "ESkyguardLandscapeCaptureDiagnosticMode",
        )
        body = enum_body(header, "ESkyguardLandscapeCaptureDiagnosticMode")
        self.assertNotIn("INDEX_NONE", enumerators)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", enumerators)
        self.assertNotIn("NAME_None", body)

    def test_diagnostic_enum_does_not_require_rifle_or_igla(self) -> None:
        enumerators = enum_enumerators(
            origin_main(HEADER_NAME),
            "ESkyguardLandscapeCaptureDiagnosticMode",
        )
        self.assertNotIn("Rifle", enumerators)
        self.assertNotIn("Igla", enumerators)
        self.assertNotIn("Yak", enumerators)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

    def test_contract_is_diagnostic_enum_only(self) -> None:
        header = origin_main(HEADER_NAME)
        body = enum_body(header, "ESkyguardLandscapeCaptureDiagnosticMode")
        self.assertIn("Lit", body)
        self.assertIn("ComponentBoundary", body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for token in SIBLING_DEFAULT_TOKENS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        enumerators = enum_enumerators(
            header,
            "ESkyguardLandscapeCaptureDiagnosticMode",
        )
        self.assertEqual(enumerators, LIVE_MODES)
        self.assertNotEqual(enumerators, ["Rifle", "Igla"])

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
