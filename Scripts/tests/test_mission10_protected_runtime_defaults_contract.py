from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMission10IntegrationDirector.h"
# Leftover #56–#64 plus Mission 10 / Last Flight production sources.
# This lane only adds an isolated Python contract.
LOCKED = {
    "SkyguardMission10IntegrationDirector.h",
    "SkyguardMission10IntegrationDirector.cpp",
    "SkyguardLastFlightBoss.h",
    "SkyguardLastFlightBoss.cpp",
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
# Isolated-test drafts #107–#214 and newer stay off this lane.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_landscape_visible_audit_defaults_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_searchlight_track_runtime_defaults_contract.py",
    "Scripts/tests/test_hoist_window_runtime_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
)
# Group default is split across two lines on origin/main; markers stay in order.
PUBLIC_FIELDS = (
    "ESkyguardMission10ProtectedGroup Group =",
    "int32 Integrity = 100;",
    "bool bDestroyed = false;",
)
IN_CLASS_DEFAULTS = {
    "Group": "ESkyguardMission10ProtectedGroup::Convoy",
    "Integrity": "100",
    "bDestroyed": "false",
}
# Full enumerator set, route phase, readiness, and Last Flight stay unlocked.
SIBLING_TYPES = (
    "FSkyguardMission10IntegrationReadiness",
    "ESkyguardMission10RoutePhase",
    "ESkyguardLastFlightStage",
    "enum class ESkyguardMission10ProtectedGroup",
    "enum class ESkyguardMission10RoutePhase",
)
ENUM_MEMBERS_NOT_LOCKED = (
    "FerryTerminal",
    "EvacuationShip",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Error =",
    "TEXT(",
    "FString()",
    'TEXT("")',
)


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def protected_runtime_body(header: str) -> str:
    marker = "struct FSkyguardMission10ProtectedRuntime"
    if marker not in header:
        raise AssertionError(
            "FSkyguardMission10ProtectedRuntime is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:ESkyguardMission10ProtectedGroup|int32|bool)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class Mission10ProtectedRuntimeDefaultsContractTests(unittest.TestCase):
    def test_protected_runtime_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn("struct FSkyguardMission10ProtectedRuntime", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", protected_runtime_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = protected_runtime_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 3)
        self.assertEqual(
            body.count("UPROPERTY(VisibleAnywhere, BlueprintReadOnly)"),
            3,
        )

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = protected_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(
            defaults.get("Group"),
            "ESkyguardMission10ProtectedGroup::Convoy",
        )
        self.assertEqual(defaults.get("Integrity"), "100")
        self.assertEqual(defaults.get("bDestroyed"), "false")
        compact = re.sub(r"\s+", " ", body)
        self.assertIn(
            "ESkyguardMission10ProtectedGroup Group = "
            "ESkyguardMission10ProtectedGroup::Convoy;",
            compact,
        )
        self.assertIn("int32 Integrity = 100;", body)
        self.assertIn("bool bDestroyed = false;", body)
        self.assertNotIn("bDestroyed = true", body)
        self.assertNotIn("Integrity = 0", body)
        self.assertEqual(len(defaults), 3, defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = protected_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", defaults.values())
        self.assertNotIn("NAME_None", defaults.values())
        self.assertNotIn("Error", defaults)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("FString Error", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_lock_readiness_route_or_last_flight(self) -> None:
        body = protected_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        for member in ENUM_MEMBERS_NOT_LOCKED:
            self.assertNotIn(member, body)
            self.assertNotIn(member, defaults.values())
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = protected_runtime_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn("IncomingRadar", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = protected_runtime_body(origin_main_header())
        defaults = in_class_defaults(body)
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                "FSkyguardMission10ProtectedRuntime contains "
                f"{banned}; escort integrity is Apache CPG, not Yak",
            )
            self.assertNotIn(banned, defaults)

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
