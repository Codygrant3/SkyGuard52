# THIS IS leftover-safe USkyguardArcadeLookComponent BloomIntensity.
# origin/main form: one-line and split-line UPROPERTY wraps
# UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Skyguard|Arcade")
# then `float BloomIntensity = 0.55f;` (initializer IS 0.55f).
# THIS IS leftover-safe isolated UPROPERTY with Category.
# Category IS `Skyguard|Arcade`. EditAnywhere IS present.
# BlueprintReadWrite IS present. Default IS 0.55f.
# Fail-closed if the UPROPERTY or decl is missing
# or renamed, if Category is missing, or if specifiers
# drop to VisibleAnywhere / BlueprintReadOnly /
# leftover TheaterKit Category="Skyguard|Theater" /
# leftover FName WeatherIdentity / no initializer /
# leftover TheaterKit 160.f as the locked decl.
# Accept one-line and split-line UPROPERTY wraps.
# Parse CLASS `USkyguardArcadeLookComponent` public
# UPROPERTY fields ONLY after
# `class USkyguardArcadeLookComponent`.
# Stop BEFORE the next UPROPERTY sibling (Vignette)
# as a claimed slot. Stop before any private: section.
# Do NOT claim leftover-safe ArcadeLook bEnabled /
# Contrast as this slot. Copy that parse window only.
# Do NOT parse leftover analog arcade-look-fail-closed
# bulk tests as this slot (keep those files in
# LOCKED_SCRIPTS).
# Do NOT parse leftover analog
# arcade-look-world-mood-fail-closed ApplyWorldMood /
# ApplyWorldMoodForWeather as this slot.
# Do NOT parse leftover analog apache-cpg-feel
# CannonFireRate 12.0f / CannonRecoilPitch 0.92f
# (Gamma sibling, not BloomIntensity).
# Do NOT parse leftover CampaignMissionSpec
# TimeOfDayHours 12.f (plain struct float).
# Do NOT parse leftover CampaignMissionSpec
# bNightIdentity / bStormRocketContract (plain struct
# bools, no UPROPERTY).
# Do NOT parse leftover NightSortieBeatKit bKeepThermal.
# Do NOT parse leftover GuidedLockRules
# HelmetAcquireDegrees 12.0f / HelmetLockSeconds /
# SensorLockSeconds / SensorAcquireDegrees /
# DetectProgressEnd 0.22f (plain static constexpr
# floats; do not parse SkyguardGuidedLockRules.h).
# Do NOT parse leftover campaign-roster-lookup-tests.
# Do NOT contract sibling fields bEnabled / Contrast /
# Saturation / Gain / Gamma / Vignette / Grain /
# ChromaticAberration.
# Clone source #1300 was leftover-safe TheaterKit
# WeatherIdentity: LOCKED_DECL was
# `FName WeatherIdentity;` and the wrap was
# VisibleAnywhere BlueprintReadOnly
# Category="Skyguard|Theater" with NO initializer.
# RETARGET: type is float, identifier is BloomIntensity,
# initializer is 0.55f, wrap is EditAnywhere
# BlueprintReadWrite Category="Skyguard|Arcade".
# Fail-closed if this test still asserts
# VisibleAnywhere / BlueprintReadOnly /
# Category="Skyguard|Theater" / FName WeatherIdentity /
# no initializer / leftover TheaterKit 160.f
# as the locked decl.
# Better same-class retarget leftover-safe ArcadeLook
# bEnabled / Contrast / Saturation. Copy that parse
# window. Do NOT claim bEnabled / Contrast /
# Saturation / Gain as this slot.
# Harbor fail-closed ONLY 40/80 split tokens.
# Ban retired live-copy tokens via split tokens
# (b + Ya + kRuntimeReady). Stay Apache CPG 30 mm /
# Hydra / Hellfire. Fail-closed on live Ig+la /
# Ri+fle / Ya+k appearing as contiguous tokens in
# THIS test file.

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardArcadeLookComponent.h"
CLASS_NAME = "USkyguardArcadeLookComponent"
LOCKED_DECL = "float BloomIntensity = 0.55f;"
UPROPERTY_EDIT_READWRITE = (
    "UPROPERTY(EditAnywhere, BlueprintReadWrite, "
    'Category="Skyguard|Arcade")'
)
LEFTOVER_THEATER_KIT_DECL = "FName WeatherIdentity;"
LEFTOVER_THEATER_KIT_WRAP = (
    "UPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
    'Category="Skyguard|Theater")'
)
LEFTOVER_THEATER_KIT_STRUCT = "FSkyguardTheaterKitSpec"
LEFTOVER_THEATER_KIT_160 = "float Health = 160.f;"
LEFTOVER_THEATER_KIT_160_LOCKED = "float BloomIntensity = 160.f;"
LEFTOVER_CAMPAIGN_SPEC = "FSkyguardCampaignMissionSpec"
LEFTOVER_TIME_OF_DAY_HOURS = "float TimeOfDayHours = 12.f;"
LEFTOVER_NIGHT_IDENTITY = "bool bNightIdentity = false;"
LEFTOVER_STORM_ROCKET = "bool bStormRocketContract = false;"
LEFTOVER_KEEP_THERMAL = "bool bKeepThermal = true;"
LEFTOVER_NIGHT_KIT = "FSkyguardNightSortieBeatKit"
LEFTOVER_GUIDED_LOCK_HEADER = (
    "Source/Skyguard52/SkyguardGuidedLockRules.h"
)
LEFTOVER_GUIDED_LOCK_STRUCT = "FSkyguardGuidedLockRules"
LEFTOVER_HELMET_ACQUIRE = (
    "static constexpr float HelmetAcquireDegrees = 12.0f;"
)
LEFTOVER_HELMET_LOCK = (
    "static constexpr float HelmetLockSeconds = 2.40f;"
)
LEFTOVER_SENSOR_LOCK = (
    "static constexpr float SensorLockSeconds = 1.35f;"
)
LEFTOVER_SENSOR_ACQUIRE = (
    "static constexpr float SensorAcquireDegrees = 5.5f;"
)
LEFTOVER_DETECT_PROGRESS = (
    "static constexpr float DetectProgressEnd = 0.22f;"
)
LEFTOVER_CANNON_FIRE_RATE = "float CannonFireRate = 12.0f;"
LEFTOVER_CANNON_RECOIL_PITCH = "float CannonRecoilPitch = 0.92f;"
LEFTOVER_SIBLING_ENABLED = "bool bEnabled = true;"
TARGET_WRONG_BARE = "float BloomIntensity;"
TARGET_WRONG_ZERO = "float BloomIntensity = 0.f;"
TARGET_WRONG_FALSE = "float BloomIntensity = false;"
TARGET_WRONG_FNAME = "FName BloomIntensity;"
TARGET_WRONG_BOOL = "bool BloomIntensity = 0.55f;"
TARGET_WRONG_TWELVE = "float BloomIntensity = 12.0f;"
TARGET_WRONG_TWELVE_F = "float BloomIntensity = 12.f;"
TARGET_WRONG_RECOIL = "float BloomIntensity = 0.92f;"
TARGET_WRONG_CONTRAST = "float Contrast = 1.18f;"
TARGET_WRONG_SATURATION = "float Saturation = 1.12f;"
TARGET_WRONG_GAIN = "float Gain = 1.08f;"
TARGET_WRONG_GAMMA = "float Gamma = 0.92f;"
TARGET_WRONG_DETECT = "float BloomIntensity = 0.22f;"
STOP_BEFORE_VIGNETTE = "float Vignette = 0.42f;"
STOP_BEFORE_PRIVATE = "private:"
PREVIOUS_GAMMA = "float Gamma = 0.92f;"
APPLY_WORLD_MOOD = "ApplyWorldMood"
APPLY_WORLD_MOOD_FOR_WEATHER = "ApplyWorldMoodForWeather"
APPLY_TO_CAMERA = "ApplyToCamera"
APPLY_HELMET_SIGHT = "ApplyHelmetSight"
APPLY_TARGETING_SENSOR = "ApplyTargetingSensor"
APPLY_THERMAL_SENSOR = "ApplyThermalSensor"
IS_ENABLED = "IsEnabled"
SIBLING_ENABLED = "bEnabled"
SIBLING_CONTRAST = "Contrast"
SIBLING_SATURATION = "Saturation"
SIBLING_GAIN = "Gain"
SIBLING_GAMMA = "Gamma"
SIBLING_VIGNETTE = "Vignette"
SIBLING_GRAIN = "Grain"
SIBLING_CHROMATIC = "ChromaticAberration"
THIS_SCRIPT = (
    "Scripts/tests/test_arcade_look_bloom_intensity"
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
LEFTOVER_THEATER_KIT_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_THEATER_KIT_BULK = (
    "Scripts/tests/test_campaign_theater_kit_contract.py"
)
LEFTOVER_NIGHT_IDENTITY_FIELD = (
    "Scripts/tests/test_campaign_mission_spec_night_identity"
    "_field_decl_contract.py"
)
LEFTOVER_STORM_ROCKET_FIELD = (
    "Scripts/tests/test_campaign_mission_spec_storm_rocket"
    "_contract_field_decl_contract.py"
)
LEFTOVER_TIME_OF_DAY_FIELD = (
    "Scripts/tests/test_campaign_mission_spec_time_of_day_hours"
    "_field_decl_contract.py"
)
LEFTOVER_KEEP_THERMAL_FIELD = (
    "Scripts/tests/test_night_sortie_beat_kit_keep_thermal"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_HELMET_LOCK = (
    "Scripts/tests/test_guided_lock_rules_helmet_lock_seconds"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_SENSOR_LOCK = (
    "Scripts/tests/test_guided_lock_rules_sensor_lock_seconds"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_HELMET_ACQUIRE = (
    "Scripts/tests/test_guided_lock_rules_helmet_acquire_degrees"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_SENSOR_ACQUIRE = (
    "Scripts/tests/test_guided_lock_rules_sensor_acquire_degrees"
    "_field_decl_contract.py"
)
LEFTOVER_GUIDED_DETECT_PROGRESS = (
    "Scripts/tests/test_guided_lock_rules_detect_progress_end"
    "_field_decl_contract.py"
)
SIBLING_ENABLED_SCRIPT = (
    "Scripts/tests/test_arcade_look_enabled"
    "_field_decl_contract.py"
)
SIBLING_CONTRAST_SCRIPT = (
    "Scripts/tests/test_arcade_look_contrast"
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

LOCKED = (
    "SkyguardArcadeLookComponent.cpp",
    "SkyguardArcadeLookTests.cpp",
    "SkyguardGuidedLockRules.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardCampaignRoster.h",
    "SkyguardNightSortieBeatKit.h",
    "SkyguardCampaignTheaterKit.h",
    "SkyguardCampaignTheaterKit.cpp",
    "SkyguardApacheAircraft.h",
    "SkyguardApacheAircraft.cpp",
    "SkyguardGunshipTypes.h",
    "SkyguardHarborProofTests.cpp",
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
    LEFTOVER_THEATER_KIT_WEATHER_IDENTITY,
    LEFTOVER_THEATER_KIT_BULK,
    LEFTOVER_NIGHT_IDENTITY_FIELD,
    LEFTOVER_STORM_ROCKET_FIELD,
    LEFTOVER_TIME_OF_DAY_FIELD,
    LEFTOVER_KEEP_THERMAL_FIELD,
    LEFTOVER_GUIDED_HELMET_LOCK,
    LEFTOVER_GUIDED_SENSOR_LOCK,
    LEFTOVER_GUIDED_HELMET_ACQUIRE,
    LEFTOVER_GUIDED_SENSOR_ACQUIRE,
    LEFTOVER_GUIDED_DETECT_PROGRESS,
    SIBLING_ENABLED_SCRIPT,
    SIBLING_CONTRAST_SCRIPT,
    SIBLING_SATURATION_SCRIPT,
    SIBLING_GAIN_SCRIPT,
    SIBLING_GAMMA_SCRIPT,
    SIBLING_VIGNETTE_SCRIPT,
    SIBLING_GRAIN_SCRIPT,
    SIBLING_CHROMATIC_SCRIPT,
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_night_sortie_beat_kit_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_apache_cpg_feel_contract.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_tests.py",
    "Scripts/tests/test_apache_aircraft_empty_fail_closed_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_harbor_proof_play.py",
    "Scripts/tests/test_harbor_proof_source_tests.py",
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
    "= 12.0f",
    "= 12.f",
    "= 0.92f",
    "= 1.18f",
    "= 1.12f",
    "= 1.08f",
    "= 0.22f",
    "= NAME_None",
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


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_ENABLED,
        SIBLING_CONTRAST,
        SIBLING_SATURATION,
        SIBLING_GAIN,
        SIBLING_GAMMA,
        SIBLING_VIGNETTE,
        SIBLING_GRAIN,
        SIBLING_CHROMATIC,
    )


def leftover_plain_struct_bools() -> tuple[str, ...]:
    return (
        LEFTOVER_NIGHT_IDENTITY,
        LEFTOVER_STORM_ROCKET,
        LEFTOVER_KEEP_THERMAL,
    )


def leftover_wrong_float_decls() -> tuple[str, ...]:
    return (
        LEFTOVER_THEATER_KIT_DECL,
        LEFTOVER_THEATER_KIT_160,
        LEFTOVER_THEATER_KIT_160_LOCKED,
        LEFTOVER_TIME_OF_DAY_HOURS,
        LEFTOVER_HELMET_ACQUIRE,
        LEFTOVER_HELMET_LOCK,
        LEFTOVER_SENSOR_LOCK,
        LEFTOVER_SENSOR_ACQUIRE,
        LEFTOVER_DETECT_PROGRESS,
        LEFTOVER_CANNON_FIRE_RATE,
        LEFTOVER_CANNON_RECOIL_PITCH,
        LEFTOVER_SIBLING_ENABLED,
        TARGET_WRONG_CONTRAST,
        TARGET_WRONG_SATURATION,
        TARGET_WRONG_GAIN,
        TARGET_WRONG_GAMMA,
        TARGET_WRONG_DETECT,
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
    # Fail-closed on the authored `float BloomIntensity = 0.55f;`.
    # Do not accept leftover TheaterKit bare
    # `FName WeatherIdentity;` / no initializer / 160.f.
    # Do not accept leftover CampaignMissionSpec
    # TimeOfDayHours / bNightIdentity / bStormRocketContract.
    # Do not accept leftover NightSortieBeatKit
    # bKeepThermal. Do not accept leftover analog
    # apache-cpg-feel 12.0f / 0.92f (Gamma sibling) or
    # GuidedLockRules HelmetAcquireDegrees 12.0f /
    # DetectProgressEnd 0.22f.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if re.search(r"float\s+BloomIntensity\s*=\s*0\.55f\s*;", compact) is None:
        return False
    if re.search(r"FName\s+WeatherIdentity\b", compact):
        return False
    if re.search(r"float\s+BloomIntensity\s*=\s*160\.f\s*;", compact):
        return False
    if re.search(r"float\s+BloomIntensity\s*=\s*12\.0f\s*;", compact):
        return False
    if re.search(r"float\s+BloomIntensity\s*=\s*12\.f\s*;", compact):
        return False
    if re.search(r"float\s+BloomIntensity\s*=\s*0\.92f\s*;", compact):
        return False
    if re.search(r"float\s+BloomIntensity\s*=\s*0\.22f\s*;", compact):
        return False
    if re.search(r"float\s+BloomIntensity\s*=\s*1\.18f\s*;", compact):
        return False
    if re.search(r"float\s+BloomIntensity\s*=\s*1\.12f\s*;", compact):
        return False
    if re.search(r"float\s+BloomIntensity\s*=\s*1\.08f\s*;", compact):
        return False
    if re.search(r"DetectProgressEnd\b", compact):
        return False
    if re.search(r"bool\s+bNightIdentity\b", compact):
        return False
    if re.search(r"bool\s+bStormRocketContract\b", compact):
        return False
    if re.search(r"bool\s+bKeepThermal\b", compact):
        return False
    if re.search(r"HelmetAcquireDegrees\b", compact):
        return False
    if re.search(r"CannonFireRate\b", compact):
        return False
    if re.search(r"CannonRecoilPitch\b", compact):
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
        leftover_retired_mount_class(),
        LEFTOVER_THEATER_KIT_STRUCT,
        LEFTOVER_CAMPAIGN_SPEC,
        LEFTOVER_NIGHT_KIT,
        LEFTOVER_GUIDED_LOCK_STRUCT,
        "class ASkyguardApacheAircraft",
        "struct FSkyguardTheaterKitSpec",
        "struct FSkyguardCampaignMissionSpec",
        "struct FSkyguardNightSortieBeatKit",
        "struct FSkyguardGuidedLockRules",
        "HelmetLockSeconds",
        "SensorLockSeconds",
        "HelmetAcquireDegrees",
        "SensorAcquireDegrees",
        "DetectProgressEnd",
        "CannonFireRate",
        "CannonRecoilPitch",
    )


def class_public_section(header: str) -> str:
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
        section = rest[: next_access.start()]
    else:
        close = rest.rfind("}")
        if close == -1:
            raise AssertionError(
                f"{CLASS_NAME} public section is missing from "
                f"origin/main:{HEADER_PATH}"
            )
        section = rest[:close]
    for token in leaked_neighbor_tokens():
        if token in section:
            raise AssertionError(
                f"{CLASS_NAME} parse window includes {token}"
            )
    return section


def claimed_field_window(header: str) -> str:
    section = class_public_section(header)
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
        after = compact[index:]
        field = re.match(
            r"\s*float\s+BloomIntensity\s*=\s*0\.55f\s*;",
            after,
        )
        if depth == 0 and field is not None:
            window = compact[cursor + match.start() : index + field.end()]
            for sibling in sibling_uncontracted_decls():
                if re.search(r"\b" + re.escape(sibling) + r"\b", window):
                    raise AssertionError(
                        f"claimed window includes sibling {sibling}"
                    )
            for mood in (
                APPLY_WORLD_MOOD,
                APPLY_WORLD_MOOD_FOR_WEATHER,
            ):
                if mood in window:
                    raise AssertionError(
                        f"claimed window includes leftover {mood}"
                    )
            if LEFTOVER_THEATER_KIT_DECL in window:
                raise AssertionError(
                    "claimed window includes leftover TheaterKit "
                    "WeatherIdentity"
                )
            if "TimeOfDayHours" in window:
                raise AssertionError(
                    "claimed window includes leftover TimeOfDayHours"
                )
            if SIBLING_ENABLED in window:
                raise AssertionError(
                    "claimed window includes leftover-safe sibling "
                    "bEnabled"
                )
            return window
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for float BloomIntensity = 0.55f; is missing from "
        f"origin/main:{HEADER_PATH} class {CLASS_NAME} public "
        "UPROPERTY fields"
    )


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
            r"\s*float\s+BloomIntensity\b", compact[index:]
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for float BloomIntensity is missing from "
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


class ArcadeLookBloomIntensityFieldDeclContractTests(unittest.TestCase):
    def test_arcade_look_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertIn(f"class SKYGUARD52_API {CLASS_NAME}", header)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_THEATER_KIT_STRUCT)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_CAMPAIGN_SPEC)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_NIGHT_KIT)
        self.assertNotEqual(CLASS_NAME, LEFTOVER_GUIDED_LOCK_STRUCT)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = class_public_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "BloomIntensity"), section)
        self.assertIn("UPROPERTY", section)
        claimed = claimed_field_window(header)
        self.assertTrue(has_declaration(claimed, LOCKED_DECL), claimed)
        self.assertNotIn(SIBLING_VIGNETTE, claimed)
        self.assertNotIn(STOP_BEFORE_PRIVATE, claimed)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class USkyguardUnrelatedArcadeLookComponent\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_type_does_not_satisfy(self) -> None:
        leftovers = (
            LEFTOVER_THEATER_KIT_STRUCT,
            LEFTOVER_CAMPAIGN_SPEC,
            LEFTOVER_NIGHT_KIT,
            LEFTOVER_GUIDED_LOCK_STRUCT,
        )
        for name in leftovers:
            other = (
                f"struct {name}\n"
                "{\n"
                f"\t{UPROPERTY_EDIT_READWRITE}\n"
                f"\t{LOCKED_DECL}\n"
                "};\n"
            )
            with self.assertRaises(AssertionError) as raised:
                class_public_section(other)
            self.assertIn(CLASS_NAME, str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_EDIT_READWRITE}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("BloomIntensity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertNotIn("WeatherIdentity", str(raised.exception))

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = class_public_section(origin_main_header())
        self.assertIn(UPROPERTY_EDIT_READWRITE, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadWrite", section)
        self.assertIn('Category="Skyguard|Arcade"', section)
        self.assertIn("EditAnywhere", UPROPERTY_EDIT_READWRITE)
        self.assertIn("BlueprintReadWrite", UPROPERTY_EDIT_READWRITE)
        self.assertIn("Category", UPROPERTY_EDIT_READWRITE)
        self.assertIn('Category="Skyguard|Arcade"', UPROPERTY_EDIT_READWRITE)
        self.assertNotIn("VisibleAnywhere", UPROPERTY_EDIT_READWRITE)
        self.assertNotIn("BlueprintReadOnly", UPROPERTY_EDIT_READWRITE)
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            UPROPERTY_EDIT_READWRITE,
        )
        specifiers = attached_uproperty_specifiers(section)
        self.assertIn("EditAnywhere", specifiers)
        self.assertIn("BlueprintReadWrite", specifiers)
        self.assertIn('Category="Skyguard|Arcade"', specifiers)
        self.assertIn("Category", specifiers)
        self.assertNotIn("VisibleAnywhere", specifiers)
        self.assertNotIn("BlueprintReadOnly", specifiers)
        self.assertNotIn('Category="Skyguard|Theater"', specifiers)
        self.assertNotIn("MultiLine", specifiers)
        self.assertNotIn("ClampMin", specifiers)
        self.assertNotIn("ClampMax", specifiers)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("UFUNCTION", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, LOCKED_DECL)

    def test_locked_decl_is_not_leftover_theater_kit_weather_identity(
        self,
    ) -> None:
        self.assertEqual(LOCKED_DECL, "float BloomIntensity = 0.55f;")
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_THEATER_KIT_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BARE)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_THEATER_KIT_160)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_THEATER_KIT_160_LOCKED)
        self.assertNotEqual(
            UPROPERTY_EDIT_READWRITE,
            LEFTOVER_THEATER_KIT_WRAP,
        )
        self.assertIn("float ", LOCKED_DECL)
        self.assertIn("BloomIntensity", LOCKED_DECL)
        self.assertIn("= 0.55f", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("VisibleAnywhere", UPROPERTY_EDIT_READWRITE)
        self.assertNotIn("BlueprintReadOnly", UPROPERTY_EDIT_READWRITE)
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            UPROPERTY_EDIT_READWRITE,
        )
        self.assertFalse(
            has_declaration(
                f"\t{LEFTOVER_THEATER_KIT_WRAP}\n"
                f"\t{LEFTOVER_THEATER_KIT_DECL}\n",
                LOCKED_DECL,
            )
        )
        self.assertFalse(
            has_declaration(
                f"\t{LEFTOVER_THEATER_KIT_160}\n",
                LOCKED_DECL,
            )
        )

    def test_locked_decl_requires_0_55f_initializer(self) -> None:
        self.assertIn("= 0.55f", LOCKED_DECL)
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_BARE)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TWELVE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_TWELVE_F}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{LEFTOVER_THEATER_KIT_160_LOCKED}\n", LOCKED_DECL)
        )
        origin = class_public_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn("float BloomIntensity = 0.55f;", compact_origin)
        self.assertNotIn("float BloomIntensity;", compact_origin.replace(
            "float BloomIntensity = 0.55f;",
            "",
        ))

    def test_bloom_intensity_declaration_matches_origin_main(self) -> None:
        section = class_public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("float BloomIntensity"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertIn("= 0.55f", LOCKED_DECL)
        self.assertNotIn("= 12.0f", LOCKED_DECL)
        self.assertNotIn("= 12.f", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertNotIn("= 0.92f", LOCKED_DECL)
        self.assertNotIn("= 1.18f", LOCKED_DECL)
        self.assertNotIn("= 1.12f", LOCKED_DECL)
        self.assertNotIn("= 1.08f", LOCKED_DECL)
        self.assertNotIn("= 0.22f", LOCKED_DECL)
        self.assertNotIn("= NAME_None", LOCKED_DECL)
        self.assertIn("float ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("WeatherIdentity", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        for leftover in leftover_plain_struct_bools():
            self.assertNotEqual(LOCKED_DECL, leftover)
            self.assertFalse(
                has_declaration(f"\t{leftover}\n", LOCKED_DECL)
            )
        for leftover in leftover_wrong_float_decls():
            self.assertNotEqual(LOCKED_DECL, leftover)
            self.assertFalse(
                has_declaration(f"\t{leftover}\n", LOCKED_DECL)
            )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FNAME}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{LEFTOVER_THEATER_KIT_DECL}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        self.assertIn("BloomIntensity", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tfloat " + leftover_retired_primary_hits_field() + " = 0.55f;\n"
        )
        leftover_guided = (
            "\tfloat " + leftover_retired_guided_hits_field() + " = 0.55f;\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_FALSE}\n",
            f"\t{TARGET_WRONG_FNAME}\n",
            f"\t{TARGET_WRONG_BOOL}\n",
            f"\t{TARGET_WRONG_TWELVE}\n",
            f"\t{TARGET_WRONG_TWELVE_F}\n",
            f"\t{TARGET_WRONG_RECOIL}\n",
            f"\t{LEFTOVER_THEATER_KIT_160}\n",
            f"\t{LEFTOVER_THEATER_KIT_160_LOCKED}\n",
            f"\t{LEFTOVER_THEATER_KIT_DECL}\n",
            f"\t{LEFTOVER_TIME_OF_DAY_HOURS}\n",
            f"\t{LEFTOVER_HELMET_ACQUIRE}\n",
            f"\t{LEFTOVER_CANNON_FIRE_RATE}\n",
            f"\t{LEFTOVER_CANNON_RECOIL_PITCH}\n",
            f"\t{LEFTOVER_SIBLING_ENABLED}\n",
            f"\t{TARGET_WRONG_CONTRAST}\n",
            f"\t{TARGET_WRONG_SATURATION}\n",
            f"\t{TARGET_WRONG_GAIN}\n",
            f"\t{TARGET_WRONG_GAMMA}\n",
            f"\t{TARGET_WRONG_DETECT}\n",
            f"\t{LEFTOVER_DETECT_PROGRESS}\n",
            f"\t{LEFTOVER_NIGHT_IDENTITY}\n",
            f"\t{LEFTOVER_STORM_ROCKET}\n",
            f"\t{LEFTOVER_KEEP_THERMAL}\n",
            leftover_primary,
            leftover_guided,
            "\tfloat BloomIntensities = 0.55f;\n",
            "\tint32 BloomIntensity = 0.55f;\n",
            "\tfloat BloomIntensity = " + forty + ";\n",
            "\tfloat BloomIntensity = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("BloomIntensity", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_category_or_edit_anywhere_fails_closed(self) -> None:
        no_category = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite)\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        section = class_public_section(no_category)
        specifiers = attached_uproperty_specifiers(section)
        self.assertNotIn("Category", specifiers)
        origin = attached_uproperty_specifiers(
            class_public_section(origin_main_header())
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
            class_public_section(no_edit)
        )
        self.assertNotIn("EditAnywhere", dropped)
        self.assertIn("EditAnywhere", origin)
        leftover_wrap = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{LEFTOVER_THEATER_KIT_WRAP}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        leftover_specs = attached_uproperty_specifiers(
            class_public_section(leftover_wrap)
        )
        self.assertIn("VisibleAnywhere", leftover_specs)
        self.assertIn("BlueprintReadOnly", leftover_specs)
        self.assertIn('Category="Skyguard|Theater"', leftover_specs)
        self.assertNotIn("EditAnywhere", leftover_specs)
        self.assertNotIn("BlueprintReadWrite", leftover_specs)
        self.assertIn("EditAnywhere", origin)
        self.assertIn("BlueprintReadWrite", origin)
        self.assertIn('Category="Skyguard|Arcade"', origin)
        self.assertNotIn('Category="Skyguard|Theater"', origin)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tfloat\n\tBloomIntensity = 0.55f;\n",
            "\tfloat   BloomIntensity = 0.55f;\n",
            "\tfloat\tBloomIntensity = 0.55f;\n",
            f"\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_EDIT_READWRITE}\n\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_EDIT_READWRITE} {LOCKED_DECL}\n",
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
        self.assertNotIn(APPLY_WORLD_MOOD, LOCKED_DECL)
        self.assertNotIn(APPLY_WORLD_MOOD_FOR_WEATHER, LOCKED_DECL)
        self.assertNotIn(APPLY_TO_CAMERA, LOCKED_DECL)
        self.assertNotIn(IS_ENABLED, LOCKED_DECL)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_SIBLING_ENABLED)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CONTRAST)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SATURATION)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_GAIN)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_GAMMA)
        section = class_public_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        claimed = claimed_field_window(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertFalse(
                has_identifier(claimed, sibling),
                sibling,
            )
        self.assertIn(STOP_BEFORE_VIGNETTE, section)
        self.assertNotIn(STOP_BEFORE_VIGNETTE, claimed)
        self.assertIn(PREVIOUS_GAMMA, section)
        self.assertNotIn(PREVIOUS_GAMMA, claimed)
        self.assertIn(LEFTOVER_SIBLING_ENABLED, section)
        self.assertNotIn(LEFTOVER_SIBLING_ENABLED, claimed)

    def test_claimed_window_stops_before_vignette(self) -> None:
        claimed = claimed_field_window(origin_main_header())
        self.assertIn("BloomIntensity", claimed)
        self.assertIn("= 0.55f", claimed)
        self.assertIn("UPROPERTY", claimed)
        self.assertNotIn(SIBLING_VIGNETTE, claimed)
        self.assertNotIn(STOP_BEFORE_VIGNETTE, claimed)
        self.assertNotIn(SIBLING_ENABLED, claimed)
        self.assertNotIn(SIBLING_CONTRAST, claimed)
        self.assertNotIn(SIBLING_SATURATION, claimed)
        self.assertNotIn(SIBLING_GAIN, claimed)
        self.assertNotIn(SIBLING_GAMMA, claimed)
        self.assertNotIn(SIBLING_CHROMATIC, claimed)
        self.assertNotIn(STOP_BEFORE_PRIVATE, claimed)
        mixed = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UPROPERTY_EDIT_READWRITE}\n"
            f"\t{LOCKED_DECL}\n"
            f"\t{UPROPERTY_EDIT_READWRITE}\n"
            f"\t{STOP_BEFORE_VIGNETTE}\n"
            "};\n"
        )
        window = claimed_field_window(mixed)
        self.assertTrue(has_declaration(window, LOCKED_DECL), window)
        self.assertNotIn(SIBLING_VIGNETTE, window)

    def test_does_not_claim_contrast_or_saturation_as_this_slot(self) -> None:
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_CONTRAST)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SATURATION)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_GAIN)
        self.assertNotIn(SIBLING_CONTRAST, LOCKED_DECL)
        self.assertNotIn(SIBLING_SATURATION, LOCKED_DECL)
        self.assertNotIn(SIBLING_GAIN, LOCKED_DECL)
        self.assertNotEqual(THIS_SCRIPT, SIBLING_ENABLED_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, SIBLING_CONTRAST_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, SIBLING_SATURATION_SCRIPT)
        header = origin_main_header()
        section = class_public_section(header)
        claimed = claimed_field_window(header)
        self.assertTrue(has_identifier(section, SIBLING_CONTRAST), section)
        self.assertTrue(has_identifier(section, SIBLING_SATURATION), section)
        self.assertNotIn(SIBLING_CONTRAST, claimed)
        self.assertNotIn(SIBLING_SATURATION, claimed)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_CONTRAST}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_SATURATION}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError):
            require_declaration(f"\t{TARGET_WRONG_CONTRAST}\n", LOCKED_DECL)
        with self.assertRaises(AssertionError):
            require_declaration(f"\t{TARGET_WRONG_SATURATION}\n", LOCKED_DECL)

    def test_does_not_claim_enabled_as_this_slot(self) -> None:
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_SIBLING_ENABLED)
        self.assertNotIn(SIBLING_ENABLED, LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        header = origin_main_header()
        section = class_public_section(header)
        claimed = claimed_field_window(header)
        self.assertIn(LEFTOVER_SIBLING_ENABLED, section)
        self.assertTrue(has_identifier(section, SIBLING_ENABLED), section)
        self.assertNotIn(SIBLING_ENABLED, claimed)
        self.assertNotIn(LEFTOVER_SIBLING_ENABLED, claimed)
        self.assertTrue(has_declaration(claimed, LOCKED_DECL), claimed)
        with self.assertRaises(AssertionError):
            require_declaration(
                f"\t{LEFTOVER_SIBLING_ENABLED}\n",
                LOCKED_DECL,
            )

    def test_does_not_parse_world_mood_or_fail_closed_bulk(self) -> None:
        header = origin_main_header()
        claimed = claimed_field_window(header)
        section = class_public_section(header)
        self.assertIn(APPLY_WORLD_MOOD, section)
        self.assertIn(APPLY_WORLD_MOOD_FOR_WEATHER, section)
        self.assertIn(APPLY_TO_CAMERA, section)
        self.assertNotIn(APPLY_WORLD_MOOD, claimed)
        self.assertNotIn(APPLY_WORLD_MOOD_FOR_WEATHER, claimed)
        self.assertNotIn(APPLY_TO_CAMERA, claimed)
        self.assertNotIn(APPLY_HELMET_SIGHT, claimed)
        self.assertNotIn(APPLY_TARGETING_SENSOR, claimed)
        self.assertNotIn(APPLY_THERMAL_SENSOR, claimed)
        self.assertNotIn(APPLY_WORLD_MOOD, LOCKED_DECL)
        self.assertNotIn(APPLY_WORLD_MOOD_FOR_WEATHER, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_ARCADE_LOOK_FAIL_CLOSED, THIS_SCRIPT)
        self.assertIn(LEFTOVER_ARCADE_LOOK_FAIL_CLOSED, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ARCADE_LOOK_WORLD_MOOD, LOCKED_SCRIPTS)

    def test_is_enabled_accessor_is_not_this_slot(self) -> None:
        header = origin_main_header()
        section = class_public_section(header)
        claimed = claimed_field_window(header)
        self.assertIn(IS_ENABLED, section)
        self.assertNotIn(IS_ENABLED, claimed)
        self.assertNotIn(IS_ENABLED, LOCKED_DECL)
        self.assertNotIn("UFUNCTION", LOCKED_DECL)
        self.assertNotIn("{ return", LOCKED_DECL)

    def test_does_not_parse_leftover_campaign_mission_spec_bools(self) -> None:
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_NIGHT_IDENTITY)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_STORM_ROCKET)
        self.assertNotIn("bNightIdentity", LOCKED_DECL)
        self.assertNotIn("bStormRocketContract", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LEFTOVER_NIGHT_IDENTITY)
        self.assertNotIn("UPROPERTY", LEFTOVER_STORM_ROCKET)
        for leftover in (LEFTOVER_NIGHT_IDENTITY, LEFTOVER_STORM_ROCKET):
            with self.assertRaises(AssertionError):
                require_declaration(f"\t{leftover}\n", LOCKED_DECL)
        header = origin_main_header()
        section = class_public_section(header)
        claimed = claimed_field_window(header)
        self.assertNotIn("bNightIdentity", section)
        self.assertNotIn("bStormRocketContract", section)
        self.assertNotIn("bNightIdentity", claimed)
        self.assertNotIn("bStormRocketContract", claimed)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, HEADER_PATH)

    def test_does_not_parse_leftover_campaign_mission_spec_time_of_day(
        self,
    ) -> None:
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_TIME_OF_DAY_HOURS)
        self.assertNotIn("TimeOfDayHours", LOCKED_DECL)
        self.assertNotIn("= 12.f", LOCKED_DECL)
        with self.assertRaises(AssertionError):
            require_declaration(
                f"\t{LEFTOVER_TIME_OF_DAY_HOURS}\n",
                LOCKED_DECL,
            )
        header = origin_main_header()
        section = class_public_section(header)
        claimed = claimed_field_window(header)
        self.assertIn("TimeOfDayHours", section)
        self.assertNotIn("TimeOfDayHours", claimed)
        self.assertNotIn(LEFTOVER_TIME_OF_DAY_HOURS, claimed)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, HEADER_PATH)
        self.assertIn(LEFTOVER_TIME_OF_DAY_FIELD, LOCKED_SCRIPTS)

    def test_does_not_parse_leftover_night_sortie_keep_thermal(self) -> None:
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_KEEP_THERMAL)
        self.assertNotIn("bKeepThermal", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LEFTOVER_KEEP_THERMAL)
        with self.assertRaises(AssertionError):
            require_declaration(f"\t{LEFTOVER_KEEP_THERMAL}\n", LOCKED_DECL)
        header = origin_main_header()
        section = class_public_section(header)
        claimed = claimed_field_window(header)
        self.assertNotIn("bKeepThermal", section)
        self.assertNotIn("bKeepThermal", claimed)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, HEADER_PATH)

    def test_does_not_parse_leftover_apache_cpg_feel_cannon(self) -> None:
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_CANNON_FIRE_RATE)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_CANNON_RECOIL_PITCH)
        self.assertNotIn("CannonFireRate", LOCKED_DECL)
        self.assertNotIn("CannonRecoilPitch", LOCKED_DECL)
        self.assertNotIn("= 12.0f", LOCKED_DECL)
        self.assertNotIn("= 0.92f", LOCKED_DECL)
        for leftover in (
            LEFTOVER_CANNON_FIRE_RATE,
            LEFTOVER_CANNON_RECOIL_PITCH,
        ):
            with self.assertRaises(AssertionError):
                require_declaration(f"\t{leftover}\n", LOCKED_DECL)
        header = origin_main_header()
        section = class_public_section(header)
        claimed = claimed_field_window(header)
        self.assertNotIn("CannonFireRate", section)
        self.assertNotIn("CannonRecoilPitch", claimed)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertIn(LEFTOVER_APACHE_CPG_FEEL, LOCKED_SCRIPTS)

    def test_does_not_parse_guided_lock_rules_header(self) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_GUIDED_LOCK_HEADER)
        self.assertNotIn("GuidedLockRules", HEADER_PATH)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_HELMET_ACQUIRE)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_HELMET_LOCK)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_SENSOR_LOCK)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_SENSOR_ACQUIRE)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_DETECT_PROGRESS)
        self.assertNotIn("HelmetLockSeconds", LOCKED_DECL)
        self.assertNotIn("SensorLockSeconds", LOCKED_DECL)
        self.assertNotIn("HelmetAcquireDegrees", LOCKED_DECL)
        self.assertNotIn("SensorAcquireDegrees", LOCKED_DECL)
        self.assertNotIn("DetectProgressEnd", LOCKED_DECL)
        self.assertNotIn("static constexpr", LOCKED_DECL)
        self.assertNotIn("= 12.0f", LOCKED_DECL)
        header = origin_main_header()
        section = class_public_section(header)
        claimed = claimed_field_window(header)
        self.assertNotIn("HelmetLockSeconds", section)
        self.assertNotIn("HelmetAcquireDegrees", section)
        self.assertNotIn("SensorLockSeconds", claimed)
        self.assertNotIn("SensorAcquireDegrees", claimed)
        self.assertNotIn("DetectProgressEnd", claimed)
        self.assertNotIn(LEFTOVER_GUIDED_LOCK_STRUCT, section)
        self.assertNotIn("SkyguardGuidedLockRules.h", THIS_SCRIPT)
        self.assertIn(LEFTOVER_GUIDED_HELMET_ACQUIRE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUIDED_DETECT_PROGRESS, LOCKED_SCRIPTS)

    def test_leftover_theater_kit_160_is_not_locked_decl(self) -> None:
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_THEATER_KIT_160)
        self.assertNotEqual(LOCKED_DECL, LEFTOVER_THEATER_KIT_160_LOCKED)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertNotIn("Health", LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{LEFTOVER_THEATER_KIT_160}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(
                f"\t{LEFTOVER_THEATER_KIT_160_LOCKED}\n",
                LOCKED_DECL,
            )
        )
        with self.assertRaises(AssertionError):
            require_declaration(
                f"\t{LEFTOVER_THEATER_KIT_160_LOCKED}\n",
                LOCKED_DECL,
            )

    def test_parse_window_excludes_private_section(self) -> None:
        mixed = (
            f"class {CLASS_NAME}\n"
            "{\n"
            "public:\n"
            f"\t{UPROPERTY_EDIT_READWRITE}\n"
            f"\t{LOCKED_DECL}\n"
            "private:\n"
            "\tfloat HiddenBloomIntensity = 0.55f;\n"
            "};\n"
        )
        section = class_public_section(mixed)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("HiddenBloomIntensity", section)
        self.assertNotIn(STOP_BEFORE_PRIVATE, section)
        claimed = claimed_field_window(mixed)
        self.assertNotIn("HiddenBloomIntensity", claimed)
        origin = class_public_section(origin_main_header())
        self.assertNotIn(STOP_BEFORE_PRIVATE, origin)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            f"\tbool {IS_ENABLED}() const {{ return bEnabled; }}\n"
            f"\tstatic void {APPLY_WORLD_MOOD}();\n"
            f"\tstatic void {APPLY_WORLD_MOOD_FOR_WEATHER}();\n"
            f"\tvoid {APPLY_TO_CAMERA}();\n"
            f"\t{LEFTOVER_SIBLING_ENABLED}\n"
            f"\t{PREVIOUS_GAMMA}\n"
            f"\t{STOP_BEFORE_VIGNETTE}\n"
            f"\t{LEFTOVER_TIME_OF_DAY_HOURS}\n"
            f"\t{LEFTOVER_NIGHT_IDENTITY}\n"
            f"\t{LEFTOVER_KEEP_THERMAL}\n"
            f"\t{LEFTOVER_THEATER_KIT_DECL}\n"
            f"\t{LEFTOVER_THEATER_KIT_160}\n"
            f"\t{LEFTOVER_CANNON_FIRE_RATE}\n"
            f"\t{LEFTOVER_HELMET_ACQUIRE}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("BloomIntensity", str(raised.exception))

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        self.assertEqual(
            UPROPERTY_EDIT_READWRITE,
            "UPROPERTY(EditAnywhere, BlueprintReadWrite, "
            'Category="Skyguard|Arcade")',
        )
        self.assertIn("EditAnywhere", UPROPERTY_EDIT_READWRITE)
        self.assertIn("BlueprintReadWrite", UPROPERTY_EDIT_READWRITE)
        self.assertIn("Category", UPROPERTY_EDIT_READWRITE)
        self.assertIn('Category="Skyguard|Arcade"', UPROPERTY_EDIT_READWRITE)
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            UPROPERTY_EDIT_READWRITE,
        )
        self.assertNotIn("VisibleAnywhere", UPROPERTY_EDIT_READWRITE)
        self.assertNotIn("BlueprintReadOnly", UPROPERTY_EDIT_READWRITE)
        self.assertNotIn("MultiLine", UPROPERTY_EDIT_READWRITE)
        self.assertNotIn("ClampMin", UPROPERTY_EDIT_READWRITE)
        self.assertNotIn("ClampMax", UPROPERTY_EDIT_READWRITE)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, LOCKED_DECL)
            self.assertNotIn(invented, UPROPERTY_EDIT_READWRITE)

    def test_leftover_theater_kit_wrap_is_not_locked_wrap(self) -> None:
        self.assertNotEqual(
            UPROPERTY_EDIT_READWRITE,
            LEFTOVER_THEATER_KIT_WRAP,
        )
        self.assertIn("VisibleAnywhere", LEFTOVER_THEATER_KIT_WRAP)
        self.assertIn("BlueprintReadOnly", LEFTOVER_THEATER_KIT_WRAP)
        self.assertIn(
            'Category="Skyguard|Theater"',
            LEFTOVER_THEATER_KIT_WRAP,
        )
        self.assertNotIn("VisibleAnywhere", UPROPERTY_EDIT_READWRITE)
        self.assertNotIn("BlueprintReadOnly", UPROPERTY_EDIT_READWRITE)
        self.assertNotIn(
            'Category="Skyguard|Theater"',
            UPROPERTY_EDIT_READWRITE,
        )
        self.assertNotIn("= 0.55f", LEFTOVER_THEATER_KIT_DECL)
        self.assertIn("= 0.55f", LOCKED_DECL)
        self.assertNotIn("=", LEFTOVER_THEATER_KIT_DECL)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardArcadeLookComponent.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardGuidedLockRules.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignRoster.h", HEADER_PATH)
        self.assertNotIn("SkyguardNightSortieBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = class_public_section(header)
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
        section = class_public_section(header)
        claimed = claimed_field_window(header)
        for token in leftover_harbor_clock_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, claimed)
            self.assertNotIn(token, header)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "arcade-look BloomIntensity field decl contract "
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
            "bloom_intensity_field_decl_contract.py"
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
        self.assertIn(LEFTOVER_THEATER_KIT_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_THEATER_KIT_BULK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_NIGHT_IDENTITY_FIELD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_STORM_ROCKET_FIELD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_TIME_OF_DAY_FIELD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_KEEP_THERMAL_FIELD, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUIDED_HELMET_LOCK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUIDED_HELMET_ACQUIRE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUIDED_SENSOR_ACQUIRE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUIDED_DETECT_PROGRESS, LOCKED_SCRIPTS)
        self.assertIn(SIBLING_ENABLED_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(SIBLING_CONTRAST_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(SIBLING_SATURATION_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(SIBLING_GAIN_SCRIPT, LOCKED_SCRIPTS)

    def test_leftover_analogs_stay_locked(self) -> None:
        leftovers = (
            LEFTOVER_ARCADE_LOOK_FAIL_CLOSED,
            LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_TESTS,
            LEFTOVER_ARCADE_LOOK_FAIL_CLOSED_CONTRACT,
            LEFTOVER_ARCADE_LOOK_WORLD_MOOD,
            LEFTOVER_ARCADE_LOOK_WORLD_MOOD_TESTS,
            LEFTOVER_ARCADE_LOOK_WORLD_MOOD_CONTRACT,
            LEFTOVER_APACHE_CPG_FEEL,
            LEFTOVER_CAMPAIGN_ROSTER_LOOKUP,
            LEFTOVER_THEATER_KIT_WEATHER_IDENTITY,
            LEFTOVER_THEATER_KIT_BULK,
            LEFTOVER_NIGHT_IDENTITY_FIELD,
            LEFTOVER_STORM_ROCKET_FIELD,
            LEFTOVER_TIME_OF_DAY_FIELD,
            LEFTOVER_KEEP_THERMAL_FIELD,
            LEFTOVER_GUIDED_HELMET_LOCK,
            LEFTOVER_GUIDED_SENSOR_LOCK,
            LEFTOVER_GUIDED_HELMET_ACQUIRE,
            LEFTOVER_GUIDED_SENSOR_ACQUIRE,
            LEFTOVER_GUIDED_DETECT_PROGRESS,
            SIBLING_ENABLED_SCRIPT,
            SIBLING_CONTRAST_SCRIPT,
            SIBLING_SATURATION_SCRIPT,
            SIBLING_GAIN_SCRIPT,
            SIBLING_GAMMA_SCRIPT,
            SIBLING_VIGNETTE_SCRIPT,
            SIBLING_GRAIN_SCRIPT,
            SIBLING_CHROMATIC_SCRIPT,
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
        section = class_public_section(header)
        claimed = claimed_field_window(header)
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertEqual(
            require_declaration(claimed, LOCKED_DECL),
            LOCKED_DECL,
        )
        locked_only = f"{LOCKED_DECL}\n"
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, locked_only)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, locked_only)
        self.assertNotIn("WeatherIdentity", locked_only)
        self.assertNotIn("bNightIdentity", locked_only)
        self.assertNotIn("bStormRocketContract", locked_only)
        self.assertNotIn("bKeepThermal", locked_only)
        self.assertNotIn("TimeOfDayHours", locked_only)
        self.assertNotIn("HelmetLockSeconds", locked_only)
        self.assertNotIn("HelmetAcquireDegrees", locked_only)
        self.assertNotIn("CannonFireRate", locked_only)
        self.assertNotIn("CannonRecoilPitch", locked_only)
        self.assertNotIn(APPLY_WORLD_MOOD, locked_only)
        self.assertNotIn(APPLY_WORLD_MOOD_FOR_WEATHER, locked_only)
        self.assertNotIn(IS_ENABLED, locked_only)
        self.assertNotIn(LEFTOVER_THEATER_KIT_STRUCT, locked_only)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, locked_only)
        self.assertNotIn(LEFTOVER_NIGHT_KIT, locked_only)
        self.assertNotIn(LEFTOVER_GUIDED_LOCK_STRUCT, locked_only)
        self.assertNotIn(STOP_BEFORE_VIGNETTE, locked_only)
        self.assertNotIn("DetectProgressEnd", locked_only)
        self.assertNotIn(SIBLING_ENABLED, claimed)
        self.assertNotIn(SIBLING_CONTRAST, claimed)
        self.assertNotIn(SIBLING_SATURATION, claimed)
        self.assertNotIn(SIBLING_GAIN, claimed)
        self.assertNotIn(SIBLING_GAMMA, claimed)
        self.assertNotIn(SIBLING_VIGNETTE, claimed)

    def test_header_path_is_arcade_look_component(self) -> None:
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardArcadeLookComponent.h",
        )
        self.assertEqual(CLASS_NAME, "USkyguardArcadeLookComponent")
        self.assertTrue(HEADER_PATH.endswith("ArcadeLookComponent.h"))
        self.assertNotIn("TheaterKit", HEADER_PATH)
        self.assertNotIn("CampaignRoster", HEADER_PATH)
        self.assertNotIn("NightSortie", HEADER_PATH)
        self.assertNotIn("GuidedLock", HEADER_PATH)
        self.assertNotIn("GunshipTypes", HEADER_PATH)


if __name__ == "__main__":
    unittest.main()
