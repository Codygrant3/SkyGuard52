from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardDaySortieBeatKit.h"
STRUCT_NAME = "FSkyguardDaySortieBeat"
# Leftover #56–#64 plus DaySortieBeatKit production sources/tests.
# This lane only adds an isolated Python defaults contract.
LOCKED = {
    "SkyguardDaySortieBeatKit.h",
    "SkyguardDaySortieBeatKit.cpp",
    "SkyguardDaySortieBeatKitTests.cpp",
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
# Isolated-test drafts #107–#243 and newer stay off this lane.
# On-main beat-kit contract plus in-flight day/night/storm beat-kind
# enum contracts and sibling isolated defaults stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
    "Scripts/tests/test_sortie_beat_enum_contract.py",
    "Scripts/tests/test_mission09_pool_runtime_defaults_contract.py",
    "Scripts/tests/test_mission09_pool_budget_defaults_contract.py",
    "Scripts/tests/test_mission09_wave_state_enum_contract.py",
    "Scripts/tests/test_iron_rain_maneuver_enum_contract.py",
    "Scripts/tests/test_search_track_runtime_defaults_contract.py",
    "Scripts/tests/test_search_sector_enum_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
)
# Apache CPG day-sortie beat in-struct defaults. RidgeIngress is the
# Kind default only — not the full ESkyguardDaySortieBeatKind set.
PUBLIC_FIELDS = (
    "ESkyguardDaySortieBeatKind Kind = ESkyguardDaySortieBeatKind::RidgeIngress;",
    'const TCHAR* Call = TEXT("");',
    "ESkyguardThreatKind Threat = ESkyguardThreatKind::GroundArmor;",
)
IN_CLASS_DEFAULTS = {
    "Kind": "ESkyguardDaySortieBeatKind::RidgeIngress",
    "Call": 'TEXT("")',
    "Threat": "ESkyguardThreatKind::GroundArmor",
}
# Full beat-kind enum (#244 in flight), threat-kind enum (#127), kit
# sequences, and BrokenHighway() stay unlocked.
TYPES_NOT_LOCKED = (
    "enum class ESkyguardDaySortieBeatKind",
    "enum class ESkyguardThreatKind",
    "struct FSkyguardDaySortieBeatKit",
    "BrokenHighway",
    "DustOffensive",
    "HunterKiller",
    "ForMission",
    "SequencesDiffer",
    "BeatIndexForElapsed",
    "KindAt",
    "WeatherIdentity",
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
BEAT_KINDS_NOT_LOCKED = (
    "TechnicalScreen",
    "ClusterRidge",
    "TankAmbush",
    "ConvoyPressure",
    "ArmorColumn",
    "HazeIngress",
    "FenceSweep",
    "DugInLine",
    "AdaAcquire",
    "AdaSuppress",
    "ArmorPush",
    "DuskIngress",
    "SensorTrack",
    "DecoyScreen",
    "TelAcquire",
    "TelStrike",
    "ConvoyBreak",
    "Extraction",
)
THREAT_KINDS_NOT_LOCKED = (
    "FastAttacker",
    "HeavyAttacker",
    "RotorScout",
    "FastBoat",
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Error =",
    "FString()",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")
HARBOR_INCOMING = "IncomingRadar"


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def day_sortie_beat_body(header: str) -> str:
    marker = f"struct {STRUCT_NAME}"
    if marker not in header:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:ESkyguardDaySortieBeatKind|const TCHAR\*|ESkyguardThreatKind)"
            r"\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class DaySortieBeatDefaultsContractTests(unittest.TestCase):
    def test_day_sortie_beat_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        body = day_sortie_beat_body(header)
        self.assertIn("ESkyguardDaySortieBeatKind Kind =", body)
        self.assertNotIn("USTRUCT(", body)
        self.assertNotIn("GENERATED_BODY()", body)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            day_sortie_beat_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = day_sortie_beat_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(body.count("UPROPERTY("), 0)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = day_sortie_beat_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(
            defaults.get("Kind"),
            "ESkyguardDaySortieBeatKind::RidgeIngress",
        )
        self.assertEqual(defaults.get("Call"), 'TEXT("")')
        self.assertEqual(
            defaults.get("Threat"),
            "ESkyguardThreatKind::GroundArmor",
        )
        self.assertIn(
            "ESkyguardDaySortieBeatKind Kind = "
            "ESkyguardDaySortieBeatKind::RidgeIngress;",
            body,
        )
        self.assertIn('const TCHAR* Call = TEXT("");', body)
        self.assertIn(
            "ESkyguardThreatKind Threat = ESkyguardThreatKind::GroundArmor;",
            body,
        )
        self.assertNotIn("Kind = INDEX_NONE", body)
        self.assertNotIn("Call = INDEX_NONE", body)
        self.assertNotIn("Threat = INDEX_NONE", body)
        self.assertEqual(len(defaults), 3, defaults)
        self.assertNotIn("Error", defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = day_sortie_beat_body(origin_main_header())
        defaults = in_class_defaults(body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", defaults.values())
        self.assertNotIn("NAME_None", defaults.values())
        self.assertNotIn("Error", defaults)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("FString Error", body)
        self.assertNotIn("FString", body)
        self.assertEqual(defaults.get("Call"), 'TEXT("")')
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_lock_beat_kind_or_threat_kind_enums(self) -> None:
        body = day_sortie_beat_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertNotIn("enum class ESkyguardDaySortieBeatKind", body)
        self.assertNotIn("enum class ESkyguardThreatKind", body)
        self.assertIn("ESkyguardDaySortieBeatKind::RidgeIngress", body)
        self.assertIn("ESkyguardThreatKind::GroundArmor", body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
            self.assertNotIn(f"ESkyguardDaySortieBeatKind::{name}", body)
        for name in THREAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
            self.assertNotIn(f"ESkyguardThreatKind::{name}", body)
        self.assertNotIn("enum class", body)

    def test_contract_does_not_lock_kit_sequences_or_broken_highway(self) -> None:
        body = day_sortie_beat_body(origin_main_header())
        defaults = in_class_defaults(body)
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        self.assertNotIn("FSkyguardDaySortieBeatKit", body)
        self.assertNotIn("BrokenHighway", body)
        self.assertNotIn("DustOffensive", body)
        self.assertNotIn("HunterKiller", body)
        self.assertNotIn("SequencesDiffer", body)
        self.assertNotIn("BeatIndexForElapsed", body)
        self.assertNotIn("KindAt", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = day_sortie_beat_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = day_sortie_beat_body(origin_main_header())
        defaults = in_class_defaults(body)
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "day-sortie-beat defaults are Apache CPG ridge ingress, "
                "not Yak",
            )
            self.assertNotIn(banned, defaults)

    def test_contract_is_day_sortie_beat_defaults_only(self) -> None:
        body = day_sortie_beat_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn(
            "ESkyguardDaySortieBeatKind Kind = "
            "ESkyguardDaySortieBeatKind::RidgeIngress;",
            body,
        )
        self.assertIn('const TCHAR* Call = TEXT("");', body)
        self.assertIn(
            "ESkyguardThreatKind Threat = ESkyguardThreatKind::GroundArmor;",
            body,
        )
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for name in THREAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotEqual(list(defaults), ["Rifle", "Igla"])
        self.assertNotIn("BrokenHighway", defaults)
        self.assertNotIn("SequencesDiffer", defaults)
        self.assertEqual(len(defaults), 3, defaults)

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
