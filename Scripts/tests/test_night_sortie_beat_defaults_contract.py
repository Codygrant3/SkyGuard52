from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardNightSortieBeatKit.h"
STRUCT_NAME = "FSkyguardNightSortieBeat"
# Leftover #56–#64 plus NightSortieBeatKit production sources.
# This lane only adds an isolated Python contract.
LOCKED = {
    "SkyguardNightSortieBeatKit.h",
    "SkyguardNightSortieBeatKit.cpp",
    "SkyguardNightSortieBeatKitTests.cpp",
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
# enum contracts and ESkyguardThreatKind (#127) are siblings.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_day_sortie_beat_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_threat_kind_roster_contract.py",
    "Scripts/tests/test_sortie_beat_enum_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_storm_runtime_defaults_contract.py",
)
# Apache CPG night-sortie beat in-struct defaults. Lock these only —
# not ESkyguardNightSortieBeatKind enumerators, not ESkyguardThreatKind,
# and not FSkyguardNightSortieBeatKit sequences / bKeepThermal.
PUBLIC_FIELDS = (
    "ESkyguardNightSortieBeatKind Kind = ESkyguardNightSortieBeatKind::DarkIngress;",
    'const TCHAR* Call = TEXT("");',
    "ESkyguardThreatKind Threat = ESkyguardThreatKind::FastAttacker;",
)
IN_CLASS_DEFAULTS = {
    "Kind": "ESkyguardNightSortieBeatKind::DarkIngress",
    "Call": 'TEXT("")',
    "Threat": "ESkyguardThreatKind::FastAttacker",
}
# Kit sequences, thermal flag, full beat-kind enum, and threat roster
# stay unlocked. DarkIngress / FastAttacker are in-struct defaults only.
TYPES_NOT_LOCKED = (
    "struct FSkyguardNightSortieBeatKit",
    "enum class ESkyguardNightSortieBeatKind",
    "enum class ESkyguardThreatKind",
    "bKeepThermal",
    "Beats[7]",
    "NightEyes",
    "DownedBird",
    "FName MissionId",
    "FName WeatherIdentity",
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
BEAT_KIND_ENUMERATORS_NOT_LOCKED = (
    "ThermalHunt",
    "RadarVanHunt",
    "RooftopHeat",
    "RadarNetCollapse",
    "IslandIngress",
    "SearchIsland",
    "HoldTheWreck",
    "RescuePressure",
    "RescueLift",
    "MixedSwarm",
    "Extraction",
)
THREAT_KIND_ENUMERATORS_NOT_LOCKED = (
    "HeavyAttacker",
    "RotorScout",
    "GroundArmor",
    "FastBoat",
)
INVENTED_DEFAULTS = (
    "NAME_None",
    "INDEX_NONE",
    "Error =",
    "FString()",
    "FString",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_TUNING = ("40.f", "80.f")
HARBOR_INCOMING = "IncomingRadar"
STRUCT_BODY_RE = re.compile(rf"struct {STRUCT_NAME}\s*\{{")


def origin_main_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{HEADER_PATH}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def night_sortie_beat_body(header: str) -> str:
    match = STRUCT_BODY_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = match.start()
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: re.sub(r"\s+", " ", value).strip()
        for name, value in re.findall(
            r"(?:ESkyguardNightSortieBeatKind|const TCHAR\*|ESkyguardThreatKind)"
            r"\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class NightSortieBeatDefaultsContractTests(unittest.TestCase):
    def test_night_sortie_beat_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertRegex(header, r"struct FSkyguardNightSortieBeat\s*\{")
        body = night_sortie_beat_body(header)
        self.assertIn("Kind =", body)
        self.assertIn("Call =", body)
        self.assertIn("Threat =", body)
        self.assertNotIn("USTRUCT", body)
        self.assertNotIn("GENERATED_BODY()", body)
        self.assertNotIn("UPROPERTY", body)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            night_sortie_beat_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_kit_struct_alone_does_not_satisfy_beat_struct(self) -> None:
        kit_only = (
            "struct FSkyguardNightSortieBeatKit\n"
            "{\n"
            "\tbool bKeepThermal = true;\n"
            "\tFSkyguardNightSortieBeat Beats[7];\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            night_sortie_beat_body(kit_only)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = night_sortie_beat_body(origin_main_header())
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertNotIn("USTRUCT", body)
        self.assertNotIn("UPROPERTY", body)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = night_sortie_beat_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(
            defaults.get("Kind"),
            "ESkyguardNightSortieBeatKind::DarkIngress",
        )
        self.assertEqual(defaults.get("Call"), 'TEXT("")')
        self.assertEqual(
            defaults.get("Threat"),
            "ESkyguardThreatKind::FastAttacker",
        )
        self.assertIn(
            "ESkyguardNightSortieBeatKind Kind = "
            "ESkyguardNightSortieBeatKind::DarkIngress;",
            body,
        )
        self.assertIn('const TCHAR* Call = TEXT("");', body)
        self.assertIn(
            "ESkyguardThreatKind Threat = ESkyguardThreatKind::FastAttacker;",
            body,
        )
        self.assertNotIn("Kind = INDEX_NONE", body)
        self.assertNotIn("Call = INDEX_NONE", body)
        self.assertNotIn("Threat = INDEX_NONE", body)
        self.assertNotIn("Call = NAME_None", body)
        self.assertEqual(len(defaults), 3, defaults)
        self.assertNotIn("Error", defaults)
        self.assertNotIn("bKeepThermal", defaults)
        self.assertNotIn("Beats", defaults)

    def test_struct_does_not_invent_index_none_or_error_defaults(self) -> None:
        body = night_sortie_beat_body(origin_main_header())
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
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})
        self.assertEqual(defaults.get("Call"), 'TEXT("")')

    def test_contract_does_not_lock_beat_kind_enum_or_kit(self) -> None:
        body = night_sortie_beat_body(origin_main_header())
        defaults = in_class_defaults(body)
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(name, defaults)
        self.assertNotIn("FSkyguardNightSortieBeatKit", body)
        self.assertNotIn("enum class ESkyguardNightSortieBeatKind", body)
        self.assertNotIn("enum class ESkyguardThreatKind", body)
        self.assertNotIn("bKeepThermal", body)
        self.assertNotIn("Beats[7]", body)
        self.assertNotIn("NightEyes", body)
        self.assertNotIn("DownedBird", body)
        self.assertNotIn("enum class", body)
        self.assertIn("ESkyguardNightSortieBeatKind::DarkIngress", body)
        self.assertIn("ESkyguardThreatKind::FastAttacker", body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(f"ESkyguardNightSortieBeatKind::{name}", body)
        for name in THREAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(f"ESkyguardThreatKind::{name}", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = night_sortie_beat_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = night_sortie_beat_body(origin_main_header())
        defaults = in_class_defaults(body)
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "night-sortie-beat defaults are Apache CPG beat fields, "
                "not Yak",
            )
            self.assertNotIn(banned, defaults)

    def test_contract_is_night_sortie_beat_defaults_only(self) -> None:
        body = night_sortie_beat_body(origin_main_header())
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertIn(
            "ESkyguardNightSortieBeatKind Kind = "
            "ESkyguardNightSortieBeatKind::DarkIngress;",
            body,
        )
        self.assertIn('const TCHAR* Call = TEXT("");', body)
        self.assertIn(
            "ESkyguardThreatKind Threat = ESkyguardThreatKind::FastAttacker;",
            body,
        )
        for name in TYPES_NOT_LOCKED:
            self.assertNotIn(name, body)
        for name in BEAT_KIND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for name in THREAT_KIND_ENUMERATORS_NOT_LOCKED:
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
        self.assertNotIn("bKeepThermal", defaults)
        self.assertNotIn("Beats", defaults)
        self.assertNotIn("MissionId", defaults)
        self.assertNotIn("WeatherIdentity", defaults)
        self.assertEqual(len(defaults), 3, defaults)
        self.assertEqual(list(defaults), ["Kind", "Call", "Threat"])

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
