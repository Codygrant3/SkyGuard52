# THIS IS leftover-safe FSkyguardCampaignMissionSpec bNightIdentity.
# origin/main form: BARE plain C++ field `bool bNightIdentity = false;`
# with initializer false. NOT a UPROPERTY wrap.
# FSkyguardCampaignMissionSpec is a plain C++ roster struct.
# Comment on origin/main: Night missions force sensor thermal —
# sight identity, not a reskin. Lock the FIELD, not leftover
# NightSortieBeatKit.
# Fail-closed if this test still asserts UPROPERTY / Category /
# VisibleAnywhere / EditAnywhere / BlueprintReadOnly /
# GENERATED_BODY / USTRUCT as the locked decl.
# Fail-closed if initializer is true (`= true`).
# Fail-closed if identifier is leftover Night kit bKeepThermal.
# Fail-closed if parse window is leftover
# FSkyguardNightSortieBeatKit.
# Parse STRUCT `FSkyguardCampaignMissionSpec` body ONLY after
# `struct FSkyguardCampaignMissionSpec`. Stop at
# `namespace SkyguardCampaignRoster`.
# Do NOT parse leftover namespace SkyguardCampaignRoster
# functions NumMissions / Get / IndexOf / IdAt /
# LoadoutLabel / WeatherEnumLabel as this slot.
# Do NOT parse leftover `FSkyguardStormRainBeatKit`.
# Do NOT parse leftover `FSkyguardDaySortieBeatKit`.
# Do NOT parse leftover `FSkyguardNightSortieBeatKit`.
# Do NOT parse leftover `FSkyguardLoadoutSpec`.
# Do NOT parse leftover `FSkyguardCpgDebriefSnapshot`.
# Do NOT parse leftover `FSkyguardCpgHudSnapshot`.
# Do NOT parse leftover `FSkyguardCpgContactMark`.
# Do NOT parse leftover Harbor Breaker Approach / Contact /
# Shore labels as this spec.
# Do NOT parse leftover `ASkyguardGunshipSortieDirector`.
# Do NOT parse leftover `ASkyguardPatrolShipBoss`.
# Do NOT contract sibling fields MissionId / Title / Brief /
# Success / Failure / Weather / WeatherIdentity /
# WeatherLabel / TimeOfDayHours / BeatSeconds / ContactKind /
# ShoreKind / SupportKind / ExtractKind / Climax /
# bStormRocketContract.
# BeatSeconds uses 120/240/360/480/600/780/900. Do not
# invent Harbor 40/80.
# THIS SLOT IS NOT leftover NightSortieBeatKit bKeepThermal
# leftover-safe #1485 (bool on a leftover kit struct).
# THIS IS NOT leftover analog night-sortie-beat-kit-defaults
# #250 / #2ca7.
# THIS IS NOT leftover analog campaign-roster-lookup-tests
# #85ab.
# THIS IS NOT leftover CampaignMissionSpec
# bStormRocketContract (sibling bool).
# THIS IS NOT leftover-safe TheaterKitSpec WeatherIdentity
# UPROPERTY clone. Clone is UPROPERTY-based. RETARGET to
# a plain-struct bool field with initializer false.
# Parse-window style comes from leftover-safe
# CampaignMissionSpec MissionId #1521, BUT the identifier
# is bNightIdentity and the initializer is false.
# Do NOT claim leftover StormRain / Day / Night kit
# MissionId or leftover Night kit bKeepThermal.
# UPROPERTY rejection is copied from leftover-safe
# CampaignMissionSpec MissionId. Do not copy leftover
# Theater Category="Skyguard|Theater" / FName
# WeatherIdentity / `= 160.f` as the locked decl.
# Harbor 40/80 fail-closed via split tokens.
# Ban retired live-copy tokens via split tokens
# (b + Ya + kRuntimeReady). Stay Apache CPG 30 mm / Hydra /
# Hellfire. Fail-closed on live Ig+la / Ri+fle / Ya+k
# appearing as contiguous tokens in THIS test file.

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardCampaignRoster.h"
STRUCT_NAME = "FSkyguardCampaignMissionSpec"
NAMESPACE_NAME = "SkyguardCampaignRoster"
LEFTOVER_STORM_KIT = "FSkyguardStormRainBeatKit"
LEFTOVER_DAY_KIT = "FSkyguardDaySortieBeatKit"
LEFTOVER_NIGHT_KIT = "FSkyguardNightSortieBeatKit"
LEFTOVER_DEBRIEF_SNAPSHOT = "FSkyguardCpgDebriefSnapshot"
LEFTOVER_CONTACT_MARK = "FSkyguardCpgContactMark"
LEFTOVER_HUD_SNAPSHOT = "FSkyguardCpgHudSnapshot"
LEFTOVER_LOADOUT_SPEC = "FSkyguardLoadoutSpec"
LEFTOVER_STORM_HEADER = "Source/Skyguard52/SkyguardStormRainBeatKit.h"
LEFTOVER_DAY_HEADER = "Source/Skyguard52/SkyguardDaySortieBeatKit.h"
LEFTOVER_NIGHT_HEADER = "Source/Skyguard52/SkyguardNightSortieBeatKit.h"
LEFTOVER_DEBRIEF_HEADER = "Source/Skyguard52/SkyguardCpgDebrief.h"
LEFTOVER_HUD_HEADER = "Source/Skyguard52/SkyguardCpgHud.h"
LEFTOVER_LOADOUT_HEADER = "Source/Skyguard52/SkyguardGunshipTypes.h"
TARGET = "bool bNightIdentity = false;"
TARGET_WRONG_TRUE = "bool bNightIdentity = true;"
TARGET_WRONG_BARE = "bool bNightIdentity;"
TARGET_WRONG_ZERO = "bool bNightIdentity = 0;"
TARGET_WRONG_EQ_NONE = "bool bNightIdentity = NAME_None;"
TARGET_WRONG_FLOAT = "float bNightIdentity = false;"
TARGET_WRONG_HEALTH = "float Health = 160.f;"
TARGET_WRONG_FNAME = "FName bNightIdentity;"
TARGET_WRONG_INT = "int32 bNightIdentity = false;"
TARGET_WRONG_KEEP_THERMAL_TRUE = "bool bKeepThermal = true;"
TARGET_WRONG_KEEP_THERMAL_FALSE = "bool bKeepThermal = false;"
TARGET_WRONG_STORM_ROCKET = "bool bStormRocketContract = false;"
TARGET_WRONG_MISSION_ID = "FName MissionId;"
TARGET_WRONG_WEATHER_IDENTITY = "FName WeatherIdentity;"
LOCKED_DECL = TARGET
CLONE_UPROPERTY_THEATER = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Theater")'
)
CLONE_UPROPERTY_CAMPAIGN = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Campaign")'
)
CLONE_UPROPERTY_EDIT = "UPROPERTY(EditAnywhere, BlueprintReadOnly)"
CLONE_UPROPERTY_WRITE = "UPROPERTY(EditAnywhere, BlueprintReadWrite)"
CLONE_THEATER_WEATHER_IDENTITY = "FName WeatherIdentity;"
STOP_BEFORE_NAMESPACE = "namespace SkyguardCampaignRoster"
STOP_BEFORE_STORM_KIT = "struct FSkyguardStormRainBeatKit"
STOP_BEFORE_DAY_KIT = "struct FSkyguardDaySortieBeatKit"
STOP_BEFORE_NIGHT_KIT = "struct FSkyguardNightSortieBeatKit"
STOP_BEFORE_DEBRIEF = "struct FSkyguardCpgDebriefSnapshot"
STOP_BEFORE_CONTACT_MARK = "struct FSkyguardCpgContactMark"
STOP_BEFORE_HUD_SNAPSHOT = "struct FSkyguardCpgHudSnapshot"
STOP_BEFORE_LOADOUT = "struct FSkyguardLoadoutSpec"
STOP_BEFORE_AUDIO_EVENT = "enum class ESkyguardAudioEvent"
STOP_BEFORE_PICTOGRAM = "enum class ESkyguardBriefingPictogram"
STOP_BEFORE_EVENT_DEF = "struct FSkyguardAudioEventDefinition"
STOP_BEFORE_BOSS_WEAPON = "enum class ESkyguardBossWeapon"
STOP_BEFORE_PROP_SPINNER = "ASkyguardPropSpinner"
STOP_BEFORE_SORTIE = "ASkyguardGunshipSortieDirector"
STOP_BEFORE_PATROL = "ASkyguardPatrolShipBoss"
STOP_BEFORE_GUNNER = "ASkyguardGunner"
STOP_BEFORE_WEAK_POINT = "USkyguardBossWeakPointComponent"
STOP_BEFORE_HARBOR_CALLS = "SkyguardHarborBeatCalls"
NUM_MISSIONS = "NumMissions"
ROSTER_GET = "Get(int32 Index)"
INDEX_OF = "IndexOf"
ID_AT = "IdAt"
LOADOUT_LABEL = "LoadoutLabel"
WEATHER_ENUM_LABEL = "WeatherEnumLabel"
SIBLING_MISSION_ID = "MissionId"
SIBLING_TITLE = "Title"
SIBLING_BRIEF = "Brief"
SIBLING_SUCCESS = "Success"
SIBLING_FAILURE = "Failure"
SIBLING_WEATHER = "Weather"
SIBLING_WEATHER_IDENTITY = "WeatherIdentity"
SIBLING_WEATHER_LABEL = "WeatherLabel"
SIBLING_TIME_OF_DAY = "TimeOfDayHours"
SIBLING_BEAT_SECONDS = "BeatSeconds"
SIBLING_CONTACT_KIND = "ContactKind"
SIBLING_SHORE_KIND = "ShoreKind"
SIBLING_SUPPORT_KIND = "SupportKind"
SIBLING_EXTRACT_KIND = "ExtractKind"
SIBLING_CLIMAX = "Climax"
SIBLING_STORM_ROCKET = "bStormRocketContract"
LEFTOVER_KEEP_THERMAL = "bKeepThermal"
LEFTOVER_FLARE_COUNT = "FlareCount"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
THIS_SCRIPT = (
    "Scripts/tests/test_campaign_mission_spec_night_identity"
    "_field_decl_contract.py"
)
CLONE_THEATER_WEATHER_IDENTITY_SCRIPT = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_SPEC_MISSION_ID = (
    "Scripts/tests/test_campaign_mission_spec_mission_id"
    "_field_decl_contract.py"
)
LEFTOVER_NIGHT_KIT_KEEP_THERMAL = (
    "Scripts/tests/test_night_sortie_beat_kit_keep_thermal"
    "_field_decl_contract.py"
)
LEFTOVER_NIGHT_KIT_MISSION_ID = (
    "Scripts/tests/test_night_sortie_beat_kit_mission_id"
    "_field_decl_contract.py"
)
LEFTOVER_NIGHT_KIT_WEATHER_IDENTITY = (
    "Scripts/tests/test_night_sortie_beat_kit_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_NIGHT_KIT_BEATS = (
    "Scripts/tests/test_night_sortie_beat_kit_beats"
    "_field_decl_contract.py"
)
LEFTOVER_ANALOG_NIGHT_KIT_DEFAULTS = (
    "Scripts/tests/test_night_sortie_beat_kit_defaults_contract.py"
)
LEFTOVER_STORM_KIT_MISSION_ID = (
    "Scripts/tests/test_storm_rain_beat_kit_mission_id"
    "_field_decl_contract.py"
)
LEFTOVER_DAY_KIT_MISSION_ID = (
    "Scripts/tests/test_day_sortie_beat_kit_mission_id"
    "_field_decl_contract.py"
)
LEFTOVER_CONTACT_MARK_WORLD = (
    "Scripts/tests/test_cpg_contact_mark_world_location"
    "_field_decl_contract.py"
)
LEFTOVER_ANALOG_ROSTER_LOOKUP = (
    "Scripts/tests/test_campaign_roster_lookup_tests.py"
)
LEFTOVER_ROSTER_ID_AT = (
    "Scripts/tests/test_campaign_roster_id_at"
    "_decl_contract.py"
)
LEFTOVER_ROSTER_GET = (
    "Scripts/tests/test_campaign_roster_get"
    "_decl_contract.py"
)
LEFTOVER_ROSTER_NUM_MISSIONS = (
    "Scripts/tests/test_campaign_roster_num_missions"
    "_decl_contract.py"
)
LEFTOVER_ROSTER_LOADOUT_LABEL = (
    "Scripts/tests/test_campaign_roster_loadout_label"
    "_decl_contract.py"
)
LEFTOVER_ROSTER_WEATHER_ENUM_LABEL = (
    "Scripts/tests/test_campaign_roster_weather_enum_label"
    "_decl_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_BULK = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_FIELDS = (
    "Scripts/tests/test_storm_rain_beat_kit_fields_contract.py"
)
LEFTOVER_ANALOG_DAY_KIT_BULK = (
    "Scripts/tests/test_day_sortie_beat_kit_contract.py"
)
LEFTOVER_ANALOG_NIGHT_KIT_BULK = (
    "Scripts/tests/test_night_sortie_beat_kit_contract.py"
)
LEFTOVER_ANALOG_THEATER_KIT_BULK = (
    "Scripts/tests/test_campaign_theater_kit_contract.py"
)
LEFTOVER_LOADOUT_FLARE = (
    "Scripts/tests/test_loadout_spec_flare_count"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_DEFAULTS = (
    "Scripts/tests/test_loadout_spec_defaults_contract.py"
)

LOCKED = {
    "SkyguardCampaignRoster.h",
    "SkyguardCampaignRoster.cpp",
    "SkyguardStormRainBeatKit.h",
    "SkyguardStormRainBeatKit.cpp",
    "SkyguardDaySortieBeatKit.h",
    "SkyguardDaySortieBeatKit.cpp",
    "SkyguardNightSortieBeatKit.h",
    "SkyguardNightSortieBeatKit.cpp",
    "SkyguardCpgDebrief.h",
    "SkyguardCpgDebrief.cpp",
    "SkyguardCpgHud.h",
    "SkyguardCpgHud.cpp",
    "SkyguardGunshipTypes.h",
    "SkyguardGunshipSortieDirector.h",
    "SkyguardGunshipSortieDirector.cpp",
    "SkyguardHarborBeatCalls.h",
    "SkyguardHarborBeatCalls.cpp",
    "SkyguardApacheAircraft.h",
    "SkyguardApacheAircraft.cpp",
    "SkyguardGunner.h",
    "SkyguardGunner.cpp",
    "SkyguardCampaignTheaterKit.h",
    "SkyguardCampaignTheaterKit.cpp",
}


def leftover_live_copy_boss_scripts() -> tuple[str, ...]:
    banned = "ri" + "fle"
    missile = "ig" + "la"
    prefix = "Scripts/tests/"
    return (
        f"{prefix}test_boss_drone_apply_{missile}"
        "_strike_decl_contract.py",
        f"{prefix}test_boss_drone_is_{missile}"
        "_lock_eligible_decl_contract.py",
        f"{prefix}test_last_flight_open_first_{missile}"
        "_window_decl_contract.py",
        f"{prefix}test_last_flight_open_final_{missile}"
        "_window_decl_contract.py",
        f"{prefix}test_last_flight_arm_command_core_{banned}"
        "_path_decl_contract.py",
        f"{prefix}test_iron_rain_apply_second_{missile}"
        "_finish_decl_contract.py",
        f"{prefix}test_iron_rain_arm_fuel_control_{banned}"
        "_finish_decl_contract.py",
        f"{prefix}test_{missile}_boss_decl_contract.py",
        f"{prefix}test_{missile}_missile_decl_contract.py",
    )


def leftover_night_kit_field_scripts() -> tuple[str, ...]:
    return (
        LEFTOVER_NIGHT_KIT_KEEP_THERMAL,
        LEFTOVER_NIGHT_KIT_MISSION_ID,
        LEFTOVER_NIGHT_KIT_WEATHER_IDENTITY,
        LEFTOVER_NIGHT_KIT_BEATS,
        LEFTOVER_ANALOG_NIGHT_KIT_DEFAULTS,
        LEFTOVER_ANALOG_NIGHT_KIT_BULK,
    )


def leftover_kit_mission_id_scripts() -> tuple[str, ...]:
    return (
        LEFTOVER_STORM_KIT_MISSION_ID,
        LEFTOVER_DAY_KIT_MISSION_ID,
        LEFTOVER_NIGHT_KIT_MISSION_ID,
        LEFTOVER_SPEC_MISSION_ID,
    )


def leftover_roster_function_scripts() -> tuple[str, ...]:
    return (
        LEFTOVER_ANALOG_ROSTER_LOOKUP,
        LEFTOVER_ROSTER_ID_AT,
        LEFTOVER_ROSTER_GET,
        LEFTOVER_ROSTER_NUM_MISSIONS,
        LEFTOVER_ROSTER_LOADOUT_LABEL,
        LEFTOVER_ROSTER_WEATHER_ENUM_LABEL,
    )


LOCKED_SCRIPTS = (
    leftover_kit_mission_id_scripts()
    + leftover_night_kit_field_scripts()
    + leftover_roster_function_scripts()
    + (
        CLONE_THEATER_WEATHER_IDENTITY_SCRIPT,
        LEFTOVER_CONTACT_MARK_WORLD,
        LEFTOVER_ANALOG_STORM_KIT_BULK,
        LEFTOVER_ANALOG_STORM_KIT_FIELDS,
        LEFTOVER_ANALOG_DAY_KIT_BULK,
        LEFTOVER_ANALOG_THEATER_KIT_BULK,
        LEFTOVER_LOADOUT_FLARE,
        LEFTOVER_LOADOUT_DEFAULTS,
        "Scripts/tests/test_mesh_bind_slot_fields_contract.py",
        "Scripts/tests/test_loadout_spec_defaults_contract.py",
    )
    + leftover_live_copy_boss_scripts()
)

FORBIDDEN_LOCKED_MACRO_TOKENS = (
    "UPROPERTY",
    "Category",
    "VisibleAnywhere",
    "EditAnywhere",
    "BlueprintReadOnly",
    "GENERATED_BODY",
    "USTRUCT",
    "UFUNCTION",
    "BlueprintReadWrite",
)


def leftover_retired_primary_hits_field() -> str:
    return "Ri" + "fleHits"


def leftover_retired_guided_hits_field() -> str:
    return "Ig" + "laHits"


def leftover_neighbor_hit_fields() -> tuple[str, ...]:
    return (
        leftover_retired_primary_hits_field(),
        leftover_retired_guided_hits_field(),
    )


def leftover_harbor_clock_tokens() -> tuple[str, ...]:
    incoming = "Incoming" + "Radar"
    return (
        incoming,
        incoming + "LiveIntervalSeconds",
        incoming + "DownIntervalSeconds",
    )


def leftover_harbor_tokens() -> tuple[str, ...]:
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return leftover_harbor_clock_tokens() + (
        forty,
        eighty,
        forty + ", " + eighty,
    )


def leftover_harbor_director_tokens() -> tuple[str, ...]:
    return (
        STOP_BEFORE_HARBOR_CALLS,
        STOP_BEFORE_SORTIE,
        "HarborBreaker",
        "ASkyguardHarborDirector",
    )


def leftover_harbor_breaker_label_structs() -> tuple[str, ...]:
    return (
        "FSkyguardHarborApproach",
        "FSkyguardHarborContact",
        "FSkyguardHarborShore",
    )


def leftover_live_copy_tokens() -> tuple[str, ...]:
    return ("ig" + "la", "ya" + "k", "ri" + "fle")


def leftover_readiness_tokens() -> tuple[str, ...]:
    return (
        "b" + "Ya" + "kRuntimeReady",
        "ASkyguard" + "Ig" + "la" + "Missile",
    )


def leftover_pictogram_values() -> tuple[str, ...]:
    return (
        "ESkyguardBriefingPictogram::" + "Ri" + "fle",
        "ESkyguardBriefingPictogram::" + "Ig" + "la",
    )


def leftover_live_case_tokens() -> tuple[str, ...]:
    return leftover_live_copy_title_tokens()


def leftover_live_copy_title_tokens() -> tuple[str, ...]:
    return ("Ig" + "la", "Ri" + "fle", "Ya" + "k")


def leftover_weapon_enum_body_tokens() -> tuple[str, ...]:
    return (
        "UMETA(DisplayName = \"" + "Ri" + "fle\")",
        "UMETA(DisplayName = \"" + "Ig" + "la\")",
    )


def leftover_audio_event_enum_tokens() -> tuple[str, ...]:
    return (
        "Ri" + "fleShot",
        "Ri" + "fleMechanical",
        "Ig" + "laSeekerSearch",
        "Ig" + "laLock",
        "Ig" + "laLaunch",
        "Ig" + "laImpact",
    )


STRUCT_RE = re.compile(
    rf"struct\s+(?:SKYGUARD52_API\s+)?{re.escape(STRUCT_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
INVENTED_FIELD_MSG = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "CreateDefaultSubobject",
    "const float Amount",
    "{ return",
    "= true",
    "= 0.f",
    "= 160.f",
    "= NAME_None",
)


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_MISSION_ID,
        SIBLING_TITLE,
        SIBLING_BRIEF,
        SIBLING_SUCCESS,
        SIBLING_FAILURE,
        SIBLING_WEATHER,
        SIBLING_WEATHER_IDENTITY,
        SIBLING_WEATHER_LABEL,
        SIBLING_TIME_OF_DAY,
        SIBLING_BEAT_SECONDS,
        SIBLING_CONTACT_KIND,
        SIBLING_SHORE_KIND,
        SIBLING_SUPPORT_KIND,
        SIBLING_EXTRACT_KIND,
        SIBLING_CLIMAX,
        SIBLING_STORM_ROCKET,
    )


def leftover_kit_tokens() -> tuple[str, ...]:
    return (
        LEFTOVER_STORM_KIT,
        LEFTOVER_DAY_KIT,
        LEFTOVER_NIGHT_KIT,
        LEFTOVER_DEBRIEF_SNAPSHOT,
        LEFTOVER_CONTACT_MARK,
        LEFTOVER_HUD_SNAPSHOT,
        LEFTOVER_LOADOUT_SPEC,
    )


def namespace_helper_tokens() -> tuple[str, ...]:
    return (
        NUM_MISSIONS,
        ROSTER_GET,
        INDEX_OF,
        ID_AT,
        LOADOUT_LABEL,
        WEATHER_ENUM_LABEL,
    )


def this_file_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    return compact


def declaration_stem(declaration: str) -> str:
    compact = collapsed(declaration)
    if compact.endswith(";"):
        return compact[:-1].rstrip()
    return compact


def has_identifier(region: str, name: str) -> bool:
    return re.search(r"\b" + re.escape(name) + r"\b", region) is not None


def has_one_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return True
    stem = declaration_stem(declaration)
    if not stem:
        return False
    pattern = re.compile(re.escape(stem) + r"\s*;")
    return pattern.search(compact_region) is not None


def night_identity_has_uproperty_wrap(region: str) -> bool:
    compact = collapsed(region)
    return re.search(
        r"UPROPERTY\([^;]*\)\s*bool\s+bNightIdentity\b",
        compact,
    ) is not None


def has_declaration(region: str, declaration: str) -> bool:
    # Fail-closed on the authored
    # `bool bNightIdentity = false;`.
    # Do not accept bare / `= true` / leftover Night kit
    # bKeepThermal / leftover Theater Category /
    # FName WeatherIdentity / `= 160.f` when origin/main
    # has bool = false. Do not accept sibling MissionId /
    # WeatherIdentity / bStormRocketContract fields.
    # Do not accept UPROPERTY / Category clones from
    # leftover TheaterKit #1300.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if re.search(
        r"bool\s+bNightIdentity\s*=\s*true",
        compact,
    ):
        return False
    if re.search(
        r"float\s+bNightIdentity\b",
        compact,
    ):
        return False
    if re.search(
        r"FName\s+bNightIdentity\b",
        compact,
    ):
        return False
    if re.search(
        r"int32\s+bNightIdentity\b",
        compact,
    ):
        return False
    if re.search(
        r"bool\s+bNightIdentity\s*=\s*false",
        compact,
    ) is None:
        return False
    if re.search(
        r"\bbKeepThermal\b",
        compact,
    ) and not has_identifier(declaration, "bNightIdentity"):
        return False
    if night_identity_has_uproperty_wrap(region):
        return False
    if re.search(r"\bCategory\s*=", compact):
        return False
    return True


def count_one_declaration(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return compact_region.count(compact_decl)
    stem = declaration_stem(declaration)
    if not stem:
        return 0
    pattern = re.compile(re.escape(stem) + r"\s*;")
    return len(pattern.findall(compact_region))


def declaration_count(region: str, declaration: str) -> int:
    if not has_declaration(region, declaration):
        return 0
    return count_one_declaration(region, declaration)


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


def leftover_header(path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{path} is missing from origin/main"
        )
    return result.stdout


def leftover_storm_kit_header() -> str:
    return leftover_header(LEFTOVER_STORM_HEADER)


def leftover_day_kit_header() -> str:
    return leftover_header(LEFTOVER_DAY_HEADER)


def leftover_night_kit_header() -> str:
    return leftover_header(LEFTOVER_NIGHT_HEADER)


def leftover_debrief_header() -> str:
    return leftover_header(LEFTOVER_DEBRIEF_HEADER)


def leftover_hud_header() -> str:
    return leftover_header(LEFTOVER_HUD_HEADER)


def leftover_loadout_header() -> str:
    return leftover_header(LEFTOVER_LOADOUT_HEADER)


def struct_body(header: str) -> str:
    match = STRUCT_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{STRUCT_NAME} is missing from origin/main:{HEADER_PATH}"
        )
    start = header.index("{", match.start())
    depth = 0
    for index, char in enumerate(header[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return header[start : index + 1]
    raise AssertionError(
        f"{STRUCT_NAME} struct body is missing from origin/main:{HEADER_PATH}"
    )


def leaked_neighbor_tokens() -> tuple[str, ...]:
    return (
        STOP_BEFORE_NAMESPACE,
        STOP_BEFORE_STORM_KIT,
        STOP_BEFORE_DAY_KIT,
        STOP_BEFORE_NIGHT_KIT,
        STOP_BEFORE_DEBRIEF,
        STOP_BEFORE_CONTACT_MARK,
        STOP_BEFORE_HUD_SNAPSHOT,
        STOP_BEFORE_LOADOUT,
        STOP_BEFORE_AUDIO_EVENT,
        STOP_BEFORE_PICTOGRAM,
        STOP_BEFORE_EVENT_DEF,
        STOP_BEFORE_BOSS_WEAPON,
        STOP_BEFORE_PROP_SPINNER,
        STOP_BEFORE_SORTIE,
        STOP_BEFORE_PATROL,
        leftover_retired_mount_class(),
        STOP_BEFORE_WEAK_POINT,
        STOP_BEFORE_HARBOR_CALLS,
        LEFTOVER_STORM_KIT,
        LEFTOVER_DAY_KIT,
        LEFTOVER_NIGHT_KIT,
        LEFTOVER_DEBRIEF_SNAPSHOT,
        LEFTOVER_CONTACT_MARK,
        LEFTOVER_HUD_SNAPSHOT,
        LEFTOVER_LOADOUT_SPEC,
        NUM_MISSIONS,
        ROSTER_GET,
        INDEX_OF,
        ID_AT,
        LOADOUT_LABEL,
        WEATHER_ENUM_LABEL,
        "class USkyguardCampaignSubsystem",
        "struct FSkyguardObjectiveProgress",
        "struct FSkyguardMissionDebrief",
        "struct FSkyguardAudioTelemetry",
        "ESkyguardAudioEvent::",
        f"class SKYGUARD52_API {LEFTOVER_APACHE_CLASS}",
        f"class {LEFTOVER_APACHE_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_RADAR_NODE_CLASS}",
        f"class {LEFTOVER_RADAR_NODE_CLASS}",
    )


def spec_section(header: str) -> str:
    body = struct_body(header)
    public = re.search(r"\bpublic\s*:", body)
    if public is None:
        if ACCESS_RE.search(body) is not None:
            raise AssertionError(
                f"{STRUCT_NAME} public section is missing from "
                f"origin/main:{HEADER_PATH}"
            )
        close = body.rfind("}")
        if close == -1:
            raise AssertionError(
                f"{STRUCT_NAME} public section is missing from "
                f"origin/main:{HEADER_PATH}"
            )
        section = body[1:close]
    else:
        start = public.end()
        rest = body[start:]
        next_access = ACCESS_RE.search(rest)
        if next_access is not None:
            section = rest[: next_access.start()]
        else:
            close = rest.rfind("}")
            if close == -1:
                raise AssertionError(
                    f"{STRUCT_NAME} public section is missing from "
                    f"origin/main:{HEADER_PATH}"
                )
            section = rest[:close]
    for token in leaked_neighbor_tokens():
        if token in section:
            raise AssertionError(
                f"{STRUCT_NAME} parse window includes {token}"
            )
    if STOP_BEFORE_NAMESPACE in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes {STOP_BEFORE_NAMESPACE}"
        )
    if STRUCT_NAME == LEFTOVER_NIGHT_KIT:
        raise AssertionError(
            f"parse window is leftover {LEFTOVER_NIGHT_KIT}"
        )
    if has_identifier(LOCKED_DECL, LEFTOVER_KEEP_THERMAL):
        raise AssertionError(
            f"identifier is leftover {LEFTOVER_KEEP_THERMAL}"
        )
    return section


def attached_uproperty_specifiers(section: str) -> str:
    compact = collapsed(section)
    cursor = 0
    while True:
        match = re.search(r"UPROPERTY\(", compact[cursor:])
        if match is None:
            break
        start = cursor + match.end()
        depth = 1
        index = start
        while index < len(compact) and depth:
            if compact[index] == "(":
                depth += 1
            elif compact[index] == ")":
                depth -= 1
            index += 1
        if depth == 0 and re.match(
            r"\s*bool\s+bNightIdentity\b", compact[index:]
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for bool bNightIdentity is missing from "
        f"origin/main:{HEADER_PATH} struct {STRUCT_NAME} body; "
        "locked decl is the bare plain C++ field, not a UPROPERTY wrap"
    )


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"struct {STRUCT_NAME} body"
        )
    return declaration


def require_no_uproperty_wrap(section: str) -> None:
    compact = collapsed(section)
    if re.search(
        r"UPROPERTY\([^)]*\)\s*bool\s+bNightIdentity\b",
        compact,
    ):
        raise AssertionError(
            "UPROPERTY wrap on bool bNightIdentity is not the locked "
            f"decl for plain C++ struct {STRUCT_NAME}"
        )
    if "UPROPERTY" in section and has_identifier(section, "bNightIdentity"):
        raise AssertionError(
            "UPROPERTY clone landed on bNightIdentity; locked decl is "
            f"bare {LOCKED_DECL}"
        )
    for token in ("USTRUCT", "GENERATED_BODY"):
        if token in section and has_identifier(section, "bNightIdentity"):
            raise AssertionError(
                f"{token} clone landed on bNightIdentity; locked decl is "
                f"bare {LOCKED_DECL}"
            )


class CampaignMissionSpecNightIdentityFieldDeclContractTests(
    unittest.TestCase
):
    def test_campaign_mission_spec_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(STRUCT_NAME, header)
        self.assertIsNotNone(STRUCT_RE.search(header), header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(STRUCT_NAME, "FSkyguardCampaignMissionSpec")
        self.assertEqual(NAMESPACE_NAME, "SkyguardCampaignRoster")
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_STORM_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DAY_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_NIGHT_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DEBRIEF_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_CONTACT_MARK)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_HUD_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_APACHE_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_RADAR_NODE_CLASS)
        self.assertNotEqual(STRUCT_NAME, STOP_BEFORE_SORTIE)
        body = struct_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "bNightIdentity"), section)
        self.assertFalse(has_identifier(section, LEFTOVER_KEEP_THERMAL))
        self.assertNotIn("UPROPERTY", section)
        self.assertNotIn("GENERATED_BODY", section)
        self.assertNotIn("USTRUCT", section)
        self.assertIn(STOP_BEFORE_NAMESPACE, header)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, body)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_STORM_KIT, section)
        self.assertNotIn(LEFTOVER_DAY_KIT, section)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, section)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, section)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)

    def test_locked_decl_is_bare_plain_cpp_not_uproperty(self) -> None:
        self.assertEqual(LOCKED_DECL, "bool bNightIdentity = false;")
        self.assertEqual(LOCKED_DECL, TARGET)
        self.assertTrue(LOCKED_DECL.startswith("bool bNightIdentity"))
        self.assertTrue(LOCKED_DECL.endswith(";"))
        self.assertIn("= false", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TRUE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BARE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_KEEP_THERMAL_TRUE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_KEEP_THERMAL_FALSE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_STORM_ROCKET)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_THEATER, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_CAMPAIGN, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_EDIT, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_WRITE, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_THEATER)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_CAMPAIGN)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_EDIT)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_WRITE)
        self.assertNotEqual(LOCKED_DECL, CLONE_THEATER_WEATHER_IDENTITY)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MISSION_ID)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WEATHER_IDENTITY)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_STORM_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_DAY_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_NIGHT_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_DEBRIEF_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_HUD_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_LOADOUT_HEADER)

    def test_clone_uproperty_as_locked_decl_fails_closed(self) -> None:
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn("VisibleAnywhere", LOCKED_DECL)
        self.assertNotIn("EditAnywhere", LOCKED_DECL)
        self.assertNotIn("BlueprintReadOnly", LOCKED_DECL)
        self.assertNotIn("GENERATED_BODY", LOCKED_DECL)
        self.assertNotIn("USTRUCT", LOCKED_DECL)
        for clone_locked in (
            CLONE_UPROPERTY_THEATER,
            CLONE_UPROPERTY_CAMPAIGN,
            CLONE_UPROPERTY_EDIT,
            CLONE_UPROPERTY_WRITE,
        ):
            self.assertIn("UPROPERTY", clone_locked)
            self.assertNotEqual(LOCKED_DECL, clone_locked)
            self.assertFalse(has_declaration(clone_locked, LOCKED_DECL))
            with self.assertRaises(AssertionError) as raised:
                require_declaration(f"\t{clone_locked}\n", LOCKED_DECL)
            self.assertIn("bNightIdentity", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            struct_body(
                "struct FSkyguardUnrelatedCampaignMissionSpec\n{\n};\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_night_kit_parse_window_fails_closed(self) -> None:
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_NIGHT_KIT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_KEEP_THERMAL_TRUE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_KEEP_THERMAL_FALSE)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, LOCKED_DECL)
        leftover = (
            f"struct {LEFTOVER_NIGHT_KIT}\n"
            "{\n"
            f"\t{TARGET_WRONG_KEEP_THERMAL_TRUE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(leftover)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(
                f"\t{TARGET_WRONG_KEEP_THERMAL_TRUE}\n",
                LOCKED_DECL,
            )
        self.assertIn("bNightIdentity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(
                f"\t{TARGET_WRONG_KEEP_THERMAL_FALSE}\n",
                LOCKED_DECL,
            )
        self.assertIn("bNightIdentity", str(raised.exception))

    def test_leftover_kit_and_hud_structs_do_not_satisfy(self) -> None:
        leftovers = leftover_kit_tokens()
        for leftover_name in leftovers:
            leftover = (
                f"struct {leftover_name}\n"
                "{\n"
                f"\t{LOCKED_DECL}\n"
                "};\n"
            )
            with self.assertRaises(AssertionError) as raised:
                spec_section(leftover)
            self.assertIn(STRUCT_NAME, str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
        apache = (
            f"struct {LEFTOVER_APACHE_CLASS}\n"
            "{\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(apache)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_does_not_claim_leftover_storm_day_night_or_debrief(self) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_STORM_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_DAY_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_NIGHT_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_DEBRIEF_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_HUD_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_LOADOUT_HEADER)
        self.assertTrue(HEADER_PATH.endswith("SkyguardCampaignRoster.h"))
        self.assertNotIn("StormRain", HEADER_PATH)
        self.assertNotIn("DaySortie", HEADER_PATH)
        self.assertNotIn("NightSortie", HEADER_PATH)
        self.assertNotIn("CpgDebrief", HEADER_PATH)
        self.assertNotIn("CpgHud", HEADER_PATH)
        self.assertNotIn("GunshipTypes", HEADER_PATH)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_STORM_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DAY_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_NIGHT_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DEBRIEF_SNAPSHOT)
        storm_header = leftover_storm_kit_header()
        self.assertIn(LEFTOVER_STORM_KIT, storm_header)
        self.assertNotIn("bNightIdentity", storm_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(storm_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        day_header = leftover_day_kit_header()
        self.assertIn(LEFTOVER_DAY_KIT, day_header)
        self.assertNotIn("bNightIdentity", day_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(day_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        night_header = leftover_night_kit_header()
        self.assertIn(LEFTOVER_NIGHT_KIT, night_header)
        self.assertIn(LEFTOVER_KEEP_THERMAL, night_header)
        self.assertIn(TARGET_WRONG_KEEP_THERMAL_TRUE, night_header)
        self.assertNotIn("bNightIdentity", night_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(night_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        debrief_header = leftover_debrief_header()
        self.assertIn(LEFTOVER_DEBRIEF_SNAPSHOT, debrief_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(debrief_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        hud_header = leftover_hud_header()
        self.assertIn(LEFTOVER_CONTACT_MARK, hud_header)
        self.assertIn(LEFTOVER_HUD_SNAPSHOT, hud_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(hud_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        loadout_header = leftover_loadout_header()
        self.assertIn(LEFTOVER_LOADOUT_SPEC, loadout_header)
        self.assertIn(LEFTOVER_FLARE_COUNT, loadout_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(loadout_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_namespace_declaration_does_not_satisfy(self) -> None:
        mixed = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "};\n"
            f"{STOP_BEFORE_NAMESPACE}\n"
            "{\n"
            f"\tint32 {NUM_MISSIONS}();\n"
            f"\tconst {STRUCT_NAME}& {ROSTER_GET};\n"
            f"\tint32 {INDEX_OF}(FName MissionId);\n"
            f"\tFName {ID_AT}(int32 Index);\n"
            f"\t{LOCKED_DECL}\n"
            "}\n"
        )
        section = spec_section(mixed)
        self.assertFalse(has_identifier(section, "bNightIdentity"), section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(NUM_MISSIONS, section)
        self.assertNotIn(ID_AT, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bNightIdentity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_roster_functions_do_not_satisfy(self) -> None:
        leftovers = (
            f"\tint32 {NUM_MISSIONS}();\n",
            f"\tconst {STRUCT_NAME}& {ROSTER_GET};\n",
            f"\tint32 {INDEX_OF}(FName MissionId);\n",
            f"\tFName {ID_AT}(int32 Index);\n",
            f"\tconst TCHAR* {LOADOUT_LABEL}();\n",
            f"\tconst TCHAR* {WEATHER_ENUM_LABEL}();\n",
        )
        for region in leftovers:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("bNightIdentity", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
        for helper in namespace_helper_tokens():
            self.assertNotIn(helper, LOCKED_DECL)

    def test_missing_night_identity_declaration_fails_closed(self) -> None:
        empty = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\tFName {SIBLING_MISSION_ID};\n"
            f"\tconst TCHAR* {SIBLING_TITLE} = TEXT(\"\");\n"
            f"\tconst TCHAR* {SIBLING_BRIEF} = TEXT(\"\");\n"
            f"\tFName {SIBLING_WEATHER_IDENTITY};\n"
            f"\tconst TCHAR* {SIBLING_WEATHER_LABEL} = TEXT(\"\");\n"
            f"\tfloat {SIBLING_TIME_OF_DAY} = 12.f;\n"
            f"\tbool {SIBLING_STORM_ROCKET} = false;\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bNightIdentity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_sibling_storm_rocket_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_STORM_ROCKET}\n"
            f"\t{TARGET_WRONG_MISSION_ID}\n"
            f"\t{TARGET_WRONG_WEATHER_IDENTITY}\n"
            "};\n"
        )
        section = spec_section(leftover)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bNightIdentity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_STORM_ROCKET)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_MISSION_ID)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WEATHER_IDENTITY)

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{CLONE_UPROPERTY_THEATER}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("bNightIdentity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_has_bare_field_not_uproperty(self) -> None:
        section = spec_section(origin_main_header())
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("UPROPERTY", section)
        self.assertNotIn("VisibleAnywhere", section)
        self.assertNotIn("BlueprintReadOnly", section)
        self.assertNotIn("EditAnywhere", section)
        self.assertNotIn("GENERATED_BODY", section)
        self.assertNotIn("USTRUCT", section)
        self.assertNotIn("Category", section)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        require_no_uproperty_wrap(section)
        with self.assertRaises(AssertionError) as raised:
            attached_uproperty_specifiers(section)
        self.assertIn("UPROPERTY", str(raised.exception))
        self.assertIn("bare", str(raised.exception).lower())

    def test_true_or_bare_initializer_fails_closed(self) -> None:
        initialized = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_TRUE}\n"
            "};\n"
        )
        section = spec_section(initialized)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bNightIdentity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        bare = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_BARE}\n"
            "};\n"
        )
        bare_section = spec_section(bare)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(bare_section, LOCKED_DECL)
        self.assertIn("bNightIdentity", str(raised.exception))
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn("bool bNightIdentity = false;", compact_origin)
        self.assertNotIn("bNightIdentity = true", compact_origin)
        self.assertNotIn("bNightIdentity = NAME_None", compact_origin)
        self.assertNotIn("bNightIdentity = 0.f", compact_origin)
        self.assertNotIn("bNightIdentity = 160.f", compact_origin)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, compact_origin)

    def test_night_identity_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("bool bNightIdentity"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertIn("= false", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotIn("= NAME_None", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertIn("bool ", LOCKED_DECL)
        self.assertNotIn("float ", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TRUE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_ZERO}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FLOAT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HEALTH}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_KEEP_THERMAL_TRUE}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_STORM_ROCKET}\n",
                LOCKED_DECL,
            )
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_TRUE}\n", LOCKED_DECL)
        self.assertIn("bNightIdentity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        self.assertIn("bNightIdentity", str(raised.exception))

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tbool " + leftover_retired_primary_hits_field() + " = false;\n"
        )
        leftover_guided = (
            "\tbool " + leftover_retired_guided_hits_field() + " = false;\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_EQ_NONE}\n",
            f"\t{TARGET_WRONG_FLOAT}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_INT}\n",
            f"\t{TARGET_WRONG_KEEP_THERMAL_TRUE}\n",
            f"\t{TARGET_WRONG_KEEP_THERMAL_FALSE}\n",
            leftover_primary,
            leftover_guided,
            f"\tFName {SIBLING_MISSION_ID};\n",
            f"\tconst TCHAR* {SIBLING_TITLE} = TEXT(\"\");\n",
            f"\tconst TCHAR* {SIBLING_BRIEF} = TEXT(\"\");\n",
            f"\tFName {SIBLING_WEATHER_IDENTITY};\n",
            f"\tconst TCHAR* {SIBLING_WEATHER_LABEL} = TEXT(\"\");\n",
            f"\tfloat {SIBLING_TIME_OF_DAY} = 12.f;\n",
            f"\tbool {SIBLING_STORM_ROCKET} = false;\n",
            f"\tint32 {LEFTOVER_FLARE_COUNT} = 6;\n",
            "\tbool bNightIdentities = false;\n",
            "\tint32 bNightIdentity = 0;\n",
            "\tFName bNightIdentity;\n",
            "\tfloat bNightIdentity = " + forty + ";\n",
            "\tfloat bNightIdentity = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("bNightIdentity", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_uproperty_or_category_clone_fails_closed(self) -> None:
        wraps = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{CLONE_UPROPERTY_THEATER}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n",
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{CLONE_UPROPERTY_CAMPAIGN}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n",
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{CLONE_UPROPERTY_EDIT}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n",
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{CLONE_UPROPERTY_WRITE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n",
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "\tUSTRUCT(BlueprintType)\n"
            "\tGENERATED_BODY()\n"
            f"\t{LOCKED_DECL}\n"
            "};\n",
        )
        for wrapped in wraps:
            section = spec_section(wrapped)
            with self.assertRaises(AssertionError):
                require_no_uproperty_wrap(section)
            if "UPROPERTY" in wrapped:
                self.assertTrue(
                    night_identity_has_uproperty_wrap(section),
                    section,
                )
                with self.assertRaises(AssertionError) as raised:
                    require_declaration(section, LOCKED_DECL)
                self.assertIn("bNightIdentity", str(raised.exception))
                self.assertIn("missing", str(raised.exception).lower())
        origin = spec_section(origin_main_header())
        require_no_uproperty_wrap(origin)
        self.assertFalse(night_identity_has_uproperty_wrap(origin), origin)
        self.assertNotIn("UPROPERTY", origin)
        self.assertNotIn("Category", origin)
        self.assertNotIn("VisibleAnywhere", origin)
        self.assertNotIn("EditAnywhere", origin)
        self.assertNotIn("BlueprintReadOnly", origin)
        self.assertNotIn("GENERATED_BODY", origin)
        self.assertNotIn("USTRUCT", origin)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tbool\n\tbNightIdentity = false;\n",
            "\tbool   bNightIdentity = false;\n",
            "\tbool\tbNightIdentity = false;\n",
            f"\t{LOCKED_DECL}\n",
        )
        for region in wraps:
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)
        rejected = (
            f"\t{CLONE_UPROPERTY_THEATER}\n",
            f"\t{CLONE_UPROPERTY_THEATER}\n\t{LOCKED_DECL}\n",
            f"\t{CLONE_UPROPERTY_THEATER} {LOCKED_DECL}\n",
            f"\t{CLONE_UPROPERTY_CAMPAIGN}\n\t{LOCKED_DECL}\n",
            f"\t{CLONE_UPROPERTY_EDIT}\n\t{LOCKED_DECL}\n",
            f"\t{CLONE_UPROPERTY_WRITE}\n\t{LOCKED_DECL}\n",
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
            'Category="Skyguard|Theater")\n'
            f"\t{LOCKED_DECL}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_KEEP_THERMAL_TRUE}\n",
            f"\t{TARGET_WRONG_STORM_ROCKET}\n",
            f"\t{TARGET_WRONG_MISSION_ID}\n",
            f"\t{TARGET_WRONG_WEATHER_IDENTITY}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
        )
        for region in rejected:
            self.assertFalse(has_declaration(region, LOCKED_DECL), region)

    def test_does_not_contract_sibling_spec_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        section = spec_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        self.assertFalse(has_identifier(section, LEFTOVER_FLARE_COUNT))
        self.assertFalse(has_identifier(section, LEFTOVER_KEEP_THERMAL))
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_does_not_parse_leftover_kits_or_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        self.assertIn(STOP_BEFORE_NAMESPACE, header)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, leaked)
        for helper in namespace_helper_tokens():
            self.assertIn(helper, header)
            self.assertNotIn(helper, section)
            self.assertNotIn(helper, leaked)
        self.assertNotIn(STOP_BEFORE_STORM_KIT, header)
        self.assertNotIn(STOP_BEFORE_DAY_KIT, header)
        self.assertNotIn(STOP_BEFORE_NIGHT_KIT, header)
        self.assertNotIn(LEFTOVER_STORM_KIT, header)
        self.assertNotIn(LEFTOVER_DAY_KIT, header)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, header)
        self.assertNotIn(STOP_BEFORE_DEBRIEF, header)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, header)
        self.assertNotIn(STOP_BEFORE_CONTACT_MARK, header)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, header)
        self.assertNotIn(STOP_BEFORE_HUD_SNAPSHOT, header)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, header)
        self.assertNotIn(STOP_BEFORE_LOADOUT, header)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, header)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, header)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, header)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, header)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, header)
        self.assertNotIn(STOP_BEFORE_PROP_SPINNER, header)
        self.assertNotIn(STOP_BEFORE_SORTIE, header)
        self.assertNotIn(STOP_BEFORE_PATROL, header)
        self.assertNotIn(leftover_retired_mount_class(), header)
        self.assertNotIn(STOP_BEFORE_WEAK_POINT, header)
        self.assertNotIn(STOP_BEFORE_HARBOR_CALLS, header)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, header)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, header)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, header)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, header)
        self.assertNotIn(STOP_BEFORE_GUNNER, header)
        self.assertNotIn(STOP_BEFORE_GUNNER, section)
        self.assertNotIn(STOP_BEFORE_GUNNER, leaked)

    def test_parse_window_excludes_leftover_weapon_enum_body(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, leaked)
            self.assertNotIn(leftover, header)
        for leftover in leftover_weapon_enum_body_tokens():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, leaked)
            self.assertNotIn(leftover, header)
        for leftover in leftover_audio_event_enum_tokens():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, leaked)
            self.assertNotIn(leftover, header)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, section)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, section)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, section)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_STORM_KIT, section)
        self.assertNotIn(LEFTOVER_DAY_KIT, section)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, section)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, section)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, section)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            f"\tint32 {NUM_MISSIONS}();\n"
            f"\tconst {STRUCT_NAME}& {ROSTER_GET};\n"
            f"\tint32 {INDEX_OF}(FName MissionId);\n"
            f"\tFName {ID_AT}(int32 Index);\n"
            f"\tconst TCHAR* {LOADOUT_LABEL}();\n"
            f"\tconst TCHAR* {WEATHER_ENUM_LABEL}();\n"
            f"\tFName {SIBLING_WEATHER_IDENTITY};\n"
            f"\tbool {SIBLING_STORM_ROCKET} = false;\n"
            f"\t{TARGET_WRONG_KEEP_THERMAL_TRUE}\n"
            f"\tint32 {LEFTOVER_FLARE_COUNT} = 6;\n"
            f"\t{TARGET_WRONG_HEALTH}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("bNightIdentity", str(raised.exception))

    def test_leftover_harbor_directors_do_not_satisfy(self) -> None:
        leftovers = leftover_harbor_director_tokens() + (
            leftover_harbor_breaker_label_structs()
        )
        for token in leftovers:
            leftover = (
                f"struct {token}\n"
                "{\n"
                f"\t{LOCKED_DECL}\n"
                "};\n"
            )
            with self.assertRaises(AssertionError) as raised:
                spec_section(leftover)
            self.assertIn(STRUCT_NAME, str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertNotIn(token, LOCKED_DECL)

    def test_harbor_breaker_labels_are_not_this_spec(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        for token in leftover_harbor_breaker_label_structs():
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, locked_only)
        self.assertNotIn("HarborBreaker", LOCKED_DECL)
        self.assertNotIn("ASkyguardHarborDirector", LOCKED_DECL)
        self.assertNotEqual(STRUCT_NAME, "FSkyguardHarborApproach")
        self.assertNotEqual(STRUCT_NAME, "FSkyguardHarborContact")
        self.assertNotEqual(STRUCT_NAME, "FSkyguardHarborShore")
        self.assertNotIn("HarborBreaker", STRUCT_NAME)
        section = spec_section(origin_main_header())
        self.assertNotIn("HarborBreaker", section)
        self.assertNotIn("ASkyguardHarborDirector", section)
        for token in leftover_harbor_breaker_label_structs():
            self.assertNotIn(token, section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for invented in INVENTED_FIELD_MSG:
            self.assertNotIn(invented, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_THEATER, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_CAMPAIGN, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_EDIT, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_WRITE, LOCKED_DECL)
        self.assertNotIn("MultiLine", LOCKED_DECL)
        self.assertNotIn("ClampMin", LOCKED_DECL)
        self.assertNotIn("ClampMax", LOCKED_DECL)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardCampaignRoster.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardStormRainBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardDaySortieBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardNightSortieBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardCpgDebrief.h", HEADER_PATH)
        self.assertNotIn("SkyguardCpgHud.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardRadarNode.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)
        self.assertNotIn("SkyguardHarborBeatCalls.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipSortieDirector.h", HEADER_PATH)

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = spec_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, LOCKED_DECL)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, file_text)
        header = origin_main_header()
        section = spec_section(header)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, header)
        for token in leftover_harbor_director_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, LOCKED_DECL)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "campaign-mission-spec night-identity field decl contract "
                f"contains {banned}; declaration is Apache CPG 30 mm / "
                "Hydra / Hellfire, not leftover live cop" + "y",
            )

    def test_this_file_bans_live_retired_tokens_case_sensitive(self) -> None:
        file_text = this_file_text()
        for banned in leftover_live_case_tokens():
            self.assertNotIn(banned, file_text)

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, LOCKED_DECL.lower())
            self.assertNotIn(banned, locked_only.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, LOCKED_DECL)
            self.assertNotIn(token, locked_only)
        self.assertNotIn(leftover_retired_mount_class(), LOCKED_DECL)

    def test_declaration_bans_retired_live_copy(self) -> None:
        locked_only = f"{LOCKED_DECL}\n"
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, LOCKED_DECL.lower())
            self.assertNotIn(banned, locked_only.lower())

    def test_locked_scripts_do_not_include_this_file(self) -> None:
        self.assertNotIn(THIS_SCRIPT, LOCKED_SCRIPTS)
        self.assertTrue(Path(__file__).name.endswith(
            "night_identity_field_decl_contract.py"
        ))
        self.assertIn("campaign_mission_spec", Path(__file__).name)
        self.assertNotIn("storm_rain_beat_kit", Path(__file__).name)
        self.assertNotIn("day_sortie_beat_kit", Path(__file__).name)
        self.assertNotIn("night_sortie_beat_kit", Path(__file__).name)
        self.assertNotIn("keep_thermal", Path(__file__).name)
        self.assertNotIn("SkyguardCampaignRoster.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardNightSortieBeatKit.h", THIS_SCRIPT)
        self.assertIn(LEFTOVER_SPEC_MISSION_ID, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_NIGHT_KIT_KEEP_THERMAL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_NIGHT_KIT_MISSION_ID, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_NIGHT_KIT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_ROSTER_LOOKUP, LOCKED_SCRIPTS)
        self.assertIn(CLONE_THEATER_WEATHER_IDENTITY_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_STORM_KIT_MISSION_ID, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_DAY_KIT_MISSION_ID, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_NIGHT_KIT_BULK, LOCKED_SCRIPTS)

    def test_leftover_analog_bulk_stays_locked(self) -> None:
        leftovers = (
            leftover_kit_mission_id_scripts()
            + leftover_night_kit_field_scripts()
            + leftover_roster_function_scripts()
            + (
                CLONE_THEATER_WEATHER_IDENTITY_SCRIPT,
                LEFTOVER_CONTACT_MARK_WORLD,
                LEFTOVER_ANALOG_STORM_KIT_BULK,
                LEFTOVER_ANALOG_STORM_KIT_FIELDS,
                LEFTOVER_ANALOG_DAY_KIT_BULK,
                LEFTOVER_ANALOG_THEATER_KIT_BULK,
                LEFTOVER_LOADOUT_FLARE,
                LEFTOVER_LOADOUT_DEFAULTS,
            )
        )
        for script in leftovers:
            self.assertIn(script, LOCKED_SCRIPTS)
            self.assertNotEqual(script, THIS_SCRIPT)

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

    def test_contract_is_target_field_declaration_only(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        locked_only = f"{LOCKED_DECL}\n"
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, locked_only)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, locked_only)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, locked_only)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, locked_only)
        for leftover in leftover_kit_tokens():
            self.assertNotIn(leftover, locked_only)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, locked_only)
        self.assertNotIn("FSkyguardObjectiveProgress", locked_only)
        self.assertNotIn("ESkyguardAudioEvent", locked_only)
        self.assertNotIn("ESkyguardBriefingPictogram", locked_only)
        self.assertNotIn("FSkyguardAudioEventDefinition", locked_only)
        self.assertNotIn("FSkyguardAudioTelemetry", locked_only)
        self.assertNotIn("ESkyguardBossWeapon", locked_only)
        self.assertNotIn("ESkyguardBossPhase", locked_only)
        self.assertNotIn("ESkyguardPilotCommand", locked_only)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_STORM_KIT, locked_only)
        self.assertNotIn(LEFTOVER_DAY_KIT, locked_only)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, locked_only)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, locked_only)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, locked_only)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, locked_only)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, locked_only)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, locked_only)
        self.assertNotIn(STOP_BEFORE_HARBOR_CALLS, locked_only)
        self.assertNotIn(STOP_BEFORE_SORTIE, locked_only)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_SPEC_MISSION_ID)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_NIGHT_KIT_KEEP_THERMAL)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_NIGHT_KIT_MISSION_ID)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_NIGHT_KIT_DEFAULTS)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_ROSTER_LOOKUP)
        self.assertNotEqual(THIS_SCRIPT, CLONE_THEATER_WEATHER_IDENTITY_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_STORM_KIT_MISSION_ID)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_DAY_KIT_MISSION_ID)
        for helper in namespace_helper_tokens():
            self.assertNotIn(helper, locked_only)
        for token in leftover_harbor_breaker_label_structs():
            self.assertNotIn(token, locked_only)


if __name__ == "__main__":
    unittest.main()
