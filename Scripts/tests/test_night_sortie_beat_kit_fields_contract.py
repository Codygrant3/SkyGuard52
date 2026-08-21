from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardNightSortieBeatKit.h"
STRUCT_NAME = "FSkyguardNightSortieBeatKit"
# Leftover #56–#64 plus NightSortieBeatKit production sources. This lane
# only adds an isolated Python field-presence contract.
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
# Isolated-test drafts stay off this lane. Beats[7] (#252),
# bKeepThermal (#250), night beat-kind enum (#246), night beat
# defaults (#247), NightEyes()/DownedBird() sequences (on-main),
# day-kit Beats[7] (#251), and loadout defaults (#253) are siblings.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_defaults_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_night_sortie_beat_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Apache CPG night-sortie-kit FName field presence only. These
# declarations have no in-struct initializer on origin/main.
PUBLIC_FIELDS = (
    "FName MissionId;",
    "FName WeatherIdentity;",
)
# Beats[7] (#252) and bKeepThermal (#250) may appear in the kit body
# but are not this lock surface.
SIBLING_FIELDS_NOT_LOCKED = (
    "FSkyguardNightSortieBeat Beats[7];",
    "bool bKeepThermal = true;",
)
BEAT_KINDS_NOT_LOCKED = (
    "DarkIngress",
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
NIGHT_BEAT_DEFAULTS_NOT_LOCKED = (
    "ESkyguardNightSortieBeatKind Kind =",
    "const TCHAR* Call =",
    "ESkyguardThreatKind Threat =",
    "ESkyguardNightSortieBeatKind::DarkIngress",
    'TEXT("")',
    "ESkyguardThreatKind::FastAttacker",
)
KIT_SEQUENCES_NOT_LOCKED = (
    "NightEyes",
    "DownedBird",
    "ForMission",
    "SequencesDiffer",
    "BeatIndexForElapsed",
    "KindAt",
)
SIBLING_TYPES = (
    "enum class ESkyguardNightSortieBeatKind",
    "struct FSkyguardNightSortieBeat",
    "FSkyguardDaySortieBeatKit",
    "FSkyguardDaySortieBeat",
    "ESkyguardDaySortieBeatKind",
    "FSkyguardStormRainBeatKit",
    "ESkyguardStormRainBeatKind",
    "ESkyguardSortieBeat",
    "FSkyguardLoadoutSpec",
    "ESkyguardMissionWeather",
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
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{HEADER_PATH} is missing from origin/main:{HEADER_PATH}: "
            f"{result.stderr.strip()}"
        )
    return result.stdout


def kit_body(header: str) -> str:
    marker = f"struct {STRUCT_NAME}"
    if marker not in header:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index(marker)
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def require_public_field(body: str, field: str) -> None:
    if field not in body:
        raise AssertionError(
            f"{field} is missing from origin/main:{HEADER_PATH} "
            f"struct {STRUCT_NAME}"
        )


def fname_presence_declarations(body: str) -> list[str]:
    return re.findall(r"^\s*FName\s+(\w+);", body, re.M)


def fname_assignments(body: str) -> dict[str, str]:
    return dict(
        re.findall(r"FName\s+(\w+)\s*=\s*([^;]+);", body)
    )


class NightSortieBeatKitFieldsContractTests(unittest.TestCase):
    def test_night_sortie_beat_kit_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"struct {STRUCT_NAME}", header)
        body = kit_body(header)
        self.assertIn("FName MissionId;", body)
        self.assertIn("FName WeatherIdentity;", body)
        self.assertNotIn("USTRUCT(", body)
        self.assertNotIn("GENERATED_BODY()", body)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            kit_body("struct FSkyguardUnrelated {\n};\n")
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_beat_struct_alone_does_not_satisfy_kit_struct(self) -> None:
        beat_only = (
            "struct FSkyguardNightSortieBeat\n"
            "{\n"
            "\tESkyguardNightSortieBeatKind Kind = "
            "ESkyguardNightSortieBeatKind::DarkIngress;\n"
            '\tconst TCHAR* Call = TEXT("");\n'
            "\tESkyguardThreatKind Threat = "
            "ESkyguardThreatKind::FastAttacker;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            kit_body(beat_only)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_mission_id_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            require_public_field(
                "{\n"
                "\tFName WeatherIdentity;\n"
                "\tbool bKeepThermal = true;\n"
                "\tFSkyguardNightSortieBeat Beats[7];\n"
                "};\n",
                "FName MissionId;",
            )
        self.assertIn("FName MissionId;", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_missing_weather_identity_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            require_public_field(
                "{\n"
                "\tFName MissionId;\n"
                "\tbool bKeepThermal = true;\n"
                "\tFSkyguardNightSortieBeat Beats[7];\n"
                "};\n",
                "FName WeatherIdentity;",
            )
        self.assertIn("FName WeatherIdentity;", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_public_fields_are_present_in_order(self) -> None:
        body = kit_body(origin_main_header())
        for field in PUBLIC_FIELDS:
            require_public_field(body, field)
            self.assertIn(field, body)
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        self.assertEqual(
            fname_presence_declarations(body),
            ["MissionId", "WeatherIdentity"],
        )
        self.assertNotIn("USTRUCT", body)
        self.assertNotIn("UPROPERTY", body)

    def test_fname_fields_have_no_in_struct_initializer(self) -> None:
        body = kit_body(origin_main_header())
        self.assertEqual(fname_assignments(body), {})
        self.assertNotIn("MissionId =", body)
        self.assertNotIn("WeatherIdentity =", body)
        self.assertNotIn("FName MissionId =", body)
        self.assertNotIn("FName WeatherIdentity =", body)
        self.assertIn("FName MissionId;", body)
        self.assertIn("FName WeatherIdentity;", body)
        self.assertNotIn("MissionId = NAME_None", body)
        self.assertNotIn("WeatherIdentity = NAME_None", body)
        self.assertNotIn("MissionId = INDEX_NONE", body)
        self.assertNotIn("WeatherIdentity = INDEX_NONE", body)

    def test_struct_does_not_invent_index_none(self) -> None:
        body = kit_body(origin_main_header())
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("= INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("FString", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_relock_beats_or_bkeepthermal(self) -> None:
        self.assertEqual(
            PUBLIC_FIELDS,
            (
                "FName MissionId;",
                "FName WeatherIdentity;",
            ),
        )
        joined = "\n".join(PUBLIC_FIELDS)
        self.assertNotIn("Beats[7]", joined)
        self.assertNotIn("bKeepThermal", joined)
        self.assertNotIn("true", joined)
        for field in SIBLING_FIELDS_NOT_LOCKED:
            self.assertNotIn(field, PUBLIC_FIELDS)
        self.assertNotEqual(
            PUBLIC_FIELDS,
            ("FSkyguardNightSortieBeat Beats[7];",),
        )
        self.assertNotEqual(
            PUBLIC_FIELDS,
            ("bool bKeepThermal = true;",),
        )

    def test_contract_does_not_relock_beat_kind_enum(self) -> None:
        body = kit_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardNightSortieBeatKind", body)
        self.assertNotIn("enum class", body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(f"ESkyguardNightSortieBeatKind::{name}", body)

    def test_contract_does_not_relock_night_sortie_beat_defaults(self) -> None:
        body = kit_body(origin_main_header())
        for token in NIGHT_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("Kind =", body)
        self.assertNotIn("Call =", body)
        self.assertNotIn("Threat =", body)
        self.assertNotIn("struct FSkyguardNightSortieBeat", body)

    def test_contract_does_not_lock_kit_sequences(self) -> None:
        body = kit_body(origin_main_header())
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
        self.assertNotIn("NightEyes()", body)
        self.assertNotIn("DownedBird()", body)
        self.assertNotIn("SequencesDiffer", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = kit_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = kit_body(origin_main_header())
        self.assertEqual(
            fname_presence_declarations(body),
            ["MissionId", "WeatherIdentity"],
        )
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(PUBLIC_FIELDS, ("Rifle", "Igla"))
        self.assertNotEqual(
            fname_presence_declarations(body),
            ["Rifle", "Igla"],
        )

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = kit_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "night-sortie-beat-kit fields are Apache CPG mission / "
                "weather identity, not Yak",
            )

    def test_contract_is_night_sortie_beat_kit_fields_only(self) -> None:
        header = origin_main_header()
        body = kit_body(header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        for field in PUBLIC_FIELDS:
            require_public_field(body, field)
            self.assertIn(field, body)
        self.assertEqual(
            fname_presence_declarations(body),
            ["MissionId", "WeatherIdentity"],
        )
        self.assertEqual(fname_assignments(body), {})
        self.assertNotIn("Beats[7]", "\n".join(PUBLIC_FIELDS))
        self.assertNotIn("bKeepThermal", "\n".join(PUBLIC_FIELDS))
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in NIGHT_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NightEyes", body)
        self.assertNotIn("DownedBird", body)
        self.assertNotIn("SequencesDiffer", body)
        self.assertNotEqual(PUBLIC_FIELDS, ("Rifle", "Igla"))

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
