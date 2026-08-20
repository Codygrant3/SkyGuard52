from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardCpgDebrief.h"
LOCKED = {
    "SkyguardCpgDebrief.h",
    "SkyguardCpgDebrief.cpp",
    "SkyguardCpgDebriefFailClosedTests.cpp",
    "SkyguardCpgDebriefLoadoutTests.cpp",
    "SkyguardCpgDebriefCargoCaptureTests.cpp",
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
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
    "Scripts/tests/test_mesh_bind_slot_contract.py",
    "Scripts/tests/test_audible_receipt_contract.py",
)
PUBLIC_FIELDS = (
    "bool bValid = false;",
    "bool bWon = false;",
    "FString MissionTitle;",
    "FString OutcomeNarrative;",
    "int32 Score = 0;",
    "int32 Medal = 0;",
    "int32 ShotsFired = 0;",
    "int32 Hits = 0;",
    "int32 CargoPercent = 100;",
    "bool bRadarDead = false;",
    "TArray<ESkyguardPatrolShipSystem> DestroyedSystems;",
    "ESkyguardLoadout SelectedLoadout = ESkyguardLoadout::Balanced;",
    "int32 CannonReady = 0;",
    "int32 RocketReady = 0;",
    "int32 GuidedReady = 0;",
)
IN_CLASS_DEFAULTS = {
    "bValid": "false",
    "bWon": "false",
    "Score": "0",
    "Medal": "0",
    "ShotsFired": "0",
    "Hits": "0",
    "CargoPercent": "100",
    "bRadarDead": "false",
    "SelectedLoadout": "ESkyguardLoadout::Balanced",
    "CannonReady": "0",
    "RocketReady": "0",
    "GuidedReady": "0",
}
PRESENCE_ONLY_FIELDS = (
    "FString MissionTitle;",
    "FString OutcomeNarrative;",
    "TArray<ESkyguardPatrolShipSystem> DestroyedSystems;",
)
LOADOUTS_NOT_LOCKED = (
    "AntiArmor",
    "RocketHeavy",
    "Intercept",
)
CAPTURE_COPY_SYMBOLS = (
    "SkyguardCaptureCpgDebrief",
    "SkyguardBuildCpgDebriefCopy",
)
HARBOR_TUNING = ("40.f", "80.f")


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def snapshot_body(header: str) -> str:
    start = header.index("struct FSkyguardCpgDebriefSnapshot")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:bool|int32|ESkyguardLoadout)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class CpgDebriefSnapshotDefaultsContractTests(unittest.TestCase):
    def test_snapshot_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardCpgDebriefSnapshot", header)
        self.assertIn('#include "SkyguardGunshipTypes.h"', header)
        body = snapshot_body(header)
        self.assertNotIn("USTRUCT", body)
        self.assertNotIn("GENERATED_BODY()", body)

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = snapshot_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = snapshot_body(origin_main(HEADER_NAME))
        self.assertEqual(in_class_defaults(body), IN_CLASS_DEFAULTS)
        self.assertIn("bool bValid = false;", body)
        self.assertIn("bool bWon = false;", body)
        self.assertIn("int32 Score = 0;", body)
        self.assertIn("int32 Medal = 0;", body)
        self.assertIn("int32 ShotsFired = 0;", body)
        self.assertIn("int32 Hits = 0;", body)
        self.assertIn("int32 CargoPercent = 100;", body)
        self.assertIn("bool bRadarDead = false;", body)
        self.assertIn(
            "ESkyguardLoadout SelectedLoadout = ESkyguardLoadout::Balanced;",
            body,
        )
        self.assertIn("int32 CannonReady = 0;", body)
        self.assertIn("int32 RocketReady = 0;", body)
        self.assertIn("int32 GuidedReady = 0;", body)
        self.assertEqual(
            re.findall(r"ESkyguardLoadout::(\w+)", body),
            ["Balanced"],
        )

    def test_string_and_array_fields_are_presence_only(self) -> None:
        body = snapshot_body(origin_main(HEADER_NAME))
        for field in PRESENCE_ONLY_FIELDS:
            self.assertIn(field, body)
        self.assertNotIn("MissionTitle =", body)
        self.assertNotIn("OutcomeNarrative =", body)
        self.assertNotIn("DestroyedSystems =", body)
        self.assertNotIn("TEXT(", body)
        self.assertNotIn("TArray<", body[body.index("DestroyedSystems") :])
        defaults = in_class_defaults(body)
        self.assertNotIn("MissionTitle", defaults)
        self.assertNotIn("OutcomeNarrative", defaults)
        self.assertNotIn("DestroyedSystems", defaults)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = snapshot_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)

    def test_contract_does_not_lock_capture_or_copy(self) -> None:
        body = snapshot_body(origin_main(HEADER_NAME))
        for symbol in CAPTURE_COPY_SYMBOLS:
            self.assertNotIn(symbol, body)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", body)

    def test_contract_does_not_relock_other_loadouts_or_ship_enums(self) -> None:
        body = snapshot_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardLoadout", body)
        self.assertNotIn("enum class ESkyguardPatrolShipSystem", body)
        for name in LOADOUTS_NOT_LOCKED:
            self.assertNotIn(f"ESkyguardLoadout::{name}", body)
        self.assertNotIn("ESkyguardPatrolShipSystem::", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = snapshot_body(origin_main(HEADER_NAME))
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)

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
