from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardRuntimeMeshCatalog.h"
LOCKED = {
    "SkyguardRuntimeMeshCatalog.h",
    "SkyguardRuntimeMeshCatalog.cpp",
    "SkyguardRuntimeMeshCatalogTests.cpp",
    "SkyguardRuntimeMeshCatalogFailClosedTests.cpp",
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
SIBLING_CONTRACTS = (
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
    "Scripts/tests/test_route_definition_defaults_contract.py",
    "Scripts/tests/test_route_point_defaults_contract.py",
    "Scripts/tests/test_runtime_mesh_catalog_fail_closed.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
PUBLIC_FIELDS = (
    "FName SlotId;",
    "TSoftObjectPtr<UStaticMesh> Preferred;",
    "TSoftObjectPtr<UStaticMesh> ProxyFallback;",
    "FString Notes;",
)
# USkyguardRuntimeMeshCatalog unknown-slot fail-closed (#140) stays on
# its own isolated draft. This contract locks bind-slot fields only.
CATALOG_FAIL_CLOSED_SYMBOLS = (
    "FindSlot",
    "ResolveMesh",
    "ResolveDefaultSlot",
    "ResolveSlot",
    "EnsureDefaultSlots",
    "GetCodeDefaultSlots",
    "GetWebGameLastResortPath",
    "ResolveOrderedSoftPaths",
    "LogWebGameLastResortOnce",
    "DefaultCatalogAssetPath",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "FSoftObjectPath",
    "/Game/",
    "TEXT(",
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


def mesh_bind_slot_body(header: str) -> str:
    start = header.index("struct FSkyguardMeshBindSlot")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def assigned_fields(body: str) -> list[str]:
    return re.findall(
        r"(?:FName|TSoftObjectPtr<UStaticMesh>|FString)\s+(\w+)\s*=",
        body,
    )


class MeshBindSlotFieldsContractTests(unittest.TestCase):
    def test_mesh_bind_slot_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardMeshBindSlot", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", mesh_bind_slot_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = mesh_bind_slot_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertIn("SlotId", body)
        self.assertIn("Preferred", body)
        self.assertIn("ProxyFallback", body)
        self.assertIn("Notes", body)
        self.assertEqual(body.count("UPROPERTY("), 4)
        self.assertEqual(
            body.count(
                'UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Skyguard|MeshBind")'
            ),
            4,
        )

    def test_struct_has_no_in_class_numeric_or_invented_defaults(self) -> None:
        body = mesh_bind_slot_body(origin_main(HEADER_NAME))
        self.assertEqual(assigned_fields(body), [])
        self.assertNotIn("SlotId =", body)
        self.assertNotIn("Preferred =", body)
        self.assertNotIn("ProxyFallback =", body)
        self.assertNotIn("Notes =", body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn(" = NAME_None", body)
        self.assertNotIn(" = INDEX_NONE", body)
        self.assertNotIn("int32", body)
        self.assertNotIn("float", body)
        self.assertNotIn(" = 0", body)
        self.assertNotIn(" = 0.f", body)

    def test_contract_does_not_relock_catalog_fail_closed(self) -> None:
        body = mesh_bind_slot_body(origin_main(HEADER_NAME))
        self.assertNotIn("class USkyguardRuntimeMeshCatalog", body)
        self.assertNotIn("USkyguardRuntimeMeshCatalog", body)
        for name in CATALOG_FAIL_CLOSED_SYMBOLS:
            self.assertNotIn(name, body)
        self.assertNotIn("nullptr", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("unknown", body.lower())
        self.assertNotIn("fail-closed", body.lower())
        self.assertNotIn("FailClosed", body)

    def test_struct_does_not_retune_harbor_or_invent_live_copy(self) -> None:
        body = mesh_bind_slot_body(origin_main(HEADER_NAME))
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("rifle", body.lower())

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = mesh_bind_slot_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardMeshBindSlot contains {banned}",
            )

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in SIBLING_CONTRACTS:
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
