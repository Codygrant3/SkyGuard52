# THIS IS leftover-safe USkyguardArcadeLookComponent Contrast.
# origin/main form: one-line and split-line UPROPERTY wraps
# UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
# then `float Contrast = 1.18f;`.
# THIS IS leftover-safe isolated UPROPERTY with Category.
# Category IS `Skyguard|Arcade`. EditAnywhere IS present.
# BlueprintReadWrite IS present. Type IS float.
# Initializer IS `= 1.18f`.
# Fail-closed if the UPROPERTY or decl is missing
# or renamed, if Category is missing, if specifiers
# drop to VisibleAnywhere / BlueprintReadOnly, if
# type is not float, or if initializer is not `= 1.18f`.
# Accept one-line and split-line UPROPERTY wraps.
# Parse CLASS `USkyguardArcadeLookComponent` public
# UPROPERTY fields ONLY after
# `class USkyguardArcadeLookComponent`.
# Stop before claiming sibling UPROPERTY fields
# bEnabled / Saturation / Gain / Gamma /
# BloomIntensity / Vignette / Grain /
# ChromaticAberration as this slot.
# Do NOT parse leftover analog arcade-look-fail-closed
# bulk tests (keep those files in LOCKED_SCRIPTS).
# Do NOT parse leftover analog
# arcade-look-world-mood-fail-closed ApplyWorldMood /
# ApplyWorldMoodForWeather as this slot.
# Do NOT parse leftover analog apache-cpg-feel
# CannonFireRate / CannonRecoilPitch / CannonDamage.
# This is Contrast = 1.18f, not those feel constants.
# Do NOT parse leftover GuidedLockRules HelmetLockSeconds /
# HelmetAcquireDegrees / SensorLockSeconds /
# SensorAcquireDegrees. Do NOT parse
# SkyguardGuidedLockRules.h.
# Do NOT parse leftover CampaignMissionSpec
# TimeOfDayHours (12.f).
# Do NOT parse leftover WeatherProfile fields.
# Do NOT parse leftover campaign-roster-lookup tests.
# Clone source leftover-safe TheaterKit WeatherIdentity
# was VisibleAnywhere BlueprintReadOnly
# Category="Skyguard|Theater" wrapping bare
# `FName WeatherIdentity;` with NO initializer.
# RETARGET: type is float, identifier is Contrast,
# initializer is 1.18f, UPROPERTY is EditAnywhere
# BlueprintReadWrite Category="Skyguard|Arcade".
# Fail-closed if this test still asserts VisibleAnywhere /
# BlueprintReadOnly / Category="Skyguard|Theater" /
# FName WeatherIdentity / no initializer as the
# locked decl.
# Fail-closed on leftover TheaterKit 160.f health
# initializer.
# Better same-class retarget if leftover-safe ArcadeLook
# bEnabled lands. Copy that parse window. Do NOT claim
# bEnabled as this slot.
# Do NOT parse enum class ESkyguardAudioEvent.
# Do NOT parse FSkyguardAudioEventDefinition.
# Do NOT parse ESkyguardBriefingPictogram.
# Do NOT parse ESkyguardBossWeapon.
# Do NOT parse ASkyguardPropSpinner.
# Do NOT parse ASkyguardGunshipSortieDirector.
# Do NOT parse ASkyguardPatrolShipBoss.
# Do NOT parse leftover retired mount class (split tokens).
# Do NOT parse ASkyguardGunner.
# Do NOT parse USkyguardBossWeakPointComponent.
# Harbor fail-closed ONLY 40/80.
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
HEADER_PATH = "Source/Skyguard52/SkyguardArcadeLookComponent.h"
CLASS_NAME = "USkyguardArcadeLookComponent"
THEATER_KIT_SPEC = "FSkyguardTheaterKitSpec"
THEATER_KIT_ACTOR = "ASkyguardCampaignTheaterKit"
GUIDED_LOCK_HEADER = "Source/Skyguard52/SkyguardGuidedLockRules.h"
GUIDED_LOCK_STRUCT = "FSkyguardGuidedLockRules"
WEATHER_PROFILE_STRUCT = "FSkyguardWeatherProfile"
CAMPAIGN_MISSION_SPEC = "FSkyguardCampaignMissionSpec"
TARGET = "float Contrast = 1.18f;"
TARGET_WRONG_BARE = "float Contrast;"
TARGET_WRONG_FALSE = "float Contrast = false;"
TARGET_WRONG_TRUE = "float Contrast = true;"
TARGET_WRONG_ZERO = "float Contrast = 0.f;"
TARGET_WRONG_ONE = "float Contrast = 1.f;"
TARGET_WRONG_NO_F = "float Contrast = 1.18;"
TARGET_WRONG_FNAME = "FName Contrast;"
TARGET_WRONG_INT = "int32 Contrast = 0;"
TARGET_WRONG_BOOL = "bool Contrast = true;"
TARGET_WRONG_HEALTH = "float Health = 160.f;"
TARGET_WRONG_WEATHER_IDENTITY = "FName WeatherIdentity;"
TARGET_WRONG_WEATHER_IDENTITY_FLOAT = "float WeatherIdentity;"
TARGET_WRONG_CANNON_RATE = "float Contrast = 12.0f;"
TARGET_WRONG_CANNON_RECOIL = "float Contrast = 0.92f;"
TARGET_WRONG_CANNON_DAMAGE = "float Contrast = 22.0f;"
TARGET_WRONG_TIME_OF_DAY = "float Contrast = 12.f;"
TARGET_WRONG_SENSOR_ACQUIRE = "float Contrast = 5.5f;"
TARGET_WRONG_CLOUD = "float Contrast = 0.25f;"
TARGET_WRONG_THEATER_WRAP = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Theater")'
)
TARGET_WRONG_CAMPAIGN_WRAP = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Campaign")'
)
TARGET_WRONG_READONLY_WRAP = (
    'UPROPERTY(EditAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Arcade")'
)
LOCKED_DECL = TARGET
UPROPERTY_EDIT_WRITE = (
    'UPROPERTY(EditAnywhere, BlueprintReadWrite, '
    'Category="Skyguard|Arcade")'
)
STOP_BEFORE_APPLY_WORLD_MOOD = "ApplyWorldMood"
STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER = "ApplyWorldMoodForWeather"
STOP_BEFORE_AUDIO_EVENT = "enum class ESkyguardAudioEvent"
STOP_BEFORE_PICTOGRAM = "enum class ESkyguardBriefingPictogram"
STOP_BEFORE_EVENT_DEF = "struct FSkyguardAudioEventDefinition"
STOP_BEFORE_BOSS_WEAPON = "enum class ESkyguardBossWeapon"
STOP_BEFORE_PROP_SPINNER = "ASkyguardPropSpinner"
STOP_BEFORE_SORTIE = "ASkyguardGunshipSortieDirector"
STOP_BEFORE_PATROL = "ASkyguardPatrolShipBoss"
STOP_BEFORE_GUNNER = "ASkyguardGunner"
STOP_BEFORE_WEAK_POINT = "USkyguardBossWeakPointComponent"
STOP_BEFORE_GUIDED_LOCK = "struct FSkyguardGuidedLockRules"
STOP_BEFORE_WEATHER_PROFILE = "struct FSkyguardWeatherProfile"
STOP_BEFORE_CAMPAIGN_SPEC = "struct FSkyguardCampaignMissionSpec"
GET_OBJECTIVE_RUNTIME = "GetObjectiveRuntime"
ADD_OBJECTIVE_PROGRESS = "AddObjectiveProgress"
BIND_RUNTIME_ACTORS = "BindRuntimeActors"
HANDLE_DRONE_CITY_IMPACT = "HandleDroneCityImpact"
GET_STORM_RAIN_BEAT_KIT = "GetStormRainBeatKit"
SIBLING_ENABLED = "bEnabled"
SIBLING_SATURATION = "Saturation"
SIBLING_GAIN = "Gain"
SIBLING_GAMMA = "Gamma"
SIBLING_BLOOM = "BloomIntensity"
SIBLING_VIGNETTE = "Vignette"
SIBLING_GRAIN = "Grain"
SIBLING_CHROMATIC = "ChromaticAberration"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
LEFTOVER_CANNON_FIRE_RATE = "CannonFireRate"
LEFTOVER_CANNON_RECOIL_PITCH = "CannonRecoilPitch"
LEFTOVER_CANNON_DAMAGE = "CannonDamage"
LEFTOVER_HELMET_LOCK_SECONDS = "HelmetLockSeconds"
LEFTOVER_HELMET_ACQUIRE_DEGREES = "HelmetAcquireDegrees"
LEFTOVER_SENSOR_LOCK_SECONDS = "SensorLockSeconds"
LEFTOVER_SENSOR_ACQUIRE_DEGREES = "SensorAcquireDegrees"
LEFTOVER_TIME_OF_DAY_HOURS = "TimeOfDayHours"
LEFTOVER_CLOUD_COVERAGE = "CloudCoverage"
LEFTOVER_PRECIPITATION = "Precipitation"
LEFTOVER_WIND_SPEED = "WindSpeedMetersPerSecond"
LEFTOVER_PROFILE_ID = "ProfileId"
THIS_SCRIPT = (
    "Scripts/tests/test_arcade_look_contrast"
    "_field_decl_contract.py"
)
LEFTOVER_ARCADE_LOOK_FAIL_CLOSED = (
    "Scripts/tests/test_arcade_look_fail_closed.py"
)
LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_TESTS = (
    "Scripts/tests/test_arcade_look_fail_closed_tests.py"
)
LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_CONTRACT = (
    "Scripts/tests/test_arcade_look_fail_closed_contract.py"
)
LEFTOVER_ARCADE_LOOK_WORLD_MOOD = (
    "Scripts/tests/test_arcade_look_world_mood_fail_closed.py"
)
LEFTOVER_ARCADE_LOOK_WORLD_MOOD_TESTS = (
    "Scripts/tests/test_arcade_look_world_mood_fail_closed_tests.py"
)
LEFTOVER_ARCADE_LOOK_WORLD_MOOD_CONTRACT = (
    "Scripts/tests/test_arcade_look_world_mood_fail_closed_contract.py"
)
LEFTOVER_APACHE_CPG_FEEL = (
    "Scripts/tests/test_apache_cpg_feel_contract.py"
)
LEFTOVER_CAMPAIGN_ROSTER_LOOKUP = (
    "Scripts/tests/test_campaign_roster_lookup_tests.py"
)
CLONE_THEATER_KIT_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
SIBLING_ENABLED_SCRIPT = (
    "Scripts/tests/test_arcade_look_enabled"
    "_field_decl_contract.py"
)
SIBLING_SATURATION_SCRIPT = (
    "Scripts/tests/test_arcade_look_saturation"
    "_field_decl_contract.py"
)
SIBLING_GAIN_SCRIPT = (
    "Scripts/tests/test_arcade_look_gain"
    "_field_decl_contract.py"
)
SIBLING_GAMMA_SCRIPT = (
    "Scripts/tests/test_arcade_look_gamma"
    "_field_decl_contract.py"
)
SIBLING_BLOOM_SCRIPT = (
    "Scripts/tests/test_arcade_look_bloom_intensity"
    "_field_decl_contract.py"
)
SIBLING_VIGNETTE_SCRIPT = (
    "Scripts/tests/test_arcade_look_vignette"
    "_field_decl_contract.py"
)
SIBLING_GRAIN_SCRIPT = (
    "Scripts/tests/test_arcade_look_grain"
    "_field_decl_contract.py"
)
SIBLING_CHROMATIC_SCRIPT = (
    "Scripts/tests/test_arcade_look_chromatic_aberration"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_HELMET_LOCK = (
    "Scripts/tests/test_guided_lock_rules_helmet_lock_seconds"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_HELMET_ACQUIRE = (
    "Scripts/tests/test_guided_lock_rules_helmet_acquire_degrees"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_SENSOR_LOCK = (
    "Scripts/tests/test_guided_lock_rules_sensor_lock_seconds"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_SENSOR_ACQUIRE = (
    "Scripts/tests/test_guided_lock_rules_sensor_acquire_degrees"
    "_field_decl_contract.py"
)
LEFTOVER_CAMPAIGN_SPEC_TIME_OF_DAY = (
    "Scripts/tests/test_campaign_mission_spec_time_of_day_hours"
    "_field_decl_contract.py"
)
LEFTOVER_WEATHER_PROFILE_CLOUD = (
    "Scripts/tests/test_weather_profile_cloud_coverage"
    "_field_decl_contract.py"
)
LEFTOVER_WEATHER_PROFILE_PRECIP = (
    "Scripts/tests/test_weather_profile_precipitation"
    "_field_decl_contract.py"
)
LEFTOVER_WEATHER_PROFILE_TIME = (
    "Scripts/tests/test_weather_profile_time_of_day_hours"
    "_field_decl_contract.py"
)
LEFTOVER_WEATHER_PROFILE_WIND = (
    "Scripts/tests/test_weather_profile_wind_speed_meters_per_second"
    "_field_decl_contract.py"
)
LEFTOVER_WEATHER_PROFILE_WEATHER = (
    "Scripts/tests/test_weather_profile_weather"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_KIT_BULK = (
    "Scripts/tests/test_campaign_theater_kit_contract.py"
)


LOCKED = {
    "SkyguardGuidedLockRules.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardCampaignTheaterKit.h",
    "SkyguardCampaignTheaterKit.cpp",
    "SkyguardMissionTypes.h",
    "SkyguardGunshipTypes.h",
    "SkyguardArcadeLookComponent.cpp",
    "SkyguardArcadeLookTests.cpp",
    "SkyguardMission10IntegrationDirector.h",
    "SkyguardMission10IntegrationDirector.cpp",
    "SkyguardMission09IntegrationDirector.h",
    "SkyguardMission09IntegrationDirector.cpp",
    "SkyguardMission08IntegrationDirector.h",
    "SkyguardMission08IntegrationDirector.cpp",
    "SkyguardMission07IntegrationDirector.h",
    "SkyguardMission07IntegrationDirector.cpp",
    "SkyguardMission06IntegrationDirector.h",
    "SkyguardMission06IntegrationDirector.cpp",
    "SkyguardMission05IntegrationDirector.h",
    "SkyguardMission05IntegrationDirector.cpp",
    "SkyguardMission04IntegrationDirector.h",
    "SkyguardMission04IntegrationDirector.cpp",
    "SkyguardMission03IntegrationDirector.h",
    "SkyguardMission03IntegrationDirector.cpp",
    "SkyguardMission02IntegrationDirector.h",
    "SkyguardMission02IntegrationDirector.cpp",
    "SkyguardMission01IntegrationDirector.h",
    "SkyguardMission01IntegrationDirector.cpp",
    "SkyguardRadarNode.cpp",
    "SkyguardRadarNode.h",
    "SkyguardProtectAsset.cpp",
    "SkyguardProtectAsset.h",
    "SkyguardGunner.cpp",
    "SkyguardGunner.h",
    "SkyguardHarborProofTests.cpp",
    "SkyguardCpgHud.cpp",
    "SkyguardCpgHud.h",
    "SkyguardCampaignSubsystem.h",
    "SkyguardCampaignSubsystem.cpp",
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
        f"{prefix}test_{missile}_boss_decl_contract.py",
        f"{prefix}test_{missile}_missile_decl_contract.py",
        f"{prefix}test_last_flight_arm_command_core_{banned}"
        "_path_decl_contract.py",
    )


LOCKED_SCRIPTS = (
    LEFTOVER_ARCADE_LOOK_FAIL_CLOSED,
    LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_TESTS,
    LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_CONTRACT,
    LEFTOVER_ARCADE_LOOK_WORLD_MOOD,
    LEFTOVER_ARCADE_LOOK_WORLD_MOOD_TESTS,
    LEFTOVER_ARCADE_LOOK_WORLD_MOOD_CONTRACT,
    LEFTOVER_APACHE_CPG_FEEL,
    LEFTOVER_CAMPAIGN_ROSTER_LOOKUP,
    CLONE_THEATER_KIT_WEATHER_IDENTITY,
    SIBLING_ENABLED_SCRIPT,
    SIBLING_SATURATION_SCRIPT,
    SIBLING_GAIN_SCRIPT,
    SIBLING_GAMMA_SCRIPT,
    SIBLING_BLOOM_SCRIPT,
    SIBLING_VIGNETTE_SCRIPT,
    SIBLING_GRAIN_SCRIPT,
    SIBLING_CHROMATIC_SCRIPT,
    LEFTOVER_GUIDED_HELMET_LOCK,
    LEFTOVER_GUIDED_HELMET_ACQUIRE,
    LEFTOVER_GUIDED_SENSOR_LOCK,
    LEFTOVER_GUIDED_SENSOR_ACQUIRE,
    LEFTOVER_CAMPAIGN_SPEC_TIME_OF_DAY,
    LEFTOVER_WEATHER_PROFILE_CLOUD,
    LEFTOVER_WEATHER_PROFILE_PRECIP,
    LEFTOVER_WEATHER_PROFILE_TIME,
    LEFTOVER_WEATHER_PROFILE_WIND,
    LEFTOVER_WEATHER_PROFILE_WEATHER,
    LEFTOVER_THEATER_KIT_BULK,
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_weather_profile_profile_id_field_decl_contract.py",
    "Scripts/tests/test_campaign_mission_spec_weather_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_card_card_id_field_decl_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_roster_lookup.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
) + leftover_live_copy_boss_scripts()


def leftover_retired_primary_hits_field() -> str:
    return "Ri" + "fleHits"


def leftover_retired_guided_hits_field() -> str:
    return "Ig" + "laHits"


def leftover_neighbor_hit_fields() -> tuple[str, ...]:
    return (
        leftover_retired_primary_hits_field(),
        leftover_retired_guided_hits_field(),
    )


def leftover_harbor_tokens() -> tuple[str, ...]:
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return (
        forty,
        eighty,
        forty + ", " + eighty,
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


CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
INVENTED_UPROPERTY = (
    "VisibleAnywhere",
    "BlueprintReadOnly",
    "BlueprintCallable",
    "BlueprintPure",
    "Transient",
    "MultiLine",
    "BlueprintAuthorityOnly",
    "ClampMin",
    "ClampMax",
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
    "= true",
    "= false",
    "= 0.f",
    "= 160.f",
    "= 12.0f",
    "= 22.0f",
    "= 12.f",
    "= 5.5f",
    "= 0.25f",
    "= NAME_None",
)


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_ENABLED,
        SIBLING_SATURATION,
        SIBLING_GAIN,
        SIBLING_GAMMA,
        SIBLING_BLOOM,
        SIBLING_VIGNETTE,
        SIBLING_GRAIN,
        SIBLING_CHROMATIC,
    )


def leftover_analog_feel_fields() -> tuple[str, ...]:
    return (
        LEFTOVER_CANNON_FIRE_RATE,
        LEFTOVER_CANNON_RECOIL_PITCH,
        LEFTOVER_CANNON_DAMAGE,
    )


def leftover_guided_lock_fields() -> tuple[str, ...]:
    return (
        LEFTOVER_HELMET_LOCK_SECONDS,
        LEFTOVER_HELMET_ACQUIRE_DEGREES,
        LEFTOVER_SENSOR_LOCK_SECONDS,
        LEFTOVER_SENSOR_ACQUIRE_DEGREES,
    )


def leftover_weather_profile_fields() -> tuple[str, ...]:
    return (
        LEFTOVER_CLOUD_COVERAGE,
        LEFTOVER_PRECIPITATION,
        LEFTOVER_WIND_SPEED,
        LEFTOVER_PROFILE_ID,
        LEFTOVER_TIME_OF_DAY_HOURS,
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
    # Fail-closed on the authored `float Contrast = 1.18f;`.
    # Do not accept bare `float Contrast;` / leftover
    # TheaterKit WeatherIdentity / leftover 160.f Health /
    # leftover apache-cpg-feel CannonFireRate 12.0f /
    # CannonRecoilPitch 0.92f / CannonDamage 22.0f /
    # leftover TimeOfDayHours 12.f / leftover
    # SensorAcquireDegrees 5.5f / leftover CloudCoverage
    # 0.25f when origin/main has Contrast = 1.18f.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if re.search(
        r"float\s+Contrast\s*=\s*1\.18f\s*;",
        compact,
    ) is None:
        return False
    if re.search(
        r"FName\s+Contrast\b",
        compact,
    ):
        return False
    if re.search(
        r"int32\s+Contrast\b",
        compact,
    ):
        return False
    if re.search(
        r"bool\s+Contrast\b",
        compact,
    ):
        return False
    if re.search(
        r"FName\s+WeatherIdentity\b",
        compact,
    ):
        return False
    if re.search(
        r"float\s+Contrast\s*;",
        compact,
    ):
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


def class_body(header: str) -> str:
    match = CLASS_RE.search(header)
    if match is None:
        raise AssertionError(
            f"{CLASS_NAME} is missing from origin/main:{HEADER_PATH}"
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
        f"{CLASS_NAME} class body is missing from origin/main:{HEADER_PATH}"
    )


def leaked_neighbor_tokens() -> tuple[str, ...]:
    return (
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
        STOP_BEFORE_GUIDED_LOCK,
        STOP_BEFORE_WEATHER_PROFILE,
        STOP_BEFORE_CAMPAIGN_SPEC,
        GET_OBJECTIVE_RUNTIME,
        ADD_OBJECTIVE_PROGRESS,
        BIND_RUNTIME_ACTORS,
        HANDLE_DRONE_CITY_IMPACT,
        GET_STORM_RAIN_BEAT_KIT,
        GUIDED_LOCK_HEADER,
        GUIDED_LOCK_STRUCT,
        WEATHER_PROFILE_STRUCT,
        CAMPAIGN_MISSION_SPEC,
        THEATER_KIT_SPEC,
        THEATER_KIT_ACTOR,
        "class USkyguardCampaignSubsystem",
        "class ASkyguardMission01IntegrationDirector",
        "class ASkyguardMission05IntegrationDirector",
        "class ASkyguardMission10IntegrationDirector",
        "struct FSkyguardLandscapeVisibleAudit",
        "class USkyguardSortiePresentationComponent",
        "struct FSkyguardBriefingCard",
        "struct FSkyguardMissionResult",
        "struct FSkyguardObjectiveProgress",
        "struct FSkyguardMissionDebrief",
        "struct FSkyguardBossTelemetry",
        "struct FSkyguardAudioTelemetry",
        "ESkyguardAudioEvent::",
        f"class SKYGUARD52_API {LEFTOVER_APACHE_CLASS}",
        f"class {LEFTOVER_APACHE_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class {LEFTOVER_PROTECT_ASSET_CLASS}",
        f"class SKYGUARD52_API {LEFTOVER_RADAR_NODE_CLASS}",
        f"class {LEFTOVER_RADAR_NODE_CLASS}",
    )


def public_section(header: str) -> str:
    body = class_body(header)
    public = re.search(r"\bpublic\s*:", body)
    if public is None:
        raise AssertionError(
            f"{CLASS_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = public.end()
    rest = body[start:]
    next_access = ACCESS_RE.search(rest)
    if next_access is not None:
        return rest[: next_access.start()]
    close = rest.rfind("}")
    if close == -1:
        raise AssertionError(
            f"{CLASS_NAME} public section is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    return rest[:close]


def spec_section(header: str) -> str:
    section = public_section(header)
    first_prop = section.find("UPROPERTY")
    if first_prop == -1:
        raise AssertionError(
            f"{CLASS_NAME} public UPROPERTY fields are missing from "
            f"origin/main:{HEADER_PATH}"
        )
    section = section[first_prop:]
    for token in leaked_neighbor_tokens():
        if token in section:
            raise AssertionError(
                f"{CLASS_NAME} parse window includes {token}"
            )
    for stop in (
        STOP_BEFORE_APPLY_WORLD_MOOD,
        STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER,
        LEFTOVER_TIME_OF_DAY_HOURS,
    ):
        if stop in section:
            raise AssertionError(
                f"{CLASS_NAME} parse window includes {stop}"
            )
    for leftover in leftover_guided_lock_fields():
        if leftover in section:
            raise AssertionError(
                f"{CLASS_NAME} parse window includes {leftover}"
            )
    for leftover in leftover_analog_feel_fields():
        if leftover in section:
            raise AssertionError(
                f"{CLASS_NAME} parse window includes {leftover}"
            )
    forty = "40" + ".f"
    eighty = "80" + ".f"
    if forty in section or eighty in section:
        raise AssertionError(
            f"{CLASS_NAME} parse window includes Harbor 40/80 tokens"
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
            r"\s*float\s+Contrast\b", compact[index:]
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for float Contrast is missing from "
        f"origin/main:{HEADER_PATH} class {CLASS_NAME} public "
        "UPROPERTY fields"
    )


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} public UPROPERTY fields"
        )
    return declaration


class ArcadeLookContrastFieldDeclContractTests(unittest.TestCase):
    def test_arcade_look_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertIn(f"class SKYGUARD52_API {CLASS_NAME}", header)
        self.assertNotEqual(CLASS_NAME, THEATER_KIT_SPEC)
        self.assertNotEqual(CLASS_NAME, THEATER_KIT_ACTOR)
        self.assertNotEqual(CLASS_NAME, GUIDED_LOCK_STRUCT)
        self.assertNotEqual(CLASS_NAME, WEATHER_PROFILE_STRUCT)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_APACHE_CLASS)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_RADAR_NODE_CLASS)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "Contrast"), section)
        self.assertIn("UPROPERTY", section)
        self.assertNotIn(STOP_BEFORE_APPLY_WORLD_MOOD, section)
        self.assertNotIn(STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER, section)
        self.assertNotIn(GUIDED_LOCK_HEADER, section)
        self.assertNotIn(GUIDED_LOCK_STRUCT, section)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, section)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class USkyguardUnrelatedArcadeLook\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_type_does_not_satisfy(self) -> None:
        other = (
            f"struct {THEATER_KIT_SPEC}\n"
            "{\n"
            f"\t{UPROPERTY_EDIT_WRITE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        radar = (
            f"class {LEFTOVER_RADAR_NODE_CLASS}\n"
            "{\n"
            "public:\n"
            f"\t{UPROPERTY_EDIT_WRITE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(radar)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_neighbor_class_declaration_does_not_satisfy(self) -> None:
        mixed = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UPROPERTY_EDIT_WRITE}\n"
            f"\tbool {SIBLING_ENABLED} = true;\n"
            "};\n"
            f"class {THEATER_KIT_ACTOR}\n"
            "{\n"
            "public:\n"
            f"\t{UPROPERTY_EDIT_WRITE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        section = spec_section(mixed)
        self.assertFalse(has_identifier(section, "Contrast"), section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_contrast_declaration_fails_closed(self) -> None:
        empty = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UPROPERTY_EDIT_WRITE}\n"
            f"\tbool {SIBLING_ENABLED} = true;\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_EDIT_WRITE}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = spec_section(origin_main_header())
        self.assertIn(UPROPERTY_EDIT_WRITE, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadWrite", section)
        self.assertIn('Category="Skyguard|Arcade"', section)
        self.assertIn("EditAnywhere", UPROPERTY_EDIT_WRITE)
        self.assertIn("BlueprintReadWrite", UPROPERTY_EDIT_WRITE)
        self.assertIn("Category", UPROPERTY_EDIT_WRITE)
        self.assertIn('Category="Skyguard|Arcade"', UPROPERTY_EDIT_WRITE)
        self.assertNotIn("VisibleAnywhere", UPROPERTY_EDIT_WRITE)
        self.assertNotIn("BlueprintReadOnly", UPROPERTY_EDIT_WRITE)
        self.assertNotIn('Category="Skyguard|Theater"', UPROPERTY_EDIT_WRITE)
        specifiers = attached_uproperty_specifiers(section)
        self.assertIn("EditAnywhere", specifiers)
        self.assertIn("BlueprintReadWrite", specifiers)
        self.assertIn('Category="Skyguard|Arcade"', specifiers)
        self.assertIn("Category", specifiers)
        self.assertNotIn("VisibleAnywhere", specifiers)
        self.assertNotIn("BlueprintReadOnly", specifiers)
        self.assertNotIn("MultiLine", specifiers)
        self.assertNotIn("ClampMin", specifiers)
        self.assertNotIn("ClampMax", specifiers)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("UFUNCTION", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, LOCKED_DECL)

    def test_missing_or_wrong_initializer_fails_closed(self) -> None:
        initialized = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UPROPERTY_EDIT_WRITE}\n"
            f"\t{TARGET_WRONG_BARE}\n"
            "};\n"
        )
        section = spec_section(initialized)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn("float Contrast = 1.18f;", compact_origin)
        self.assertNotIn("Contrast = NAME_None", compact_origin)
        self.assertNotIn("Contrast = false", compact_origin)
        self.assertNotIn("Contrast = true", compact_origin)
        self.assertNotIn("Contrast = 0.f", compact_origin)
        self.assertNotIn("Contrast = 160.f", compact_origin)
        self.assertNotIn("Contrast = 12.0f", compact_origin)
        self.assertNotIn("Contrast = 22.0f", compact_origin)

    def test_contrast_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("float Contrast"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertIn("=", LOCKED_DECL)
        self.assertIn("= 1.18f", LOCKED_DECL)
        self.assertIn("float ", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("= NAME_None", LOCKED_DECL)
        self.assertNotIn("= false", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertNotIn("= 12.0f", LOCKED_DECL)
        self.assertNotIn("= 0.92f", LOCKED_DECL)
        self.assertNotIn("= 22.0f", LOCKED_DECL)
        self.assertNotIn("= 12.f", LOCKED_DECL)
        self.assertNotIn("= 5.5f", LOCKED_DECL)
        self.assertNotIn("= 0.25f", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
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
            has_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_ZERO}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HEALTH}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_WEATHER_IDENTITY}\n",
                LOCKED_DECL,
            )
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_FALSE}\n", LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tfloat " + leftover_retired_primary_hits_field() + " = 1.18f;\n"
        )
        leftover_guided = (
            "\tfloat " + leftover_retired_guided_hits_field() + " = 1.18f;\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_FALSE}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_ONE}\n",
            f"\t{TARGET_WRONG_NO_F}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_INT}\n",
            f"\t{TARGET_WRONG_BOOL}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            f"\t{TARGET_WRONG_WEATHER_IDENTITY}\n",
            f"\t{TARGET_WRONG_WEATHER_IDENTITY_FLOAT}\n",
            f"\t{TARGET_WRONG_CANNON_RATE}\n",
            f"\t{TARGET_WRONG_CANNON_RECOIL}\n",
            f"\t{TARGET_WRONG_CANNON_DAMAGE}\n",
            f"\t{TARGET_WRONG_TIME_OF_DAY}\n",
            f"\t{TARGET_WRONG_SENSOR_ACQUIRE}\n",
            f"\t{TARGET_WRONG_CLOUD}\n",
            leftover_primary,
            leftover_guided,
            f"\tfloat {SIBLING_SATURATION} = 1.12f;\n",
            "\tfloat Contrasts = 1.18f;\n",
            "\tint32 Contrast = 1;\n",
            "\tbool Contrast = true;\n",
            "\tfloat Contrast = " + forty + ";\n",
            "\tfloat Contrast = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("Contrast", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_theater_kit_leftover_wrap_fails_closed(self) -> None:
        self.assertNotEqual(UPROPERTY_EDIT_WRITE, TARGET_WRONG_THEATER_WRAP)
        self.assertNotIn("VisibleAnywhere", UPROPERTY_EDIT_WRITE)
        self.assertNotIn("BlueprintReadOnly", UPROPERTY_EDIT_WRITE)
        self.assertNotIn('Category="Skyguard|Theater"', UPROPERTY_EDIT_WRITE)
        self.assertNotIn("FName WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertIn("=", LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WEATHER_IDENTITY)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_HEALTH)
        origin = attached_uproperty_specifiers(
            spec_section(origin_main_header())
        )
        self.assertNotIn("VisibleAnywhere", origin)
        self.assertNotIn("BlueprintReadOnly", origin)
        self.assertNotIn('Category="Skyguard|Theater"', origin)
        theater = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{TARGET_WRONG_THEATER_WRAP}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        theater_specs = attached_uproperty_specifiers(
            spec_section(theater)
        )
        self.assertIn("VisibleAnywhere", theater_specs)
        self.assertIn("BlueprintReadOnly", theater_specs)
        self.assertIn('Category="Skyguard|Theater"', theater_specs)
        self.assertNotIn("EditAnywhere", theater_specs)
        self.assertNotIn("BlueprintReadWrite", theater_specs)
        self.assertIn("EditAnywhere", origin)
        self.assertIn("BlueprintReadWrite", origin)
        self.assertIn('Category="Skyguard|Arcade"', origin)

    def test_missing_category_or_edit_anywhere_fails_closed(self) -> None:
        no_category = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite)\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        section = spec_section(no_category)
        specifiers = attached_uproperty_specifiers(section)
        self.assertNotIn("Category", specifiers)
        origin = attached_uproperty_specifiers(
            spec_section(origin_main_header())
        )
        self.assertIn("Category", origin)
        self.assertIn('Category="Skyguard|Arcade"', origin)
        self.assertIn("EditAnywhere", origin)
        self.assertIn("BlueprintReadWrite", origin)
        no_edit = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            "\tUPROPERTY(BlueprintReadWrite, "
            'Category="Skyguard|Arcade")\n'
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        dropped = attached_uproperty_specifiers(
            spec_section(no_edit)
        )
        self.assertNotIn("EditAnywhere", dropped)
        self.assertIn("EditAnywhere", origin)
        readonly = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{TARGET_WRONG_READONLY_WRAP}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        read_specs = attached_uproperty_specifiers(
            spec_section(readonly)
        )
        self.assertIn("BlueprintReadOnly", read_specs)
        self.assertNotIn("BlueprintReadWrite", read_specs)
        self.assertIn("BlueprintReadWrite", origin)
        self.assertNotIn("BlueprintReadOnly", origin)
        campaign = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{TARGET_WRONG_CAMPAIGN_WRAP}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        campaign_specs = attached_uproperty_specifiers(
            spec_section(campaign)
        )
        self.assertIn('Category="Skyguard|Campaign"', campaign_specs)
        self.assertNotIn('Category="Skyguard|Arcade"', campaign_specs)
        self.assertIn('Category="Skyguard|Arcade"', origin)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tfloat\n\tContrast = 1.18f;\n",
            "\tfloat   Contrast = 1.18f;\n",
            "\tfloat\tContrast = 1.18f;\n",
            f"\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_EDIT_WRITE}\n\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_EDIT_WRITE} {LOCKED_DECL}\n",
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite, "
            'Category="Skyguard|Arcade")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUPROPERTY(\n\t\tEditAnywhere, BlueprintReadWrite, "
            'Category="Skyguard|Arcade")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite,\n"
            '\t\tCategory="Skyguard|Arcade")\n'
            f"\t{LOCKED_DECL}\n",
        )
        for region in wraps:
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)

    def test_does_not_contract_sibling_arcade_look_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertNotIn(SIBLING_ENABLED, LOCKED_DECL)
        self.assertNotIn(STOP_BEFORE_APPLY_WORLD_MOOD, LOCKED_DECL)
        self.assertNotIn(STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER, LOCKED_DECL)
        section = spec_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_enabled_sibling_is_not_this_slot(self) -> None:
        self.assertNotEqual(LOCKED_DECL, "bool bEnabled = true;")
        self.assertNotIn(SIBLING_ENABLED, LOCKED_DECL)
        self.assertNotEqual(THIS_SCRIPT, SIBLING_ENABLED_SCRIPT)
        section = spec_section(origin_main_header())
        self.assertTrue(has_identifier(section, SIBLING_ENABLED), section)
        self.assertFalse(
            has_declaration("\tbool bEnabled = true;\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration("\tbool bEnabled = true;\n", LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))

    def test_does_not_parse_apply_world_mood_as_this_slot(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        public = public_section(header)
        self.assertIn(STOP_BEFORE_APPLY_WORLD_MOOD, header)
        self.assertIn(STOP_BEFORE_APPLY_WORLD_MOOD, public)
        self.assertNotIn(STOP_BEFORE_APPLY_WORLD_MOOD, section)
        self.assertIn(STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER, header)
        self.assertIn(STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER, public)
        self.assertNotIn(STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER, section)
        self.assertNotIn(STOP_BEFORE_APPLY_WORLD_MOOD, LOCKED_DECL)
        self.assertNotIn(STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_TIME_OF_DAY_HOURS, section)
        self.assertNotIn(LEFTOVER_TIME_OF_DAY_HOURS, LOCKED_DECL)
        mood = (
            f"\tstatic void {STOP_BEFORE_APPLY_WORLD_MOOD}"
            "(UObject* WorldContextObject);\n"
            f"\tstatic void {STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER}"
            "(UObject* WorldContextObject);\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(mood, LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))

    def test_does_not_parse_guided_lock_rules_header(self) -> None:
        self.assertEqual(HEADER_PATH, (
            "Source/Skyguard52/SkyguardArcadeLookComponent.h"
        ))
        self.assertNotEqual(HEADER_PATH, GUIDED_LOCK_HEADER)
        self.assertNotIn("SkyguardGuidedLockRules.h", HEADER_PATH)
        self.assertNotIn(GUIDED_LOCK_STRUCT, LOCKED_DECL)
        for leftover in leftover_guided_lock_fields():
            self.assertNotIn(leftover, LOCKED_DECL)
        header = origin_main_header()
        section = spec_section(header)
        self.assertNotIn(GUIDED_LOCK_HEADER, header)
        self.assertNotIn(GUIDED_LOCK_STRUCT, header)
        self.assertNotIn(GUIDED_LOCK_STRUCT, section)
        for leftover in leftover_guided_lock_fields():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, header)

    def test_does_not_parse_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = class_body(header)
        self.assertNotIn(THEATER_KIT_SPEC, header)
        self.assertNotIn(THEATER_KIT_SPEC, section)
        self.assertNotIn(THEATER_KIT_SPEC, leaked)
        self.assertNotIn(THEATER_KIT_ACTOR, header)
        self.assertNotIn(STOP_BEFORE_AUDIO_EVENT, header)
        self.assertNotIn(STOP_BEFORE_PICTOGRAM, header)
        self.assertNotIn(STOP_BEFORE_EVENT_DEF, header)
        self.assertNotIn(STOP_BEFORE_BOSS_WEAPON, header)
        self.assertNotIn(STOP_BEFORE_PROP_SPINNER, header)
        self.assertNotIn(STOP_BEFORE_SORTIE, header)
        self.assertNotIn(STOP_BEFORE_PATROL, header)
        self.assertNotIn(leftover_retired_mount_class(), header)
        self.assertNotIn(STOP_BEFORE_GUNNER, header)
        self.assertNotIn(STOP_BEFORE_WEAK_POINT, header)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, header)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, header)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, header)
        self.assertNotIn(WEATHER_PROFILE_STRUCT, header)
        self.assertNotIn(CAMPAIGN_MISSION_SPEC, header)
        self.assertNotIn(GUIDED_LOCK_STRUCT, leaked)
        self.assertNotIn(WEATHER_PROFILE_STRUCT, leaked)
        self.assertNotIn(CAMPAIGN_MISSION_SPEC, leaked)

    def test_parse_window_is_uproperty_fields_only(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        public = public_section(header)
        self.assertIn("UFUNCTION", public)
        self.assertNotIn("UFUNCTION", section)
        self.assertIn("ApplyToCamera", public)
        self.assertNotIn("ApplyToCamera", section)
        self.assertIn("ApplyHelmetSight", public)
        self.assertNotIn("ApplyHelmetSight", section)
        self.assertIn("ApplyTargetingSensor", public)
        self.assertNotIn("ApplyTargetingSensor", section)
        self.assertIn("ApplyThermalSensor", public)
        self.assertNotIn("ApplyThermalSensor", section)
        self.assertIn("IsEnabled", public)
        self.assertNotIn("IsEnabled", section)
        self.assertTrue(section.lstrip().startswith("UPROPERTY"), section)

    def test_parse_window_excludes_leftover_weapon_enum_body(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = class_body(header)
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
        self.assertNotIn(LEFTOVER_APACHE_CLASS, leaked)

    def test_leftover_analog_feel_initializers_do_not_satisfy(self) -> None:
        for leftover in leftover_analog_feel_fields():
            self.assertNotIn(leftover, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, "float CannonFireRate = 12.0f;")
        self.assertNotEqual(LOCKED_DECL, "float CannonRecoilPitch = 0.92f;")
        self.assertNotEqual(LOCKED_DECL, "float CannonDamage = 22.0f;")
        feel = (
            f"\tfloat {LEFTOVER_CANNON_FIRE_RATE} = 12.0f;\n"
            f"\tfloat {LEFTOVER_CANNON_RECOIL_PITCH} = 0.92f;\n"
            f"\tfloat {LEFTOVER_CANNON_DAMAGE} = 22.0f;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(feel, LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_CANNON_RATE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_CANNON_RECOIL}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_CANNON_DAMAGE}\n", LOCKED_DECL)
        )

    def test_leftover_weather_profile_and_time_of_day_do_not_satisfy(
        self,
    ) -> None:
        for leftover in leftover_weather_profile_fields():
            self.assertNotIn(leftover, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, "float CloudCoverage = 0.25f;")
        self.assertNotEqual(LOCKED_DECL, "float TimeOfDayHours = 12.f;")
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WEATHER_IDENTITY)
        weather = (
            f"\tfloat {LEFTOVER_CLOUD_COVERAGE} = 0.25f;\n"
            f"\tfloat {LEFTOVER_TIME_OF_DAY_HOURS} = 12.f;\n"
            f"\t{TARGET_WRONG_WEATHER_IDENTITY}\n"
            f"\t{TARGET_WRONG_HEALTH}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(weather, LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_CLOUD}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TIME_OF_DAY}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HEALTH}\n", LOCKED_DECL)
        )

    def test_leftover_guided_lock_degrees_do_not_satisfy(self) -> None:
        for leftover in leftover_guided_lock_fields():
            self.assertNotIn(leftover, LOCKED_DECL)
        guided = (
            f"\tfloat {LEFTOVER_HELMET_LOCK_SECONDS} = 0.35f;\n"
            f"\tfloat {LEFTOVER_HELMET_ACQUIRE_DEGREES} = 8.f;\n"
            f"\tfloat {LEFTOVER_SENSOR_LOCK_SECONDS} = 0.55f;\n"
            f"\tfloat {LEFTOVER_SENSOR_ACQUIRE_DEGREES} = 5.5f;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(guided, LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_SENSOR_ACQUIRE}\n",
                LOCKED_DECL,
            )
        )

    def test_clone_source_theater_kit_weather_identity_is_not_locked_decl(
        self,
    ) -> None:
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_WEATHER_IDENTITY)
        self.assertNotEqual(UPROPERTY_EDIT_WRITE, TARGET_WRONG_THEATER_WRAP)
        self.assertNotEqual(THIS_SCRIPT, CLONE_THEATER_KIT_WEATHER_IDENTITY)
        self.assertIn(CLONE_THEATER_KIT_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn("float ", LOCKED_DECL)
        self.assertIn("Contrast", LOCKED_DECL)
        self.assertIn("1.18f", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("160.f", LOCKED_DECL)
        self.assertFalse(
            has_declaration(
                f"\t{TARGET_WRONG_THEATER_WRAP}\n"
                f"\t{TARGET_WRONG_WEATHER_IDENTITY}\n",
                LOCKED_DECL,
            )
        )

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            f"\tstatic void {STOP_BEFORE_APPLY_WORLD_MOOD}();\n"
            f"\tstatic void {STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER}();\n"
            f"\tbool {SIBLING_ENABLED} = true;\n"
            f"\tfloat {SIBLING_SATURATION} = 1.12f;\n"
            f"\t{TARGET_WRONG_HEALTH}\n"
            f"\t{TARGET_WRONG_WEATHER_IDENTITY}\n"
            "\tUSkyguardObjectiveRuntime* GetObjectiveRuntime() const;\n"
            "\tbool AddObjectiveProgress(\n"
            "\t\tFName ObjectiveId,\n"
            "\t\tint32 MedalTier);\n"
            "\tvoid BindRuntimeActors();\n"
            "\tvoid HandleDroneCityImpact();\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("Contrast", str(raised.exception))

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        self.assertEqual(
            UPROPERTY_EDIT_WRITE,
            'UPROPERTY(EditAnywhere, BlueprintReadWrite, '
            'Category="Skyguard|Arcade")',
        )
        self.assertIn("EditAnywhere", UPROPERTY_EDIT_WRITE)
        self.assertIn("BlueprintReadWrite", UPROPERTY_EDIT_WRITE)
        self.assertIn("Category", UPROPERTY_EDIT_WRITE)
        self.assertIn('Category="Skyguard|Arcade"', UPROPERTY_EDIT_WRITE)
        self.assertNotIn('Category="Skyguard|Theater"', UPROPERTY_EDIT_WRITE)
        self.assertNotIn('Category="Skyguard|Campaign"', UPROPERTY_EDIT_WRITE)
        self.assertNotIn("VisibleAnywhere", UPROPERTY_EDIT_WRITE)
        self.assertNotIn("BlueprintReadOnly", UPROPERTY_EDIT_WRITE)
        self.assertNotIn("MultiLine", UPROPERTY_EDIT_WRITE)
        self.assertNotIn("ClampMin", UPROPERTY_EDIT_WRITE)
        self.assertNotIn("ClampMax", UPROPERTY_EDIT_WRITE)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, LOCKED_DECL)
            self.assertNotIn(invented, UPROPERTY_EDIT_WRITE)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardArcadeLookComponent.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardGuidedLockRules.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardMissionTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardRadarNode.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)

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
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, header)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "arcade-look Contrast field decl contract "
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
            "contrast_field_decl_contract.py"
        ))
        self.assertNotIn("SkyguardArcadeLookComponent.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardGuidedLockRules.h", THIS_SCRIPT)
        self.assertIn(LEFTOVER_ARCADE_LOOK_FAIL_CLOSED, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ARCADE_LOOK_WORLD_MOOD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ARCADE_LOOK_WORLD_MOOD_TESTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ARCADE_LOOK_WORLD_MOOD_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_APACHE_CPG_FEEL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CAMPAIGN_ROSTER_LOOKUP, LOCKED_SCRIPTS)
        self.assertIn(CLONE_THEATER_KIT_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(SIBLING_ENABLED_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUIDED_HELMET_LOCK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUIDED_SENSOR_ACQUIRE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CAMPAIGN_SPEC_TIME_OF_DAY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_WEATHER_PROFILE_CLOUD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_THEATER_KIT_BULK, LOCKED_SCRIPTS)

    def test_leftover_analog_bulk_scripts_stay_locked(self) -> None:
        leftovers = (
            LEFTOVER_ARCADE_LOOK_FAIL_CLOSED,
            LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_TESTS,
            LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_CONTRACT,
            LEFTOVER_ARCADE_LOOK_WORLD_MOOD,
            LEFTOVER_ARCADE_LOOK_WORLD_MOOD_TESTS,
            LEFTOVER_ARCADE_LOOK_WORLD_MOOD_CONTRACT,
            LEFTOVER_APACHE_CPG_FEEL,
            LEFTOVER_CAMPAIGN_ROSTER_LOOKUP,
            CLONE_THEATER_KIT_WEATHER_IDENTITY,
            SIBLING_ENABLED_SCRIPT,
            SIBLING_SATURATION_SCRIPT,
            SIBLING_GAIN_SCRIPT,
            SIBLING_GAMMA_SCRIPT,
            SIBLING_BLOOM_SCRIPT,
            SIBLING_VIGNETTE_SCRIPT,
            SIBLING_GRAIN_SCRIPT,
            SIBLING_CHROMATIC_SCRIPT,
            LEFTOVER_GUIDED_HELMET_LOCK,
            LEFTOVER_GUIDED_HELMET_ACQUIRE,
            LEFTOVER_GUIDED_SENSOR_LOCK,
            LEFTOVER_GUIDED_SENSOR_ACQUIRE,
            LEFTOVER_CAMPAIGN_SPEC_TIME_OF_DAY,
            LEFTOVER_WEATHER_PROFILE_CLOUD,
            LEFTOVER_WEATHER_PROFILE_PRECIP,
            LEFTOVER_WEATHER_PROFILE_TIME,
            LEFTOVER_WEATHER_PROFILE_WIND,
            LEFTOVER_WEATHER_PROFILE_WEATHER,
            LEFTOVER_THEATER_KIT_BULK,
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

    def test_header_path_is_arcade_look_component_only(self) -> None:
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardArcadeLookComponent.h",
        )
        self.assertEqual(CLASS_NAME, "USkyguardArcadeLookComponent")
        self.assertEqual(LOCKED_DECL, "float Contrast = 1.18f;")
        self.assertEqual(
            UPROPERTY_EDIT_WRITE,
            'UPROPERTY(EditAnywhere, BlueprintReadWrite, '
            'Category="Skyguard|Arcade")',
        )

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
        for leftover in leftover_analog_feel_fields():
            self.assertNotIn(leftover, locked_only)
        for leftover in leftover_guided_lock_fields():
            self.assertNotIn(leftover, locked_only)
        for leftover in leftover_weather_profile_fields():
            self.assertNotIn(leftover, locked_only)
        self.assertNotIn(GET_OBJECTIVE_RUNTIME, locked_only)
        self.assertNotIn("FSkyguardObjectiveProgress", locked_only)
        self.assertNotIn("ESkyguardAudioEvent", locked_only)
        self.assertNotIn("ESkyguardBriefingPictogram", locked_only)
        self.assertNotIn("FSkyguardAudioEventDefinition", locked_only)
        self.assertNotIn("WeatherIdentity", locked_only)
        self.assertNotIn("VisibleAnywhere", locked_only)
        self.assertNotIn("BlueprintReadOnly", locked_only)
        self.assertNotIn('Category="Skyguard|Theater"', locked_only)
        self.assertNotIn(STOP_BEFORE_APPLY_WORLD_MOOD, locked_only)
        self.assertNotIn(STOP_BEFORE_APPLY_WORLD_MOOD_WEATHER, locked_only)
        self.assertNotIn(GUIDED_LOCK_STRUCT, locked_only)
        self.assertNotIn(WEATHER_PROFILE_STRUCT, locked_only)
        self.assertNotIn(CAMPAIGN_MISSION_SPEC, locked_only)
        self.assertNotIn(THEATER_KIT_SPEC, locked_only)
        self.assertNotIn(THEATER_KIT_ACTOR, locked_only)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, locked_only)


if __name__ == "__main__":
    unittest.main()
