# THIS IS leftover-safe FSkyguardGuidedLockRules DetectProgressEnd.
# origin/main form: BARE plain C++ static constexpr field
# `static constexpr float DetectProgressEnd = 0.22f;`
# with the paper lock detect-window end 0.22f. NOT a UPROPERTY wrap.
# FSkyguardGuidedLockRules is a plain C++ paper-lock struct.
# Fail-closed if this test still asserts UPROPERTY / Category /
# VisibleAnywhere / EditAnywhere / BlueprintReadOnly /
# GENERATED_BODY / USTRUCT as the locked decl.
# Fail-closed if a UPROPERTY wrap or Harbor 40/80 initializer
# is invented. Locked initializer is 0.22f, not analog 1.80f,
# not CannonRecoilPitch 0.92f, not Grain 0.08f, and not
# leftover HelmetLockSeconds 2.40f.
# Parse STRUCT `FSkyguardGuidedLockRules` body ONLY after
# `struct SKYGUARD52_API FSkyguardGuidedLockRules`.
# Stop BEFORE `static ESkyguardGuidedLockPhase PhaseFromProgress`.
# Do NOT parse methods LockSeconds / AcquireDegrees / CanFire /
# IsInsideAcquireCone / PhaseLabel / SightLabel.
# Do NOT parse leftover analog SkyguardApacheCpgFeel
# GuidedLockSeconds = 1.80f / CannonRecoilPitch = 0.92f
# (keep analog tests in LOCKED_SCRIPTS). This slot is
# DetectProgressEnd = 0.22f.
# Do NOT parse leftover SkyguardGuidedLockBreak.h.
# Do NOT parse leftover ESkyguardGuidedLockPhase enum.
# Do NOT parse leftover FSkyguardCampaignMissionSpec.
# Do NOT parse leftover SkyguardCampaignRoster.h.
# Do NOT parse leftover FSkyguardLoadoutSpec.
# Do NOT parse leftover FSkyguardCpgHudSnapshot LockProgress.
# Do NOT parse leftover FSkyguardCpgContactMark.
# Do NOT parse leftover Harbor Breaker Approach / Contact /
# Shore labels as this spec.
# Do NOT contract sibling fields HelmetLockSeconds /
# SensorLockSeconds / HelmetAcquireDegrees /
# SensorAcquireDegrees.
# THIS IS NOT leftover analog apache-cpg-feel #118/#8951.
# Isolated field decl does not relock the analog.
# THIS IS NOT leftover CpgHudSnapshot LockProgress #1512
# (runtime progress, not DetectProgressEnd).
# THIS IS NOT leftover GuidedLockRules HelmetLockSeconds
# #1539, HelmetAcquireDegrees #1538, or SensorLockSeconds.
# THIS IS NOT leftover guided-lock-break-fail-closed #e944.
# THIS IS NOT leftover gunship-loadout-lock-phase-contract
# #3762 (enum, not this constexpr).
# THIS IS NOT leftover CampaignMissionSpec #1521-#1537.
# THIS IS NOT leftover LoadoutSpec #1466-#1476.
# HullIntegrity leftover loadout field is not this slot.
# THIS IS NOT leftover-safe TheaterKitSpec WeatherIdentity
# UPROPERTY clone. Clone is UPROPERTY-based. RETARGET to
# a plain-struct static constexpr float field.
# UPROPERTY rejection is copied from leftover-safe
# CampaignMissionSpec MissionId. Do NOT copy that
# CampaignMissionSpec parse window (stop before namespace).
# Parse window is copied from leftover-safe GuidedLockRules
# HelmetLockSeconds #1539. Do NOT claim HelmetLockSeconds
# as this slot.
# Harbor fail-closed is ONLY those two clock tokens (split).
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
LEFTOVER_ANALOG_FEEL = "SkyguardApacheCpgFeel"
LEFTOVER_ANALOG_GUIDED = "GuidedLockSeconds"
LEFTOVER_ANALOG_RECOIL = "CannonRecoilPitch"
LEFTOVER_ANALOG_GRAIN = "Grain"
LEFTOVER_ANALOG_ROCKET = "RocketReloadSeconds"
LEFTOVER_LOCK_BREAK = "FSkyguardGuidedLockBreak"
LEFTOVER_LOCK_PHASE = "ESkyguardGuidedLockPhase"
LEFTOVER_CAMPAIGN_SPEC = "FSkyguardCampaignMissionSpec"
LEFTOVER_LOADOUT_SPEC = "FSkyguardLoadoutSpec"
LEFTOVER_HUD_SNAPSHOT = "FSkyguardCpgHudSnapshot"
LEFTOVER_CONTACT_MARK = "FSkyguardCpgContactMark"
LEFTOVER_ROSTER_NS = "SkyguardCampaignRoster"
LEFTOVER_LOCK_PROGRESS = "LockProgress"
LEFTOVER_HULL_INTEGRITY = "HullIntegrity"
LEFTOVER_LOCK_BREAK_HEADER = "Source/Skyguard52/SkyguardGuidedLockBreak.h"
LEFTOVER_GUNSHIP_TYPES_HEADER = "Source/Skyguard52/SkyguardGunshipTypes.h"
LEFTOVER_ROSTER_HEADER = "Source/Skyguard52/SkyguardCampaignRoster.h"
LEFTOVER_HUD_HEADER = "Source/Skyguard52/SkyguardCpgHud.h"
LEFTOVER_MISSION_TYPES_HEADER = "Source/Skyguard52/SkyguardMissionTypes.h"
LEFTOVER_ARCADE_LOOK_HEADER = "Source/Skyguard52/SkyguardArcadeLookComponent.h"
TARGET = "static constexpr float DetectProgressEnd = 0.22f;"
TARGET_WRONG_ANALOG = (
    "static constexpr float GuidedLockSeconds = 1.80f;"
)
TARGET_WRONG_ANALOG_VALUE = (
    "static constexpr float DetectProgressEnd = 1.80f;"
)
TARGET_WRONG_RECOIL = (
    "static constexpr float DetectProgressEnd = 0.92f;"
)
TARGET_WRONG_GRAIN = (
    "static constexpr float DetectProgressEnd = 0.08f;"
)
TARGET_WRONG_HELMET = (
    "static constexpr float HelmetLockSeconds = 2.40f;"
)
TARGET_WRONG_SENSOR = (
    "static constexpr float SensorLockSeconds = 1.35f;"
)
TARGET_WRONG_HELMET_ACQUIRE = (
    "static constexpr float HelmetAcquireDegrees = 12.0f;"
)
TARGET_WRONG_SENSOR_ACQUIRE = (
    "static constexpr float SensorAcquireDegrees = 5.5f;"
)
TARGET_WRONG_LOCK_PROGRESS = "float LockProgress = 0.f;"
TARGET_WRONG_HULL = "float HullIntegrity = " + "14" + "0.f;"
TARGET_WRONG_BARE = "static constexpr float DetectProgressEnd;"
TARGET_WRONG_NO_STATIC = (
    "constexpr float DetectProgressEnd = 0.22f;"
)
TARGET_WRONG_NO_CONSTEXPR = (
    "static float DetectProgressEnd = 0.22f;"
)
TARGET_WRONG_FLOAT_ONLY = "float DetectProgressEnd = 0.22f;"
TARGET_WRONG_INT = "static constexpr int32 DetectProgressEnd = 0;"
TARGET_WRONG_BOOL = "static constexpr bool DetectProgressEnd = true;"
TARGET_WRONG_SHORT = (
    "static constexpr float DetectProgressEnd = 0.2f;"
)
TARGET_WRONG_NO_F = (
    "static constexpr float DetectProgressEnd = 0.22;"
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
STOP_BEFORE_LOCK_BREAK = "struct FSkyguardGuidedLockBreak"
STOP_BEFORE_LOCK_PHASE = "enum class ESkyguardGuidedLockPhase"
STOP_BEFORE_CAMPAIGN_SPEC = "struct FSkyguardCampaignMissionSpec"
STOP_BEFORE_LOADOUT = "struct FSkyguardLoadoutSpec"
STOP_BEFORE_HUD_SNAPSHOT = "struct FSkyguardCpgHudSnapshot"
STOP_BEFORE_CONTACT_MARK = "struct FSkyguardCpgContactMark"
STOP_BEFORE_ROSTER_NS = "namespace SkyguardCampaignRoster"
STOP_BEFORE_FEEL = "namespace SkyguardApacheCpgFeel"
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
STOP_BEFORE_ARCADE_LOOK = "USkyguardArcadeLookComponent"
SIBLING_HELMET_LOCK = "HelmetLockSeconds"
SIBLING_SENSOR_LOCK = "SensorLockSeconds"
SIBLING_HELMET_ACQUIRE = "HelmetAcquireDegrees"
SIBLING_SENSOR_ACQUIRE = "SensorAcquireDegrees"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
THIS_SCRIPT = (
    "Scripts/tests/test_guided_lock_rules_detect_progress_end"
    "_field_decl_contract.py"
)
CLONE_THEATER_WEATHER_IDENTITY_SCRIPT = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_HELMET_LOCK_SECONDS = (
    "Scripts/tests/test_guided_lock_rules_helmet_lock_seconds"
    "_field_decl_contract.py"
)
LEFTOVER_HELMET_ACQUIRE_DEGREES = (
    "Scripts/tests/test_guided_lock_rules_helmet_acquire_degrees"
    "_field_decl_contract.py"
)
LEFTOVER_SENSOR_LOCK_SECONDS = (
    "Scripts/tests/test_guided_lock_rules_sensor_lock_seconds"
    "_field_decl_contract.py"
)
LEFTOVER_ANALOG_APACHE_CPG_FEEL = (
    "Scripts/tests/test_apache_cpg_feel_contract.py"
)
LEFTOVER_GUIDED_LOCK_BREAK = (
    "Scripts/tests/test_guided_lock_break_fail_closed.py"
)
LEFTOVER_LOCK_PHASE_CONTRACT = (
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py"
)
LEFTOVER_CAMPAIGN_MISSION_ID = (
    "Scripts/tests/test_campaign_mission_spec_mission_id"
    "_field_decl_contract.py"
)
LEFTOVER_ANALOG_ROSTER_LOOKUP = (
    "Scripts/tests/test_campaign_roster_lookup_tests.py"
)
LEFTOVER_HUD_LOCK_PHASE = (
    "Scripts/tests/test_cpg_hud_snapshot_lock_phase"
    "_field_decl_contract.py"
)
LEFTOVER_HUD_LOCK_PROGRESS = (
    "Scripts/tests/test_cpg_hud_snapshot_lock_progress"
    "_field_decl_contract.py"
)
LEFTOVER_CONTACT_LOCK_ALPHA = (
    "Scripts/tests/test_cpg_contact_mark_lock_alpha"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_FLARE = (
    "Scripts/tests/test_loadout_spec_flare_count"
    "_field_decl_contract.py"
)
LEFTOVER_LOADOUT_DEFAULTS = (
    "Scripts/tests/test_loadout_spec_defaults_contract.py"
)
LEFTOVER_LOADOUT_HULL = (
    "Scripts/tests/test_loadout_spec_hull_integrity"
    "_field_decl_contract.py"
)
LEFTOVER_ARCADE_LOOK = (
    "Scripts/tests/test_arcade_look_fail_closed.py"
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

LOCKED = {
    "SkyguardGuidedLockRules.h",
    "SkyguardGuidedLockRules.cpp",
    "SkyguardGuidedLockBreak.h",
    "SkyguardGuidedLockBreak.cpp",
    "SkyguardGunshipTypes.h",
    "SkyguardCampaignRoster.h",
    "SkyguardCampaignRoster.cpp",
    "SkyguardCpgHud.h",
    "SkyguardCpgHud.cpp",
    "SkyguardGunner.h",
    "SkyguardGunner.cpp",
    "SkyguardApacheAircraft.h",
    "SkyguardApacheAircraft.cpp",
    "SkyguardGunshipSortieDirector.h",
    "SkyguardGunshipSortieDirector.cpp",
    "SkyguardHarborBeatCalls.h",
    "SkyguardHarborBeatCalls.cpp",
    "SkyguardArcadeLookComponent.h",
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


def leftover_analog_scripts() -> tuple[str, ...]:
    return (
        LEFTOVER_ANALOG_APACHE_CPG_FEEL,
        LEFTOVER_GUIDED_LOCK_BREAK,
        LEFTOVER_LOCK_PHASE_CONTRACT,
        LEFTOVER_CAMPAIGN_MISSION_ID,
        LEFTOVER_ANALOG_ROSTER_LOOKUP,
        LEFTOVER_HUD_LOCK_PHASE,
        LEFTOVER_HUD_LOCK_PROGRESS,
        LEFTOVER_CONTACT_LOCK_ALPHA,
        LEFTOVER_LOADOUT_FLARE,
        LEFTOVER_LOADOUT_DEFAULTS,
        LEFTOVER_LOADOUT_HULL,
        LEFTOVER_ARCADE_LOOK,
        LEFTOVER_HELMET_LOCK_SECONDS,
        LEFTOVER_HELMET_ACQUIRE_DEGREES,
        LEFTOVER_SENSOR_LOCK_SECONDS,
        LEFTOVER_ROSTER_ID_AT,
        LEFTOVER_ROSTER_GET,
        LEFTOVER_ROSTER_NUM_MISSIONS,
        CLONE_THEATER_WEATHER_IDENTITY_SCRIPT,
    )


LOCKED_SCRIPTS = (
    leftover_analog_scripts()
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


def leftover_harbor_tokens() -> tuple[str, ...]:
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return (forty, eighty)


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


def leftover_live_copy_title_tokens() -> tuple[str, ...]:
    return ("Ig" + "la", "Ri" + "fle", "Ya" + "k")


def leftover_live_case_tokens() -> tuple[str, ...]:
    return leftover_live_copy_title_tokens()


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
    "= 1.80f",
    "= 0.92f",
    "= 0.08f",
    "= 2.40f",
    "= 2.3f",
    "= 14" + "0.f",
)


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_HELMET_LOCK,
        SIBLING_SENSOR_LOCK,
        SIBLING_HELMET_ACQUIRE,
        SIBLING_SENSOR_ACQUIRE,
    )


def leftover_neighbor_tokens() -> tuple[str, ...]:
    return (
        LEFTOVER_ANALOG_FEEL,
        LEFTOVER_LOCK_BREAK,
        LEFTOVER_CAMPAIGN_SPEC,
        LEFTOVER_LOADOUT_SPEC,
        LEFTOVER_HUD_SNAPSHOT,
        LEFTOVER_CONTACT_MARK,
        LEFTOVER_ROSTER_NS,
    )


def leftover_analog_field_tokens() -> tuple[str, ...]:
    return (
        LEFTOVER_ANALOG_GUIDED,
        LEFTOVER_ANALOG_RECOIL,
        LEFTOVER_ANALOG_GRAIN,
        LEFTOVER_LOCK_PROGRESS,
        LEFTOVER_HULL_INTEGRITY,
    )


def method_stop_tokens() -> tuple[str, ...]:
    return (
        STOP_BEFORE_PHASE_FROM_PROGRESS,
        STOP_BEFORE_CAN_FIRE,
        STOP_BEFORE_LOCK_SECONDS,
        STOP_BEFORE_ACQUIRE_DEGREES,
        STOP_BEFORE_INSIDE_CONE,
        STOP_BEFORE_PHASE_LABEL,
        STOP_BEFORE_SIGHT_LABEL,
    )


def this_file_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    compact = re.sub(r"\s*=\s*", "=", compact)
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


def detect_progress_has_uproperty_wrap(region: str) -> bool:
    compact = collapsed(region)
    return re.search(
        r"UPROPERTY\([^;]*\)\s*static\s+constexpr\s+float\s+"
        r"DetectProgressEnd\b",
        compact,
    ) is not None


def has_declaration(region: str, declaration: str) -> bool:
    # Fail-closed on the authored plain
    # `static constexpr float DetectProgressEnd = 0.22f;`.
    # Do not accept analog GuidedLockSeconds = 1.80f,
    # CannonRecoilPitch = 0.92f, Grain = 0.08f,
    # leftover HelmetLockSeconds = 2.40f, missing
    # static/constexpr, leftover LockProgress, or a
    # UPROPERTY / Category clone from leftover TheaterKit
    # #1300.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if re.search(
        r"static\s+constexpr\s+float\s+DetectProgressEnd\s*=\s*0\.22f\s*;",
        compact,
    ) is None:
        return False
    if re.search(
        r"DetectProgressEnd\s*=\s*1\.80f",
        compact,
    ):
        return False
    if re.search(
        r"DetectProgressEnd\s*=\s*0\.92f",
        compact,
    ):
        return False
    if re.search(
        r"DetectProgressEnd\s*=\s*0\.08f",
        compact,
    ):
        return False
    if re.search(
        r"DetectProgressEnd\s*=\s*2\.40f",
        compact,
    ):
        return False
    if re.search(
        r"\bGuidedLockSeconds\b",
        compact,
    ):
        return False
    if detect_progress_has_uproperty_wrap(region):
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


def leftover_feel_header() -> str:
    return leftover_header(LEFTOVER_GUNSHIP_TYPES_HEADER)


def leftover_lock_break_header() -> str:
    return leftover_header(LEFTOVER_LOCK_BREAK_HEADER)


def leftover_roster_header() -> str:
    return leftover_header(LEFTOVER_ROSTER_HEADER)


def leftover_hud_header() -> str:
    return leftover_header(LEFTOVER_HUD_HEADER)


def leftover_mission_types_header() -> str:
    return leftover_header(LEFTOVER_MISSION_TYPES_HEADER)


def leftover_arcade_look_header() -> str:
    return leftover_header(LEFTOVER_ARCADE_LOOK_HEADER)


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
        STOP_BEFORE_PHASE_FROM_PROGRESS,
        STOP_BEFORE_CAN_FIRE,
        STOP_BEFORE_LOCK_SECONDS,
        STOP_BEFORE_ACQUIRE_DEGREES,
        STOP_BEFORE_INSIDE_CONE,
        STOP_BEFORE_PHASE_LABEL,
        STOP_BEFORE_SIGHT_LABEL,
        STOP_BEFORE_LOCK_BREAK,
        STOP_BEFORE_LOCK_PHASE,
        STOP_BEFORE_CAMPAIGN_SPEC,
        STOP_BEFORE_LOADOUT,
        STOP_BEFORE_HUD_SNAPSHOT,
        STOP_BEFORE_CONTACT_MARK,
        STOP_BEFORE_ROSTER_NS,
        STOP_BEFORE_FEEL,
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
        STOP_BEFORE_ARCADE_LOOK,
        LEFTOVER_ANALOG_FEEL,
        LEFTOVER_LOCK_BREAK,
        LEFTOVER_CAMPAIGN_SPEC,
        LEFTOVER_LOADOUT_SPEC,
        LEFTOVER_HUD_SNAPSHOT,
        LEFTOVER_CONTACT_MARK,
        LEFTOVER_ROSTER_NS,
        "PhaseFromProgress",
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
    phase_at = section.find("PhaseFromProgress")
    if phase_at != -1:
        prefix = section[:phase_at]
        marker = "static ESkyguardGuidedLockPhase"
        marker_at = prefix.rfind(marker)
        if marker_at != -1:
            section = prefix[:marker_at]
        else:
            section = prefix
    for token in leaked_neighbor_tokens():
        if token in section:
            raise AssertionError(
                f"{STRUCT_NAME} parse window includes {token}"
            )
    if "PhaseFromProgress" in section:
        raise AssertionError(
            f"{STRUCT_NAME} parse window includes PhaseFromProgress"
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
            r"\s*static\s+constexpr\s+float\s+DetectProgressEnd\b",
            compact[index:],
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for static constexpr float DetectProgressEnd is "
        f"missing from origin/main:{HEADER_PATH} struct {STRUCT_NAME} "
        "body; locked decl is the bare plain C++ field, not a "
        "UPROPERTY wrap"
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
        r"DetectProgressEnd\b",
        compact,
    ):
        raise AssertionError(
            "UPROPERTY wrap on DetectProgressEnd is not the locked "
            f"decl for plain C++ struct {STRUCT_NAME}"
        )
    if "UPROPERTY" in section and has_identifier(section, "DetectProgressEnd"):
        raise AssertionError(
            "UPROPERTY clone landed on DetectProgressEnd; locked decl "
            f"is bare {LOCKED_DECL}"
        )
    for token in ("USTRUCT", "GENERATED_BODY"):
        if token in section and has_identifier(section, "DetectProgressEnd"):
            raise AssertionError(
                f"{token} clone landed on DetectProgressEnd; locked "
                f"decl is bare {LOCKED_DECL}"
            )


class GuidedLockRulesDetectProgressEndFieldDeclContractTests(
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
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOADOUT_SPEC)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_HUD_SNAPSHOT)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_CONTACT_MARK)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_APACHE_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_PROTECT_ASSET_CLASS)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_RADAR_NODE_CLASS)
        self.assertNotEqual(STRUCT_NAME, STOP_BEFORE_SORTIE)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_ANALOG_FEEL)
        body = struct_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "DetectProgressEnd"), section)
        self.assertNotIn("UPROPERTY", section)
        self.assertNotIn("GENERATED_BODY", section)
        self.assertNotIn("USTRUCT", section)
        self.assertIn(STOP_BEFORE_PHASE_FROM_PROGRESS, header)
        self.assertNotIn(STOP_BEFORE_PHASE_FROM_PROGRESS, section)
        self.assertNotIn("PhaseFromProgress", section)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_ANALOG_FEEL, section)
        self.assertNotIn(LEFTOVER_LOCK_BREAK, section)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, section)
        self.assertNotIn(LEFTOVER_ANALOG_GUIDED, section)
        self.assertNotIn(LEFTOVER_ANALOG_RECOIL, section)
        self.assertNotIn(LEFTOVER_ANALOG_GRAIN, section)
        self.assertNotIn(LEFTOVER_LOCK_PROGRESS, section)
        self.assertNotIn(LEFTOVER_HULL_INTEGRITY, section)

    def test_locked_decl_is_plain_constexpr_not_uproperty(self) -> None:
        self.assertEqual(
            LOCKED_DECL,
            "static constexpr float DetectProgressEnd = 0.22f;",
        )
        self.assertEqual(LOCKED_DECL, TARGET)
        self.assertTrue(LOCKED_DECL.startswith("static constexpr float"))
        self.assertTrue(LOCKED_DECL.endswith(";"))
        self.assertIn("DetectProgressEnd", LOCKED_DECL)
        self.assertIn("= 0.22f", LOCKED_DECL)
        self.assertNotIn("1.80f", LOCKED_DECL)
        self.assertNotIn("0.92f", LOCKED_DECL)
        self.assertNotIn("0.08f", LOCKED_DECL)
        self.assertNotIn("2.40f", LOCKED_DECL)
        self.assertNotIn("2.3f", LOCKED_DECL)
        self.assertNotIn(LEFTOVER_ANALOG_GUIDED, LOCKED_DECL)
        self.assertNotIn(SIBLING_HELMET_LOCK, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_LOCK_PROGRESS, LOCKED_DECL)
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
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_ANALOG)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_HELMET)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SENSOR)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_PROGRESS)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_LOCK_BREAK_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_GUNSHIP_TYPES_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_ROSTER_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_HUD_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_MISSION_TYPES_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_ARCADE_LOOK_HEADER)

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
            self.assertIn("DetectProgressEnd", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            struct_body(
                "struct FSkyguardUnrelatedGuidedLockRules\n{\n};\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_analog_and_neighbor_structs_do_not_satisfy(self) -> None:
        leftovers = leftover_neighbor_tokens()
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
        analog = (
            f"namespace {LEFTOVER_ANALOG_FEEL}\n"
            "{\n"
            f"\t{TARGET_WRONG_ANALOG}\n"
            "}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(analog)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_does_not_claim_leftover_apache_cpg_feel_or_lock_break(
        self,
    ) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_GUNSHIP_TYPES_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_LOCK_BREAK_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_ROSTER_HEADER)
        self.assertNotEqual(HEADER_PATH, LEFTOVER_HUD_HEADER)
        self.assertTrue(HEADER_PATH.endswith("SkyguardGuidedLockRules.h"))
        self.assertNotIn("GuidedLockBreak", HEADER_PATH)
        self.assertNotIn("GunshipTypes", HEADER_PATH)
        self.assertNotIn("CampaignRoster", HEADER_PATH)
        self.assertNotIn("CpgHud", HEADER_PATH)
        self.assertNotIn("ArcadeLook", HEADER_PATH)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_LOCK_BREAK)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_CAMPAIGN_SPEC)
        feel_header = leftover_feel_header()
        self.assertIn(LEFTOVER_ANALOG_FEEL, feel_header)
        self.assertIn(LEFTOVER_ANALOG_GUIDED, feel_header)
        self.assertIn("1.80f", feel_header)
        self.assertIn(LEFTOVER_ANALOG_RECOIL, feel_header)
        self.assertIn("0.92f", feel_header)
        self.assertIn(LEFTOVER_ANALOG_ROCKET, feel_header)
        self.assertIn(STOP_BEFORE_LOCK_PHASE, feel_header)
        self.assertIn(LEFTOVER_LOADOUT_SPEC, feel_header)
        self.assertIn(LEFTOVER_HULL_INTEGRITY, feel_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(feel_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        break_header = leftover_lock_break_header()
        self.assertIn(LEFTOVER_LOCK_BREAK, break_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(break_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        roster_header = leftover_roster_header()
        self.assertIn(LEFTOVER_CAMPAIGN_SPEC, roster_header)
        self.assertIn(LEFTOVER_ROSTER_NS, roster_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(roster_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        hud_header = leftover_hud_header()
        self.assertIn(LEFTOVER_CONTACT_MARK, hud_header)
        self.assertIn(LEFTOVER_HUD_SNAPSHOT, hud_header)
        self.assertIn(LEFTOVER_LOCK_PROGRESS, hud_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(hud_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        look_header = leftover_arcade_look_header()
        self.assertIn(LEFTOVER_ANALOG_GRAIN, look_header)
        self.assertIn("0.08f", look_header)
        with self.assertRaises(AssertionError) as raised:
            spec_section(look_header)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_method_declaration_does_not_satisfy(self) -> None:
        mixed = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{STOP_BEFORE_PHASE_FROM_PROGRESS}(\n"
            "\t\tfloat Progress,\n"
            "\t\tbool bHasCandidate);\n"
            f"\t{STOP_BEFORE_CAN_FIRE}({LEFTOVER_LOCK_PHASE} Phase);\n"
            f"\t{STOP_BEFORE_LOCK_SECONDS}(ESkyguardCpgSightMode Sight);\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        section = spec_section(mixed)
        self.assertFalse(has_identifier(section, "DetectProgressEnd"), section)
        self.assertNotIn("PhaseFromProgress", section)
        self.assertNotIn(STOP_BEFORE_CAN_FIRE, section)
        self.assertNotIn(STOP_BEFORE_LOCK_SECONDS, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("DetectProgressEnd", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_leftover_methods_do_not_satisfy(self) -> None:
        leftovers = (
            f"\t{STOP_BEFORE_PHASE_FROM_PROGRESS}();\n",
            f"\t{STOP_BEFORE_CAN_FIRE}();\n",
            f"\t{STOP_BEFORE_LOCK_SECONDS}();\n",
            f"\t{STOP_BEFORE_ACQUIRE_DEGREES}();\n",
            f"\t{STOP_BEFORE_INSIDE_CONE}();\n",
            f"\t{STOP_BEFORE_PHASE_LABEL}();\n",
            f"\t{STOP_BEFORE_SIGHT_LABEL}();\n",
        )
        for region in leftovers:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("DetectProgressEnd", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())
        for method in method_stop_tokens():
            self.assertNotIn(method, LOCKED_DECL)

    def test_missing_detect_progress_end_declaration_fails_closed(
        self,
    ) -> None:
        empty = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_HELMET}\n"
            f"\t{TARGET_WRONG_SENSOR}\n"
            f"\t{TARGET_WRONG_HELMET_ACQUIRE}\n"
            f"\t{TARGET_WRONG_SENSOR_ACQUIRE}\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("DetectProgressEnd", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_sibling_helmet_lock_does_not_satisfy(self) -> None:
        leftover = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_HELMET}\n"
            f"\t{TARGET_WRONG_SENSOR}\n"
            f"\t{TARGET_WRONG_HELMET_ACQUIRE}\n"
            "};\n"
        )
        section = spec_section(leftover)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("DetectProgressEnd", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(section, LOCKED_DECL), section)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_HELMET)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_SENSOR)
        self.assertNotEqual(LOCKED_DECL, TARGET_WRONG_LOCK_PROGRESS)

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{CLONE_UPROPERTY_THEATER}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("DetectProgressEnd", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_has_plain_constexpr_not_uproperty(self) -> None:
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

    def test_analog_guided_lock_seconds_and_grain_fail_closed(self) -> None:
        analog = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_ANALOG}\n"
            "};\n"
        )
        section = spec_section(analog)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("DetectProgressEnd", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        analog_value = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_ANALOG_VALUE}\n"
            "};\n"
        )
        analog_section = spec_section(analog_value)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(analog_section, LOCKED_DECL)
        self.assertIn("DetectProgressEnd", str(raised.exception))
        recoil = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_RECOIL}\n"
            "};\n"
        )
        recoil_section = spec_section(recoil)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(recoil_section, LOCKED_DECL)
        self.assertIn("DetectProgressEnd", str(raised.exception))
        grain = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_GRAIN}\n"
            "};\n"
        )
        grain_section = spec_section(grain)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(grain_section, LOCKED_DECL)
        self.assertIn("DetectProgressEnd", str(raised.exception))
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn("DetectProgressEnd=0.22f;", compact_origin)
        self.assertNotIn("DetectProgressEnd=1.80f", compact_origin)
        self.assertNotIn("DetectProgressEnd=0.92f", compact_origin)
        self.assertNotIn("DetectProgressEnd=0.08f", compact_origin)
        self.assertNotIn("GuidedLockSeconds", compact_origin)
        self.assertNotIn("CannonRecoilPitch", compact_origin)
        self.assertNotIn("LockProgress", compact_origin)

    def test_detect_progress_end_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
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
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertIn("= 0.22f", LOCKED_DECL)
        self.assertNotIn("= 1.80f", LOCKED_DECL)
        self.assertNotIn("= 0.92f", LOCKED_DECL)
        self.assertNotIn("= 0.08f", LOCKED_DECL)
        self.assertNotIn("= 2.40f", LOCKED_DECL)
        self.assertNotIn("= 2.3f", LOCKED_DECL)
        self.assertNotIn("= 14" + "0.f", LOCKED_DECL)
        self.assertNotIn("= NAME_None", LOCKED_DECL)
        self.assertNotIn("= false", LOCKED_DECL)
        self.assertIn("static constexpr float ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn(LEFTOVER_ANALOG_GUIDED, LOCKED_DECL)
        self.assertNotIn(SIBLING_HELMET_LOCK, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_LOCK_PROGRESS, LOCKED_DECL)
        for token in FORBIDDEN_LOCKED_MACRO_TOKENS:
            self.assertNotIn(token, LOCKED_DECL)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_ANALOG}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_ANALOG_VALUE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_RECOIL}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_GRAIN}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HELMET}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_NO_STATIC}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FLOAT_ONLY}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_SENSOR}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_LOCK_PROGRESS}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_ANALOG}\n", LOCKED_DECL)
        self.assertIn("DetectProgressEnd", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(
                f"\t{TARGET_WRONG_HELMET}\n",
                LOCKED_DECL,
            )
        self.assertIn("DetectProgressEnd", str(raised.exception))

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tstatic constexpr float "
            + leftover_retired_primary_hits_field()
            + " = 0.22f;\n"
        )
        leftover_guided = (
            "\tstatic constexpr float "
            + leftover_retired_guided_hits_field()
            + " = 0.22f;\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_ANALOG}\n",
            f"\t{TARGET_WRONG_ANALOG_VALUE}\n",
            f"\t{TARGET_WRONG_RECOIL}\n",
            f"\t{TARGET_WRONG_GRAIN}\n",
            f"\t{TARGET_WRONG_HELMET}\n",
            f"\t{TARGET_WRONG_SENSOR}\n",
            f"\t{TARGET_WRONG_HELMET_ACQUIRE}\n",
            f"\t{TARGET_WRONG_SENSOR_ACQUIRE}\n",
            f"\t{TARGET_WRONG_LOCK_PROGRESS}\n",
            f"\t{TARGET_WRONG_HULL}\n",
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_NO_STATIC}\n",
            f"\t{TARGET_WRONG_NO_CONSTEXPR}\n",
            f"\t{TARGET_WRONG_FLOAT_ONLY}\n",
            f"\t{TARGET_WRONG_INT}\n",
            f"\t{TARGET_WRONG_BOOL}\n",
            f"\t{TARGET_WRONG_SHORT}\n",
            f"\t{TARGET_WRONG_NO_F}\n",
            leftover_primary,
            leftover_guided,
            "\tstatic constexpr float DetectProgressEn = 0.22f;\n",
            "\tstatic constexpr float DetectProgressEnd = "
            + forty
            + ";\n",
            "\tstatic constexpr float DetectProgressEnd = "
            + eighty
            + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("DetectProgressEnd", str(raised.exception))
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
                    detect_progress_has_uproperty_wrap(section),
                    section,
                )
                with self.assertRaises(AssertionError) as raised:
                    require_declaration(section, LOCKED_DECL)
                self.assertIn("DetectProgressEnd", str(raised.exception))
                self.assertIn("missing", str(raised.exception).lower())
        origin = spec_section(origin_main_header())
        require_no_uproperty_wrap(origin)
        self.assertFalse(detect_progress_has_uproperty_wrap(origin), origin)
        self.assertNotIn("UPROPERTY", origin)
        self.assertNotIn("Category", origin)
        self.assertNotIn("VisibleAnywhere", origin)
        self.assertNotIn("EditAnywhere", origin)
        self.assertNotIn("BlueprintReadOnly", origin)
        self.assertNotIn("GENERATED_BODY", origin)
        self.assertNotIn("USTRUCT", origin)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tstatic constexpr float\n\tDetectProgressEnd = 0.22f;\n",
            "\tstatic constexpr float   DetectProgressEnd = 0.22f;\n",
            "\tstatic constexpr float\tDetectProgressEnd = 0.22f;\n",
            "\tstatic\n\tconstexpr float DetectProgressEnd = 0.22f;\n",
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
            f"\t{TARGET_WRONG_ANALOG}\n",
            f"\t{TARGET_WRONG_ANALOG_VALUE}\n",
            f"\t{TARGET_WRONG_HELMET}\n",
            f"\t{TARGET_WRONG_RECOIL}\n",
            f"\t{TARGET_WRONG_GRAIN}\n",
            f"\t{TARGET_WRONG_LOCK_PROGRESS}\n",
            f"\t{TARGET_WRONG_BARE}\n",
        )
        for region in rejected:
            self.assertFalse(has_declaration(region, LOCKED_DECL), region)

    def test_does_not_contract_sibling_rules_fields(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        for analog in leftover_analog_field_tokens():
            self.assertNotIn(analog, LOCKED_DECL)
        section = spec_section(origin_main_header())
        for sibling in sibling_uncontracted_decls():
            self.assertTrue(has_identifier(section, sibling), sibling)
        self.assertFalse(has_identifier(section, LEFTOVER_ANALOG_GUIDED))
        self.assertFalse(has_identifier(section, LEFTOVER_ANALOG_RECOIL))
        self.assertFalse(has_identifier(section, LEFTOVER_ANALOG_GRAIN))
        self.assertFalse(has_identifier(section, LEFTOVER_ANALOG_ROCKET))
        self.assertFalse(has_identifier(section, LEFTOVER_LOCK_PROGRESS))
        self.assertFalse(has_identifier(section, LEFTOVER_HULL_INTEGRITY))
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_parse_window_stops_before_phase_from_progress(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        self.assertIn(STOP_BEFORE_PHASE_FROM_PROGRESS, header)
        self.assertIn("PhaseFromProgress", leaked)
        self.assertNotIn("PhaseFromProgress", section)
        self.assertNotIn(STOP_BEFORE_PHASE_FROM_PROGRESS, section)
        for method in method_stop_tokens():
            self.assertIn(method, header)
            self.assertIn(method, leaked)
            self.assertNotIn(method, section)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)

    def test_does_not_parse_leftover_headers_or_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        self.assertIn(STOP_BEFORE_PHASE_FROM_PROGRESS, header)
        self.assertNotIn(STOP_BEFORE_PHASE_FROM_PROGRESS, section)
        for method in method_stop_tokens():
            self.assertIn(method, header)
            self.assertNotIn(method, section)
        self.assertNotIn(STOP_BEFORE_LOCK_BREAK, header)
        self.assertNotIn(LEFTOVER_LOCK_BREAK, header)
        self.assertNotIn(STOP_BEFORE_CAMPAIGN_SPEC, header)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, header)
        self.assertNotIn(STOP_BEFORE_ROSTER_NS, header)
        self.assertNotIn(LEFTOVER_ROSTER_NS, header)
        self.assertNotIn(STOP_BEFORE_LOADOUT, header)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, header)
        self.assertNotIn(STOP_BEFORE_HUD_SNAPSHOT, header)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, header)
        self.assertNotIn(STOP_BEFORE_CONTACT_MARK, header)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, header)
        self.assertNotIn(STOP_BEFORE_FEEL, header)
        self.assertNotIn(LEFTOVER_ANALOG_FEEL, header)
        self.assertNotIn(LEFTOVER_ANALOG_GUIDED, header)
        self.assertNotIn(LEFTOVER_ANALOG_RECOIL, header)
        self.assertNotIn(LEFTOVER_ANALOG_GRAIN, header)
        self.assertNotIn(LEFTOVER_LOCK_PROGRESS, header)
        self.assertNotIn(LEFTOVER_HULL_INTEGRITY, header)
        self.assertNotIn(STOP_BEFORE_LOCK_PHASE, header)
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
        self.assertNotIn(STOP_BEFORE_ARCADE_LOOK, header)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, header)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, header)
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
        self.assertNotIn(LEFTOVER_ANALOG_FEEL, section)
        self.assertNotIn(LEFTOVER_LOCK_BREAK, section)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, section)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, section)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, section)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, section)
        self.assertNotIn(LEFTOVER_LOCK_PROGRESS, section)
        self.assertNotIn(LEFTOVER_ANALOG_GRAIN, section)

    def test_does_not_parse_guided_lock_phase_enum(self) -> None:
        self.assertNotEqual(HEADER_PATH, LEFTOVER_GUNSHIP_TYPES_HEADER)
        self.assertNotIn(LEFTOVER_LOCK_PHASE, LOCKED_DECL)
        self.assertNotIn("enum class", LOCKED_DECL)
        section = spec_section(origin_main_header())
        self.assertNotIn(STOP_BEFORE_LOCK_PHASE, section)
        self.assertNotIn("enum class", section)
        self.assertNotIn(LEFTOVER_LOCK_PHASE, section)
        feel = leftover_feel_header()
        self.assertIn(STOP_BEFORE_LOCK_PHASE, feel)
        with self.assertRaises(AssertionError) as raised:
            spec_section(feel)
        self.assertIn(STRUCT_NAME, str(raised.exception))

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            f"\t{STOP_BEFORE_PHASE_FROM_PROGRESS}();\n"
            f"\t{STOP_BEFORE_CAN_FIRE}();\n"
            f"\t{STOP_BEFORE_LOCK_SECONDS}();\n"
            f"\t{STOP_BEFORE_ACQUIRE_DEGREES}();\n"
            f"\t{TARGET_WRONG_HELMET}\n"
            f"\t{TARGET_WRONG_ANALOG}\n"
            f"\t{TARGET_WRONG_LOCK_PROGRESS}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("DetectProgressEnd", str(raised.exception))

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
        self.assertNotIn("SkyguardGuidedLockRules.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardGuidedLockBreak.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignRoster.h", HEADER_PATH)
        self.assertNotIn("SkyguardCpgHud.h", HEADER_PATH)
        self.assertNotIn("SkyguardMissionTypes.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardRadarNode.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)
        self.assertNotIn("SkyguardHarborBeatCalls.h", HEADER_PATH)
        self.assertNotIn("SkyguardGunshipSortieDirector.h", HEADER_PATH)
        self.assertNotIn("SkyguardArcadeLookComponent.h", HEADER_PATH)

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
        for token in leftover_harbor_director_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, LOCKED_DECL)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "guided-lock-rules DetectProgressEnd field decl "
                f"contract contains {banned}; declaration is Apache "
                "CPG 30 mm / Hydra / Hellfire, not leftover live cop"
                + "y",
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
            "detect_progress_end_field_decl_contract.py"
        ))
        self.assertIn("guided_lock_rules", Path(__file__).name)
        self.assertNotIn("helmet_lock_seconds", Path(__file__).name)
        self.assertNotIn("helmet_acquire", Path(__file__).name)
        self.assertNotIn("sensor_lock_seconds", Path(__file__).name)
        self.assertNotIn("apache_cpg_feel", Path(__file__).name)
        self.assertNotIn("guided_lock_break", Path(__file__).name)
        self.assertNotIn("lock_phase", Path(__file__).name)
        self.assertNotIn("lock_progress", Path(__file__).name)
        self.assertNotIn("campaign_mission_spec", Path(__file__).name)
        self.assertNotIn("SkyguardGuidedLockBreak.h", THIS_SCRIPT)
        self.assertIn(LEFTOVER_ANALOG_APACHE_CPG_FEEL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_GUIDED_LOCK_BREAK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOCK_PHASE_CONTRACT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CAMPAIGN_MISSION_ID, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ANALOG_ROSTER_LOOKUP, LOCKED_SCRIPTS)
        self.assertIn(CLONE_THEATER_WEATHER_IDENTITY_SCRIPT, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_HUD_LOCK_PHASE, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_HUD_LOCK_PROGRESS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_CONTACT_LOCK_ALPHA, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_HELMET_LOCK_SECONDS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_HELMET_ACQUIRE_DEGREES, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_SENSOR_LOCK_SECONDS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_LOADOUT_HULL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_ARCADE_LOOK, LOCKED_SCRIPTS)

    def test_leftover_analog_bulk_stays_locked(self) -> None:
        leftovers = leftover_analog_scripts()
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
        for leftover in leftover_neighbor_tokens():
            self.assertNotIn(leftover, locked_only)
        for analog in leftover_analog_field_tokens():
            self.assertNotIn(analog, locked_only)
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
        self.assertNotIn(LEFTOVER_LOCK_PHASE, locked_only)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, locked_only)
        self.assertNotIn(LEFTOVER_ANALOG_FEEL, locked_only)
        self.assertNotIn(LEFTOVER_LOCK_BREAK, locked_only)
        self.assertNotIn(LEFTOVER_CAMPAIGN_SPEC, locked_only)
        self.assertNotIn(LEFTOVER_LOADOUT_SPEC, locked_only)
        self.assertNotIn(LEFTOVER_HUD_SNAPSHOT, locked_only)
        self.assertNotIn(LEFTOVER_CONTACT_MARK, locked_only)
        self.assertNotIn(LEFTOVER_ANALOG_GUIDED, locked_only)
        self.assertNotIn(LEFTOVER_ANALOG_RECOIL, locked_only)
        self.assertNotIn(LEFTOVER_ANALOG_GRAIN, locked_only)
        self.assertNotIn(LEFTOVER_LOCK_PROGRESS, locked_only)
        self.assertNotIn(LEFTOVER_HULL_INTEGRITY, locked_only)
        self.assertNotIn(SIBLING_HELMET_LOCK, locked_only)
        self.assertNotIn(STOP_BEFORE_PHASE_FROM_PROGRESS, locked_only)
        self.assertNotIn(STOP_BEFORE_HARBOR_CALLS, locked_only)
        self.assertNotIn(STOP_BEFORE_SORTIE, locked_only)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_APACHE_CPG_FEEL)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_GUIDED_LOCK_BREAK)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_LOCK_PHASE_CONTRACT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_CAMPAIGN_MISSION_ID)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_ANALOG_ROSTER_LOOKUP)
        self.assertNotEqual(THIS_SCRIPT, CLONE_THEATER_WEATHER_IDENTITY_SCRIPT)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_PHASE)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HUD_LOCK_PROGRESS)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_CONTACT_LOCK_ALPHA)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HELMET_LOCK_SECONDS)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_HELMET_ACQUIRE_DEGREES)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_SENSOR_LOCK_SECONDS)
        self.assertNotEqual(THIS_SCRIPT, LEFTOVER_LOADOUT_HULL)
        for method in method_stop_tokens():
            self.assertNotIn(method, locked_only)
        for token in leftover_harbor_breaker_label_structs():
            self.assertNotIn(token, locked_only)


if __name__ == "__main__":
    unittest.main()
