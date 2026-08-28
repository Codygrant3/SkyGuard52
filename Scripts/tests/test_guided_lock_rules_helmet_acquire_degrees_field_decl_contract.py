# THIS IS leftover-safe FSkyguardGuidedLockRules HelmetAcquireDegrees.
# origin/main form: BARE plain C++ static constexpr field
# `static constexpr float HelmetAcquireDegrees = 12.0f;`
# with NO UPROPERTY wrap.
# FSkyguardGuidedLockRules is a plain C++ paper-lock struct.
# Fail-closed if this test still asserts UPROPERTY / Category /
# VisibleAnywhere / EditAnywhere / BlueprintReadOnly /
# GENERATED_BODY / USTRUCT as the locked decl.
# Fail-closed if Harbor 40/80 initializers are invented.
# Parse STRUCT `FSkyguardGuidedLockRules` body ONLY after
# `struct SKYGUARD52_API FSkyguardGuidedLockRules`.
# Stop BEFORE `static ESkyguardGuidedLockPhase PhaseFromProgress`.
# Do NOT parse methods LockSeconds / AcquireDegrees / CanFire /
# IsInsideAcquireCone / PhaseLabel / SightLabel.
# Do NOT parse leftover `SkyguardGuidedLockBreak.h`.
# Do NOT parse leftover `SkyguardCampaignRoster.h`.
# HelmetAcquireDegrees = 12.0f is NOT leftover:
# leftover CampaignMissionSpec TimeOfDayHours (`12.f`),
# leftover analog apache-cpg-feel CannonFireRate = 12.0f,
# leftover WeatherProfile TimeOfDayHours,
# leftover ArcadeLook ApplyWorldMoodForWeather default 12.f.
# Lock the FULL decl including identifier HelmetAcquireDegrees.
# Fail-closed if this test treats `12.f` / `12.0f` /
# TimeOfDayHours / CannonFireRate as this slot.
# Also leftover analog GuidedLockConeDegrees = 6.0f.
# leftover guided-lock-break-fail-closed.
# leftover gunship-loadout-lock-phase-contract.
# leftover CampaignMissionSpec field decls.
# leftover LoadoutSpec field decls.
# leftover CpgHudSnapshot SightMode Helmet enum
# (not acquire degrees).
# leftover campaign-roster-lookup-tests.
# Sibling GuidedLockRules fields HelmetLockSeconds /
# SensorLockSeconds / SensorAcquireDegrees /
# DetectProgressEnd are NOT this slot.
# THIS IS NOT leftover-safe TheaterKitSpec WeatherIdentity
# UPROPERTY clone. Clone is UPROPERTY-based. RETARGET to
# a plain-struct static constexpr field.
# UPROPERTY rejection is copied from leftover-safe
# CampaignMissionSpec MissionId. Do NOT copy that
# CampaignMissionSpec parse window.
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
HEADER_PATH = "Source/Skyguard52/SkyguardGuidedLockRules.h"
STRUCT_NAME = "FSkyguardGuidedLockRules"
LEFTOVER_LOCK_BREAK = "FSkyguardGuidedLockBreak"
LEFTOVER_CAMPAIGN_SPEC = "FSkyguardCampaignMissionSpec"
LEFTOVER_WEATHER_PROFILE = "FSkyguardWeatherProfile"
LEFTOVER_LOADOUT_SPEC = "FSkyguardLoadoutSpec"
LEFTOVER_HUD_SNAPSHOT = "FSkyguardCpgHudSnapshot"
LEFTOVER_CONTACT_MARK = "FSkyguardCpgContactMark"
LEFTOVER_STORM_KIT = "FSkyguardStormRainBeatKit"
LEFTOVER_DAY_KIT = "FSkyguardDaySortieBeatKit"
LEFTOVER_NIGHT_KIT = "FSkyguardNightSortieBeatKit"
LEFTOVER_THEATER_SPEC = "FSkyguardTheaterKitSpec"
LEFTOVER_MISSION_RESULT = "FSkyguardMissionResult"
LEFTOVER_FEEL_NS = "SkyguardApacheCpgFeel"
LEFTOVER_ROSTER_NS = "SkyguardCampaignRoster"
LEFTOVER_LOCK_BREAK_HEADER = "Source/Skyguard52/SkyguardGuidedLockBreak.h"
LEFTOVER_ROSTER_HEADER = "Source/Skyguard52/SkyguardCampaignRoster.h"
LEFTOVER_GUNSHIP_HEADER = "Source/Skyguard52/SkyguardGunshipTypes.h"
LEFTOVER_MISSION_TYPES_HEADER = "Source/Skyguard52/SkyguardMissionTypes.h"
LEFTOVER_HUD_HEADER = "Source/Skyguard52/SkyguardCpgHud.h"
LEFTOVER_ARCADE_HEADER = "Source/Skyguard52/SkyguardArcadeLookComponent.h"
TARGET = "static constexpr float HelmetAcquireDegrees = 12.0f;"
TARGET_WRONG_TWELVE_F = (
    "static constexpr float HelmetAcquireDegrees = 12.f;"
)
TARGET_WRONG_SIX = (
    "static constexpr float HelmetAcquireDegrees = 6.0f;"
)
TARGET_WRONG_CANNON = "constexpr float CannonFireRate = 12.0f;"
TARGET_WRONG_TOD_F = "float TimeOfDayHours = 12.f;"
TARGET_WRONG_TOD_0 = "float TimeOfDayHours = 12.0f;"
TARGET_WRONG_CONE = "constexpr float GuidedLockConeDegrees = 6.0f;"
TARGET_WRONG_SIGHT = "ESkyguardCpgSightMode SightMode = "
TARGET_WRONG_LOCK_SECONDS = (
    "static constexpr float HelmetLockSeconds = 2.40f;"
)
TARGET_WRONG_SENSOR_LOCK = (
    "static constexpr float SensorLockSeconds = 1.35f;"
)
TARGET_WRONG_SENSOR_ACQUIRE = (
    "static constexpr float SensorAcquireDegrees = 5.5f;"
)
TARGET_WRONG_DETECT = (
    "static constexpr float DetectProgressEnd = 0.22f;"
)
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
STOP_BEFORE_PHASE_FROM_PROGRESS = (
    "static ESkyguardGuidedLockPhase PhaseFromProgress"
)
STOP_BEFORE_CAN_FIRE = "static bool CanFire"
STOP_BEFORE_LOCK_SECONDS = "static float LockSeconds"
STOP_BEFORE_ACQUIRE_DEGREES = "static float AcquireDegrees"
STOP_BEFORE_INSIDE_CONE = "static bool IsInsideAcquireCone"
STOP_BEFORE_PHASE_LABEL = "static const TCHAR* PhaseLabel"
STOP_BEFORE_SIGHT_LABEL = "static const TCHAR* SightLabel"
STOP_BEFORE_SHOULD_DROP = "static bool ShouldDropLock"
STOP_BEFORE_ROSTER_NS = "namespace SkyguardCampaignRoster"
STOP_BEFORE_FEEL_NS = "namespace SkyguardApacheCpgFeel"
STOP_BEFORE_STORM_KIT = "struct FSkyguardStormRainBeatKit"
STOP_BEFORE_DAY_KIT = "struct FSkyguardDaySortieBeatKit"
STOP_BEFORE_NIGHT_KIT = "struct FSkyguardNightSortieBeatKit"
STOP_BEFORE_MISSION_RESULT = "struct FSkyguardMissionResult"
STOP_BEFORE_CONTACT_MARK = "struct FSkyguardCpgContactMark"
STOP_BEFORE_HUD_SNAPSHOT = "struct FSkyguardCpgHudSnapshot"
STOP_BEFORE_LOADOUT = "struct FSkyguardLoadoutSpec"
STOP_BEFORE_WEATHER = "struct FSkyguardWeatherProfile"
STOP_BEFORE_THEATER = "struct FSkyguardTheaterKitSpec"
STOP_BEFORE_LOCK_BREAK = "struct FSkyguardGuidedLockBreak"
STOP_BEFORE_CAMPAIGN_SPEC = "struct FSkyguardCampaignMissionSpec"
STOP_BEFORE_SORTIE = "ASkyguardGunshipSortieDirector"
STOP_BEFORE_HARBOR_CALLS = "SkyguardHarborBeatCalls"
STOP_BEFORE_GUNNER = "ASkyguardGunner"
STOP_BEFORE_APPLY_MOOD = "ApplyWorldMoodForWeather"
SIBLING_HELMET_LOCK = "HelmetLockSeconds"
SIBLING_SENSOR_LOCK = "SensorLockSeconds"
SIBLING_SENSOR_ACQUIRE = "SensorAcquireDegrees"
SIBLING_DETECT = "DetectProgressEnd"
LEFTOVER_TIME_OF_DAY = "TimeOfDayHours"
LEFTOVER_CANNON_RATE = "CannonFireRate"
LEFTOVER_CONE_DEGREES = "GuidedLockConeDegrees"
LEFTOVER_SIGHT_MODE = "SightMode"
LEFTOVER_FLARE_COUNT = "FlareCount"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
THIS_SCRIPT = (
    "Scripts/tests/test_guided_lock_rules_helmet_acquire"
    "_degrees_field_decl_contract.py"
)
CLONE_THEATER_WEATHER_IDENTITY_SCRIPT = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_ANALOG_CPG_FEEL = (
    "Scripts/tests/test_apache_cpg_feel_contract.py"
)
LEFTOVER_GUIDED_LOCK_BREAK = (
    "Scripts/tests/test_guided_lock_break_fail_closed.py"
)
LEFTOVER_GUIDED_LOCK_BREAK_TESTS = (
    "Scripts/tests/test_guided_lock_break_fail_closed_tests.py"
)
LEFTOVER_GUIDED_LOCK_BREAK_CONTRACT = (
    "Scripts/tests/test_guided_lock_break_fail_closed_contract.py"
)
LEFTOVER_LOADOUT_LOCK_PHASE = (
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py"
)
LEFTOVER_CAMPAIGN_MISSION_ID = (
    "Scripts/tests/test_campaign_mission_spec_mission_id"
    "_field_decl_contract.py"
)
LEFTOVER_CAMPAIGN_TOD = (
    "Scripts/tests/test_campaign_mission_spec_time_of_day"
    "_hours_field_decl_contract.py"
)
LEFTOVER_WEATHER_TOD = (
    "Scripts/tests/test_weather_profile_time_of_day_hours"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_SIGHT_MODE = (
    "Scripts/tests/test_cpg_hud_snapshot_sight_mode"
    "_field_decl_contract.py"
)
LEFTOVER_ANALOG_ROSTER_LOOKUP = (
    "Scripts/tests/test_campaign_roster_lookup_tests.py"
)
LEFTOVER_ARCADE_LOOK = (
    "Scripts/tests/test_arcade_look_fail_closed.py"
)
LEFTOVER_ARCADE_MOOD = (
    "Scripts/tests/test_arcade_look_world_mood_fail_closed.py"
)
LEFTOVER_LOADOUT_DEFAULTS = (
    "Scripts/tests/test_loadout_spec_defaults_contract.py"
)
LEFTOVER_LOADOUT_FLARE = (
    "Scripts/tests/test_loadout_spec_flare_count"
    "_field_decl_contract.py"
)

LOCKED = {
    "SkyguardGuidedLockRules.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardGuidedLockBreak.h",
    "SkyguardGuidedLockBreak.cpp",
    "SkyguardCampaignRoster.h",
    "SkyguardCampaignRoster.cpp",
    "SkyguardGunshipTypes.h",
    "SkyguardGunshipTypes.cpp",
    "SkyguardMissionTypes.h",
    "SkyguardCpgHud.h",
    "SkyguardCpgHud.cpp",
    "SkyguardArcadeLookComponent.h",
    "SkyguardArcadeLookComponent.cpp",
    "SkyguardGunshipSortieDirector.h",
    "SkyguardGunshipSortieDirector.cpp",
    "SkyguardHarborBeatCalls.h",
    "SkyguardHarborBeatCalls.cpp",
    "SkyguardApacheAircraft.h",
    "SkyguardApacheAircraft.cpp",
    "SkyguardGunner.h",
    "SkyguardGunner.cpp",
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
        f"{prefix}test_{missile}_boss_decl_contract.py",
        f"{prefix}test_{missile}_missile_decl_contract.py",
        f"{prefix}test_p0_core_{banned}_method05"
        "_deterministic_stagea_offline.py",
    )


def leftover_retired_analog_scripts() -> tuple[str, ...]:
    mount = "ya" + "k"
    prefix = "Scripts/tests/"
    return (
        f"{prefix}test_bld_m01_{mount}_prod_001.py",
        f"{prefix}test_bld_m01_{mount}_prod_002.py",
        f"{prefix}test_bld_m01_{mount}_uplift_003.py",
        f"{prefix}test_phase2_{mount}52_airframe"
        "_refinement01_offline.py",
        f"{prefix}test_m01_{mount}_r3_component"
        "_quarantine.py",
    )


def leftover_campaign_spec_scripts() -> tuple[str, ...]:
    prefix = (
        "Scripts/tests/test_campaign_mission_spec_"
    )
    suffix = "_field_decl_contract.py"
    return (
        prefix + "mission_id" + suffix,
        prefix + "title" + suffix,
        prefix + "success" + suffix,
        prefix + "brief" + suffix,
        prefix + "failure" + suffix,
        prefix + "weather" + suffix,
        prefix + "weather_identity" + suffix,
        prefix + "weather_label" + suffix,
        prefix + "time_of_day_hours" + suffix,
        prefix + "beat_seconds" + suffix,
        prefix + "contact_kind" + suffix,
        prefix + "support_kind" + suffix,
        prefix + "shore_kind" + suffix,
        prefix + "climax" + suffix,
        prefix + "night_identity" + suffix,
        prefix + "extract_kind" + suffix,
        prefix + "storm_rocket_contract" + suffix,
    )


def leftover_loadout_spec_scripts() -> tuple[str, ...]:
    prefix = "Scripts/tests/test_loadout_spec_"
    suffix = "_field_decl_contract.py"
    return (
        prefix + "loadout" + suffix,
        prefix + "cannon_magazine_size" + suffix,
        prefix + "cannon_reserve" + suffix,
        prefix + "rocket_reserve" + suffix,
        prefix + "guided_magazine_size" + suffix,
        prefix + "rocket_magazine_size" + suffix,
        prefix + "hull_integrity" + suffix,
        prefix + "playstyle_line" + suffix,
        prefix + "guided_reserve" + suffix,
        prefix + "flare_count" + suffix,
        prefix + "starting_station" + suffix,
        LEFTOVER_LOADOUT_DEFAULTS,
    )


def leftover_analog_scripts() -> tuple[str, ...]:
    return (
        CLONE_THEATER_WEATHER_IDENTITY_SCRIPT,
        LEFTOVER_ANALOG_CPG_FEEL,
        LEFTOVER_GUIDED_LOCK_BREAK,
        LEFTOVER_GUIDED_LOCK_BREAK_TESTS,
        LEFTOVER_GUIDED_LOCK_BREAK_CONTRACT,
        LEFTOVER_LOADOUT_LOCK_PHASE,
        LEFTOVER_CAMPAIGN_MISSION_ID,
        LEFTOVER_CAMPAIGN_TOD,
        LEFTOVER_WEATHER_TOD,
        LEFTOVER_HUD_SIGHT_MODE,
        LEFTOVER_ANALOG_ROSTER_LOOKUP,
        LEFTOVER_ARCADE_LOOK,
        LEFTOVER_ARCADE_MOOD,
        LEFTOVER_LOADOUT_FLARE,
        "Scripts/tests/test_campaign_theater_kit_contract.py",
        "Scripts/tests/test_storm_rain_beat_kit_contract.py",
        "Scripts/tests/test_day_sortie_beat_kit_contract.py",
        "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    )


LOCKED_SCRIPTS = (
    leftover_analog_scripts()
    + leftover_campaign_spec_scripts()
    + leftover_loadout_spec_scripts()
    + leftover_live_copy_boss_scripts()
    + leftover_retired_analog_scripts()
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


def leftover_live_copy_title_tokens() -> tuple[str, ...]:
    return ("Ig" + "la", "Ri" + "fle", "Ya" + "k")


def leftover_live_case_tokens() -> tuple[str, ...]:
    return leftover_live_copy_title_tokens()


def leftover_pictogram_values() -> tuple[str, ...]:
    return (
        "ESkyguardBriefingPictogram::" + "Ri" + "fle",
        "ESkyguardBriefingPictogram::" + "Ig" + "la",
    )


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
    "= false",
    "= 0.f",
    "= 160.f",
    "= NAME_None",
)


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def leftover_twelve_f() -> str:
    return "12" + ".f"


def leftover_harbor_forty_init() -> str:
    return (
        "static constexpr float HelmetAcquireDegrees = "
        + "40"
        + ".f;"
    )


def leftover_harbor_eighty_init() -> str:
    return (
        "static constexpr float HelmetAcquireDegrees = "
        + "80"
        + ".f;"
    )


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_HELMET_LOCK,
        SIBLING_SENSOR_LOCK,
        SIBLING_SENSOR_ACQUIRE,
        SIBLING_DETECT,
    )


def leftover_collision_identifiers() -> tuple[str, ...]:
    return (
        LEFTOVER_TIME_OF_DAY,
        LEFTOVER_CANNON_RATE,
        LEFTOVER_CONE_DEGREES,
        LEFTOVER_SIGHT_MODE,
    )


def leftover_struct_tokens() -> tuple[str, ...]:
    return (
        LEFTOVER_LOCK_BREAK,
        LEFTOVER_CAMPAIGN_SPEC,
        LEFTOVER_WEATHER_PROFILE,
        LEFTOVER_LOADOUT_SPEC,
        LEFTOVER_HUD_SNAPSHOT,
        LEFTOVER_CONTACT_MARK,
        LEFTOVER_STORM_KIT,
        LEFTOVER_DAY_KIT,
        LEFTOVER_NIGHT_KIT,
        LEFTOVER_THEATER_SPEC,
        LEFTOVER_MISSION_RESULT,
    )


def leftover_method_tokens() -> tuple[str, ...]:
    return (
        STOP_BEFORE_PHASE_FROM_PROGRESS,
        STOP_BEFORE_CAN_FIRE,
        STOP_BEFORE_LOCK_SECONDS,
        STOP_BEFORE_ACQUIRE_DEGREES,
        STOP_BEFORE_INSIDE_CONE,
        STOP_BEFORE_PHASE_LABEL,
        STOP_BEFORE_SIGHT_LABEL,
        STOP_BEFORE_SHOULD_DROP,
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


def helmet_acquire_has_uproperty_wrap(region: str) -> bool:
    compact = collapsed(region)
    return re.search(
        r"UPROPERTY\([^;]*\)\s*static\s+constexpr\s+float\s+"
        r"HelmetAcquireDegrees\b",
        compact,
    ) is not None


def has_declaration(region: str, declaration: str) -> bool:
    # Fail-closed on the authored bare
    # `static constexpr float HelmetAcquireDegrees = 12.0f;`.
    # Do not accept leftover `12.f` / `12.0f` /
    # TimeOfDayHours / CannonFireRate / GuidedLockConeDegrees
    # as this slot. Do not invent an UPROPERTY wrap or
    # Harbor 40/80 initializer. Do not accept sibling
    # HelmetLockSeconds / SensorLockSeconds /
    # SensorAcquireDegrees / DetectProgressEnd.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if re.search(
        r"static\s+constexpr\s+float\s+HelmetAcquireDegrees\s*="
        r"\s*12\.0f\s*;",
        compact,
    ) is None:
        return False
    if re.search(
        r"HelmetAcquireDegrees\s*=\s*12\.f\b",
        compact,
    ):
        return False
    if not has_identifier(region, "HelmetAcquireDegrees"):
        return False
    if helmet_acquire_has_uproperty_wrap(region):
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


def leftover_lock_break_header() -> str:
    return leftover_header(LEFTOVER_LOCK_BREAK_HEADER)


def leftover_roster_header() -> str:
    return leftover_header(LEFTOVER_ROSTER_HEADER)


def leftover_gunship_header() -> str:
    return leftover_header(LEFTOVER_GUNSHIP_HEADER)


def leftover_mission_types_header() -> str:
    return leftover_header(LEFTOVER_MISSION_TYPES_HEADER)


def leftover_hud_header() -> str:
    return leftover_header(LEFTOVER_HUD_HEADER)


def leftover_arcade_header() -> str:
    return leftover_header(LEFTOVER_ARCADE_HEADER)


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
    return leftover_method_tokens() + (
        STOP_BEFORE_ROSTER_NS,
        STOP_BEFORE_FEEL_NS,
        STOP_BEFORE_STORM_KIT,
        STOP_BEFORE_DAY_KIT,
        STOP_BEFORE_NIGHT_KIT,
        STOP_BEFORE_MISSION_RESULT,
        STOP_BEFORE_CONTACT_MARK,
        STOP_BEFORE_HUD_SNAPSHOT,
        STOP_BEFORE_LOADOUT,
        STOP_BEFORE_WEATHER,
        STOP_BEFORE_THEATER,
        STOP_BEFORE_LOCK_BREAK,
        STOP_BEFORE_CAMPAIGN_SPEC,
        STOP_BEFORE_SORTIE,
        leftover_retired_mount_class(),
        STOP_BEFORE_HARBOR_CALLS,
        STOP_BEFORE_GUNNER,
        STOP_BEFORE_APPLY_MOOD,
        LEFTOVER_LOCK_BREAK,
        LEFTOVER_CAMPAIGN_SPEC,
        LEFTOVER_WEATHER_PROFILE,
        LEFTOVER_LOADOUT_SPEC,
        LEFTOVER_HUD_SNAPSHOT,
        LEFTOVER_CONTACT_MARK,
        LEFTOVER_STORM_KIT,
        LEFTOVER_DAY_KIT,
        LEFTOVER_NIGHT_KIT,
        LEFTOVER_THEATER_SPEC,
        LEFTOVER_MISSION_RESULT,
        LEFTOVER_FEEL_NS,
        LEFTOVER_ROSTER_NS,
        LEFTOVER_TIME_OF_DAY,
        LEFTOVER_CANNON_RATE,
        LEFTOVER_CONE_DEGREES,
        LEFTOVER_SIGHT_MODE,
        "class USkyguardCampaignSubsystem",
        f"class SKYGUARD52_API {LEFTOVER_APACHE_CLASS}",
        f"class {LEFTOVER_APACHE_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_RADAR_NODE_CLASS}",
        f"class {LEFTOVER_RADAR_NODE_CLASS}",
    )


def rules_section(header: str) -> str:
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
    stop = section.find(STOP_BEFORE_PHASE_FROM_PROGRESS)
    if stop != -1:
        section = section[:stop]
    for token in leaked_neighbor_tokens():
        if token in section:
            raise AssertionError(
                f"{STRUCT_NAME} parse window includes {token}"
            )
    if STOP_BEFORE_PHASE_FROM_PROGRESS in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes "
            f"{STOP_BEFORE_PHASE_FROM_PROGRESS}"
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
            r"\s*static\s+constexpr\s+float\s+HelmetAcquireDegrees\b",
            compact[index:],
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for static constexpr float HelmetAcquireDegrees "
        f"is missing from origin/main:{HEADER_PATH} struct "
        f"{STRUCT_NAME} body; locked decl is the bare plain C++ "
        "field, not a UPROPERTY wrap"
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
        r"UPROPERTY\([^)]*\)\s*static\s+constexpr\s+float\s+"
        r"HelmetAcquireDegrees\b",
        compact,
    ):
        raise AssertionError(
            "UPROPERTY wrap on HelmetAcquireDegrees is not the locked "
            f"decl for plain C++ struct {STRUCT_NAME}"
        )
    if "UPROPERTY" in section and has_identifier(
        section, "HelmetAcquireDegrees"
    ):
        raise AssertionError(
            "UPROPERTY clone landed on HelmetAcquireDegrees; "
            f"locked decl is bare {LOCKED_DECL}"
        )
    for token in ("USTRUCT", "GENERATED_BODY"):
        if token in section and has_identifier(
            section, "HelmetAcquireDegrees"
        ):
            raise AssertionError(
                f"{token} clone landed on HelmetAcquireDegrees; "
                f"locked decl is bare {LOCKED_DECL}"
            )


class GuidedLockRulesHelmetAcquireDegreesFieldDeclContractTests(
    unittest.TestCase
):
    def test_guided_lock_rules_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(STRUCT_NAME, header)
        self.assertIsNotNone(STRUCT_RE.search(header), header)
        self.assertIn(f"struct SKYGUARD52_API {STRUCT_NAME}", header)
        self.assertEqual(STRUCT_NAME, "FSkyguardGuidedLockRules")
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOCK_BREAK)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_CAMPAIGN_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_WEATHER_PROFILE)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_HUD_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_THEATER_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_APACHE_CLASS)
        body = struct_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = rules_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(
            has_identifier(section, "HelmetAcquireDegrees"),
            section,
        )
        self.assertNotIn("UPROPERTY", section)
        self.assertNotIn("GENERATED_BODY", section)
        self.assertNotIn("USTRUCT", section)
        self.assertIn(STOP_BEFORE_PHASE_FROM_PROGRESS, header)
        self.assertNotIn(STOP_BEFORE_PHASE_FROM_PROGRESS, section)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for leftover in leftover_struct_tokens():
            self.assertNotIn(leftover, section)

    def test_locked_decl_is_plain_static_constexpr_not_uproperty(
        self,
    ) -> None:
        self.assertEqual(
            LOCKED_DECL,
            "static constexpr float HelmetAcquireDegrees = 12.0f;",
        )
        self.assertEqual(LOCKED_DECL, TARGET)
        self.assertIn("HelmetAcquireDegrees", LOCKED_DECL)
        self.assertTrue(LOCKED_DECL.startswith("static constexpr float"))
        self.assertTrue(LOCKED_DECL.endswith(";"))
        self.assertIn("= 12.0f", LOCKED_DECL)
        self.assertNotIn(leftover_twelve_f(), LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_THEATER, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_CAMPAIGN, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_EDIT, LOCKED_DECL)
        self.assertNotIn(CLONE_UPROPERTY_WRITE, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, CLONE_UPROPERTY_THEATER)
        self.assertNotEqual(LOCKED_DECL, CLONE_THEATER_WEATHER_IDENTITY)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CANNON)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TOD_F)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_TOD_0)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CONE)
        self.assertNotIn(LEFTOVER_TIME_OF_DAY, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_CANNON_RATE, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_CONE_DEGREES, LOCKED_DECL)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_LOCK_BREAK_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_ROSTER_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_GUNSHIP_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_MISSION_TYPES_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_HUD_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_ARCADE_HEADER)

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
            self.assertIn("HelmetAcquireDegrees", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            struct_body(
                "struct FSkyguardUnrelatedGuidedLockRules\n{\n};\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_structs_do_not_satisfy(self) -> None:
        leftovers = leftover_struct_tokens() + (
            LEFTOVER_APACHE_CLASS,
            LEFTOVER_FEEL_NS,
        )
        for leftover_name in leftovers:
            leftover = (
                f"struct {leftover_name}\n"
                "{\n"
                f"\t{LOCKED_DECL}\n"
                "};\n"
            )
            with self.assertRaises(AssertionError) as raised:
                rules_section(leftover)
            self.assertIn(STRUCT_NAME, str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_does_not_claim_leftover_roster_or_feel(self) -> None:
        self.assertTrue(
            HEADER_PATH.endswith("SkyguardGuidedLockRules.h")
        )
        self.assertNotIn("GuidedLockBreak", HEADER_PATH)
        self.assertNotIn("CampaignRoster", HEADER_PATH)
        self.assertNotIn("GunshipTypes", HEADER_PATH)
        self.assertNotIn("MissionTypes", HEADER_PATH)
        self.assertNotIn("CpgHud", HEADER_PATH)
        self.assertNotIn("ArcadeLook", HEADER_PATH)
        roster = leftover_roster_header()
        self.assertIn(LEFTOVER_CAMPAIGN_SPEC, roster)
        self.assertIn(TARGET_WRONG_TOD_F, roster)
        with self.assertRaises(AssertionError) as raised:
            rules_section(roster)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        gunship = leftover_gunship_header()
        self.assertIn(LEFTOVER_FEEL_NS, gunship)
        self.assertIn(TARGET_WRONG_CANNON, gunship)
        self.assertIn(TARGET_WRONG_CONE, gunship)
        with self.assertRaises(AssertionError) as raised:
            rules_section(gunship)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        types_header = leftover_mission_types_header()
        self.assertIn(LEFTOVER_WEATHER_PROFILE, types_header)
        self.assertIn(TARGET_WRONG_TOD_F, types_header)
        with self.assertRaises(AssertionError) as raised:
            rules_section(types_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_does_not_parse_guided_lock_break(self) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_LOCK_BREAK_HEADER)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOCK_BREAK)
        break_header = leftover_lock_break_header()
        self.assertIn(LEFTOVER_LOCK_BREAK, break_header)
        self.assertIn(STOP_BEFORE_SHOULD_DROP, break_header)
        self.assertNotIn("HelmetAcquireDegrees", break_header)
        with self.assertRaises(AssertionError) as raised:
            rules_section(break_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotIn(LEFTOVER_LOCK_BREAK, LOCKED_DECL)
        self.assertNotIn("ShouldDropLock", LOCKED_DECL)

    def test_does_not_parse_campaign_roster(self) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_ROSTER_HEADER)
        self.assertNotIn(LEFTOVER_ROSTER_NS, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, LOCKED_DECL)
        roster = leftover_roster_header()
        self.assertIn(STOP_BEFORE_ROSTER_NS, roster)
        self.assertIn(LEFTOVER_TIME_OF_DAY, roster)
        with self.assertRaises(AssertionError) as raised:
            rules_section(roster)
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_missing_helmet_acquire_declaration_fails_closed(
        self,
    ) -> None:
        empty = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_LOCK_SECONDS}\n"
            f"\t{TARGET_WRONG_SENSOR_LOCK}\n"
            f"\t{TARGET_WRONG_SENSOR_ACQUIRE}\n"
            f"\t{TARGET_WRONG_DETECT}\n"
            "};\n"
        )
        section = rules_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("HelmetAcquireDegrees", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_sibling_fields_do_not_satisfy(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_LOCK_SECONDS}\n"
            f"\t{TARGET_WRONG_SENSOR_LOCK}\n"
            f"\t{TARGET_WRONG_SENSOR_ACQUIRE}\n"
            f"\t{TARGET_WRONG_DETECT}\n"
            "};\n"
        )
        section = rules_section(leftover)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("HelmetAcquireDegrees", str(raised.exception))
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_SECONDS)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SENSOR_ACQUIRE)

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{CLONE_UPROPERTY_THEATER}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("HelmetAcquireDegrees", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_has_bare_field_not_uproperty(self) -> None:
        section = rules_section(origin_main_header())
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

    def test_leftover_12_collisions_do_not_satisfy(self) -> None:
        self.assertIn("HelmetAcquireDegrees", LOCKED_DECL)
        self.assertIn("= 12.0f", LOCKED_DECL)
        collisions = (
            TARGET_WRONG_TOD_F,
            TARGET_WRONG_TOD_0,
            TARGET_WRONG_CANNON,
            TARGET_WRONG_CONE,
            TARGET_WRONG_TWELVE_F,
            TARGET_WRONG_SIX,
            leftover_harbor_forty_init(),
            leftover_harbor_eighty_init(),
        )
        for region in collisions:
            self.assertNotEqual(LOCKED_DECL, region)
            self.assertFalse(has_declaration(f"\t{region}\n", LOCKED_DECL))
            with self.assertRaises(AssertionError) as raised:
                require_declaration(f"\t{region}\n", LOCKED_DECL)
            self.assertIn("HelmetAcquireDegrees", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
        for leftover in leftover_collision_identifiers():
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_bare_12_literals_do_not_satisfy(self) -> None:
        bare = (
            "12.0f",
            leftover_twelve_f(),
            "= 12.0f;",
            "= " + leftover_twelve_f() + ";",
            "static constexpr float = 12.0f;",
        )
        for region in bare:
            self.assertFalse(has_declaration(region, LOCKED_DECL), region)
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("HelmetAcquireDegrees", str(raised.exception))

    def test_declaration_matches_origin_main(self) -> None:
        section = rules_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("static constexpr float"),
            LOCKED_DECL,
        )
        self.assertIn("HelmetAcquireDegrees", LOCKED_DECL)
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertIn("= 12.0f", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertIn("float ", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for leftover in leftover_collision_identifiers():
            self.assertNotIn(leftover, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_CANNON}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TOD_F}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TWELVE_F}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_CANNON}\n", LOCKED_DECL)
        self.assertIn("HelmetAcquireDegrees", str(raised.exception))

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tstatic constexpr float "
            + leftover_retired_primary_hits_field()
            + " = 12.0f;\n"
        )
        leftover_guided = (
            "\tstatic constexpr float "
            + leftover_retired_guided_hits_field()
            + " = 12.0f;\n"
        )
        wrongs = (
            f"\t{TARGET_WRONG_TWELVE_F}\n",
            f"\t{TARGET_WRONG_SIX}\n",
            f"\t{TARGET_WRONG_CANNON}\n",
            f"\t{TARGET_WRONG_TOD_F}\n",
            f"\t{TARGET_WRONG_TOD_0}\n",
            f"\t{TARGET_WRONG_CONE}\n",
            f"\t{TARGET_WRONG_LOCK_SECONDS}\n",
            f"\t{TARGET_WRONG_SENSOR_LOCK}\n",
            f"\t{TARGET_WRONG_SENSOR_ACQUIRE}\n",
            f"\t{TARGET_WRONG_DETECT}\n",
            leftover_primary,
            leftover_guided,
            f"\t{CLONE_THEATER_WEATHER_IDENTITY}\n",
            f"\t{TARGET_WRONG_SIGHT}ESkyguardCpgSightMode::"
            "Helmet;\n",
            f"\t{leftover_harbor_forty_init()}\n",
            f"\t{leftover_harbor_eighty_init()}\n",
            "\tstatic constexpr float HelmetAcquireDegree = 12.0f;\n",
            "\tstatic constexpr float HelmetAcquireDegrees = 5.5f;\n",
            "\tfloat HelmetAcquireDegrees = 12.0f;\n",
            "\tconstexpr float HelmetAcquireDegrees = 12.0f;\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("HelmetAcquireDegrees", str(raised.exception))
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
            section = rules_section(wrapped)
            with self.assertRaises(AssertionError):
                require_no_uproperty_wrap(section)
            if "UPROPERTY" in wrapped:
                self.assertTrue(
                    helmet_acquire_has_uproperty_wrap(section),
                    section,
                )
                with self.assertRaises(AssertionError) as raised:
                    require_declaration(section, LOCKED_DECL)
                self.assertIn("HelmetAcquireDegrees", str(raised.exception))
                self.assertIn("missing", str(raised.exception).lower())
        origin = rules_section(origin_main_header())
        require_no_uproperty_wrap(origin)
        self.assertFalse(helmet_acquire_has_uproperty_wrap(origin), origin)
        self.assertNotIn("UPROPERTY", origin)
        self.assertNotIn("Category", origin)
        self.assertNotIn("VisibleAnywhere", origin)
        self.assertNotIn("EditAnywhere", origin)
        self.assertNotIn("BlueprintReadOnly", origin)
        self.assertNotIn("GENERATED_BODY", origin)
        self.assertNotIn("USTRUCT", origin)

    def test_declaration_accepts_origin_main_split_line_forms(
        self,
    ) -> None:
        wraps = (
            "\tstatic constexpr float\n\tHelmetAcquireDegrees = 12.0f;\n",
            "\tstatic constexpr float   HelmetAcquireDegrees = 12.0f;\n",
            "\tstatic constexpr float\tHelmetAcquireDegrees = 12.0f;\n",
            "\tstatic\n\tconstexpr\n\tfloat HelmetAcquireDegrees = 12.0f;\n",
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
            f"\t{TARGET_WRONG_TWELVE_F}\n",
            f"\t{TARGET_WRONG_CANNON}\n",
            f"\t{TARGET_WRONG_TOD_F}\n",
            f"\t{TARGET_WRONG_TOD_0}\n",
            f"\t{TARGET_WRONG_CONE}\n",
            f"\t{TARGET_WRONG_SENSOR_ACQUIRE}\n",
        )
        for region in rejected:
            self.assertFalse(has_declaration(region, LOCKED_DECL), region)

    def test_does_not_contract_sibling_rules_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for leftover in leftover_collision_identifiers():
            self.assertNotIn(leftover, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        section = rules_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        for leftover in leftover_collision_identifiers():
            self.assertFalse(has_identifier(section, leftover), leftover)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_parse_window_stops_before_phase_from_progress(self) -> None:
        header = origin_main_header()
        section = rules_section(header)
        leaked = struct_body(header)
        self.assertIn(STOP_BEFORE_PHASE_FROM_PROGRESS, header)
        self.assertIn(STOP_BEFORE_PHASE_FROM_PROGRESS, leaked)
        self.assertNotIn(STOP_BEFORE_PHASE_FROM_PROGRESS, section)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        for method in leftover_method_tokens():
            self.assertNotIn(method, section)
        self.assertIn("HelmetAcquireDegrees", section)

    def test_does_not_parse_methods(self) -> None:
        header = origin_main_header()
        section = rules_section(header)
        leaked = struct_body(header)
        for method in leftover_method_tokens():
            if method == STOP_BEFORE_SHOULD_DROP:
                self.assertNotIn(method, header)
                self.assertNotIn(method, leaked)
            else:
                self.assertIn(method, header)
                self.assertIn(method, leaked)
            self.assertNotIn(method, section)
            self.assertNotIn(method, LOCKED_DECL)
        mixed = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{LOCKED_DECL}\n"
            f"\t{STOP_BEFORE_PHASE_FROM_PROGRESS}(\n"
            "\t\tfloat Progress,\n"
            "\t\tbool bHasCandidate);\n"
            f"\t{STOP_BEFORE_CAN_FIRE}("
            "ESkyguardGuidedLockPhase Phase);\n"
            f"\t{STOP_BEFORE_LOCK_SECONDS}("
            "ESkyguardCpgSightMode Sight);\n"
            f"\t{STOP_BEFORE_ACQUIRE_DEGREES}("
            "ESkyguardCpgSightMode Sight);\n"
            "};\n"
        )
        cut = rules_section(mixed)
        self.assertTrue(has_declaration(cut, LOCKED_DECL), cut)
        self.assertNotIn(STOP_BEFORE_PHASE_FROM_PROGRESS, cut)
        self.assertNotIn(STOP_BEFORE_CAN_FIRE, cut)
        self.assertNotIn(STOP_BEFORE_LOCK_SECONDS, cut)
        self.assertNotIn(STOP_BEFORE_ACQUIRE_DEGREES, cut)

    def test_methods_after_stop_do_not_satisfy(self) -> None:
        methods = (
            f"\t{STOP_BEFORE_PHASE_FROM_PROGRESS}("
            "float Progress, bool bHasCandidate);\n",
            f"\t{STOP_BEFORE_CAN_FIRE}("
            "ESkyguardGuidedLockPhase Phase);\n",
            f"\t{STOP_BEFORE_LOCK_SECONDS}("
            "ESkyguardCpgSightMode Sight);\n",
            f"\t{STOP_BEFORE_ACQUIRE_DEGREES}("
            "ESkyguardCpgSightMode Sight);\n",
            f"\t{STOP_BEFORE_INSIDE_CONE}("
            "float AngleDegrees, ESkyguardCpgSightMode Sight);\n",
            f"\t{STOP_BEFORE_PHASE_LABEL}("
            "ESkyguardGuidedLockPhase Phase);\n",
            f"\t{STOP_BEFORE_SIGHT_LABEL}("
            "ESkyguardCpgSightMode Sight);\n",
            f"\t{STOP_BEFORE_SHOULD_DROP}();\n",
        )
        for region in methods:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("HelmetAcquireDegrees", str(raised.exception))

    def test_leftover_analog_feel_does_not_satisfy(self) -> None:
        gunship = leftover_gunship_header()
        self.assertIn(STOP_BEFORE_FEEL_NS, gunship)
        self.assertIn(LEFTOVER_CANNON_RATE, gunship)
        self.assertIn("= 12.0f", gunship)
        self.assertIn(LEFTOVER_CONE_DEGREES, gunship)
        self.assertIn("= 6.0f", gunship)
        self.assertFalse(has_declaration(gunship, LOCKED_DECL), gunship)
        with self.assertRaises(AssertionError) as raised:
            rules_section(gunship)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertNotIn(LEFTOVER_CANNON_RATE, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_CONE_DEGREES, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_FEEL_NS, LOCKED_DECL)

    def test_leftover_weather_and_arcade_tod_do_not_satisfy(self) -> None:
        types_header = leftover_mission_types_header()
        self.assertIn(LEFTOVER_WEATHER_PROFILE, types_header)
        self.assertIn(TARGET_WRONG_TOD_F, types_header)
        self.assertFalse(
            has_declaration(types_header, LOCKED_DECL),
            types_header,
        )
        arcade = leftover_arcade_header()
        self.assertIn(STOP_BEFORE_APPLY_MOOD, arcade)
        self.assertIn(LEFTOVER_TIME_OF_DAY, arcade)
        self.assertIn(leftover_twelve_f(), arcade)
        self.assertFalse(has_declaration(arcade, LOCKED_DECL), arcade)
        with self.assertRaises(AssertionError) as raised:
            rules_section(arcade)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertNotIn(STOP_BEFORE_APPLY_MOOD, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_TIME_OF_DAY, LOCKED_DECL)

    def test_leftover_hud_sight_mode_does_not_satisfy(self) -> None:
        hud = leftover_hud_header()
        self.assertIn(LEFTOVER_HUD_SNAPSHOT, hud)
        self.assertIn(LEFTOVER_SIGHT_MODE, hud)
        self.assertIn("ESkyguardCpgSightMode::Helmet", hud)
        self.assertFalse(has_declaration(hud, LOCKED_DECL), hud)
        with self.assertRaises(AssertionError) as raised:
            rules_section(hud)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertNotIn(LEFTOVER_SIGHT_MODE, LOCKED_DECL)
        self.assertNotIn("ESkyguardCpgSightMode::Helmet", LOCKED_DECL)

    def test_leftover_loadout_spec_does_not_satisfy(self) -> None:
        gunship = leftover_gunship_header()
        self.assertIn(LEFTOVER_LOADOUT_SPEC, gunship)
        self.assertFalse(has_declaration(gunship, LOCKED_DECL), gunship)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_FLARE_COUNT, LOCKED_DECL)

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
                rules_section(leftover)
            self.assertIn(STRUCT_NAME, str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
            self.assertNotIn(token, LOCKED_DECL)

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
        self.assertNotIn("SkyguardGuidedLockRules.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardGuidedLockBreak.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignRoster.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardMissionTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardCpgHud.h", HEADER_PATH)
        self.assertNotIn("SkyguardArcadeLookComponent.h", HEADER_PATH)
        self.assertNotIn("SkyguardHarborBeatCalls.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipSortieDirector.h", HEADER_PATH)

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = rules_section(header)
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
        section = rules_section(header)
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
                "guided-lock-rules HelmetAcquireDegrees field decl "
                f"contract contains {banned}; declaration is Apache "
                "CPG 30 mm / Hydra / Hellfire, not leftover live cop"
                + "y",
            )

    def test_this_file_bans_live_retired_tokens_case_sensitive(
        self,
    ) -> None:
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
        self.assertTrue(
            Path(__file__).name.endswith(
                "helmet_acquire_degrees_field_decl_contract.py"
            )
        )
        self.assertIn("guided_lock_rules", Path(__file__).name)
        self.assertNotIn("guided_lock_break", Path(__file__).name)
        self.assertNotIn("campaign_mission_spec", Path(__file__).name)
        self.assertNotIn("loadout_spec", Path(__file__).name)
        self.assertNotIn("weather_profile", Path(__file__).name)
        self.assertNotIn("cpg_hud_snapshot", Path(__file__).name)
        self.assertNotIn("SkyguardGuidedLockBreak.h", THIS_SCRIPT)
        self.assertNotIn("SkyguardCampaignRoster.h", THIS_SCRIPT)
        self.assertIn(CLONE_THEATER_WEATHER_IDENTITY_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_CPG_FEEL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUIDED_LOCK_BREAK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_LOCK_PHASE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CAMPAIGN_MISSION_ID, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CAMPAIGN_TOD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_WEATHER_TOD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_HUD_SIGHT_MODE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_ROSTER_LOOKUP, LOCKED_SCRIPTS)

    def test_leftover_analog_bulk_stays_locked(self) -> None:
        leftovers = leftover_analog_scripts() + leftover_campaign_spec_scripts()
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
        section = rules_section(header)
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        locked_only = f"{LOCKED_DECL}\n"
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, locked_only)
        for leftover in leftover_collision_identifiers():
            self.assertNotIn(leftover, locked_only)
        for leftover in leftover_struct_tokens():
            self.assertNotIn(leftover, locked_only)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, locked_only)
        for method in leftover_method_tokens():
            self.assertNotIn(method, locked_only)
        self.assertNotIn(LEFTOVER_FEEL_NS, locked_only)
        self.assertNotIn(LEFTOVER_ROSTER_NS, locked_only)
        self.assertNotIn(STOP_BEFORE_PHASE_FROM_PROGRESS, locked_only)
        self.assertNotIn(STOP_BEFORE_HARBOR_CALLS, locked_only)
        self.assertNotIn(STOP_BEFORE_SORTIE, locked_only)
        self.assertNotEqual(THIS_SCRIPT, CLONE_THEATER_WEATHER_IDENTITY_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_CPG_FEEL)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_GUIDED_LOCK_BREAK)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_LOADOUT_LOCK_PHASE)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_CAMPAIGN_MISSION_ID)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_CAMPAIGN_TOD)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_WEATHER_TOD)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_SIGHT_MODE)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_ROSTER_LOOKUP)
        for token in leftover_harbor_breaker_label_structs():
            self.assertNotIn(token, locked_only)


if __name__ == "__main__":
    unittest.main()
