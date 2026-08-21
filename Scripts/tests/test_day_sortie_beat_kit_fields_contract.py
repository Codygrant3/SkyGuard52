from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardDaySortieBeatKit.h"
STRUCT_NAME = "FSkyguardDaySortieBeatKit"
# Leftover #56–#64 plus DaySortieBeatKit production sources/tests.
# This lane only adds an isolated Python FName field-presence contract.
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
# Isolated-test drafts #107–#253 and newer stay off this lane.
# Beats[7] (#251), beat-kind enum (#244), beat defaults (#249),
# night-kit Beats[7] (#252), loadout defaults (#253), and on-main
# BrokenHighway() sequences stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_day_sortie_beat_kit_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_day_sortie_beat_defaults_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_storm_rain_beat_kit_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Apache CPG day-sortie kit FName field presence only.
# MissionId / WeatherIdentity have no in-struct initializer on
# origin/main. Lock declaration presence, not values. Beats[7]
# may appear in the kit body but is not the lock surface (#251).
LOCKED_FIELDS = (
    "FName MissionId;",
    "FName WeatherIdentity;",
)
BEATS_NOT_LOCKED = "FSkyguardDaySortieBeat Beats[7];"
BEAT_KINDS_NOT_LOCKED = (
    "RidgeIngress",
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
DAY_BEAT_DEFAULTS_NOT_LOCKED = (
    "ESkyguardDaySortieBeatKind Kind =",
    "const TCHAR* Call =",
    "ESkyguardThreatKind Threat =",
    "ESkyguardDaySortieBeatKind::RidgeIngress",
    'TEXT("")',
    "ESkyguardThreatKind::GroundArmor",
)
KIT_SEQUENCES_NOT_LOCKED = (
    "BrokenHighway",
    "DustOffensive",
    "HunterKiller",
    "ForMission",
    "SequencesDiffer",
    "BeatIndexForElapsed",
    "KindAt",
)
LOADOUT_NOT_LOCKED = (
    "FSkyguardLoadoutSpec",
    "ESkyguardLoadout",
    "CannonMagazineSize",
    "GuidedMagazineSize",
    "FlareCount",
    "PlaystyleLine",
    "StartingStation",
)
NIGHT_BEATS_NOT_LOCKED = (
    "FSkyguardNightSortieBeat Beats[7];",
    "FSkyguardNightSortieBeatKit",
    "FSkyguardNightSortieBeat",
    "ESkyguardNightSortieBeatKind",
    "bKeepThermal",
)
SIBLING_TYPES = (
    "enum class ESkyguardDaySortieBeatKind",
    "struct FSkyguardDaySortieBeat",
    "namespace SkyguardDaySortieBeatKit",
    "FSkyguardStormRainBeatKit",
    "ESkyguardStormRainBeatKind",
    "ESkyguardSortieBeat",
    "FSkyguardMission04IntegrationReadiness",
    "bYakRuntimeReady",
)
INVENTED_FIELDS = (
    "BeatCount",
    "Kinds",
    "Threats",
    "Stations",
    "Calls",
    "Title",
    "WeatherLabel",
    "bHydraForClusters",
    "bKeepThermal",
    "INDEX_NONE",
    "NAME_None",
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
STRUCT_BODY_RE = re.compile(rf"struct {STRUCT_NAME}\s*\{{")


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
    match = STRUCT_BODY_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = match.start()
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def fname_declaration(body: str, name: str) -> str:
    match = re.search(rf"FName\s+{re.escape(name)};", body)
    if match is None:
        raise AssertionError(
            f"FName {name} is missing from origin/main:{HEADER_PATH} "
            f"struct {STRUCT_NAME}"
        )
    return match.group(0)


def fname_declarations(body: str) -> list[str]:
    return re.findall(r"FName\s+[A-Za-z_][A-Za-z0-9_]*;", body)


def fname_assignments(body: str) -> dict[str, str]:
    return dict(re.findall(r"FName\s+(\w+)\s*=\s*([^;]+);", body))


class DaySortieBeatKitFieldsContractTests(unittest.TestCase):
    def test_day_sortie_beat_kit_struct_exists(self) -> None:
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
            "struct FSkyguardDaySortieBeat\n"
            "{\n"
            "\tESkyguardDaySortieBeatKind Kind = "
            "ESkyguardDaySortieBeatKind::RidgeIngress;\n"
            '\tconst TCHAR* Call = TEXT("");\n'
            "\tESkyguardThreatKind Threat = "
            "ESkyguardThreatKind::GroundArmor;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            kit_body(beat_only)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_mission_id_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            fname_declaration(
                "{\n\tFName WeatherIdentity;\n};\n",
                "MissionId",
            )
        self.assertIn("MissionId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_missing_weather_identity_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            fname_declaration(
                "{\n\tFName MissionId;\n};\n",
                "WeatherIdentity",
            )
        self.assertIn("WeatherIdentity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_initialized_fname_does_not_satisfy_declaration(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            fname_declaration(
                "{\n\tFName MissionId = NAME_None;\n"
                "\tFName WeatherIdentity = NAME_None;\n};\n",
                "MissionId",
            )
        self.assertIn("MissionId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_public_fname_fields_match_origin_main_in_order(self) -> None:
        body = kit_body(origin_main_header())
        fields = fname_declarations(body)
        self.assertEqual(fields, list(LOCKED_FIELDS))
        positions = [body.index(field) for field in LOCKED_FIELDS]
        self.assertEqual(positions, sorted(positions), LOCKED_FIELDS)
        for field in LOCKED_FIELDS:
            self.assertIn(field, body)
        self.assertEqual(fname_declaration(body, "MissionId"), "FName MissionId;")
        self.assertEqual(
            fname_declaration(body, "WeatherIdentity"),
            "FName WeatherIdentity;",
        )
        self.assertEqual(body.count("UPROPERTY("), 0)

    def test_fname_fields_have_no_in_struct_initializer(self) -> None:
        body = kit_body(origin_main_header())
        self.assertEqual(fname_assignments(body), {})
        self.assertNotIn("MissionId =", body)
        self.assertNotIn("WeatherIdentity =", body)
        self.assertNotIn(" = NAME_None", body)
        self.assertNotIn(" = INDEX_NONE", body)
        self.assertNotIn("= NAME_None", body)
        self.assertNotIn("= INDEX_NONE", body)
        for field in LOCKED_FIELDS:
            self.assertNotIn(f"{field[:-1]} =", body)

    def test_struct_does_not_invent_index_none_or_extra_fields(self) -> None:
        body = kit_body(origin_main_header())
        fields = fname_declarations(body)
        self.assertEqual(fields, list(LOCKED_FIELDS))
        for token in INVENTED_FIELDS:
            self.assertNotIn(token, fields)
            if token in ("INDEX_NONE", "NAME_None"):
                self.assertNotIn(token, body)
        for token in INVENTED_DEFAULTS:
            self.assertNotIn(token, body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("FString", body)
        self.assertNotIn("int32", body)
        self.assertNotIn("float", body)
        string_defaults = dict(
            re.findall(r"FString\s+(\w+)\s*=\s*([^;]+);", body)
        )
        self.assertEqual(string_defaults, {})

    def test_contract_does_not_lock_beats_array(self) -> None:
        body = kit_body(origin_main_header())
        fields = fname_declarations(body)
        self.assertEqual(fields, list(LOCKED_FIELDS))
        self.assertNotIn(BEATS_NOT_LOCKED, LOCKED_FIELDS)
        self.assertNotIn("Beats[7]", LOCKED_FIELDS)
        self.assertNotIn("Beats", fields)
        self.assertNotIn("FSkyguardDaySortieBeat Beats[7];", fields)

    def test_contract_does_not_relock_beat_kind_enum(self) -> None:
        body = kit_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardDaySortieBeatKind", body)
        self.assertNotIn("enum class", body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(f"ESkyguardDaySortieBeatKind::{name}", body)

    def test_contract_does_not_relock_day_sortie_beat_defaults(self) -> None:
        body = kit_body(origin_main_header())
        for token in DAY_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("Kind =", body)
        self.assertNotIn("Call =", body)
        self.assertNotIn("Threat =", body)
        self.assertNotIn("struct FSkyguardDaySortieBeat", body)

    def test_contract_does_not_lock_kit_sequences(self) -> None:
        body = kit_body(origin_main_header())
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
        self.assertNotIn("BrokenHighway()", body)
        self.assertNotIn("DustOffensive()", body)
        self.assertNotIn("HunterKiller()", body)
        self.assertNotIn("namespace SkyguardDaySortieBeatKit", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)

    def test_contract_does_not_lock_night_kit_beats_or_loadout(self) -> None:
        body = kit_body(origin_main_header())
        for token in NIGHT_BEATS_NOT_LOCKED:
            self.assertNotIn(token, body)
        for token in LOADOUT_NOT_LOCKED:
            self.assertNotIn(token, body)
        self.assertNotIn("FSkyguardNightSortieBeat Beats[7];", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = kit_body(origin_main_header())
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("FSkyguardMission04IntegrationReadiness", body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = kit_body(origin_main_header())
        fields = fname_declarations(body)
        self.assertEqual(fields, list(LOCKED_FIELDS))
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(fields, ["Rifle", "Igla"])
        self.assertNotEqual(fields, ["FName Rifle;", "FName Igla;"])

    def test_struct_bans_igla_yak_rifle(self) -> None:
        body = kit_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"{STRUCT_NAME} contains {banned}; "
                "day-sortie-beat-kit FName fields are Apache CPG "
                "mission/weather identity, not Yak",
            )

    def test_contract_is_day_sortie_beat_kit_fields_only(self) -> None:
        header = origin_main_header()
        body = kit_body(header)
        fields = fname_declarations(body)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(fields, list(LOCKED_FIELDS))
        self.assertIn("FName MissionId;", body)
        self.assertIn("FName WeatherIdentity;", body)
        self.assertEqual(fname_assignments(body), {})
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for name in BEAT_KINDS_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in DAY_BEAT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, body)
        for name in KIT_SEQUENCES_NOT_LOCKED:
            self.assertNotIn(name, body)
        for token in NIGHT_BEATS_NOT_LOCKED:
            self.assertNotIn(token, body)
        for token in LOADOUT_NOT_LOCKED:
            self.assertNotIn(token, body)
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
        self.assertNotIn("NAME_None", body)
        self.assertNotEqual(fields, ["Rifle", "Igla"])
        self.assertNotIn("BrokenHighway", body)
        self.assertNotIn("SequencesDiffer", body)
        self.assertNotIn("Beats", fields)
        self.assertNotIn(BEATS_NOT_LOCKED, LOCKED_FIELDS)

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
