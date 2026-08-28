# THIS IS leftover-safe FSkyguardStormRainBeatKit bHydraForClusters.
# origin/main form: plain C++ field `bool bHydraForClusters = true;`
# with in-struct initializer true. NOT a UPROPERTY wrap.
# Apache Hydra for clusters. Stay Apache CPG 30 mm / Hydra /
# Hellfire. Do not restore the retired live mount or player
# guided-tube fantasy.
# FSkyguardStormRainBeatKit is a plain C++ kit struct.
# Fail-closed if this test still asserts UPROPERTY / Category /
# VisibleAnywhere / EditAnywhere / BlueprintReadOnly /
# GENERATED_BODY / USTRUCT as the locked decl.
# Parse STRUCT `FSkyguardStormRainBeatKit` body ONLY after
# `struct FSkyguardStormRainBeatKit`. Stop at
# `namespace SkyguardStormRainBeatKits` (plural Kits).
# Do NOT parse leftover `enum class ESkyguardStormRainBeatKind`.
# Do NOT parse leftover `FSkyguardDaySortieBeatKit` or
# `FSkyguardNightSortieBeatKit` or `FSkyguardLoadoutSpec`.
# Do NOT parse leftover `FSkyguardCampaignMissionSpec` Title.
# Do NOT parse leftover Harbor Breaker Approach / Contact / Shore
# as this kit. Do NOT parse leftover
# `ASkyguardGunshipSortieDirector`.
# Do NOT contract sibling fields BeatCount / MissionId / Title /
# WeatherIdentity / WeatherLabel / Weather /
# Kinds / Threats / Stations / Calls.
# Fail-closed if this lane claims leftover Title
# instead of bHydraForClusters. Same bool and `= true` must
# not steal leftover Night kit bKeepThermal.
# THIS IS NOT leftover Night kit bKeepThermal #1485.
# THIS IS NOT leftover analog storm-rain-beat-kit-fields
# #260 / #6879.
# THIS IS NOT leftover analog storm-rain-keeps-hydra
# #561d.
# THIS IS NOT leftover analog storm-rain-beat-kit-defaults
# #248 / #ff81.
# THIS IS NOT leftover analog storm-rain-beat-kit-contract
# bulk. Keep those files in LOCKED_SCRIPTS.
# THIS IS NOT leftover-safe StormRain Title isolated field
# decl. THIS IS NOT leftover DaySortieBeatKit isolated
# MissionId. THIS IS NOT leftover NightSortieBeatKit isolated
# WeatherIdentity. THIS IS NOT leftover LoadoutSpec isolated
# FlareCount. THIS IS NOT leftover-safe TheaterKitSpec
# WeatherIdentity #1300 UPROPERTY clone. Isolated field
# decl does not relock the analog bulk.
# If a clone asserts UPROPERTY / Category="Skyguard|Theater" /
# VisibleAnywhere / FName WeatherIdentity / `= 160.f` /
# bare `FName MissionId;` / `const TCHAR* Title = TEXT("");` /
# leftover `bool bKeepThermal = true;`, retarget: type is
# bool, identifier is bHydraForClusters, initializer is
# true, locked decl is the plain field, not a UPROPERTY wrap.
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
HEADER_PATH = "Source/Skyguard52/SkyguardStormRainBeatKit.h"
STRUCT_NAME = "FSkyguardStormRainBeatKit"
LEFTOVER_KIND_ENUM = "ESkyguardStormRainBeatKind"
LEFTOVER_DAY_KIT = "FSkyguardDaySortieBeatKit"
LEFTOVER_NIGHT_KIT = "FSkyguardNightSortieBeatKit"
LEFTOVER_LOADOUT_SPEC = "FSkyguardLoadoutSpec"
LEFTOVER_CAMPAIGN_SPEC = "FSkyguardCampaignMissionSpec"
LEFTOVER_DAY_HEADER = "Source/Skyguard52/SkyguardDaySortieBeatKit.h"
LEFTOVER_NIGHT_HEADER = "Source/Skyguard52/SkyguardNightSortieBeatKit.h"
LEFTOVER_LOADOUT_HEADER = "Source/Skyguard52/SkyguardGunshipTypes.h"
LEFTOVER_CAMPAIGN_HEADER = "Source/Skyguard52/SkyguardCampaignRoster.h"
NAMESPACE_NAME = "SkyguardStormRainBeatKits"
TARGET = "bool bHydraForClusters = true;"
TARGET_WRONG_BARE = "bool bHydraForClusters;"
TARGET_WRONG_FALSE = "bool bHydraForClusters = false;"
TARGET_WRONG_ZERO = "bool bHydraForClusters = 0;"
TARGET_WRONG_ZERO_F = "bool bHydraForClusters = 0.f;"
TARGET_WRONG_SIX = "bool bHydraForClusters = 6;"
TARGET_WRONG_INT = "int32 bHydraForClusters = true;"
TARGET_WRONG_FLOAT = "float bHydraForClusters = true;"
TARGET_WRONG_FNAME = "FName bHydraForClusters = true;"
TARGET_WRONG_TCHAR = 'const TCHAR* bHydraForClusters = TEXT("");'
TARGET_WRONG_TITLE = 'const TCHAR* Title = TEXT("");'
TARGET_WRONG_KEEP_THERMAL = "bool bKeepThermal = true;"
TARGET_WRONG_LABEL = 'const TCHAR* WeatherLabel = TEXT("");'
LOCKED_DECL = TARGET
CLONE_UPROPERTY_THEATER = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Theater")'
)
CLONE_UPROPERTY_CAMPAIGN = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Campaign")'
)
CLONE_WRONG_USTRUCT = "USTRUCT(BlueprintType)"
CLONE_WRONG_GENERATED = "GENERATED_BODY()"
CLONE_DAY_MISSION_ID = "FName MissionId;"
STOP_BEFORE_NAMESPACE = "namespace SkyguardStormRainBeatKits"
STOP_BEFORE_LEFTOVER_KIND = "enum class ESkyguardStormRainBeatKind"
STOP_BEFORE_DAY_KIT = "struct FSkyguardDaySortieBeatKit"
STOP_BEFORE_NIGHT_KIT = "struct FSkyguardNightSortieBeatKit"
STOP_BEFORE_LOADOUT = "struct FSkyguardLoadoutSpec"
STOP_BEFORE_CAMPAIGN_SPEC = "struct FSkyguardCampaignMissionSpec"
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
RIVER_HAMMER = "RiverHammer"
IRON_RAIN = "IronRain"
FOR_MISSION = "ForMission"
KEEPS_HYDRA = "KeepsHydraForClusters"
APPLY_HYDRA = "ApplyHydraForClusters"
BEAT_INDEX_FOR_ELAPSED = "BeatIndexForElapsed"
SIBLING_BEAT_COUNT = "BeatCount"
SIBLING_MISSION_ID = "MissionId"
SIBLING_TITLE = "Title"
SIBLING_WEATHER_IDENTITY = "WeatherIdentity"
SIBLING_WEATHER_LABEL = "WeatherLabel"
SIBLING_WEATHER = "Weather"
SIBLING_KINDS = "Kinds"
SIBLING_THREATS = "Threats"
SIBLING_STATIONS = "Stations"
SIBLING_CALLS = "Calls"
LEFTOVER_KEEP_THERMAL = "bKeepThermal"
LEFTOVER_HARBOR_APPROACH = "ESkyguardSortieBeat::Approach"
LEFTOVER_HARBOR_CONTACT = "ESkyguardSortieBeat::InitialContact"
LEFTOVER_HARBOR_SHORE = "ESkyguardSortieBeat::ShoreAssault"
LEFTOVER_FLARE_COUNT = "FlareCount"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
THIS_SCRIPT = (
    "Scripts/tests/test_storm_rain_beat_kit_hydra_for_clusters"
    "_field_decl_contract.py"
)
CLONE_THEATER_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
CLONE_DAY_KIT_MISSION_ID = (
    "Scripts/tests/test_day_sortie_beat_kit_mission_id"
    "_field_decl_contract.py"
)
CLONE_NIGHT_KIT_WEATHER_IDENTITY = (
    "Scripts/tests/test_night_sortie_beat_kit_weather_identity"
    "_field_decl_contract.py"
)
CLONE_NIGHT_KIT_MISSION_ID = (
    "Scripts/tests/test_night_sortie_beat_kit_mission_id"
    "_field_decl_contract.py"
)
LEFTOVER_TITLE_FIELD_DECL = (
    "Scripts/tests/test_storm_rain_beat_kit_title"
    "_field_decl_contract.py"
)
LEFTOVER_WEATHER_IDENTITY_FIELD_DECL = (
    "Scripts/tests/test_storm_rain_beat_kit_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_MISSION_ID_FIELD_DECL = (
    "Scripts/tests/test_storm_rain_beat_kit_mission_id"
    "_field_decl_contract.py"
)
LEFTOVER_KEEP_THERMAL_FIELD_DECL = (
    "Scripts/tests/test_night_sortie_beat_kit_keep_thermal"
    "_field_decl_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_BULK = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_LABELS = (
    "Scripts/tests/test_storm_rain_beat_kit_labels_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_FIELDS = (
    "Scripts/tests/test_storm_rain_beat_kit_fields_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_DEFAULTS = (
    "Scripts/tests/test_storm_rain_beat_kit_defaults_contract.py"
)
LEFTOVER_ANALOG_KEEPS_HYDRA = (
    "Scripts/tests/test_storm_rain_keeps_hydra_contract.py"
)
LEFTOVER_ANALOG_DAY_KIT_BULK = (
    "Scripts/tests/test_day_sortie_beat_kit_contract.py"
)
LEFTOVER_ANALOG_NIGHT_KIT_BULK = (
    "Scripts/tests/test_night_sortie_beat_kit_contract.py"
)
LEFTOVER_ANALOG_DAY_KIT_FIELDS = (
    "Scripts/tests/test_day_sortie_beat_kit_fields_contract.py"
)
LEFTOVER_ANALOG_NIGHT_KIT_FIELDS = (
    "Scripts/tests/test_night_sortie_beat_kit_fields_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_KINDS = (
    "Scripts/tests/test_storm_rain_beat_kit_kinds_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_THREATS = (
    "Scripts/tests/test_storm_rain_beat_kit_threats_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_STATIONS = (
    "Scripts/tests/test_storm_rain_beat_kit_stations_contract.py"
)
LEFTOVER_ANALOG_STORM_KIT_CALLS = (
    "Scripts/tests/test_storm_rain_beat_kit_calls_contract.py"
)
LEFTOVER_LOADOUT_FLARE = (
    "Scripts/tests/test_loadout_spec_flare_count"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_STATION = (
    "Scripts/tests/test_loadout_spec_starting_station"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_LOADOUT = (
    "Scripts/tests/test_loadout_spec_loadout"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_CANNON_MAG = (
    "Scripts/tests/test_loadout_spec_cannon_magazine_size"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_CANNON_RESERVE = (
    "Scripts/tests/test_loadout_spec_cannon_reserve"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_ROCKET_RESERVE = (
    "Scripts/tests/test_loadout_spec_rocket_reserve"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_GUIDED_MAG = (
    "Scripts/tests/test_loadout_spec_guided_magazine_size"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_ROCKET_MAG = (
    "Scripts/tests/test_loadout_spec_rocket_magazine_size"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_HULL = (
    "Scripts/tests/test_loadout_spec_hull_integrity"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_PLAYSTYLE = (
    "Scripts/tests/test_loadout_spec_playstyle_line"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_GUIDED_RESERVE = (
    "Scripts/tests/test_loadout_spec_guided_reserve"
    "_field_decl_contract.py"
)

LOCKED = {
    "SkyguardStormRainBeatKit.h",
    "SkyguardStormRainBeatKit.cpp",
    "SkyguardStormRainBeatKitTests.cpp",
    "SkyguardDaySortieBeatKit.h",
    "SkyguardDaySortieBeatKit.cpp",
    "SkyguardNightSortieBeatKit.h",
    "SkyguardNightSortieBeatKit.cpp",
    "SkyguardGunshipTypes.h",
    "SkyguardCampaignRoster.cpp",
    "SkyguardCampaignRoster.h",
    "SkyguardMission05IntegrationDirector.h",
    "SkyguardMission05IntegrationDirector.cpp",
    "SkyguardMission08IntegrationDirector.h",
    "SkyguardMission08IntegrationDirector.cpp",
    "SkyguardGunshipSortieDirector.h",
    "SkyguardGunshipSortieDirector.cpp",
    "SkyguardHarborBeatCalls.h",
    "SkyguardHarborBeatCalls.cpp",
    "SkyguardApacheAircraft.h",
    "SkyguardApacheAircraft.cpp",
    "SkyguardCpgHud.h",
    "SkyguardCpgHud.cpp",
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


LOCKED_SCRIPTS = (
    LEFTOVER_ANALOG_STORM_KIT_BULK,
    LEFTOVER_ANALOG_STORM_KIT_LABELS,
    LEFTOVER_ANALOG_STORM_KIT_FIELDS,
    LEFTOVER_ANALOG_STORM_KIT_DEFAULTS,
    LEFTOVER_ANALOG_KEEPS_HYDRA,
    LEFTOVER_ANALOG_STORM_KIT_KINDS,
    LEFTOVER_ANALOG_STORM_KIT_THREATS,
    LEFTOVER_ANALOG_STORM_KIT_STATIONS,
    LEFTOVER_ANALOG_STORM_KIT_CALLS,
    LEFTOVER_TITLE_FIELD_DECL,
    LEFTOVER_WEATHER_IDENTITY_FIELD_DECL,
    LEFTOVER_MISSION_ID_FIELD_DECL,
    LEFTOVER_KEEP_THERMAL_FIELD_DECL,
    LEFTOVER_ANALOG_DAY_KIT_BULK,
    LEFTOVER_ANALOG_NIGHT_KIT_BULK,
    LEFTOVER_ANALOG_DAY_KIT_FIELDS,
    LEFTOVER_ANALOG_NIGHT_KIT_FIELDS,
    CLONE_DAY_KIT_MISSION_ID,
    CLONE_NIGHT_KIT_WEATHER_IDENTITY,
    CLONE_NIGHT_KIT_MISSION_ID,
    LEFTOVER_LOADOUT_GUIDED_RESERVE,
    LEFTOVER_LOADOUT_PLAYSTYLE,
    LEFTOVER_LOADOUT_HULL,
    LEFTOVER_LOADOUT_ROCKET_MAG,
    LEFTOVER_LOADOUT_GUIDED_MAG,
    LEFTOVER_LOADOUT_ROCKET_RESERVE,
    LEFTOVER_LOADOUT_CANNON_RESERVE,
    LEFTOVER_LOADOUT_CANNON_MAG,
    LEFTOVER_LOADOUT_LOADOUT,
    LEFTOVER_LOADOUT_FLARE,
    LEFTOVER_LOADOUT_STATION,
    CLONE_THEATER_WEATHER_IDENTITY,
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_mesh_bind_slot_fields_contract.py",
    "Scripts/tests/test_theater_kit_spec_kit_id_field_decl_contract.py",
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_beats_contract.py",
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_sortie_beat_enum_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_card_title_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults_contract.py",
    "Scripts/tests/test_protect_asset_current_integrity_field_decl_contract.py",
    "Scripts/tests/test_radar_node_health_field_decl_contract.py",
    "Scripts/tests/test_radar_node_max_health_field_decl_contract.py",
) + leftover_live_copy_boss_scripts()


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
        LEFTOVER_HARBOR_APPROACH,
        LEFTOVER_HARBOR_CONTACT,
        LEFTOVER_HARBOR_SHORE,
    )


def leftover_harbor_beat_tokens() -> tuple[str, ...]:
    return (
        LEFTOVER_HARBOR_APPROACH,
        LEFTOVER_HARBOR_CONTACT,
        LEFTOVER_HARBOR_SHORE,
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
HYDRA_DECL_RE = re.compile(
    r"bool\s+bHydraForClusters\s*=\s*true\s*;"
)
HYDRA_INIT_RE = re.compile(
    r"bool\s+bHydraForClusters\s*=\s*([^;]+);"
)
INVENTED_UPROPERTY = (
    "EditAnywhere",
    "BlueprintReadWrite",
    "BlueprintCallable",
    "BlueprintPure",
    "Transient",
    "MultiLine",
    "BlueprintAuthorityOnly",
    "meta=",
)
INVENTED_FIELD_META = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "CreateDefaultSubobject",
    "const float Amount",
    "{ return",
    "= false",
    "= 0.f",
    "= 160.f",
    "= NAME_None",
    "= 0;",
    "= 100",
    "= 6",
)


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_BEAT_COUNT,
        SIBLING_MISSION_ID,
        SIBLING_TITLE,
        SIBLING_WEATHER_IDENTITY,
        SIBLING_WEATHER_LABEL,
        SIBLING_WEATHER,
        SIBLING_KINDS,
        SIBLING_THREATS,
        SIBLING_STATIONS,
        SIBLING_CALLS,
    )


def namespace_helper_tokens() -> tuple[str, ...]:
    return (
        RIVER_HAMMER,
        IRON_RAIN,
        FOR_MISSION,
        KEEPS_HYDRA,
        APPLY_HYDRA,
        BEAT_INDEX_FOR_ELAPSED,
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


def has_declaration(region: str, declaration: str) -> bool:
    # Fail-closed on authored `bool bHydraForClusters = true;`.
    # Do not accept missing initializer, `= false`, `= 0`,
    # `= 0.f`, `= 6`, int32 / float / FName / TCHAR retargets,
    # leftover Title, leftover WeatherLabel, or leftover
    # Night kit bKeepThermal.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if HYDRA_DECL_RE.search(compact) is None:
        return False
    if re.search(r"bool\s+bHydraForClusters\s*=\s*false\b", compact):
        return False
    if re.search(r"bool\s+bHydraForClusters\s*=\s*0\b", compact):
        return False
    if re.search(r"bool\s+bHydraForClusters\s*=\s*0\.f", compact):
        return False
    if re.search(r"bool\s+bHydraForClusters\s*=\s*6\b", compact):
        return False
    if re.search(r"int32\s+bHydraForClusters\b", compact):
        return False
    if re.search(r"float\s+bHydraForClusters\b", compact):
        return False
    if re.search(r"FName\s+bHydraForClusters\b", compact):
        return False
    if re.search(r"const\s+TCHAR\s*\*\s*bHydraForClusters\b", compact):
        return False
    if re.search(r"bool\s+bKeepThermal\b", compact) and not has_identifier(
        compact,
        "bHydraForClusters",
    ):
        return False
    if re.search(r"bool\s+bHydraForClusters\s*;", compact) and not re.search(
        r"bool\s+bHydraForClusters\s*=",
        compact,
    ):
        return False
    for match in HYDRA_INIT_RE.finditer(compact):
        if collapsed(match.group(1)) != "true":
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


def leftover_day_kit_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_DAY_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_DAY_HEADER} is missing from origin/main"
        )
    return result.stdout


def leftover_night_kit_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_NIGHT_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_NIGHT_HEADER} is missing from origin/main"
        )
    return result.stdout


def leftover_loadout_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_LOADOUT_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_LOADOUT_HEADER} is missing from origin/main"
        )
    return result.stdout


def leftover_campaign_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_CAMPAIGN_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_CAMPAIGN_HEADER} is missing from origin/main"
        )
    return result.stdout


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
        STOP_BEFORE_LEFTOVER_KIND,
        STOP_BEFORE_DAY_KIT,
        STOP_BEFORE_NIGHT_KIT,
        STOP_BEFORE_LOADOUT,
        STOP_BEFORE_CAMPAIGN_SPEC,
        STOP_BEFORE_AUDIO_EVENT,
        STOP_BEFORE_PICTOGRAM,
        STOP_BEFORE_EVENT_DEF,
        STOP_BEFORE_BOSS_WEAPON,
        STOP_BEFORE_PROP_SPINNER,
        STOP_BEFORE_SORTIE,
        STOP_BEFORE_PATROL,
        leftover_retired_mount_class(),
        STOP_BEFORE_GUNNER,
        STOP_BEFORE_WEAK_POINT,
        STOP_BEFORE_HARBOR_CALLS,
        LEFTOVER_DAY_KIT,
        LEFTOVER_NIGHT_KIT,
        LEFTOVER_LOADOUT_SPEC,
        LEFTOVER_CAMPAIGN_SPEC,
        LEFTOVER_HARBOR_APPROACH,
        LEFTOVER_HARBOR_CONTACT,
        LEFTOVER_HARBOR_SHORE,
        "class USkyguardCampaignSubsystem",
        "struct FSkyguardMissionResult",
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
    if STOP_BEFORE_LEFTOVER_KIND in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes leftover "
            f"{STOP_BEFORE_LEFTOVER_KIND}"
        )
    for harbor in leftover_harbor_beat_tokens():
        if harbor in section:
            raise AssertionError(
                f"{STRUCT_NAME} parse window includes leftover "
                f"Harbor {harbor}"
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
            r"\s*bool bHydraForClusters\b", compact[index:]
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for bool bHydraForClusters is missing from "
        f"origin/main:{HEADER_PATH} struct {STRUCT_NAME} body; "
        "locked decl is the plain C++ field, not a UPROPERTY wrap"
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
        r"UPROPERTY\([^)]*\)\s*bool bHydraForClusters\b",
        compact,
    ):
        raise AssertionError(
            "UPROPERTY wrap on bool bHydraForClusters is not the locked "
            f"decl for plain C++ struct {STRUCT_NAME}"
        )
    if "UPROPERTY" in section and has_identifier(section, "bHydraForClusters"):
        raise AssertionError(
            "UPROPERTY clone landed on bHydraForClusters; locked decl is "
            f"plain {LOCKED_DECL}"
        )
    for token in ("USTRUCT", "GENERATED_BODY"):
        if token in section and has_identifier(section, "bHydraForClusters"):
            raise AssertionError(
                f"{token} clone landed on bHydraForClusters; locked decl is "
                f"plain {LOCKED_DECL}"
            )


class StormRainBeatKitHydraForClustersFieldDeclContractTests(unittest.TestCase):
    def test_storm_rain_beat_kit_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(STRUCT_NAME, header)
        self.assertIsNotNone(STRUCT_RE.search(header), header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(STRUCT_NAME, "FSkyguardStormRainBeatKit")
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DAY_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_NIGHT_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_CAMPAIGN_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_APACHE_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_RADAR_NODE_CLASS)
        self.assertNotEqual(STRUCT_NAME, STOP_BEFORE_SORTIE)
        body = struct_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "bHydraForClusters"), section)
        self.assertNotIn("UPROPERTY", section)
        self.assertNotIn("GENERATED_BODY", section)
        self.assertNotIn("USTRUCT", section)
        self.assertIn(STOP_BEFORE_NAMESPACE, header)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, body)
        self.assertIn(STOP_BEFORE_LEFTOVER_KIND, header)
        self.assertNotIn(STOP_BEFORE_LEFTOVER_KIND, section)
        self.assertNotIn(STOP_BEFORE_LEFTOVER_KIND, body)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_DAY_KIT, section)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)

    def test_locked_decl_is_plain_cpp_not_uproperty(self) -> None:
        self.assertEqual(LOCKED_DECL, "bool bHydraForClusters = true;")
        self.assertEqual(LOCKED_DECL, TARGET)
        self.assertTrue(LOCKED_DECL.startswith("bool bHydraForClusters"))
        self.assertTrue(LOCKED_DECL.endswith(";"))
        self.assertIn("=", LOCKED_DECL)
        self.assertIn("= true", LOCKED_DECL)
        self.assertIn("bHydraForClusters", LOCKED_DECL)
        self.assertNotIn(SIBLING_TITLE, LOCKED_DECL)
        self.assertNotIn(SIBLING_WEATHER_LABEL, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_THEATER, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_CAMPAIGN, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_THEATER)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_CAMPAIGN)
        self.assertNotEqual(LOCKED_DECL, CLONE_DAY_MISSION_ID)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TITLE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_KEEP_THERMAL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LABEL)
        self.assertNotEqual(LOCKED_DECL, "FName WeatherIdentity;")
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BARE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_FALSE)

    def test_clone_uproperty_as_locked_decl_fails_closed(self) -> None:
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn("VisibleAnywhere", LOCKED_DECL)
        self.assertNotIn("EditAnywhere", LOCKED_DECL)
        self.assertNotIn("BlueprintReadOnly", LOCKED_DECL)
        self.assertNotIn("GENERATED_BODY", LOCKED_DECL)
        self.assertNotIn("USTRUCT", LOCKED_DECL)
        clone_locked = CLONE_UPROPERTY_THEATER
        self.assertIn("UPROPERTY", clone_locked)
        self.assertNotEqual(LOCKED_DECL, clone_locked)
        self.assertFalse(has_declaration(clone_locked, LOCKED_DECL))
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{clone_locked}\n", LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            struct_body(
                "struct FSkyguardUnrelatedStormRainBeatKit\n{\n};\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_kind_enum_does_not_satisfy(self) -> None:
        leftover = (
            f"enum class {LEFTOVER_KIND_ENUM} : uint8\n"
            "{\n"
            "\tApproach,\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(leftover)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_day_night_loadout_campaign_do_not_satisfy(self) -> None:
        leftovers = (
            LEFTOVER_DAY_KIT,
            LEFTOVER_NIGHT_KIT,
            LEFTOVER_LOADOUT_SPEC,
            LEFTOVER_CAMPAIGN_SPEC,
        )
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

    def test_does_not_claim_leftover_day_night_loadout_or_campaign(self) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_DAY_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_NIGHT_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_LOADOUT_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_CAMPAIGN_HEADER)
        self.assertTrue(HEADER_PATH.endswith("SkyguardStormRainBeatKit.h"))
        self.assertNotIn("DaySortie", HEADER_PATH)
        self.assertNotIn("NightSortie", HEADER_PATH)
        self.assertNotIn("GunshipTypes", HEADER_PATH)
        self.assertNotIn("CampaignRoster", HEADER_PATH)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DAY_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_NIGHT_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_CAMPAIGN_SPEC)
        day_header = leftover_day_kit_header()
        self.assertIn(LEFTOVER_DAY_KIT, day_header)
        self.assertIn(CLONE_DAY_MISSION_ID, day_header)
        self.assertNotIn(LOCKED_DECL, day_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(day_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        night_header = leftover_night_kit_header()
        self.assertIn(LEFTOVER_NIGHT_KIT, night_header)
        self.assertIn("FName WeatherIdentity;", night_header)
        self.assertIn(TARGET_WRONG_KEEP_THERMAL, night_header)
        self.assertNotIn(LOCKED_DECL, night_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(night_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        loadout_header = leftover_loadout_header()
        self.assertIn(LEFTOVER_LOADOUT_SPEC, loadout_header)
        self.assertIn(LEFTOVER_FLARE_COUNT, loadout_header)
        self.assertNotIn(LOCKED_DECL, loadout_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(loadout_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        campaign_header = leftover_campaign_header()
        self.assertIn(LEFTOVER_CAMPAIGN_SPEC, campaign_header)
        self.assertIn(TARGET_WRONG_TITLE, campaign_header)
        self.assertNotIn(LOCKED_DECL, campaign_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(campaign_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_namespace_declaration_does_not_satisfy(self) -> None:
        mixed = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "};\n"
            f"{STOP_BEFORE_NAMESPACE}\n"
            "{\n"
            f"\tconst {STRUCT_NAME}& {RIVER_HAMMER}();\n"
            f"\t{LOCKED_DECL}\n"
            "}\n"
        )
        section = spec_section(mixed)
        self.assertFalse(has_identifier(section, "bHydraForClusters"), section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_hydra_declaration_fails_closed(self) -> None:
        empty = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\tFName {SIBLING_MISSION_ID};\n"
            f"\t{TARGET_WRONG_TITLE}\n"
            f"\t{TARGET_WRONG_LABEL}\n"
            f"\tFName {SIBLING_WEATHER_IDENTITY};\n"
            f"\t{TARGET_WRONG_KEEP_THERMAL}\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_title_does_not_satisfy_hydra(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_TITLE}\n"
            "};\n"
        )
        section = spec_section(leftover)
        self.assertTrue(has_identifier(section, SIBLING_TITLE), section)
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TITLE)
        self.assertNotIn(SIBLING_TITLE, LOCKED_DECL)

    def test_leftover_keep_thermal_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_KEEP_THERMAL}\n"
            "};\n"
        )
        section = spec_section(leftover)
        self.assertTrue(has_identifier(section, LEFTOVER_KEEP_THERMAL), section)
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_KEEP_THERMAL)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, LOCKED_DECL)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_KEEP_THERMAL_FIELD_DECL)
        self.assertIn(LEFTOVER_KEEP_THERMAL_FIELD_DECL, LOCKED_SCRIPTS)

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{CLONE_UPROPERTY_THEATER}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_has_plain_field_not_uproperty(self) -> None:
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
        self.assertIn("plain", str(raised.exception).lower())

    def test_initializer_must_be_true(self) -> None:
        missing = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_BARE}\n"
            "};\n"
        )
        section = spec_section(missing)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        wrong_false = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_FALSE}\n"
            "};\n"
        )
        section = spec_section(wrong_false)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn("bool bHydraForClusters = true;", compact_origin)
        self.assertNotIn("bool bHydraForClusters = false;", compact_origin)
        self.assertNotIn("bool bHydraForClusters = 0;", compact_origin)
        self.assertNotIn("bool bHydraForClusters = 0.f;", compact_origin)
        self.assertNotIn(
            "bool bHydraForClusters;",
            compact_origin.replace("bool bHydraForClusters = true;", ""),
        )

    def test_hydra_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("bool bHydraForClusters"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertIn("=", LOCKED_DECL)
        self.assertIn("= true", LOCKED_DECL)
        self.assertNotIn("= false", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertNotIn("= NAME_None", LOCKED_DECL)
        self.assertIn("bool ", LOCKED_DECL)
        self.assertNotIn("float ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("const TCHAR*", LOCKED_DECL)
        self.assertNotIn("FSkyguardMissionResult", LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FALSE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_ZERO}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_ZERO_F}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_INT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FLOAT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TCHAR}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TITLE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_KEEP_THERMAL}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LABEL}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_KEEP_THERMAL}\n", LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tbool " + leftover_retired_primary_hits_field()
            + " = true;\n"
        )
        leftover_guided = (
            "\tbool " + leftover_retired_guided_hits_field()
            + " = true;\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_FALSE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_ZERO_F}\n",
            f"\t{TARGET_WRONG_SIX}\n",
            f"\t{TARGET_WRONG_INT}\n",
            f"\t{TARGET_WRONG_FLOAT}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_TCHAR}\n",
            f"\t{TARGET_WRONG_TITLE}\n",
            f"\t{TARGET_WRONG_KEEP_THERMAL}\n",
            f"\t{TARGET_WRONG_LABEL}\n",
            leftover_primary,
            leftover_guided,
            f"\tFName {SIBLING_MISSION_ID};\n",
            f"\tFName {SIBLING_WEATHER_IDENTITY};\n",
            f"\tint32 {LEFTOVER_FLARE_COUNT} = 6;\n",
            "\tbool bHydraForCluster = true;\n",
            "\tbool bHydraForClusterss = true;\n",
            "\tint32 bHydraForClusters;\n",
            "\tfloat bHydraForClusters = " + forty + ";\n",
            "\tfloat bHydraForClusters = " + eighty + ";\n",
            "\tbool bHydraForClusters = " + forty + ";\n",
            "\tbool bHydraForClusters = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("bHydraForClusters", str(raised.exception))
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
            f"\t{CLONE_WRONG_USTRUCT}\n"
            f"\t{CLONE_WRONG_GENERATED}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n",
        )
        for wrapped in wraps:
            section = spec_section(wrapped)
            with self.assertRaises(AssertionError):
                require_no_uproperty_wrap(section)
        origin = spec_section(origin_main_header())
        require_no_uproperty_wrap(origin)
        self.assertNotIn("UPROPERTY", origin)
        self.assertNotIn("Category", origin)
        self.assertNotIn("VisibleAnywhere", origin)
        self.assertNotIn("EditAnywhere", origin)
        self.assertNotIn("BlueprintReadOnly", origin)
        self.assertNotIn("GENERATED_BODY", origin)
        self.assertNotIn("USTRUCT", origin)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tbool\n\tbHydraForClusters = true;\n",
            "\tbool   bHydraForClusters = true;\n",
            "\tbool\tbHydraForClusters = true;\n",
            f"\t{LOCKED_DECL}\n",
        )
        for region in wraps:
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)
        self.assertFalse(
            has_declaration(
                f"\t{CLONE_UPROPERTY_THEATER}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_TITLE}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_KEEP_THERMAL}\n",
                LOCKED_DECL,
            )
        )

    def test_does_not_contract_sibling_kit_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        section = spec_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        self.assertTrue(has_identifier(section, SIBLING_TITLE))
        self.assertTrue(has_identifier(section, SIBLING_WEATHER_LABEL))
        self.assertFalse(has_identifier(section, LEFTOVER_KEEP_THERMAL))
        self.assertFalse(has_identifier(section, LEFTOVER_FLARE_COUNT))
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_does_not_parse_leftover_kind_enum_or_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        self.assertIn(STOP_BEFORE_NAMESPACE, header)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, leaked)
        self.assertIn(STOP_BEFORE_LEFTOVER_KIND, header)
        self.assertNotIn(STOP_BEFORE_LEFTOVER_KIND, section)
        self.assertNotIn(STOP_BEFORE_LEFTOVER_KIND, leaked)
        for helper in namespace_helper_tokens():
            self.assertIn(helper, header)
            self.assertNotIn(helper, section)
            self.assertNotIn(helper, leaked)
        self.assertNotIn(STOP_BEFORE_DAY_KIT, header)
        self.assertNotIn(STOP_BEFORE_NIGHT_KIT, header)
        self.assertNotIn(LEFTOVER_DAY_KIT, header)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, header)
        self.assertNotIn(STOP_BEFORE_LOADOUT, header)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, header)
        self.assertNotIn(STOP_BEFORE_CAMPAIGN_SPEC, header)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, header)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, header)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, header)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, header)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, header)
        self.assertNotIn(STOP_BEFORE_PROP_SPINNER, header)
        self.assertNotIn(STOP_BEFORE_SORTIE, header)
        self.assertNotIn(STOP_BEFORE_PATROL, header)
        self.assertNotIn(leftover_retired_mount_class(), header)
        self.assertNotIn(STOP_BEFORE_GUNNER, section)
        self.assertNotIn(STOP_BEFORE_GUNNER, leaked)
        self.assertNotIn(STOP_BEFORE_WEAK_POINT, header)
        self.assertNotIn(STOP_BEFORE_HARBOR_CALLS, header)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, header)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, header)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, header)
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, header)
        for harbor in leftover_harbor_beat_tokens():
            self.assertNotIn(harbor, section)
            self.assertNotIn(harbor, leaked)
            self.assertNotIn(harbor, LOCKED_DECL)

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
        self.assertNotIn(LEFTOVER_DAY_KIT, section)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, section)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            f"\tconst {STRUCT_NAME}& {RIVER_HAMMER}();\n"
            f"\tconst {STRUCT_NAME}& {IRON_RAIN}();\n"
            f"\tconst {STRUCT_NAME}& {FOR_MISSION}(FName MissionId);\n"
            f"\tbool {KEEPS_HYDRA}();\n"
            f"\tbool {APPLY_HYDRA}();\n"
            f"\tint32 {BEAT_INDEX_FOR_ELAPSED}();\n"
            f"\tFName {SIBLING_MISSION_ID};\n"
            f"\tFName {SIBLING_WEATHER_IDENTITY};\n"
            f"\t{TARGET_WRONG_TITLE}\n"
            f"\t{TARGET_WRONG_LABEL}\n"
            f"\t{TARGET_WRONG_KEEP_THERMAL}\n"
            f"\tint32 {LEFTOVER_FLARE_COUNT} = 6;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("bHydraForClusters", str(raised.exception))

    def test_leftover_harbor_directors_do_not_satisfy(self) -> None:
        for token in leftover_harbor_director_tokens():
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

    def test_harbor_breaker_beats_are_not_this_kit(self) -> None:
        self.assertNotEqual(STRUCT_NAME, "HarborBreaker")
        self.assertNotEqual(STRUCT_NAME, STOP_BEFORE_SORTIE)
        for harbor in leftover_harbor_beat_tokens():
            self.assertNotIn(harbor, LOCKED_DECL)
            leftover = (
                f"struct {harbor}\n"
                "{\n"
                f"\t{LOCKED_DECL}\n"
                "};\n"
            )
            with self.assertRaises(AssertionError) as raised:
                spec_section(leftover)
            self.assertIn(STRUCT_NAME, str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
        header = origin_main_header()
        section = spec_section(header)
        for harbor in leftover_harbor_beat_tokens():
            self.assertNotIn(harbor, section)
            self.assertNotIn(harbor, LOCKED_DECL)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        self.assertEqual(LOCKED_DECL, "bool bHydraForClusters = true;")
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, LOCKED_DECL)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_THEATER, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_CAMPAIGN, LOCKED_DECL)
        self.assertNotIn("MultiLine", LOCKED_DECL)
        self.assertNotIn("ClampMin", LOCKED_DECL)
        self.assertNotIn("ClampMax", LOCKED_DECL)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardStormRainBeatKit.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardDaySortieBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardNightSortieBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignRoster.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardRadarNode.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)
        self.assertNotIn("SkyguardHarborBeatCalls.h", HEADER_PATH)

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
                "storm-rain-beat-kit bHydraForClusters field decl contract "
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
            "hydra_for_clusters_field_decl_contract.py"
        ))
        self.assertIn("storm_rain_beat_kit", Path(__file__).name)
        self.assertNotIn("keep_thermal", Path(__file__).name)
        self.assertNotIn("SkyguardStormRainBeatKit.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardDaySortieBeatKit.h", THIS_SCRIPT)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_BULK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_LABELS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_FIELDS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_KEEPS_HYDRA, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_TITLE_FIELD_DECL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_KEEP_THERMAL_FIELD_DECL, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DAY_KIT_MISSION_ID, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NIGHT_KIT_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NIGHT_KIT_MISSION_ID, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_GUIDED_RESERVE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_PLAYSTYLE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_HULL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_ROCKET_MAG, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_GUIDED_MAG, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_ROCKET_RESERVE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_CANNON_RESERVE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_CANNON_MAG, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_LOADOUT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_FLARE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_STATION, LOCKED_SCRIPTS)
        self.assertIn(CLONE_THEATER_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_DAY_KIT_BULK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_NIGHT_KIT_BULK, LOCKED_SCRIPTS)

    def test_leftover_analog_bulk_stays_locked(self) -> None:
        leftovers = (
            LEFTOVER_ANALOG_STORM_KIT_BULK,
            LEFTOVER_ANALOG_STORM_KIT_LABELS,
            LEFTOVER_ANALOG_STORM_KIT_FIELDS,
            LEFTOVER_ANALOG_STORM_KIT_DEFAULTS,
            LEFTOVER_ANALOG_KEEPS_HYDRA,
            LEFTOVER_ANALOG_STORM_KIT_KINDS,
            LEFTOVER_ANALOG_STORM_KIT_THREATS,
            LEFTOVER_ANALOG_STORM_KIT_STATIONS,
            LEFTOVER_ANALOG_STORM_KIT_CALLS,
            LEFTOVER_TITLE_FIELD_DECL,
            LEFTOVER_WEATHER_IDENTITY_FIELD_DECL,
            LEFTOVER_MISSION_ID_FIELD_DECL,
            LEFTOVER_KEEP_THERMAL_FIELD_DECL,
            LEFTOVER_ANALOG_DAY_KIT_BULK,
            LEFTOVER_ANALOG_NIGHT_KIT_BULK,
            LEFTOVER_ANALOG_DAY_KIT_FIELDS,
            LEFTOVER_ANALOG_NIGHT_KIT_FIELDS,
            CLONE_DAY_KIT_MISSION_ID,
            CLONE_NIGHT_KIT_WEATHER_IDENTITY,
            CLONE_NIGHT_KIT_MISSION_ID,
            LEFTOVER_LOADOUT_GUIDED_RESERVE,
            LEFTOVER_LOADOUT_PLAYSTYLE,
            LEFTOVER_LOADOUT_HULL,
            LEFTOVER_LOADOUT_ROCKET_MAG,
            LEFTOVER_LOADOUT_GUIDED_MAG,
            LEFTOVER_LOADOUT_ROCKET_RESERVE,
            LEFTOVER_LOADOUT_CANNON_RESERVE,
            LEFTOVER_LOADOUT_CANNON_MAG,
            LEFTOVER_LOADOUT_LOADOUT,
            LEFTOVER_LOADOUT_FLARE,
            LEFTOVER_LOADOUT_STATION,
            CLONE_THEATER_WEATHER_IDENTITY,
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
        self.assertNotIn(LEFTOVER_KEEP_THERMAL, locked_only)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, locked_only)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, locked_only)
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
        self.assertNotIn(LEFTOVER_DAY_KIT, locked_only)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, locked_only)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, locked_only)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, locked_only)
        self.assertNotIn(LEFTOVER_KIND_ENUM, locked_only)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, locked_only)
        self.assertNotIn(STOP_BEFORE_HARBOR_CALLS, locked_only)
        self.assertNotIn(SIBLING_TITLE, locked_only)
        self.assertNotIn(SIBLING_WEATHER_LABEL, locked_only)
        for harbor in leftover_harbor_beat_tokens():
            self.assertNotIn(harbor, locked_only)
        for helper in namespace_helper_tokens():
            self.assertNotIn(helper, locked_only)


if __name__ == "__main__":
    unittest.main()
