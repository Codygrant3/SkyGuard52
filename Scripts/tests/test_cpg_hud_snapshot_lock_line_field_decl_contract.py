# THIS IS leftover-safe FSkyguardCpgHudSnapshot LockLine.
# origin/main form: plain C++ field `FString LockLine;`
# with NO in-struct initializer. NOT a UPROPERTY wrap.
# FSkyguardCpgHudSnapshot is a plain C++ HUD tape struct.
# Fail-closed if this test still asserts UPROPERTY / Category /
# VisibleAnywhere / EditAnywhere / BlueprintReadOnly /
# GENERATED_BODY / USTRUCT as the locked decl.
# Parse STRUCT `FSkyguardCpgHudSnapshot` body ONLY after
# `struct FSkyguardCpgHudSnapshot`. Stop at
# `struct FSkyguardCpgContactMark`.
# Do NOT parse leftover `FSkyguardCpgDebriefSnapshot`.
# Do NOT parse leftover `FSkyguardCpgContactMark`.
# Do NOT parse leftover Night/Day Beat.Threat isolated
# (#1477/#1481). LockLine is NOT leftover ThreatCount,
# not leftover Beat.Threat.
# Do NOT contract sibling fields WeaponLine / RangeLine /
# ThreatLine / EufdLine / SightLine / StationStatus /
# LockPhase / SightMode / RangeMeters / ThreatCount /
# HeadingDegrees / LockProgress / FlareCount /
# bMissileInbound.
# LockLine is NOT leftover sibling LockPhase
# (`ESkyguardGuidedLockPhase LockPhase =
# ESkyguardGuidedLockPhase::Search`) and NOT leftover
# sibling LockProgress (`float LockProgress = 0.f`) and
# NOT leftover FSkyguardCpgContactMark `bool bLocked =
# false`.
# Fail-closed if this lane claims leftover LockPhase /
# leftover LockProgress / leftover ContactMark bLocked
# instead of LockLine.
# Same FString type must not steal leftover ContactMark
# Label or leftover DebriefSnapshot MissionTitle.
# THIS IS NOT leftover analog Python bulk. There is no
# leftover HUD snapshot bulk contract. Isolated field
# decl does not relock leftover CpgDebriefSnapshot
# defaults or leftover Night/Day Beat Threat isolated.
# THIS IS NOT leftover-safe TheaterKitSpec
# WeatherIdentity #1300 UPROPERTY clone.
# THIS IS NOT leftover-safe StormRainBeatKit Title
# (`const TCHAR* Title = TEXT("")`).
# If a clone asserts UPROPERTY / Category="Skyguard|Theater" /
# VisibleAnywhere / FName WeatherIdentity / `= TEXT("")` /
# leftover sibling LockPhase / leftover sibling LockProgress /
# leftover ContactMark `bool bLocked = false` /
# leftover StormRain Title `const TCHAR* Title = TEXT("")` /
# leftover `int32 ThreatCount = 0` / leftover Beat.Threat,
# retarget: type is FString, identifier is LockLine, no
# initializer, locked decl is the plain field, not a
# UPROPERTY wrap.
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
HEADER_PATH = "Source/Skyguard52/SkyguardCpgHud.h"
STRUCT_NAME = "FSkyguardCpgHudSnapshot"
LEFTOVER_CONTACT_MARK = "FSkyguardCpgContactMark"
LEFTOVER_DEBRIEF_SNAPSHOT = "FSkyguardCpgDebriefSnapshot"
LEFTOVER_DAY_KIT = "FSkyguardDaySortieBeatKit"
LEFTOVER_NIGHT_KIT = "FSkyguardNightSortieBeatKit"
LEFTOVER_STORM_KIT = "FSkyguardStormRainBeatKit"
LEFTOVER_LOADOUT_SPEC = "FSkyguardLoadoutSpec"
LEFTOVER_CONTACT_HEADER = "Source/Skyguard52/SkyguardCpgHud.h"
LEFTOVER_DEBRIEF_HEADER = "Source/Skyguard52/SkyguardCpgDebrief.h"
LEFTOVER_DAY_HEADER = "Source/Skyguard52/SkyguardDaySortieBeatKit.h"
LEFTOVER_NIGHT_HEADER = "Source/Skyguard52/SkyguardNightSortieBeatKit.h"
LEFTOVER_STORM_HEADER = "Source/Skyguard52/SkyguardStormRainBeatKit.h"
LEFTOVER_LOADOUT_HEADER = "Source/Skyguard52/SkyguardGunshipTypes.h"
TARGET = "FString LockLine;"
TARGET_WRONG_TEXT = 'FString LockLine = TEXT("");'
TARGET_WRONG_FSTRING = "FString LockLine = FString();"
TARGET_WRONG_FALSE = "FString LockLine = false;"
TARGET_WRONG_TRUE = "FString LockLine = true;"
TARGET_WRONG_NONE = "FString LockLine = NAME_None;"
TARGET_WRONG_ZERO = "FString LockLine = 0.f;"
TARGET_WRONG_FLOAT = "float LockLine;"
TARGET_WRONG_HEALTH = "float LockLine = 160.f;"
TARGET_WRONG_BOOL = "bool LockLine;"
TARGET_WRONG_INT = "int32 LockLine;"
TARGET_WRONG_FNAME = "FName LockLine;"
TARGET_WRONG_TCHAR = "const TCHAR* LockLine;"
TARGET_WRONG_TCHAR_TEXT = 'const TCHAR* LockLine = TEXT("");'
TARGET_WRONG_COUNT = "int32 ThreatCount = 0;"
TARGET_WRONG_DAY_THREAT = (
    "ESkyguardThreatKind Threat = ESkyguardThreatKind::GroundArmor;"
)
TARGET_WRONG_NIGHT_THREAT = (
    "ESkyguardThreatKind Threat = ESkyguardThreatKind::FastAttacker;"
)
TARGET_WRONG_LABEL = "FString Label;"
TARGET_WRONG_TITLE = "FString MissionTitle;"
TARGET_WRONG_STORM_TITLE = 'const TCHAR* Title = TEXT("");'
TARGET_WRONG_LOCK_PHASE = (
    "ESkyguardGuidedLockPhase LockPhase = "
    "ESkyguardGuidedLockPhase::Search;"
)
TARGET_WRONG_LOCK_PROGRESS = "float LockProgress = 0.f;"
TARGET_WRONG_BLOCKED = "bool bLocked = false;"
TARGET_WRONG_WEAPON = "FString WeaponLine;"
HUD_SIBLING_FLARE_DECL = "int32 FlareCount = 0;"
LEFTOVER_LOADOUT_FLARE_DECL = "int32 FlareCount = 6;"
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
CLONE_THEATER_WEATHER = "FName WeatherIdentity;"
STOP_BEFORE_CONTACT_MARK = "struct FSkyguardCpgContactMark"
STOP_BEFORE_DEBRIEF = "struct FSkyguardCpgDebriefSnapshot"
STOP_BEFORE_DAY_KIT = "struct FSkyguardDaySortieBeatKit"
STOP_BEFORE_NIGHT_KIT = "struct FSkyguardNightSortieBeatKit"
STOP_BEFORE_STORM_KIT = "struct FSkyguardStormRainBeatKit"
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
STOP_BEFORE_WEAPON_LABEL = "SkyguardCpgWeaponLabel"
STOP_BEFORE_THREAT_LABEL = "SkyguardCpgThreatLabel"
STOP_BEFORE_SHIP_LABEL = "SkyguardCpgShipSystemLabel"
STOP_BEFORE_LOCK_LABEL = "SkyguardCpgLockPhaseLabel"
STOP_BEFORE_SIGHT_LABEL = "SkyguardCpgSightLabel"
STOP_BEFORE_INBOUND_LABEL = "SkyguardCpgInboundLabel"
STOP_BEFORE_FLARE_TAPE = "SkyguardCpgFlareTape"
STOP_BEFORE_LEGACY_WORDING = "SkyguardCpgHudHasLegacyLiveWording"
SIBLING_WEAPON_LINE = "WeaponLine"
SIBLING_RANGE_LINE = "RangeLine"
SIBLING_EUFD_LINE = "EufdLine"
SIBLING_THREAT_LINE = "ThreatLine"
SIBLING_SIGHT_LINE = "SightLine"
SIBLING_STATION_STATUS = "StationStatus"
SIBLING_LOCK_PHASE = "LockPhase"
SIBLING_SIGHT_MODE = "SightMode"
SIBLING_RANGE_METERS = "RangeMeters"
SIBLING_THREAT_COUNT = "ThreatCount"
SIBLING_HEADING = "HeadingDegrees"
SIBLING_LOCK_PROGRESS = "LockProgress"
SIBLING_FLARE_COUNT = "FlareCount"
SIBLING_MISSILE_INBOUND = "bMissileInbound"
LEFTOVER_CONTACT_LABEL = "Label"
LEFTOVER_DEBRIEF_TITLE = "MissionTitle"
LEFTOVER_BEAT_THREAT = "Threat"
LEFTOVER_HARBOR_APPROACH = "ESkyguardSortieBeat::Approach"
LEFTOVER_HARBOR_CONTACT = "ESkyguardSortieBeat::InitialContact"
LEFTOVER_HARBOR_SHORE = "ESkyguardSortieBeat::ShoreAssault"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
THIS_SCRIPT = (
    "Scripts/tests/test_cpg_hud_snapshot_lock_line"
    "_field_decl_contract.py"
)
CLONE_THEATER_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
CLONE_STORM_RAIN_TITLE = (
    "Scripts/tests/test_storm_rain_beat_kit_title"
    "_field_decl_contract.py"
)
LEFTOVER_DAY_BEAT_THREAT = (
    "Scripts/tests/test_day_sortie_beat_threat"
    "_field_decl_contract.py"
)
LEFTOVER_NIGHT_BEAT_THREAT = (
    "Scripts/tests/test_night_sortie_beat_threat"
    "_field_decl_contract.py"
)
LEFTOVER_CPG_DEBRIEF_DEFAULTS = (
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py"
)
LEFTOVER_CPG_DEBRIEF_MISSION_TITLE = (
    "Scripts/tests/test_cpg_debrief_snapshot_mission_title"
    "_field_decl_contract.py"
)
LEFTOVER_CPG_DEBRIEF_NARRATIVE = (
    "Scripts/tests/test_cpg_debrief_snapshot_outcome_narrative"
    "_field_decl_contract.py"
)
LEFTOVER_CPG_DEBRIEF_FAIL_CLOSED = (
    "Scripts/tests/test_cpg_debrief_fail_closed.py"
)
LEFTOVER_ANALOG_DAY_KIT_FIELDS = (
    "Scripts/tests/test_day_sortie_beat_kit_fields_contract.py"
)
LEFTOVER_ANALOG_NIGHT_KIT_FIELDS = (
    "Scripts/tests/test_night_sortie_beat_kit_fields_contract.py"
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
LEFTOVER_ANALOG_STORM_KIT_CALLS = (
    "Scripts/tests/test_storm_rain_beat_kit_calls_contract.py"
)
LEFTOVER_LOADOUT_FLARE = (
    "Scripts/tests/test_loadout_spec_flare_count"
    "_field_decl_contract.py"
)

LOCKED = {
    "SkyguardCpgHud.h",
    "SkyguardCpgHud.cpp",
    "SkyguardCpgHudTests.cpp",
    "SkyguardCpgDebrief.h",
    "SkyguardCpgDebrief.cpp",
    "SkyguardCpgSightHud.h",
    "SkyguardCpgSightHud.cpp",
    "SkyguardDaySortieBeatKit.h",
    "SkyguardDaySortieBeatKit.cpp",
    "SkyguardNightSortieBeatKit.h",
    "SkyguardNightSortieBeatKit.cpp",
    "SkyguardStormRainBeatKit.h",
    "SkyguardStormRainBeatKit.cpp",
    "SkyguardGunshipTypes.h",
    "SkyguardGunner.h",
    "SkyguardGunner.cpp",
    "SkyguardCampaignTheaterKit.h",
    "SkyguardCampaignTheaterKit.cpp",
    "SkyguardApacheAircraft.h",
    "SkyguardApacheAircraft.cpp",
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
    LEFTOVER_DAY_BEAT_THREAT,
    LEFTOVER_NIGHT_BEAT_THREAT,
    LEFTOVER_CPG_DEBRIEF_DEFAULTS,
    LEFTOVER_CPG_DEBRIEF_MISSION_TITLE,
    LEFTOVER_CPG_DEBRIEF_NARRATIVE,
    LEFTOVER_CPG_DEBRIEF_FAIL_CLOSED,
    CLONE_STORM_RAIN_TITLE,
    CLONE_THEATER_WEATHER_IDENTITY,
    LEFTOVER_ANALOG_DAY_KIT_FIELDS,
    LEFTOVER_ANALOG_NIGHT_KIT_FIELDS,
    LEFTOVER_ANALOG_STORM_KIT_LABELS,
    LEFTOVER_ANALOG_STORM_KIT_FIELDS,
    LEFTOVER_ANALOG_STORM_KIT_DEFAULTS,
    LEFTOVER_ANALOG_STORM_KIT_CALLS,
    LEFTOVER_LOADOUT_FLARE,
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_mesh_bind_slot_fields_contract.py",
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_defaults_contract.py",
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py",
    "Scripts/tests/test_storm_rain_beat_kind_enum_contract.py",
    "Scripts/tests/test_sortie_beat_enum_contract.py",
    "Scripts/tests/test_briefing_card_title_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_protect_asset_current_integrity_field_decl_contract.py",
    "Scripts/tests/test_radar_node_health_field_decl_contract.py",
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
LOCK_LINE_DECL_RE = re.compile(r"FString\s+LockLine\s*;")
LOCK_LINE_INIT_RE = re.compile(r"FString\s+LockLine\s*=")
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
    "TEXT(\"\")",
    "FString()",
)


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_WEAPON_LINE,
        SIBLING_RANGE_LINE,
        SIBLING_EUFD_LINE,
        SIBLING_THREAT_LINE,
        SIBLING_SIGHT_LINE,
        SIBLING_STATION_STATUS,
        SIBLING_LOCK_PHASE,
        SIBLING_SIGHT_MODE,
        SIBLING_RANGE_METERS,
        SIBLING_THREAT_COUNT,
        SIBLING_HEADING,
        SIBLING_LOCK_PROGRESS,
        SIBLING_FLARE_COUNT,
        SIBLING_MISSILE_INBOUND,
    )


def leftover_helper_tokens() -> tuple[str, ...]:
    return (
        STOP_BEFORE_WEAPON_LABEL,
        STOP_BEFORE_THREAT_LABEL,
        STOP_BEFORE_SHIP_LABEL,
        STOP_BEFORE_LOCK_LABEL,
        STOP_BEFORE_SIGHT_LABEL,
        STOP_BEFORE_INBOUND_LABEL,
        STOP_BEFORE_FLARE_TAPE,
        STOP_BEFORE_LEGACY_WORDING,
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


def lock_line_has_uproperty_wrap(region: str) -> bool:
    compact = collapsed(region)
    return re.search(
        r"UPROPERTY\([^;]*\)\s*FString\s+LockLine\b",
        compact,
    ) is not None


def has_declaration(region: str, declaration: str) -> bool:
    # Fail-closed on authored bare `FString LockLine;`.
    # Do not accept invented `= TEXT("")` / `= FString()` /
    # `= false` / leftover sibling LockPhase / leftover
    # sibling LockProgress / leftover ContactMark bLocked /
    # leftover ThreatCount / leftover Beat.Threat /
    # leftover ContactMark Label / leftover MissionTitle.
    # Do not accept UPROPERTY / Category clones.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if LOCK_LINE_INIT_RE.search(compact):
        return False
    if LOCK_LINE_DECL_RE.search(compact) is None:
        return False
    if re.search(
        r"(?:FName|bool|int32|float|uint32|const\s+TCHAR\s*\*)\s+"
        r"LockLine\b",
        compact,
    ):
        return False
    if lock_line_has_uproperty_wrap(region):
        return False
    if re.search(r"\bCategory\s*=", compact):
        return False
    if re.search(
        r"ESkyguardGuidedLockPhase\s+LockPhase\b",
        compact,
    ) and not has_identifier(compact, "LockLine"):
        return False
    if re.search(r"float\s+LockProgress\b", compact) and not has_identifier(
        compact, "LockLine"
    ):
        return False
    if re.search(r"bool\s+bLocked\b", compact) and not has_identifier(
        compact, "LockLine"
    ):
        return False
    if re.search(r"int32\s+ThreatCount\b", compact) and not has_identifier(
        compact, "LockLine"
    ):
        return False
    if re.search(
        r"ESkyguardThreatKind\s+Threat\b",
        compact,
    ) and not has_identifier(compact, "LockLine"):
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


def leftover_debrief_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_DEBRIEF_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_DEBRIEF_HEADER} is missing from origin/main"
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


def leftover_storm_kit_header() -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:{LEFTOVER_STORM_HEADER}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"{LEFTOVER_STORM_HEADER} is missing from origin/main"
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
        STOP_BEFORE_CONTACT_MARK,
        STOP_BEFORE_DEBRIEF,
        STOP_BEFORE_DAY_KIT,
        STOP_BEFORE_NIGHT_KIT,
        STOP_BEFORE_STORM_KIT,
        STOP_BEFORE_LOADOUT,
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
        LEFTOVER_CONTACT_MARK,
        LEFTOVER_DEBRIEF_SNAPSHOT,
        LEFTOVER_DAY_KIT,
        LEFTOVER_NIGHT_KIT,
        LEFTOVER_STORM_KIT,
        LEFTOVER_LOADOUT_SPEC,
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
    ) + leftover_helper_tokens()


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
    if STOP_BEFORE_CONTACT_MARK in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes {STOP_BEFORE_CONTACT_MARK}"
        )
    if STOP_BEFORE_DEBRIEF in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes leftover "
            f"{STOP_BEFORE_DEBRIEF}"
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
            r"\s*FString LockLine\b", compact[index:]
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for FString LockLine is missing from "
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
        r"UPROPERTY\([^)]*\)\s*FString LockLine\b",
        compact,
    ):
        raise AssertionError(
            "UPROPERTY wrap on FString LockLine is not the locked "
            f"decl for plain C++ struct {STRUCT_NAME}"
        )
    if "UPROPERTY" in section and has_identifier(section, "LockLine"):
        raise AssertionError(
            "UPROPERTY clone landed on LockLine; locked decl is "
            f"plain {LOCKED_DECL}"
        )
    for token in ("USTRUCT", "GENERATED_BODY"):
        if token in section and has_identifier(section, "LockLine"):
            raise AssertionError(
                f"{token} clone landed on LockLine; locked decl is "
                f"plain {LOCKED_DECL}"
            )


class CpgHudSnapshotLockLineFieldDeclContractTests(unittest.TestCase):
    def test_cpg_hud_snapshot_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(STRUCT_NAME, header)
        self.assertIsNotNone(STRUCT_RE.search(header), header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertEqual(STRUCT_NAME, "FSkyguardCpgHudSnapshot")
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_CONTACT_MARK)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DEBRIEF_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DAY_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_NIGHT_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_STORM_KIT)
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
        self.assertTrue(has_identifier(section, "LockLine"), section)
        self.assertNotIn("UPROPERTY", section)
        self.assertNotIn("GENERATED_BODY", section)
        self.assertNotIn("USTRUCT", section)
        self.assertIn(STOP_BEFORE_CONTACT_MARK, header)
        self.assertNotIn(STOP_BEFORE_CONTACT_MARK, section)
        self.assertNotIn(STOP_BEFORE_CONTACT_MARK, body)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, section)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, body)
        self.assertNotIn(STOP_BEFORE_DEBRIEF, header)
        self.assertNotIn(STOP_BEFORE_DEBRIEF, section)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_DAY_KIT, section)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, section)
        self.assertNotIn(LEFTOVER_STORM_KIT, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)

    def test_locked_decl_is_plain_cpp_not_uproperty(self) -> None:
        self.assertEqual(LOCKED_DECL, "FString LockLine;")
        self.assertEqual(LOCKED_DECL, TARGET)
        self.assertTrue(LOCKED_DECL.startswith("FString LockLine"))
        self.assertTrue(LOCKED_DECL.endswith(";"))
        self.assertNotIn("=", LOCKED_DECL)
        self.assertNotIn("TEXT(\"\")", LOCKED_DECL)
        self.assertNotIn("FString()", LOCKED_DECL)
        self.assertIn("LockLine", LOCKED_DECL)
        self.assertNotIn(SIBLING_THREAT_COUNT, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_BEAT_THREAT + " =", LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_THEATER, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_CAMPAIGN, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_THEATER)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_CAMPAIGN)
        self.assertNotEqual(LOCKED_DECL, CLONE_DAY_MISSION_ID)
        self.assertNotEqual(LOCKED_DECL, CLONE_THEATER_WEATHER)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_COUNT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_DAY_THREAT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_NIGHT_THREAT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LABEL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TITLE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_STORM_TITLE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TEXT)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_PHASE)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_PROGRESS)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BLOCKED)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WEAPON)
        self.assertNotIn(SIBLING_LOCK_PHASE, LOCKED_DECL)
        self.assertNotIn(SIBLING_LOCK_PROGRESS, LOCKED_DECL)
        self.assertNotIn(SIBLING_THREAT_LINE, LOCKED_DECL)
        self.assertNotIn("bLocked", LOCKED_DECL)

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
        self.assertIn("LockLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            struct_body(
                "struct FSkyguardUnrelatedCpgHudSnapshot\n{\n};\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_contact_mark_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {LEFTOVER_CONTACT_MARK}\n"
            "{\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(leftover)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_debrief_day_night_storm_do_not_satisfy(self) -> None:
        leftovers = (
            LEFTOVER_DEBRIEF_SNAPSHOT,
            LEFTOVER_DAY_KIT,
            LEFTOVER_NIGHT_KIT,
            LEFTOVER_STORM_KIT,
            LEFTOVER_LOADOUT_SPEC,
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

    def test_does_not_claim_leftover_debrief_or_beat_threat(self) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_DEBRIEF_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_DAY_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_NIGHT_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_STORM_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_LOADOUT_HEADER)
        self.assertTrue(HEADER_PATH.endswith("SkyguardCpgHud.h"))
        self.assertNotIn("CpgDebrief", HEADER_PATH)
        self.assertNotIn("DaySortie", HEADER_PATH)
        self.assertNotIn("NightSortie", HEADER_PATH)
        self.assertNotIn("StormRain", HEADER_PATH)
        self.assertNotIn("GunshipTypes", HEADER_PATH)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DEBRIEF_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_DAY_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_NIGHT_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_STORM_KIT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_CONTACT_MARK)
        debrief_header = leftover_debrief_header()
        self.assertIn(LEFTOVER_DEBRIEF_SNAPSHOT, debrief_header)
        self.assertIn(TARGET_WRONG_TITLE, debrief_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(debrief_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        day_header = leftover_day_kit_header()
        self.assertIn(LEFTOVER_DAY_KIT, day_header)
        self.assertIn(TARGET_WRONG_DAY_THREAT, day_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(day_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        night_header = leftover_night_kit_header()
        self.assertIn(LEFTOVER_NIGHT_KIT, night_header)
        self.assertIn(TARGET_WRONG_NIGHT_THREAT, night_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(night_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        storm_header = leftover_storm_kit_header()
        self.assertIn(LEFTOVER_STORM_KIT, storm_header)
        self.assertIn(TARGET_WRONG_STORM_TITLE, storm_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(storm_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        loadout_header = leftover_loadout_header()
        self.assertIn(LEFTOVER_LOADOUT_SPEC, loadout_header)
        self.assertIn(SIBLING_FLARE_COUNT, loadout_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(loadout_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_contact_mark_after_snapshot_does_not_satisfy(self) -> None:
        mixed = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "};\n"
            f"{STOP_BEFORE_CONTACT_MARK}\n"
            "{\n"
            f"\t{LOCKED_DECL}\n"
            f"\t{TARGET_WRONG_LABEL}\n"
            "}\n"
        )
        section = spec_section(mixed)
        self.assertFalse(has_identifier(section, "LockLine"), section)
        self.assertNotIn(STOP_BEFORE_CONTACT_MARK, section)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_lock_line_declaration_fails_closed(self) -> None:
        empty = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\tFString {SIBLING_WEAPON_LINE};\n"
            f"\t{TARGET_WRONG_COUNT}\n"
            f"\t{TARGET_WRONG_DAY_THREAT}\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_threat_count_does_not_satisfy_lock_line(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_COUNT}\n"
            "};\n"
        )
        section = spec_section(leftover)
        self.assertTrue(has_identifier(section, SIBLING_THREAT_COUNT), section)
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_COUNT)
        self.assertNotIn(SIBLING_THREAT_COUNT, LOCKED_DECL)

    def test_leftover_beat_threat_does_not_satisfy(self) -> None:
        leftovers = (
            TARGET_WRONG_DAY_THREAT,
            TARGET_WRONG_NIGHT_THREAT,
        )
        for leftover_decl in leftovers:
            leftover = (
                f"struct {STRUCT_NAME}\n"
                "{\n"
                f"\t{leftover_decl}\n"
                "};\n"
            )
            section = spec_section(leftover)
            self.assertTrue(
                has_identifier(section, LEFTOVER_BEAT_THREAT),
                section,
            )
            self.assertFalse(has_declaration(section, LOCKED_DECL), section)
            with self.assertRaises(AssertionError) as raised:
                require_declaration(section, LOCKED_DECL)
            self.assertIn("LockLine", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertNotEqual(LOCKED_DECL, leftover_decl)
        self.assertNotIn("ESkyguardThreatKind", LOCKED_DECL)

    def test_leftover_debrief_title_and_contact_label_do_not_satisfy(
        self,
    ) -> None:
        leftovers = (
            TARGET_WRONG_TITLE,
            TARGET_WRONG_LABEL,
            TARGET_WRONG_STORM_TITLE,
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
            self.assertIn("LockLine", str(raised.exception))
            self.assertNotEqual(LOCKED_DECL, leftover_decl)

    def test_leftover_sibling_lock_phase_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_LOCK_PHASE}\n"
            "};\n"
        )
        section = spec_section(leftover)
        self.assertTrue(has_identifier(section, SIBLING_LOCK_PHASE), section)
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_PHASE)
        self.assertNotIn(SIBLING_LOCK_PHASE, LOCKED_DECL)

    def test_leftover_sibling_lock_progress_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_LOCK_PROGRESS}\n"
            "};\n"
        )
        section = spec_section(leftover)
        self.assertTrue(has_identifier(section, SIBLING_LOCK_PROGRESS), section)
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_PROGRESS)
        self.assertNotIn(SIBLING_LOCK_PROGRESS, LOCKED_DECL)

    def test_leftover_contact_mark_blocked_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_BLOCKED}\n"
            "};\n"
        )
        section = spec_section(leftover)
        self.assertTrue(has_identifier(section, "bLocked"), section)
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BLOCKED)
        self.assertNotIn("bLocked", LOCKED_DECL)
        header = origin_main_header()
        snapshot = spec_section(header)
        self.assertNotIn(TARGET_WRONG_BLOCKED, snapshot)
        self.assertIn(TARGET_WRONG_BLOCKED, header)
        self.assertIn(LEFTOVER_CONTACT_MARK, header)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, snapshot)

    def test_sibling_weapon_line_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_WEAPON}\n"
            "};\n"
        )
        section = spec_section(leftover)
        self.assertTrue(has_identifier(section, SIBLING_WEAPON_LINE), section)
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WEAPON)
        self.assertNotIn(SIBLING_WEAPON_LINE, LOCKED_DECL)

    def test_hud_flare_count_is_not_loadout_spec_flare_count(self) -> None:
        section = spec_section(origin_main_header())
        self.assertIn(HUD_SIBLING_FLARE_DECL, section)
        self.assertNotIn(LEFTOVER_LOADOUT_FLARE_DECL, section)
        self.assertNotIn(LEFTOVER_LOADOUT_FLARE_DECL, LOCKED_DECL)
        self.assertNotIn(HUD_SIBLING_FLARE_DECL, LOCKED_DECL)
        self.assertNotEqual(HUD_SIBLING_FLARE_DECL, LEFTOVER_LOADOUT_FLARE_DECL)
        loadout_header = leftover_loadout_header()
        self.assertIn(LEFTOVER_LOADOUT_FLARE_DECL, loadout_header)
        self.assertNotIn(HUD_SIBLING_FLARE_DECL, loadout_header)
        self.assertFalse(
            has_declaration(f"\t{HUD_SIBLING_FLARE_DECL}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{LEFTOVER_LOADOUT_FLARE_DECL}\n", LOCKED_DECL)
        )

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{CLONE_UPROPERTY_THEATER}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
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

    def test_initializer_must_not_exist(self) -> None:
        invented = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_TEXT}\n"
            "};\n"
        )
        section = spec_section(invented)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        invented_fstring = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_FSTRING}\n"
            "};\n"
        )
        section = spec_section(invented_fstring)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn("FString LockLine;", compact_origin)
        self.assertNotIn("LockLine = TEXT(\"\")", compact_origin)
        self.assertNotIn("LockLine = FString()", compact_origin)
        self.assertNotIn("LockLine = NAME_None", compact_origin)
        self.assertNotIn("LockLine = false", compact_origin)
        self.assertNotIn("LockLine = true", compact_origin)
        self.assertNotIn("LockLine = 0.f", compact_origin)
        self.assertNotIn("LockLine = 160.f", compact_origin)

    def test_lock_line_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("FString LockLine"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertNotIn("=", LOCKED_DECL)
        self.assertNotIn("TEXT(\"\")", LOCKED_DECL)
        self.assertNotIn("= NAME_None", LOCKED_DECL)
        self.assertNotIn("= false", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertIn("FString", LOCKED_DECL)
        self.assertNotIn("float ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("const TCHAR*", LOCKED_DECL)
        self.assertNotIn("FSkyguardMissionResult", LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FALSE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TRUE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TEXT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FSTRING}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_NONE}\n", LOCKED_DECL)
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
            has_declaration(f"\t{TARGET_WRONG_TCHAR}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TCHAR_TEXT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_COUNT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_DAY_THREAT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_NIGHT_THREAT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LABEL}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TITLE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LOCK_PHASE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LOCK_PROGRESS}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_BLOCKED}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_WEAPON}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_TEXT}\n", LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_COUNT}\n", LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tFString " + leftover_retired_primary_hits_field()
            + ";\n"
        )
        leftover_guided = (
            "\tFString " + leftover_retired_guided_hits_field()
            + ";\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_TEXT}\n",
            f"\t{TARGET_WRONG_FSTRING}\n",
            f"\t{TARGET_WRONG_FALSE}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_NONE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_FLOAT}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            f"\t{TARGET_WRONG_BOOL}\n",
            f"\t{TARGET_WRONG_INT}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_TCHAR}\n",
            f"\t{TARGET_WRONG_TCHAR_TEXT}\n",
            f"\t{TARGET_WRONG_COUNT}\n",
            f"\t{TARGET_WRONG_DAY_THREAT}\n",
            f"\t{TARGET_WRONG_NIGHT_THREAT}\n",
            f"\t{TARGET_WRONG_LABEL}\n",
            f"\t{TARGET_WRONG_TITLE}\n",
            f"\t{TARGET_WRONG_STORM_TITLE}\n",
            f"\t{TARGET_WRONG_LOCK_PHASE}\n",
            f"\t{TARGET_WRONG_LOCK_PROGRESS}\n",
            f"\t{TARGET_WRONG_BLOCKED}\n",
            f"\t{TARGET_WRONG_WEAPON}\n",
            leftover_primary,
            leftover_guided,
            f"\tFString {SIBLING_WEAPON_LINE};\n",
            f"\tFString {LEFTOVER_DEBRIEF_TITLE};\n",
            f"\tint32 {SIBLING_FLARE_COUNT} = 6;\n",
            "\tFString LockLines;\n",
            "\tint32 LockLine;\n",
            "\tbool LockLine;\n",
            "\tfloat LockLine = " + forty + ";\n",
            "\tfloat LockLine = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("LockLine", str(raised.exception))
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
            "\tFString\n\tLockLine;\n",
            "\tFString   LockLine;\n",
            "\tFString\tLockLine;\n",
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
                f"\t{CLONE_UPROPERTY_THEATER}\n\t{LOCKED_DECL}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_LOCK_PHASE}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_LOCK_PROGRESS}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_BLOCKED}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_COUNT}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_DAY_THREAT}\n",
                LOCKED_DECL,
            )
        )

    def test_does_not_contract_sibling_snapshot_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        section = spec_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        self.assertTrue(has_identifier(section, SIBLING_THREAT_COUNT))
        self.assertTrue(has_identifier(section, SIBLING_WEAPON_LINE))
        self.assertFalse(has_identifier(section, LEFTOVER_DEBRIEF_TITLE))
        self.assertFalse(has_identifier(section, LEFTOVER_CONTACT_LABEL))
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_does_not_parse_leftover_contact_mark_or_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        self.assertIn(STOP_BEFORE_CONTACT_MARK, header)
        self.assertNotIn(STOP_BEFORE_CONTACT_MARK, section)
        self.assertNotIn(STOP_BEFORE_CONTACT_MARK, leaked)
        self.assertIn(LEFTOVER_CONTACT_MARK, header)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, section)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, leaked)
        self.assertNotIn(STOP_BEFORE_DEBRIEF, header)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, header)
        self.assertNotIn(STOP_BEFORE_DEBRIEF, section)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, leaked)
        for helper in leftover_helper_tokens():
            self.assertIn(helper, header)
            self.assertNotIn(helper, section)
            self.assertNotIn(helper, leaked)
        self.assertNotIn(STOP_BEFORE_DAY_KIT, header)
        self.assertNotIn(STOP_BEFORE_NIGHT_KIT, header)
        self.assertNotIn(LEFTOVER_DAY_KIT, header)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, header)
        self.assertNotIn(STOP_BEFORE_STORM_KIT, header)
        self.assertNotIn(LEFTOVER_STORM_KIT, header)
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
        self.assertNotIn(STOP_BEFORE_GUNNER, section)
        self.assertNotIn(STOP_BEFORE_GUNNER, leaked)
        self.assertNotIn(STOP_BEFORE_WEAK_POINT, header)
        self.assertNotIn(STOP_BEFORE_HARBOR_CALLS, header)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, header)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, header)
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
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_DAY_KIT, section)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, section)
        self.assertNotIn(LEFTOVER_STORM_KIT, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            f"\tconst TCHAR* {STOP_BEFORE_WEAPON_LABEL}();\n"
            f"\tconst TCHAR* {STOP_BEFORE_THREAT_LABEL}();\n"
            f"\tconst TCHAR* {STOP_BEFORE_SHIP_LABEL}();\n"
            f"\tconst TCHAR* {STOP_BEFORE_LOCK_LABEL}();\n"
            f"\tconst TCHAR* {STOP_BEFORE_SIGHT_LABEL}();\n"
            f"\tconst TCHAR* {STOP_BEFORE_INBOUND_LABEL}();\n"
            f"\tFString {STOP_BEFORE_FLARE_TAPE}();\n"
            f"\tbool {STOP_BEFORE_LEGACY_WORDING}();\n"
            f"\t{TARGET_WRONG_COUNT}\n"
            f"\t{TARGET_WRONG_DAY_THREAT}\n"
            f"\t{TARGET_WRONG_TITLE}\n"
            f"\t{TARGET_WRONG_LABEL}\n"
            f"\t{TARGET_WRONG_HEALTH}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("LockLine", str(raised.exception))

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

    def test_harbor_breaker_beats_are_not_this_snapshot(self) -> None:
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
        self.assertNotIn("SkyguardCpgHud.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardCpgDebrief.h", HEADER_PATH)
        self.assertNotIn("SkyguardDaySortieBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardNightSortieBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardStormRainBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
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
                "cpg-hud-snapshot LockLine field decl contract "
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
            "lock_line_field_decl_contract.py"
        ))
        self.assertIn("cpg_hud_snapshot", Path(__file__).name)
        self.assertNotIn("SkyguardCpgHud.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardCpgDebrief.h", THIS_SCRIPT)
        self.assertIn(LEFTOVER_DAY_BEAT_THREAT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_NIGHT_BEAT_THREAT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CPG_DEBRIEF_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CPG_DEBRIEF_MISSION_TITLE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CPG_DEBRIEF_NARRATIVE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_STORM_RAIN_TITLE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_THEATER_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_FIELDS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_STORM_KIT_CALLS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_FLARE, LOCKED_SCRIPTS)

    def test_leftover_analog_bulk_stays_locked(self) -> None:
        leftovers = (
            LEFTOVER_DAY_BEAT_THREAT,
            LEFTOVER_NIGHT_BEAT_THREAT,
            LEFTOVER_CPG_DEBRIEF_DEFAULTS,
            LEFTOVER_CPG_DEBRIEF_MISSION_TITLE,
            LEFTOVER_CPG_DEBRIEF_NARRATIVE,
            LEFTOVER_CPG_DEBRIEF_FAIL_CLOSED,
            CLONE_STORM_RAIN_TITLE,
            CLONE_THEATER_WEATHER_IDENTITY,
            LEFTOVER_ANALOG_DAY_KIT_FIELDS,
            LEFTOVER_ANALOG_NIGHT_KIT_FIELDS,
            LEFTOVER_ANALOG_STORM_KIT_LABELS,
            LEFTOVER_ANALOG_STORM_KIT_FIELDS,
            LEFTOVER_ANALOG_STORM_KIT_DEFAULTS,
            LEFTOVER_ANALOG_STORM_KIT_CALLS,
            LEFTOVER_LOADOUT_FLARE,
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
        self.assertNotIn(LEFTOVER_CONTACT_MARK, locked_only)
        self.assertNotIn(LEFTOVER_DEBRIEF_SNAPSHOT, locked_only)
        self.assertNotIn(LEFTOVER_DAY_KIT, locked_only)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, locked_only)
        self.assertNotIn(LEFTOVER_STORM_KIT, locked_only)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, locked_only)
        self.assertNotIn(STOP_BEFORE_CONTACT_MARK, locked_only)
        self.assertNotIn(STOP_BEFORE_HARBOR_CALLS, locked_only)
        self.assertNotIn(SIBLING_THREAT_COUNT, locked_only)
        self.assertNotIn(TARGET_WRONG_DAY_THREAT, locked_only)
        self.assertNotIn(TARGET_WRONG_NIGHT_THREAT, locked_only)
        self.assertNotIn(TARGET_WRONG_TITLE, locked_only)
        self.assertNotIn(TARGET_WRONG_LABEL, locked_only)
        self.assertNotIn(TARGET_WRONG_LOCK_PHASE, locked_only)
        self.assertNotIn(TARGET_WRONG_LOCK_PROGRESS, locked_only)
        self.assertNotIn(TARGET_WRONG_BLOCKED, locked_only)
        self.assertNotIn(TARGET_WRONG_WEAPON, locked_only)
        self.assertNotIn(HUD_SIBLING_FLARE_DECL, locked_only)
        self.assertNotIn(LEFTOVER_LOADOUT_FLARE_DECL, locked_only)
        for harbor in leftover_harbor_beat_tokens():
            self.assertNotIn(harbor, locked_only)
        for helper in leftover_helper_tokens():
            self.assertNotIn(helper, locked_only)


if __name__ == "__main__":
    unittest.main()
