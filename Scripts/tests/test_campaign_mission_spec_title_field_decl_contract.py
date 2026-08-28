# THIS IS leftover-safe FSkyguardCampaignMissionSpec Title.
# origin/main form: plain C++ field `const TCHAR* Title = TEXT("");`
# with in-struct initializer TEXT(""). NOT a UPROPERTY wrap.
# FSkyguardCampaignMissionSpec is a plain C++ roster struct.
# Fail-closed if this test still asserts UPROPERTY / Category /
# VisibleAnywhere / EditAnywhere / BlueprintReadOnly /
# GENERATED_BODY / USTRUCT as the locked decl.
# Parse STRUCT `FSkyguardCampaignMissionSpec` body ONLY after
# `struct FSkyguardCampaignMissionSpec`. Stop at
# `namespace SkyguardCampaignRoster`.
# Do NOT parse leftover `FSkyguardStormRainBeatKit` Title
# leftover-safe #1491. Same TCHAR* TEXT("") must not steal
# that leftover parse window.
# Do NOT parse leftover `FSkyguardCpgContactMark` or leftover
# `FSkyguardCpgHudSnapshot`.
# Do NOT parse leftover Harbor Breaker Approach / Contact / Shore
# as this spec. Do NOT parse leftover
# `ASkyguardGunshipSortieDirector`.
# Do NOT contract sibling fields MissionId / Brief / Success /
# Failure / Weather / WeatherIdentity / WeatherLabel /
# TimeOfDayHours / BeatSeconds / kinds / Climax /
# bNightIdentity / bStormRocketContract.
# Fail-closed if leftover namespace SkyguardCampaignRoster
# helpers are parsed as this slot.
# THIS IS NOT leftover analog storm-rain-beat-kit-labels
# #261 / #b557 (Title and WeatherLabel bulk).
# THIS IS NOT leftover analog campaign-roster-lookup-tests
# #85ab.
# THIS IS NOT leftover-safe TheaterKitSpec WeatherIdentity
# #1300 UPROPERTY clone. Isolated field decl does not
# relock the analog bulk.
# If a clone asserts UPROPERTY / Category="Skyguard|Theater" /
# VisibleAnywhere / FName WeatherIdentity / `= 160.f` /
# leftover StormRainBeatKit Title, retarget: type is
# const TCHAR*, identifier is Title, initializer is
# TEXT(""), locked decl is the plain field, parse window
# is FSkyguardCampaignMissionSpec.
# Harbor 40/80 fail-closed via split tokens. BeatSeconds
# uses 120/240/360/480/600/780/900, not invented Harbor
# 40/80.
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
LEFTOVER_STORM_RAIN_KIT = "FSkyguardStormRainBeatKit"
LEFTOVER_STORM_RAIN_KIND = "ESkyguardStormRainBeatKind"
LEFTOVER_DAY_KIT = "FSkyguardDaySortieBeatKit"
LEFTOVER_NIGHT_KIT = "FSkyguardNightSortieBeatKit"
LEFTOVER_LOADOUT_SPEC = "FSkyguardLoadoutSpec"
LEFTOVER_CONTACT_MARK = "FSkyguardCpgContactMark"
LEFTOVER_HUD_SNAPSHOT = "FSkyguardCpgHudSnapshot"
LEFTOVER_STORM_RAIN_HEADER = "Source/Skyguard52/SkyguardStormRainBeatKit.h"
LEFTOVER_DAY_HEADER = "Source/Skyguard52/SkyguardDaySortieBeatKit.h"
LEFTOVER_NIGHT_HEADER = "Source/Skyguard52/SkyguardNightSortieBeatKit.h"
LEFTOVER_LOADOUT_HEADER = "Source/Skyguard52/SkyguardGunshipTypes.h"
LEFTOVER_CPG_HUD_HEADER = "Source/Skyguard52/SkyguardCpgHud.h"
NAMESPACE_NAME = "SkyguardCampaignRoster"
TARGET = 'const TCHAR* Title = TEXT("");'
TARGET_WRONG_BARE = "const TCHAR* Title;"
TARGET_WRONG_EQ_NONE = "const TCHAR* Title = NAME_None;"
TARGET_WRONG_FALSE = "const TCHAR* Title = false;"
TARGET_WRONG_TRUE = "const TCHAR* Title = true;"
TARGET_WRONG_ZERO = "const TCHAR* Title = 0.f;"
TARGET_WRONG_FLOAT = "float Title;"
TARGET_WRONG_HEALTH = "float Title = 160.f;"
TARGET_WRONG_BOOL = "bool Title;"
TARGET_WRONG_INT = "int32 Title;"
TARGET_WRONG_FNAME = "FName Title;"
TARGET_WRONG_TEXT = 'const TCHAR* Title = TEXT("Storm");'
TARGET_WRONG_BRIEF = 'const TCHAR* Brief = TEXT("");'
TARGET_WRONG_SUCCESS = 'const TCHAR* Success = TEXT("");'
TARGET_WRONG_FAILURE = 'const TCHAR* Failure = TEXT("");'
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
CLONE_DAY_MISSION_ID = "FName MissionId;"
STOP_BEFORE_NAMESPACE = "namespace SkyguardCampaignRoster"
STOP_BEFORE_STORM_RAIN_KIT = "struct FSkyguardStormRainBeatKit"
STOP_BEFORE_STORM_RAIN_KIND = "enum class ESkyguardStormRainBeatKind"
STOP_BEFORE_STORM_RAIN_NS = "namespace SkyguardStormRainBeatKits"
STOP_BEFORE_DAY_KIT = "struct FSkyguardDaySortieBeatKit"
STOP_BEFORE_NIGHT_KIT = "struct FSkyguardNightSortieBeatKit"
STOP_BEFORE_LOADOUT = "struct FSkyguardLoadoutSpec"
STOP_BEFORE_CONTACT_MARK = "struct FSkyguardCpgContactMark"
STOP_BEFORE_HUD_SNAPSHOT = "struct FSkyguardCpgHudSnapshot"
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
NS_NUM_MISSIONS = "NumMissions"
NS_GET = "Get(int32 Index)"
NS_INDEX_OF = "IndexOf"
NS_ID_AT = "IdAt"
NS_LOADOUT_LABEL = "LoadoutLabel"
NS_WEATHER_ENUM_LABEL = "WeatherEnumLabel"
SIBLING_MISSION_ID = "MissionId"
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
SIBLING_NIGHT_IDENTITY = "bNightIdentity"
SIBLING_STORM_ROCKET = "bStormRocketContract"
LEFTOVER_HARBOR_APPROACH = "ESkyguardSortieBeat::Approach"
LEFTOVER_HARBOR_CONTACT = "ESkyguardSortieBeat::InitialContact"
LEFTOVER_HARBOR_SHORE = "ESkyguardSortieBeat::ShoreAssault"
LEFTOVER_FLARE_COUNT = "FlareCount"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
THIS_SCRIPT = (
    "Scripts/tests/test_campaign_mission_spec_title"
    "_field_decl_contract.py"
)
CLONE_THEATER_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_STORM_RAIN_TITLE = (
    "Scripts/tests/test_storm_rain_beat_kit_title"
    "_field_decl_contract.py"
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
LEFTOVER_ANALOG_STORM_KIT_BULK = (
    "Scripts/tests/test_storm_rain_beat_kit_contract.py"
)
LEFTOVER_ANALOG_CAMPAIGN_ROSTER_LOOKUP = (
    "Scripts/tests/test_campaign_roster_lookup_tests.py"
)
LEFTOVER_ANALOG_CAMPAIGN_ROSTER_GET = (
    "Scripts/tests/test_campaign_roster_get_decl_contract.py"
)
LEFTOVER_ANALOG_CAMPAIGN_ROSTER_ID_AT = (
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py"
)
LEFTOVER_ANALOG_CAMPAIGN_ROSTER_NUM = (
    "Scripts/tests/test_campaign_roster_num_missions"
    "_decl_contract.py"
)
LEFTOVER_ANALOG_CAMPAIGN_ROSTER_LOADOUT = (
    "Scripts/tests/test_campaign_roster_loadout_label"
    "_decl_contract.py"
)
LEFTOVER_ANALOG_CAMPAIGN_ROSTER_WEATHER = (
    "Scripts/tests/test_campaign_roster_weather_enum_label"
    "_decl_contract.py"
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
    "SkyguardCampaignRoster.h",
    "SkyguardCampaignRoster.cpp",
    "SkyguardStormRainBeatKit.h",
    "SkyguardStormRainBeatKit.cpp",
    "SkyguardStormRainBeatKitTests.cpp",
    "SkyguardDaySortieBeatKit.h",
    "SkyguardDaySortieBeatKit.cpp",
    "SkyguardNightSortieBeatKit.h",
    "SkyguardNightSortieBeatKit.cpp",
    "SkyguardGunshipTypes.h",
    "SkyguardCpgHud.h",
    "SkyguardCpgHud.cpp",
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
        "_lock_uneligible_decl_contract.py",
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
    LEFTOVER_STORM_RAIN_TITLE,
    LEFTOVER_ANALOG_STORM_KIT_LABELS,
    LEFTOVER_ANALOG_STORM_KIT_FIELDS,
    LEFTOVER_ANALOG_STORM_KIT_DEFAULTS,
    LEFTOVER_ANALOG_STORM_KIT_BULK,
    LEFTOVER_ANALOG_CAMPAIGN_ROSTER_LOOKUP,
    LEFTOVER_ANALOG_CAMPAIGN_ROSTER_GET,
    LEFTOVER_ANALOG_CAMPAIGN_ROSTER_ID_AT,
    LEFTOVER_ANALOG_CAMPAIGN_ROSTER_NUM,
    LEFTOVER_ANALOG_CAMPAIGN_ROSTER_LOADOUT,
    LEFTOVER_ANALOG_CAMPAIGN_ROSTER_WEATHER,
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
    "Scripts/tests/test_briefing_card_title_field_decl_contract.py",
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_sortie_beat_enum_contract.py",
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
TITLE_DECL_RE = re.compile(
    r"const\s+TCHAR\s*\*\s*Title\s*=\s*TEXT\s*\(\s*\"\"\s*\)\s*;"
)
TITLE_INIT_RE = re.compile(
    r"const\s+TCHAR\s*\*\s*Title\s*=\s*([^;]+);"
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
    "= true",
    "= false",
    "= 0.f",
    "= 160.f",
    "= NAME_None",
)


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_MISSION_ID,
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
        SIBLING_NIGHT_IDENTITY,
        SIBLING_STORM_ROCKET,
    )


def leftover_sibling_locked_decls() -> tuple[str, ...]:
    return (
        TARGET_WRONG_BRIEF,
        TARGET_WRONG_SUCCESS,
        TARGET_WRONG_FAILURE,
        TARGET_WRONG_LABEL,
        CLONE_DAY_MISSION_ID,
        "FName WeatherIdentity;",
        "float TimeOfDayHours = 12.f;",
        "float BeatSeconds[7]",
        "ESkyguardThreatKind ContactKind",
        "ESkyguardThreatKind ShoreKind",
        "ESkyguardThreatKind SupportKind",
        "ESkyguardThreatKind ExtractKind",
        "ESkyguardClimaxKind Climax",
        "bool bNightIdentity = false;",
        "bool bStormRocketContract = false;",
        "ESkyguardMissionWeather Weather = ESkyguardMissionWeather::Clear;",
    )


def namespace_helper_tokens() -> tuple[str, ...]:
    return (
        NS_NUM_MISSIONS,
        NS_GET,
        NS_INDEX_OF,
        NS_ID_AT,
        NS_LOADOUT_LABEL,
        NS_WEATHER_ENUM_LABEL,
    )


def leftover_storm_rain_title_tokens() -> tuple[str, ...]:
    return (
        LEFTOVER_STORM_RAIN_KIT,
        LEFTOVER_STORM_RAIN_KIND,
        LEFTOVER_STORM_RAIN_HEADER,
        STOP_BEFORE_STORM_RAIN_KIT,
        STOP_BEFORE_STORM_RAIN_KIND,
        STOP_BEFORE_STORM_RAIN_NS,
        LEFTOVER_STORM_RAIN_TITLE,
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
    # Fail-closed on authored `const TCHAR* Title = TEXT("");`.
    # Do not accept missing TEXT(""), WeatherLabel, Brief,
    # Success, Failure, FName Title, `= NAME_None` /
    # `= false` / `= true` / `= 0.f` / `= 160.f` when
    # origin/main locks TEXT(""). Do not accept leftover
    # StormRainBeatKit Title as this CampaignMissionSpec
    # parse window.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if TITLE_DECL_RE.search(compact) is None:
        return False
    if re.search(r"float\s+Title\b", compact):
        return False
    if re.search(r"FName\s+Title\b", compact):
        return False
    if re.search(
        r"const\s+TCHAR\s*\*\s*WeatherLabel\b",
        compact,
    ) and not has_identifier(compact, "Title"):
        return False
    for match in TITLE_INIT_RE.finditer(compact):
        if collapsed(match.group(1)) != 'TEXT("")':
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


def leftover_storm_rain_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_STORM_RAIN_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_STORM_RAIN_HEADER} is missing from origin/main"
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


def leftover_cpg_hud_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_CPG_HUD_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_CPG_HUD_HEADER} is missing from origin/main"
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
        STOP_BEFORE_STORM_RAIN_KIT,
        STOP_BEFORE_STORM_RAIN_KIND,
        STOP_BEFORE_STORM_RAIN_NS,
        STOP_BEFORE_DAY_KIT,
        STOP_BEFORE_NIGHT_KIT,
        STOP_BEFORE_LOADOUT,
        STOP_BEFORE_CONTACT_MARK,
        STOP_BEFORE_HUD_SNAPSHOT,
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
        LEFTOVER_STORM_RAIN_KIT,
        LEFTOVER_STORM_RAIN_KIND,
        LEFTOVER_DAY_KIT,
        LEFTOVER_NIGHT_KIT,
        LEFTOVER_LOADOUT_SPEC,
        LEFTOVER_CONTACT_MARK,
        LEFTOVER_HUD_SNAPSHOT,
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
    if STOP_BEFORE_STORM_RAIN_KIT in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes leftover "
            f"{STOP_BEFORE_STORM_RAIN_KIT}"
        )
    for harbor in leftover_harbor_beat_tokens():
        if harbor in section:
            raise AssertionError(
                f"{STRUCT_NAME} parse window includes leftover "
                f"Harbor {harbor}"
            )
    for helper in namespace_helper_tokens():
        if helper in section:
            raise AssertionError(
                f"{STRUCT_NAME} parse window includes leftover "
                f"namespace helper {helper}"
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
            r"\s*const TCHAR\* Title\b", compact[index:]
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for const TCHAR* Title is missing from "
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
        r"UPROPERTY\([^)]*\)\s*const TCHAR\* Title\b",
        compact,
    ):
        raise AssertionError(
            "UPROPERTY wrap on const TCHAR* Title is not the locked "
            f"decl for plain C++ struct {STRUCT_NAME}"
        )
    if "UPROPERTY" in section and has_identifier(section, "Title"):
        raise AssertionError(
            "UPROPERTY clone landed on Title; locked decl is "
            f"plain {LOCKED_DECL}"
        )
    for token in ("USTRUCT", "GENERATED_BODY"):
        if token in section and has_identifier(section, "Title"):
            raise AssertionError(
                f"{token} clone landed on Title; locked decl is "
                f"plain {LOCKED_DECL}"
            )


class CampaignMissionSpecTitleFieldDeclContractTests(unittest.TestCase):
    def test_campaign_mission_spec_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(STRUCT_NAME, header)
        self.assertIsNotNone(STRUCT_RE.search(header), header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(STRUCT_NAME, "FSkyguardCampaignMissionSpec")
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_STORM_RAIN_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DAY_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_NIGHT_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_CONTACT_MARK)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_HUD_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_APACHE_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_RADAR_NODE_CLASS)
        self.assertNotEqual(STRUCT_NAME, STOP_BEFORE_SORTIE)
        body = struct_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "Title"), section)
        self.assertNotIn("UPROPERTY", section)
        self.assertNotIn("GENERATED_BODY", section)
        self.assertNotIn("USTRUCT", section)
        self.assertIn(STOP_BEFORE_NAMESPACE, header)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, body)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_STORM_RAIN_KIT, section)
        self.assertNotIn(LEFTOVER_DAY_KIT, section)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, section)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)

    def test_locked_decl_is_plain_cpp_not_uproperty(self) -> None:
        self.assertEqual(LOCKED_DECL, 'const TCHAR* Title = TEXT("");')
        self.assertEqual(LOCKED_DECL, TARGET)
        self.assertTrue(LOCKED_DECL.startswith("const TCHAR* Title"))
        self.assertTrue(LOCKED_DECL.endswith(";"))
        self.assertIn("=", LOCKED_DECL)
        self.assertIn('TEXT("")', LOCKED_DECL)
        self.assertIn("Title", LOCKED_DECL)
        self.assertNotIn(SIBLING_WEATHER_LABEL, LOCKED_DECL)
        self.assertNotIn(SIBLING_BRIEF, LOCKED_DECL)
        self.assertNotIn(SIBLING_SUCCESS, LOCKED_DECL)
        self.assertNotIn(SIBLING_FAILURE, LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_THEATER, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_CAMPAIGN, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_THEATER)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_CAMPAIGN)
        self.assertNotEqual(LOCKED_DECL, CLONE_DAY_MISSION_ID)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LABEL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BRIEF)
        self.assertNotEqual(LOCKED_DECL, "FName WeatherIdentity;")
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BARE)

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
        self.assertIn("Title", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            struct_body(
                "struct FSkyguardUnrelatedCampaignMissionSpec\n{\n};\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_storm_rain_title_does_not_satisfy(self) -> None:
        leftover = leftover_storm_rain_header()
        self.assertIn(LEFTOVER_STORM_RAIN_KIT, leftover)
        self.assertIn(LOCKED_DECL, leftover)
        self.assertIn(STOP_BEFORE_STORM_RAIN_NS, leftover)
        with self.assertRaises(AssertionError) as raised:
            spec_section(leftover)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(HEADER_PATH, LEFTOVER_STORM_RAIN_HEADER)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_STORM_RAIN_KIT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_STORM_RAIN_TITLE)
        self.assertNotEqual(STOP_BEFORE_NAMESPACE, STOP_BEFORE_STORM_RAIN_NS)
        self.assertNotIn("StormRainBeatKit", HEADER_PATH)
        self.assertNotIn("storm_rain_beat_kit_title", THIS_SCRIPT)

    def test_leftover_kind_enum_does_not_satisfy(self) -> None:
        leftover = (
            f"enum class {LEFTOVER_STORM_RAIN_KIND} : uint8\n"
            "{\n"
            "\tApproach,\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(leftover)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_neighbors_do_not_satisfy(self) -> None:
        leftovers = (
            LEFTOVER_STORM_RAIN_KIT,
            LEFTOVER_DAY_KIT,
            LEFTOVER_NIGHT_KIT,
            LEFTOVER_LOADOUT_SPEC,
            LEFTOVER_CONTACT_MARK,
            LEFTOVER_HUD_SNAPSHOT,
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

    def test_does_not_claim_leftover_storm_rain_or_neighbors(self) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_STORM_RAIN_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_DAY_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_NIGHT_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_LOADOUT_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_CPG_HUD_HEADER)
        self.assertTrue(HEADER_PATH.endswith("SkyguardCampaignRoster.h"))
        self.assertNotIn("StormRainBeatKit", HEADER_PATH)
        self.assertNotIn("DaySortie", HEADER_PATH)
        self.assertNotIn("NightSortie", HEADER_PATH)
        self.assertNotIn("GunshipTypes", HEADER_PATH)
        self.assertNotIn("CpgHud", HEADER_PATH)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_STORM_RAIN_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DAY_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_NIGHT_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_CONTACT_MARK)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_HUD_SNAPSHOT)
        storm = leftover_storm_rain_header()
        self.assertIn(LEFTOVER_STORM_RAIN_KIT, storm)
        self.assertIn(LOCKED_DECL, storm)
        with self.assertRaises(AssertionError) as raised:
            spec_section(storm)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        day_header = leftover_day_kit_header()
        self.assertIn(LEFTOVER_DAY_KIT, day_header)
        self.assertIn(CLONE_DAY_MISSION_ID, day_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(day_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        night_header = leftover_night_kit_header()
        self.assertIn(LEFTOVER_NIGHT_KIT, night_header)
        self.assertIn("FName WeatherIdentity;", night_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(night_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        loadout_header = leftover_loadout_header()
        self.assertIn(LEFTOVER_LOADOUT_SPEC, loadout_header)
        self.assertIn(LEFTOVER_FLARE_COUNT, loadout_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(loadout_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        cpg_header = leftover_cpg_hud_header()
        self.assertIn(LEFTOVER_HUD_SNAPSHOT, cpg_header)
        self.assertIn(LEFTOVER_CONTACT_MARK, cpg_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(cpg_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_namespace_declaration_does_not_satisfy(self) -> None:
        mixed = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "};\n"
            f"{STOP_BEFORE_NAMESPACE}\n"
            "{\n"
            f"\tint32 {NS_NUM_MISSIONS}();\n"
            f"\tconst {STRUCT_NAME}& {NS_GET};\n"
            f"\t{LOCKED_DECL}\n"
            "}\n"
        )
        section = spec_section(mixed)
        self.assertFalse(has_identifier(section, "Title"), section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(NS_NUM_MISSIONS, section)
        self.assertNotIn(NS_GET, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Title", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_namespace_helpers_are_not_this_slot(self) -> None:
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
            self.assertNotIn(helper, LOCKED_DECL)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_CAMPAIGN_ROSTER_LOOKUP)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_CAMPAIGN_ROSTER_GET)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_CAMPAIGN_ROSTER_ID_AT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_CAMPAIGN_ROSTER_NUM)

    def test_missing_title_declaration_fails_closed(self) -> None:
        empty = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\tFName {SIBLING_MISSION_ID};\n"
            f"\t{TARGET_WRONG_BRIEF}\n"
            f"\t{TARGET_WRONG_LABEL}\n"
            f"\tFName {SIBLING_WEATHER_IDENTITY};\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Title", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_sibling_tchar_fields_do_not_satisfy_title(self) -> None:
        leftovers = (
            TARGET_WRONG_BRIEF,
            TARGET_WRONG_SUCCESS,
            TARGET_WRONG_FAILURE,
            TARGET_WRONG_LABEL,
        )
        for leftover_decl in leftovers:
            leftover = (
                f"struct {STRUCT_NAME}\n"
                "{\n"
                f"\t{leftover_decl}\n"
                "};\n"
            )
            section = spec_section(leftover)
            self.assertFalse(has_declaration(section, LOCKED_DECL), section)
            with self.assertRaises(AssertionError) as raised:
                require_declaration(section, LOCKED_DECL)
            self.assertIn("Title", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertNotEqual(LOCKED_DECL, leftover_decl)
        self.assertNotIn(SIBLING_WEATHER_LABEL, LOCKED_DECL)
        self.assertNotIn(SIBLING_BRIEF, LOCKED_DECL)
        self.assertNotIn(SIBLING_SUCCESS, LOCKED_DECL)
        self.assertNotIn(SIBLING_FAILURE, LOCKED_DECL)

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{CLONE_UPROPERTY_THEATER}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("Title", str(raised.exception))
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

    def test_initializer_must_be_empty_text(self) -> None:
        missing = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_BARE}\n"
            "};\n"
        )
        section = spec_section(missing)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Title", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        wrong_text = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_TEXT}\n"
            "};\n"
        )
        section = spec_section(wrong_text)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Title", str(raised.exception))
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn('const TCHAR* Title = TEXT("");', compact_origin)
        self.assertNotIn("Title = NAME_None", compact_origin)
        self.assertNotIn("Title = false", compact_origin)
        self.assertNotIn("Title = true", compact_origin)
        self.assertNotIn("Title = 0.f", compact_origin)
        self.assertNotIn("Title = 160.f", compact_origin)
        self.assertNotIn('Title = TEXT("Storm")', compact_origin)

    def test_title_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("const TCHAR* Title"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertIn("=", LOCKED_DECL)
        self.assertIn('TEXT("")', LOCKED_DECL)
        self.assertNotIn("= NAME_None", LOCKED_DECL)
        self.assertNotIn("= false", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertIn("const TCHAR*", LOCKED_DECL)
        self.assertNotIn("float ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("FSkyguardMissionResult", LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FALSE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TRUE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_EQ_NONE}\n", LOCKED_DECL)
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
            has_declaration(f"\t{TARGET_WRONG_TEXT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LABEL}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_BRIEF}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        self.assertIn("Title", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_LABEL}\n", LOCKED_DECL)
        self.assertIn("Title", str(raised.exception))

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tconst TCHAR* " + leftover_retired_primary_hits_field()
            + ' = TEXT("");\n'
        )
        leftover_guided = (
            "\tconst TCHAR* " + leftover_retired_guided_hits_field()
            + ' = TEXT("");\n'
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_EQ_NONE}\n",
            f"\t{TARGET_WRONG_FALSE}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_FLOAT}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            f"\t{TARGET_WRONG_BOOL}\n",
            f"\t{TARGET_WRONG_INT}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_TEXT}\n",
            f"\t{TARGET_WRONG_LABEL}\n",
            f"\t{TARGET_WRONG_BRIEF}\n",
            f"\t{TARGET_WRONG_SUCCESS}\n",
            f"\t{TARGET_WRONG_FAILURE}\n",
            leftover_primary,
            leftover_guided,
            f"\tFName {SIBLING_MISSION_ID};\n",
            f"\tFName {SIBLING_WEATHER_IDENTITY};\n",
            f"\tint32 {LEFTOVER_FLARE_COUNT} = 6;\n",
            "\tconst TCHAR* Titles = TEXT(\"\");\n",
            "\tint32 Title;\n",
            "\tbool Title;\n",
            "\tfloat Title = " + forty + ";\n",
            "\tfloat Title = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("Title", str(raised.exception))
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
            "\tUSTRUCT(BlueprintType)\n"
            "\tGENERATED_BODY()\n"
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
            "\tconst TCHAR*\n\tTitle = TEXT(\"\");\n",
            "\tconst TCHAR*   Title = TEXT(\"\");\n",
            "\tconst TCHAR*\tTitle = TEXT(\"\");\n",
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
                f"\t{TARGET_WRONG_LABEL}\n",
                LOCKED_DECL,
            )
        )

    def test_does_not_contract_sibling_spec_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for leftover_decl in leftover_sibling_locked_decls():
            self.assertNotEqual(LOCKED_DECL, leftover_decl)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        section = spec_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        self.assertTrue(has_identifier(section, SIBLING_WEATHER_LABEL))
        self.assertTrue(has_identifier(section, SIBLING_BRIEF))
        self.assertFalse(has_identifier(section, LEFTOVER_FLARE_COUNT))
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_does_not_parse_leftover_storm_rain_or_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        self.assertIn(STOP_BEFORE_NAMESPACE, header)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, leaked)
        self.assertNotIn(STOP_BEFORE_STORM_RAIN_KIT, header)
        self.assertNotIn(STOP_BEFORE_STORM_RAIN_KIND, header)
        self.assertNotIn(LEFTOVER_STORM_RAIN_KIT, header)
        self.assertNotIn(LEFTOVER_STORM_RAIN_KIND, header)
        self.assertNotIn(STOP_BEFORE_STORM_RAIN_NS, header)
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
        self.assertNotIn(STOP_BEFORE_CONTACT_MARK, header)
        self.assertNotIn(STOP_BEFORE_HUD_SNAPSHOT, header)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, header)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, header)
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
        self.assertNotIn(LEFTOVER_STORM_RAIN_KIT, section)
        self.assertNotIn(LEFTOVER_DAY_KIT, section)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, section)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, section)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            f"\tint32 {NS_NUM_MISSIONS}();\n"
            f"\tconst {STRUCT_NAME}& {NS_GET};\n"
            f"\tint32 {NS_INDEX_OF}(FName MissionId);\n"
            f"\tFName {NS_ID_AT}(int32 Index);\n"
            f"\tconst TCHAR* {NS_LOADOUT_LABEL}();\n"
            f"\tconst TCHAR* {NS_WEATHER_ENUM_LABEL}();\n"
            f"\tFName {SIBLING_MISSION_ID};\n"
            f"\tFName {SIBLING_WEATHER_IDENTITY};\n"
            f"\t{TARGET_WRONG_LABEL}\n"
            f"\t{TARGET_WRONG_BRIEF}\n"
            f"\tint32 {LEFTOVER_FLARE_COUNT} = 6;\n"
            f"\t{TARGET_WRONG_HEALTH}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("Title", str(raised.exception))

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

    def test_harbor_breaker_beats_are_not_this_spec(self) -> None:
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
        self.assertTrue(has_identifier(section, SIBLING_BEAT_SECONDS), section)
        forty = "40" + ".f"
        eighty = "80" + ".f"
        leftover_pair = forty + ", " + eighty
        self.assertNotIn(leftover_pair, section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for invented in INVENTED_FIELD_META:
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
        self.assertNotIn("SkyguardCampaignRoster.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardStormRainBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardDaySortieBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardNightSortieBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardCpgHud.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardRadarNode.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)
        self.assertNotIn("SkyguardHarborBeatCalls.h", HEADER_PATH)
        self.assertIn("SkyguardCampaignRoster.h", HEADER_PATH)

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
                "campaign-mission-spec Title field decl contract "
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
            "title_field_decl_contract.py"
        ))
        self.assertIn("campaign_mission_spec", Path(__file__).name)
        self.assertNotIn("storm_rain_beat_kit", Path(__file__).name)
        self.assertNotIn("SkyguardStormRainBeatKit.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardStormRainBeatKit.h", THIS_SCRIPT)
        self.assertIn(LEFTOVER_STORM_RAIN_TITLE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_LABELS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_FIELDS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_CAMPAIGN_ROSTER_LOOKUP, LOCKED_SCRIPTS)
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
            LEFTOVER_STORM_RAIN_TITLE,
            LEFTOVER_ANALOG_STORM_KIT_LABELS,
            LEFTOVER_ANALOG_STORM_KIT_FIELDS,
            LEFTOVER_ANALOG_STORM_KIT_DEFAULTS,
            LEFTOVER_ANALOG_STORM_KIT_BULK,
            LEFTOVER_ANALOG_CAMPAIGN_ROSTER_LOOKUP,
            LEFTOVER_ANALOG_CAMPAIGN_ROSTER_GET,
            LEFTOVER_ANALOG_CAMPAIGN_ROSTER_ID_AT,
            LEFTOVER_ANALOG_CAMPAIGN_ROSTER_NUM,
            LEFTOVER_ANALOG_CAMPAIGN_ROSTER_LOADOUT,
            LEFTOVER_ANALOG_CAMPAIGN_ROSTER_WEATHER,
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
        self.assertNotIn(LEFTOVER_STORM_RAIN_KIT, locked_only)
        self.assertNotIn(LEFTOVER_DAY_KIT, locked_only)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, locked_only)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, locked_only)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, locked_only)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, locked_only)
        self.assertNotIn(LEFTOVER_STORM_RAIN_KIND, locked_only)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, locked_only)
        self.assertNotIn(STOP_BEFORE_HARBOR_CALLS, locked_only)
        self.assertNotIn(SIBLING_WEATHER_LABEL, locked_only)
        self.assertNotIn(SIBLING_BRIEF, locked_only)
        for harbor in leftover_harbor_beat_tokens():
            self.assertNotIn(harbor, locked_only)
        for helper in namespace_helper_tokens():
            self.assertNotIn(helper, locked_only)
        for leftover in leftover_storm_rain_title_tokens():
            self.assertNotIn(leftover, locked_only)


if __name__ == "__main__":
    unittest.main()
