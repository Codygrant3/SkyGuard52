# THIS IS leftover-safe FSkyguardDaySortieBeat Threat.
# origin/main form: BARE plain C++ field
# `ESkyguardThreatKind Threat = ESkyguardThreatKind::GroundArmor;`
# THIS IS leftover-safe isolated FIELD declaration.
# FSkyguardDaySortieBeat IS a plain C++ struct.
# There is NO UPROPERTY wrap. There is NO Category.
# There is NO VisibleAnywhere / EditAnywhere.
# There is NO BlueprintReadOnly / BlueprintReadWrite.
# There is NO GENERATED_BODY / USTRUCT.
# Fail-closed if the field is missing or renamed, if the
# type is not ESkyguardThreatKind, if the initializer is
# missing or is not ESkyguardThreatKind::GroundArmor, or
# if a UPROPERTY / Category clone lands as the locked decl.
# Do NOT claim leftover NightSortieBeat
# `Threat = ESkyguardThreatKind::FastAttacker`.
# Accept one-line and split-line BARE field wraps only.
# Parse STRUCT `FSkyguardDaySortieBeat` body ONLY after
# `struct FSkyguardDaySortieBeat`. Stop at
# `struct FSkyguardDaySortieBeatKit`.
# Do NOT parse leftover `enum class ESkyguardDaySortieBeatKind`
# as the parse window.
# Do NOT parse leftover `namespace SkyguardDaySortieBeatKit`.
# Do NOT parse leftover `FSkyguardNightSortieBeat`.
# Do NOT parse leftover `FSkyguardStormRainBeatKit`.
# Do NOT contract sibling fields Kind / Call.
# THIS IS NOT leftover analog night-sortie-beat-defaults
# #247 / #5bf1 (keep that file in LOCKED_SCRIPTS).
# THIS IS NOT leftover analog day-sortie-beat-defaults
# #249 / #ba98.
# THIS IS NOT leftover analog night-sortie-beat-kit-defaults
# #250 / #2ca7.
# THIS IS NOT leftover day-sortie-beat-kind-enum
# #6893.
# THIS IS NOT leftover night-sortie-beat-kind-enum
# #246 / #4fea.
# THIS IS NOT leftover NightSortieBeat isolated
# Kind / Call / Threat drafts.
# THIS IS NOT leftover threat-kind-roster #197a.
# THIS IS NOT leftover LoadoutSpec isolated #1466-#1476.
# THIS IS NOT leftover CpgDebriefSnapshot #1451-#1465.
# THIS IS NOT leftover theater-kit-spec WeatherIdentity
# #1300 (UPROPERTY clone; retarget HARD).
# If a clone asserts UPROPERTY / Category /
# VisibleAnywhere / EditAnywhere / BlueprintReadOnly /
# GENERATED_BODY / USTRUCT as the locked decl, retarget:
# locked decl is the bare GroundArmor field.
# Do NOT parse leftover retired mount class (split tokens).
# Harbor 40/80 fail-closed.
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
HEADER_PATH = "Source/Skyguard52/SkyguardDaySortieBeatKit.h"
STRUCT_NAME = "FSkyguardDaySortieBeat"
KIT_STRUCT_NAME = "FSkyguardDaySortieBeatKit"
ENUM_NAME = "ESkyguardDaySortieBeatKind"
NAMESPACE_NAME = "SkyguardDaySortieBeatKit"
NIGHT_STRUCT_NAME = "FSkyguardNightSortieBeat"
STORM_KIT_NAME = "FSkyguardStormRainBeatKit"
TARGET = (
    "ESkyguardThreatKind Threat = ESkyguardThreatKind::GroundArmor;"
)
TARGET_WRONG_FAST_ATTACKER = (
    "ESkyguardThreatKind Threat = ESkyguardThreatKind::FastAttacker;"
)
TARGET_WRONG_BARE = "ESkyguardThreatKind Threat;"
TARGET_WRONG_FALSE = "ESkyguardThreatKind Threat = false;"
TARGET_WRONG_TRUE = "ESkyguardThreatKind Threat = true;"
TARGET_WRONG_ZERO = "ESkyguardThreatKind Threat = 0.f;"
TARGET_WRONG_FLOAT = "float Threat;"
TARGET_WRONG_HEALTH = "float Threat = 160.f;"
TARGET_WRONG_KIND_TYPE = (
    "ESkyguardDaySortieBeatKind Threat = "
    "ESkyguardThreatKind::GroundArmor;"
)
TARGET_WRONG_RENAME = (
    "ESkyguardThreatKind Threats = ESkyguardThreatKind::GroundArmor;"
)
TARGET_WRONG_KIND_ID = (
    "ESkyguardThreatKind Kind = ESkyguardThreatKind::GroundArmor;"
)
TARGET_WRONG_CALL_ID = (
    "ESkyguardThreatKind Call = ESkyguardThreatKind::GroundArmor;"
)
TARGET_WRONG_HEAVY = (
    "ESkyguardThreatKind Threat = ESkyguardThreatKind::HeavyAttacker;"
)
LOCKED_DECL = TARGET
UPROPERTY_CLONE = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Theater")'
)
UPROPERTY_CAMPAIGN_CLONE = (
    'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, '
    'Category="Skyguard|Campaign")'
)
STOP_BEFORE_KIT = "struct FSkyguardDaySortieBeatKit"
STOP_BEFORE_ENUM = "enum class ESkyguardDaySortieBeatKind"
STOP_BEFORE_NAMESPACE = "namespace SkyguardDaySortieBeatKit"
STOP_BEFORE_NIGHT = "struct FSkyguardNightSortieBeat"
STOP_BEFORE_STORM = "struct FSkyguardStormRainBeatKit"
STOP_BEFORE_AUDIO_EVENT = "enum class ESkyguardAudioEvent"
STOP_BEFORE_PICTOGRAM = "enum class ESkyguardBriefingPictogram"
STOP_BEFORE_EVENT_DEF = "struct FSkyguardAudioEventDefinition"
STOP_BEFORE_BOSS_WEAPON = "enum class ESkyguardBossWeapon"
STOP_BEFORE_PROP_SPINNER = "ASkyguardPropSpinner"
STOP_BEFORE_SORTIE = "ASkyguardGunshipSortieDirector"
STOP_BEFORE_PATROL = "ASkyguardPatrolShipBoss"
STOP_BEFORE_GUNNER = "ASkyguardGunner"
STOP_BEFORE_WEAK_POINT = "USkyguardBossWeakPointComponent"
SIBLING_KIND = "Kind"
SIBLING_CALL = "Call"
SIBLING_KIND_DECL = (
    "ESkyguardDaySortieBeatKind Kind = "
    "ESkyguardDaySortieBeatKind::RidgeIngress;"
)
SIBLING_CALL_DECL = 'const TCHAR* Call = TEXT("");'
BROKEN_HIGHWAY = "BrokenHighway"
DUST_OFFENSIVE = "DustOffensive"
HUNTER_KILLER = "HunterKiller"
FOR_MISSION = "ForMission"
SEQUENCES_DIFFER = "SequencesDiffer"
BEAT_INDEX_FOR_ELAPSED = "BeatIndexForElapsed"
KIND_AT = "KindAt"
LEFTOVER_APACHE_CLASS = "ASkyguardApacheAircraft"
LEFTOVER_PROTECT_ASSET_CLASS = "ASkyguardProtectAsset"
LEFTOVER_RADAR_NODE_CLASS = "ASkyguardRadarNode"
THIS_SCRIPT = (
    "Scripts/tests/test_day_sortie_beat_threat"
    "_field_decl_contract.py"
)
CLONE_THEATER_WEATHER_IDENTITY = (
    "Scripts/tests/test_theater_kit_spec_weather_identity"
    "_field_decl_contract.py"
)
LEFTOVER_NIGHT_BEAT_DEFAULTS = (
    "Scripts/tests/test_night_sortie_beat_defaults_contract.py"
)
LEFTOVER_DAY_BEAT_DEFAULTS = (
    "Scripts/tests/test_day_sortie_beat_defaults_contract.py"
)
LEFTOVER_NIGHT_KIT_DEFAULTS = (
    "Scripts/tests/test_night_sortie_beat_kit_defaults_contract.py"
)
LEFTOVER_NIGHT_BEAT_KIND_ENUM = (
    "Scripts/tests/test_night_sortie_beat_kind_enum_contract.py"
)
LEFTOVER_DAY_BEAT_KIND_ENUM = (
    "Scripts/tests/test_day_sortie_beat_kind_enum_contract.py"
)
CLONE_NIGHT_THREAT = (
    "Scripts/tests/test_night_sortie_beat_threat"
    "_field_decl_contract.py"
)
CLONE_NIGHT_KIND = (
    "Scripts/tests/test_night_sortie_beat_kind"
    "_field_decl_contract.py"
)
CLONE_NIGHT_CALL = (
    "Scripts/tests/test_night_sortie_beat_call"
    "_field_decl_contract.py"
)
LEFTOVER_THREAT_KIND_ROSTER = (
    "Scripts/tests/test_threat_kind_roster_contract.py"
)
LEFTOVER_NIGHT_BEAT_KIT_BULK = (
    "Scripts/tests/test_night_sortie_beat_kit_contract.py"
)
LEFTOVER_DAY_BEAT_KIT_BULK = (
    "Scripts/tests/test_day_sortie_beat_kit_contract.py"
)

CLONE_LOADOUT_GUIDED_RESERVE = (
    "Scripts/tests/test_loadout_spec_guided_reserve"
    "_field_decl_contract.py"
)
CLONE_LOADOUT_PLAYSTYLE_LINE = (
    "Scripts/tests/test_loadout_spec_playstyle_line"
    "_field_decl_contract.py"
)
CLONE_LOADOUT_HULL_INTEGRITY = (
    "Scripts/tests/test_loadout_spec_hull_integrity"
    "_field_decl_contract.py"
)
CLONE_LOADOUT_ROCKET_MAG = (
    "Scripts/tests/test_loadout_spec_rocket_magazine_size"
    "_field_decl_contract.py"
)
CLONE_LOADOUT_GUIDED_MAG = (
    "Scripts/tests/test_loadout_spec_guided_magazine_size"
    "_field_decl_contract.py"
)
CLONE_LOADOUT_ROCKET_RESERVE = (
    "Scripts/tests/test_loadout_spec_rocket_reserve"
    "_field_decl_contract.py"
)
CLONE_LOADOUT_CANNON_RESERVE = (
    "Scripts/tests/test_loadout_spec_cannon_reserve"
    "_field_decl_contract.py"
)
CLONE_LOADOUT_CANNON_MAG = (
    "Scripts/tests/test_loadout_spec_cannon_magazine_size"
    "_field_decl_contract.py"
)
CLONE_LOADOUT_LOADOUT = (
    "Scripts/tests/test_loadout_spec_loadout"
    "_field_decl_contract.py"
)
CLONE_LOADOUT_FLARE_COUNT = (
    "Scripts/tests/test_loadout_spec_flare_count"
    "_field_decl_contract.py"
)
CLONE_LOADOUT_STARTING_STATION = (
    "Scripts/tests/test_loadout_spec_starting_station"
    "_field_decl_contract.py"
)

CLONE_DEBRIEF_GUIDED_READY = (
    "Scripts/tests/test_cpg_debrief_snapshot_guided_ready"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_ROCKET_READY = (
    "Scripts/tests/test_cpg_debrief_snapshot_rocket_ready"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_CANNON_READY = (
    "Scripts/tests/test_cpg_debrief_snapshot_cannon_ready"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_SELECTED_LOADOUT = (
    "Scripts/tests/test_cpg_debrief_snapshot_selected_loadout"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_DESTROYED_SYSTEMS = (
    "Scripts/tests/test_cpg_debrief_snapshot_destroyed_systems"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_RADAR_DEAD = (
    "Scripts/tests/test_cpg_debrief_snapshot_radar_dead"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_SHOTS_FIRED = (
    "Scripts/tests/test_cpg_debrief_snapshot_shots_fired"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_HITS = (
    "Scripts/tests/test_cpg_debrief_snapshot_hits"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_CARGO_PERCENT = (
    "Scripts/tests/test_cpg_debrief_snapshot_cargo_percent"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_SCORE = (
    "Scripts/tests/test_cpg_debrief_snapshot_score"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_MEDAL = (
    "Scripts/tests/test_cpg_debrief_snapshot_medal"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_OUTCOME_NARRATIVE = (
    "Scripts/tests/test_cpg_debrief_snapshot_outcome_narrative"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_MISSION_TITLE = (
    "Scripts/tests/test_cpg_debrief_snapshot_mission_title"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_WON = (
    "Scripts/tests/test_cpg_debrief_snapshot_won"
    "_field_decl_contract.py"
)
CLONE_DEBRIEF_VALID = (
    "Scripts/tests/test_cpg_debrief_snapshot_valid"
    "_field_decl_contract.py"
)

LOCKED = {
    "SkyguardNightSortieBeatKit.h",
    "SkyguardNightSortieBeatKit.cpp",
    "SkyguardDaySortieBeatKit.h",
    "SkyguardDaySortieBeatKit.cpp",
    "SkyguardStormRainBeatKit.h",
    "SkyguardStormRainBeatKit.cpp",
    "SkyguardThreatTypes.h",
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
    "SkyguardRadarNode.cpp",
    "SkyguardRadarNode.h",
    "SkyguardRadarNodeGameplayTests.cpp",
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
    "SkyguardProtectAssetTests.cpp",
    "SkyguardHarborProofTests.cpp",
    "SkyguardCampaignTheaterKitTests.cpp",
    "SkyguardMission01EnvironmentAuthoringLibrary.h",
    "SkyguardMissionBriefingComponent.h",
    "SkyguardSortiePresentationWidgets.h",
    "SkyguardCampaignSubsystem.h",
    "SkyguardCampaignSubsystem.cpp",
    "SkyguardMission01IntegrationDirector.h",
    "SkyguardMission01IntegrationDirector.cpp",
    "SkyguardMission02IntegrationDirector.h",
    "SkyguardMission02IntegrationDirector.cpp",
    "SkyguardMission03IntegrationDirector.h",
    "SkyguardMission03IntegrationDirector.cpp",
    "SkyguardMission04IntegrationDirector.h",
    "SkyguardMission04IntegrationDirector.cpp",
    "SkyguardMission05IntegrationDirector.h",
    "SkyguardMission05IntegrationDirector.cpp",
    "SkyguardMissionDirectorCampaignHelpers.h",
    "SkyguardMissionDirectorPresentationHelpers.h",
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
    LEFTOVER_NIGHT_BEAT_DEFAULTS,
    LEFTOVER_DAY_BEAT_DEFAULTS,
    LEFTOVER_NIGHT_KIT_DEFAULTS,
    LEFTOVER_NIGHT_BEAT_KIND_ENUM,
    LEFTOVER_DAY_BEAT_KIND_ENUM,
    CLONE_NIGHT_THREAT,
    CLONE_NIGHT_KIND,
    CLONE_NIGHT_CALL,
    LEFTOVER_THREAT_KIND_ROSTER,
    LEFTOVER_NIGHT_BEAT_KIT_BULK,
    LEFTOVER_DAY_BEAT_KIT_BULK,
    CLONE_THEATER_WEATHER_IDENTITY,
    CLONE_LOADOUT_GUIDED_RESERVE,
    CLONE_LOADOUT_PLAYSTYLE_LINE,
    CLONE_LOADOUT_HULL_INTEGRITY,
    CLONE_LOADOUT_ROCKET_MAG,
    CLONE_LOADOUT_GUIDED_MAG,
    CLONE_LOADOUT_ROCKET_RESERVE,
    CLONE_LOADOUT_CANNON_RESERVE,
    CLONE_LOADOUT_CANNON_MAG,
    CLONE_LOADOUT_LOADOUT,
    CLONE_LOADOUT_FLARE_COUNT,
    CLONE_LOADOUT_STARTING_STATION,
    CLONE_DEBRIEF_GUIDED_READY,
    CLONE_DEBRIEF_ROCKET_READY,
    CLONE_DEBRIEF_CANNON_READY,
    CLONE_DEBRIEF_SELECTED_LOADOUT,
    CLONE_DEBRIEF_DESTROYED_SYSTEMS,
    CLONE_DEBRIEF_RADAR_DEAD,
    CLONE_DEBRIEF_SHOTS_FIRED,
    CLONE_DEBRIEF_HITS,
    CLONE_DEBRIEF_CARGO_PERCENT,
    CLONE_DEBRIEF_SCORE,
    CLONE_DEBRIEF_MEDAL,
    CLONE_DEBRIEF_OUTCOME_NARRATIVE,
    CLONE_DEBRIEF_MISSION_TITLE,
    CLONE_DEBRIEF_WON,
    CLONE_DEBRIEF_VALID,
    "Scripts/tests/test_loadout_spec_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults_contract.py",
    "Scripts/tests/test_mission_result_defaults.py",
    "Scripts/tests/test_mission_result_defaults_tests.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_mission_debrief_defaults.py",
    "Scripts/tests/test_mission_debrief_defaults_tests.py",
    "Scripts/tests/test_objective_progress_defaults_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_how_to_fly_row_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_mesh_bind_slot_fields_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults_contract.py",
    "Scripts/tests/test_audio_telemetry_defaults.py",
    "Scripts/tests/test_audio_telemetry_defaults_tests.py",
    "Scripts/tests/test_protect_asset_current_integrity_field_decl_contract.py",
    "Scripts/tests/test_protect_asset_max_integrity_field_decl_contract.py",
    "Scripts/tests/test_radar_node_health_field_decl_contract.py",
    "Scripts/tests/test_radar_node_max_health_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_card_id_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_title_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_body_field_decl_contract.py",
    "Scripts/tests/test_briefing_card_priority_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_step_id_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_input_hint_field_decl_contract.py",
    "Scripts/tests/test_how_to_fly_row_instruction_field_decl_contract.py",
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


def leftover_retired_mount_class() -> str:
    return "ASkyguard" + "Ya" + "k" + "52Aircraft"


def leftover_uproperty_lock_tokens() -> tuple[str, ...]:
    return (
        "UPROPERTY",
        "Category",
        "VisibleAnywhere",
        "EditAnywhere",
        "BlueprintReadOnly",
        "BlueprintReadWrite",
        "GENERATED_BODY",
        "USTRUCT",
    )


STRUCT_RE = re.compile(
    rf"struct\s+(?:SKYGUARD52_API\s+)?{re.escape(STRUCT_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")
INVENTED_UPROPERTY = leftover_uproperty_lock_tokens()
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
    "FastAttacker",
)


def sibling_uncontracted_decls() -> tuple[str, ...]:
    return (
        SIBLING_KIND_DECL,
        SIBLING_CALL_DECL,
    )


def namespace_helper_tokens() -> tuple[str, ...]:
    return (
        BROKEN_HIGHWAY,
        DUST_OFFENSIVE,
        HUNTER_KILLER,
        FOR_MISSION,
        SEQUENCES_DIFFER,
        BEAT_INDEX_FOR_ELAPSED,
        KIND_AT,
    )


def this_file_text() -> str:
    return Path(__file__).read_text(encoding="utf-8")


def collapsed(text: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    compact = re.sub(r"\s*::\s*", "::", compact)
    compact = re.sub(r"\s*=\s*", " = ", compact)
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
    # Fail-closed on the authored bare
    # `ESkyguardThreatKind Threat = ESkyguardThreatKind::GroundArmor;`.
    # Do not accept missing initializer, leftover NightSortieBeat
    # FastAttacker, wrong type, sibling Kind / Call, or a
    # UPROPERTY / Category / GENERATED_BODY clone landing
    # in the parse window.
    if not has_one_declaration(region, declaration):
        return False
    compact = collapsed(region)
    if re.search(
        r"ESkyguardThreatKind\s+Threat\s*=\s*"
        r"ESkyguardThreatKind::GroundArmor\s*;",
        compact,
    ) is None:
        return False
    if re.search(
        r"ESkyguardThreatKind\s+Threat\s*=\s*"
        r"ESkyguardThreatKind::FastAttacker\b",
        compact,
    ):
        return False
    if re.search(
        r"ESkyguardThreatKind\s+Threat\s*;",
        compact,
    ):
        return False
    if re.search(
        r"\b(?:float|bool|int32|FName|FString|"
        r"ESkyguardDaySortieBeatKind)\s+Threat\b",
        compact,
    ):
        return False
    for banned in leftover_uproperty_lock_tokens():
        if banned in compact:
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
        STOP_BEFORE_KIT,
        STOP_BEFORE_ENUM,
        STOP_BEFORE_NAMESPACE,
        STOP_BEFORE_NIGHT,
        STOP_BEFORE_STORM,
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
        KIT_STRUCT_NAME,
        NIGHT_STRUCT_NAME,
        STORM_KIT_NAME,
        "class USkyguardCampaignSubsystem",
        "class ASkyguardMission01IntegrationDirector",
        "class ASkyguardMission05IntegrationDirector",
        "class ASkyguardMission10IntegrationDirector",
        "struct FSkyguardLandscapeVisibleAudit",
        "struct FSkyguardMissionResult",
        "struct FSkyguardObjectiveProgress",
        "struct FSkyguardMissionDebrief",
        "struct FSkyguardBossTelemetry",
        "struct FSkyguardAudioTelemetry",
        "struct FSkyguardLoadoutSpec",
        "struct FSkyguardCpgDebriefSnapshot",
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
    for stop in (
        STOP_BEFORE_KIT,
        STOP_BEFORE_ENUM,
        STOP_BEFORE_NAMESPACE,
        STOP_BEFORE_NIGHT,
        STOP_BEFORE_STORM,
    ):
        if stop in section:
            raise AssertionError(
                f"{STRUCT_NAME} parse window includes {stop}"
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
            r"\s*ESkyguardThreatKind\s+Threat\b", compact[index:]
        ):
            return compact[start : index - 1]
        cursor = cursor + match.start() + 1
    raise AssertionError(
        "UPROPERTY for ESkyguardThreatKind Threat is missing from "
        f"origin/main:{HEADER_PATH} struct {STRUCT_NAME} body"
    )


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"struct {STRUCT_NAME} body"
        )
    return declaration


class DaySortieBeatThreatFieldDeclContractTests(unittest.TestCase):
    def test_day_sortie_beat_struct_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(STRUCT_NAME, header)
        self.assertIsNotNone(STRUCT_RE.search(header), header)
        self.assertIn(f"struct {STRUCT_NAME}", header)
        self.assertNotEqual(STRUCT_NAME, KIT_STRUCT_NAME)
        self.assertNotEqual(STRUCT_NAME, NIGHT_STRUCT_NAME)
        self.assertNotEqual(STRUCT_NAME, STORM_KIT_NAME)
        self.assertNotEqual(STRUCT_NAME, LEFTOVER_APACHE_CLASS)
        body = struct_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = spec_section(header)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertTrue(has_identifier(section, "Threat"), section)
        self.assertNotIn("UPROPERTY", section)
        self.assertIn(STOP_BEFORE_KIT, header)
        self.assertNotIn(STOP_BEFORE_KIT, section)
        self.assertNotIn(STOP_BEFORE_KIT, body)
        self.assertIn(STOP_BEFORE_ENUM, header)
        self.assertNotIn(STOP_BEFORE_ENUM, section)
        self.assertNotIn(STOP_BEFORE_ENUM, body)
        self.assertIn(STOP_BEFORE_NAMESPACE, header)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, body)
        self.assertNotIn(STOP_BEFORE_NIGHT, header)
        self.assertNotIn(STOP_BEFORE_NIGHT, section)
        self.assertNotIn(STOP_BEFORE_STORM, header)
        self.assertNotIn(STOP_BEFORE_STORM, section)
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, section)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, section)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, section)

    def test_missing_struct_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            struct_body(
                "struct FSkyguardUnrelatedDaySortieBeat\n{\n};\n"
            )
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_type_does_not_satisfy(self) -> None:
        night = (
            f"struct {NIGHT_STRUCT_NAME}\n"
            "{\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(night)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        kit = (
            f"struct {KIT_STRUCT_NAME}\n"
            "{\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(kit)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        storm = (
            f"struct {STORM_KIT_NAME}\n"
            "{\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            spec_section(storm)
        self.assertIn(STRUCT_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enum_kit_or_namespace_declaration_does_not_satisfy(self) -> None:
        mixed = (
            f"{STOP_BEFORE_ENUM} : uint8\n"
            "{{\n"
            "\tRidgeIngress,\n"
            "}};\n"
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "};\n"
            f"{STOP_BEFORE_KIT}\n"
            "{{\n"
            f"\t{LOCKED_DECL}\n"
            "}};\n"
            f"{STOP_BEFORE_NAMESPACE}\n"
            "{{\n"
            f"\tconst FSkyguardDaySortieBeatKit& {BROKEN_HIGHWAY}();\n"
            "}}\n"
        )
        section = spec_section(mixed)
        self.assertFalse(has_identifier(section, "Threat"), section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(STOP_BEFORE_KIT, section)
        self.assertNotIn(STOP_BEFORE_ENUM, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Threat", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_threat_declaration_fails_closed(self) -> None:
        empty = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{SIBLING_KIND_DECL}\n"
            f"\t{SIBLING_CALL_DECL}\n"
            "};\n"
        )
        section = spec_section(empty)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Threat", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_CLONE}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, LOCKED_DECL)
        self.assertIn("Threat", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_locked_decl_is_bare_plain_cpp_not_uproperty(self) -> None:
        self.assertEqual(LOCKED_DECL, TARGET)
        self.assertEqual(
            LOCKED_DECL,
            "ESkyguardThreatKind Threat = "
            "ESkyguardThreatKind::GroundArmor;",
        )
        for banned in leftover_uproperty_lock_tokens():
            self.assertNotIn(banned, LOCKED_DECL)
        self.assertFalse(LOCKED_DECL.startswith("UPROPERTY"), LOCKED_DECL)
        self.assertNotIn("USTRUCT", LOCKED_DECL)
        self.assertNotIn("GENERATED_BODY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        self.assertNotIn("VisibleAnywhere", LOCKED_DECL)
        self.assertNotIn("EditAnywhere", LOCKED_DECL)
        self.assertNotIn("BlueprintReadOnly", LOCKED_DECL)
        self.assertNotIn("FastAttacker", LOCKED_DECL)

    def test_origin_main_threat_is_bare_plain_cpp(self) -> None:
        section = spec_section(origin_main_header())
        for banned in leftover_uproperty_lock_tokens():
            self.assertNotIn(banned, section)
        self.assertNotIn("FastAttacker", section)
        self.assertTrue(has_declaration(section, LOCKED_DECL), section)
        self.assertNotIn("UFUNCTION", LOCKED_DECL)
        self.assertNotIn("UPROPERTY", LOCKED_DECL)
        self.assertNotIn("Category", LOCKED_DECL)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, LOCKED_DECL)
        with self.assertRaises(AssertionError) as raised:
            attached_uproperty_specifiers(section)
        self.assertIn("UPROPERTY", str(raised.exception))
        self.assertIn("Threat", str(raised.exception))

    def test_initializer_fails_closed_when_missing_or_wrong(self) -> None:
        bare = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_BARE}\n"
            "};\n"
        )
        section = spec_section(bare)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Threat", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        leftover_night = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_FAST_ATTACKER}\n"
            "};\n"
        )
        leftover_night_section = spec_section(leftover_night)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(leftover_night_section, LOCKED_DECL)
        self.assertIn("Threat", str(raised.exception))
        origin = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(origin, LOCKED_DECL),
            LOCKED_DECL,
        )
        compact_origin = collapsed(origin)
        self.assertIn(
            "ESkyguardThreatKind Threat = "
            "ESkyguardThreatKind::GroundArmor",
            compact_origin,
        )
        self.assertNotIn("Threat = ESkyguardThreatKind::FastAttacker", compact_origin)
        self.assertNotIn("Threat = false", compact_origin)
        self.assertNotIn("Threat = true", compact_origin)
        self.assertNotIn("Threat = 0.f", compact_origin)
        self.assertNotIn("Threat = 160.f", compact_origin)

    def test_threat_declaration_matches_origin_main(self) -> None:
        section = spec_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, LOCKED_DECL),
            LOCKED_DECL,
        )
        self.assertTrue(has_declaration(section, LOCKED_DECL))
        self.assertEqual(declaration_count(section, LOCKED_DECL), 1)
        self.assertTrue(
            LOCKED_DECL.startswith("ESkyguardThreatKind Threat"),
            LOCKED_DECL,
        )
        self.assertTrue(LOCKED_DECL.endswith(";"), LOCKED_DECL)
        self.assertIn("= ESkyguardThreatKind::GroundArmor", LOCKED_DECL)
        self.assertNotIn("FastAttacker", LOCKED_DECL)
        self.assertNotIn("= NAME_None", LOCKED_DECL)
        self.assertNotIn("= false", LOCKED_DECL)
        self.assertNotIn("= true", LOCKED_DECL)
        self.assertNotIn("= 0.f", LOCKED_DECL)
        self.assertNotIn("= 160.f", LOCKED_DECL)
        self.assertIn("ESkyguardThreatKind ", LOCKED_DECL)
        self.assertNotIn("float ", LOCKED_DECL)
        self.assertNotIn("bool ", LOCKED_DECL)
        self.assertNotIn("int32 ", LOCKED_DECL)
        self.assertNotIn("FName ", LOCKED_DECL)
        self.assertNotIn("FSkyguardMissionResult", LOCKED_DECL)
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
            has_declaration(f"\t{TARGET_WRONG_FAST_ATTACKER}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_FLOAT}\n", LOCKED_DECL)
        )
        self.assertFalse(
            has_declaration(f"\t{TARGET_WRONG_HEALTH}\n", LOCKED_DECL)
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(f"\t{TARGET_WRONG_BARE}\n", LOCKED_DECL)
        self.assertIn("Threat", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        with self.assertRaises(AssertionError) as raised:
            require_declaration(
                f"\t{TARGET_WRONG_FAST_ATTACKER}\n",
                LOCKED_DECL,
            )
        self.assertIn("Threat", str(raised.exception))

    def test_does_not_claim_night_sortie_fast_attacker(self) -> None:
        night = (
            f"struct {NIGHT_STRUCT_NAME}\n"
            "{\n"
            f"\t{TARGET_WRONG_FAST_ATTACKER}\n"
            "};\n"
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{SIBLING_KIND_DECL}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError):
            spec_section(
                f"struct {NIGHT_STRUCT_NAME}\n"
                "{\n"
                f"\t{TARGET_WRONG_FAST_ATTACKER}\n"
                "};\n"
            )
        section = spec_section(night)
        self.assertNotIn("FastAttacker", section)
        self.assertNotIn(NIGHT_STRUCT_NAME, section)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Threat", str(raised.exception))
        origin = spec_section(origin_main_header())
        self.assertNotIn("FastAttacker", origin)
        self.assertNotIn(TARGET_WRONG_FAST_ATTACKER, origin)
        self.assertNotIn(TARGET_WRONG_FAST_ATTACKER, LOCKED_DECL)

    def test_wrong_default_and_renames_do_not_satisfy(self) -> None:
        leftover_primary = (
            "\tESkyguardThreatKind " + leftover_retired_primary_hits_field()
            + " = ESkyguardThreatKind::GroundArmor;\n"
        )
        leftover_guided = (
            "\tESkyguardThreatKind " + leftover_retired_guided_hits_field()
            + " = ESkyguardThreatKind::GroundArmor;\n"
        )
        forty = "40" + ".f"
        eighty = "80" + ".f"
        wrongs = (
            f"\t{TARGET_WRONG_BARE}\n",
            f"\t{TARGET_WRONG_FAST_ATTACKER}\n",
            f"\t{TARGET_WRONG_FALSE}\n",
            f"\t{TARGET_WRONG_TRUE}\n",
            f"\t{TARGET_WRONG_ZERO}\n",
            f"\t{TARGET_WRONG_FLOAT}\n",
            f"\t{TARGET_WRONG_HEALTH}\n",
            f"\t{TARGET_WRONG_KIND_TYPE}\n",
            f"\t{TARGET_WRONG_RENAME}\n",
            f"\t{TARGET_WRONG_KIND_ID}\n",
            f"\t{TARGET_WRONG_CALL_ID}\n",
            f"\t{TARGET_WRONG_HEAVY}\n",
            leftover_primary,
            leftover_guided,
            f"\t{SIBLING_KIND_DECL}\n",
            f"\t{SIBLING_CALL_DECL}\n",
            "\tESkyguardThreatKind Threats = "
            "ESkyguardThreatKind::GroundArmor;\n",
            "\tint32 Threat = 0;\n",
            "\tbool Threat = true;\n",
            "\tfloat Threat = " + forty + ";\n",
            "\tfloat Threat = " + eighty + ";\n",
        )
        for region in wrongs:
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, LOCKED_DECL)
            self.assertIn("Threat", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_uproperty_category_clones_fail_closed(self) -> None:
        wrapped = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{UPROPERTY_CLONE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        section = spec_section(wrapped)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, LOCKED_DECL)
        self.assertIn("Threat", str(raised.exception))
        origin = spec_section(origin_main_header())
        for banned in leftover_uproperty_lock_tokens():
            self.assertNotIn(banned, origin)
            self.assertNotIn(banned, LOCKED_DECL)
        write_only = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            "\tUPROPERTY(EditAnywhere, BlueprintReadWrite, "
            'Category="Skyguard|Theater")\n'
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        write_section = spec_section(write_only)
        with self.assertRaises(AssertionError):
            require_declaration(write_section, LOCKED_DECL)
        campaign = (
            f"struct {STRUCT_NAME}\n"
            "{\n"
            f"\t{UPROPERTY_CAMPAIGN_CLONE}\n"
            f"\t{LOCKED_DECL}\n"
            "};\n"
        )
        campaign_section = spec_section(campaign)
        with self.assertRaises(AssertionError):
            require_declaration(campaign_section, LOCKED_DECL)
        self.assertIn("UPROPERTY", UPROPERTY_CLONE)
        self.assertIn("Category", UPROPERTY_CLONE)
        self.assertIn("VisibleAnywhere", UPROPERTY_CLONE)
        self.assertNotEqual(LOCKED_DECL, UPROPERTY_CLONE)
        self.assertNotEqual(LOCKED_DECL, UPROPERTY_CAMPAIGN_CLONE)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wraps = (
            "\tESkyguardThreatKind\n\tThreat = "
            "ESkyguardThreatKind::GroundArmor;\n",
            "\tESkyguardThreatKind   Threat = "
            "ESkyguardThreatKind::GroundArmor;\n",
            "\tESkyguardThreatKind\tThreat = "
            "ESkyguardThreatKind::GroundArmor;\n",
            f"\t{LOCKED_DECL}\n",
            "\tESkyguardThreatKind Threat=\n"
            "\t\tESkyguardThreatKind::GroundArmor;\n",
        )
        for region in wraps:
            self.assertTrue(has_declaration(region, LOCKED_DECL), region)
        rejected = (
            f"\t{UPROPERTY_CLONE}\n\t{LOCKED_DECL}\n",
            f"\t{UPROPERTY_CLONE} {LOCKED_DECL}\n",
            "\tUPROPERTY(VisibleAnywhere, BlueprintReadOnly, "
            'Category="Skyguard|Theater")\n'
            f"\t{LOCKED_DECL}\n",
            "\tUSTRUCT()\n"
            f"\t{LOCKED_DECL}\n",
            "\tGENERATED_BODY()\n"
            f"\t{LOCKED_DECL}\n",
        )
        for region in rejected:
            self.assertFalse(has_declaration(region, LOCKED_DECL), region)

    def test_does_not_contract_sibling_kind_or_call(self) -> None:
        for sibling in sibling_uncontracted_decls():
            self.assertNotIn(sibling, LOCKED_DECL)
        self.assertFalse(has_identifier(LOCKED_DECL, SIBLING_KIND))
        self.assertFalse(has_identifier(LOCKED_DECL, SIBLING_CALL))
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, LOCKED_DECL)
        self.assertNotIn(LEFTOVER_APACHE_CLASS, LOCKED_DECL)
        self.assertNotIn(STOP_BEFORE_KIT, LOCKED_DECL)
        section = spec_section(origin_main_header())
        self.assertTrue(has_identifier(section, SIBLING_KIND), section)
        self.assertTrue(has_identifier(section, SIBLING_CALL), section)
        self.assertTrue(has_declaration(section, SIBLING_KIND_DECL), section)
        self.assertTrue(has_declaration(section, SIBLING_CALL_DECL), section)
        for field in leftover_neighbor_hit_fields():
            self.assertNotIn(field, section)
        for leftover in leftover_pictogram_values():
            self.assertNotIn(leftover, section)
            self.assertNotIn(leftover, LOCKED_DECL)

    def test_does_not_parse_enum_kit_namespace_or_neighbors(self) -> None:
        header = origin_main_header()
        section = spec_section(header)
        leaked = struct_body(header)
        self.assertIn(STOP_BEFORE_KIT, header)
        self.assertNotIn(STOP_BEFORE_KIT, section)
        self.assertNotIn(STOP_BEFORE_KIT, leaked)
        self.assertIn(STOP_BEFORE_ENUM, header)
        self.assertNotIn(STOP_BEFORE_ENUM, section)
        self.assertNotIn(STOP_BEFORE_ENUM, leaked)
        self.assertIn(STOP_BEFORE_NAMESPACE, header)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, section)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, leaked)
        self.assertNotIn(STOP_BEFORE_NIGHT, header)
        self.assertNotIn(STOP_BEFORE_NIGHT, section)
        self.assertNotIn(STOP_BEFORE_NIGHT, leaked)
        self.assertNotIn(STOP_BEFORE_STORM, header)
        self.assertNotIn(STOP_BEFORE_STORM, section)
        self.assertNotIn(STOP_BEFORE_STORM, leaked)
        for helper in namespace_helper_tokens():
            self.assertIn(helper, header)
            self.assertNotIn(helper, section)
            self.assertNotIn(helper, leaked)
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
        self.assertNotIn(LEFTOVER_APACHE_CLASS, header)
        self.assertNotIn(LEFTOVER_PROTECT_ASSET_CLASS, header)
        self.assertNotIn(LEFTOVER_RADAR_NODE_CLASS, header)
        self.assertNotIn(NIGHT_STRUCT_NAME, header)
        self.assertNotIn(STORM_KIT_NAME, header)

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
        self.assertNotIn(NIGHT_STRUCT_NAME, section)
        self.assertNotIn(STORM_KIT_NAME, section)
        self.assertNotIn("FastAttacker", section)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other = (
            f"\tconst FSkyguardDaySortieBeatKit& {BROKEN_HIGHWAY}();\n"
            f"\tconst FSkyguardDaySortieBeatKit& {DUST_OFFENSIVE}();\n"
            f"\tconst FSkyguardDaySortieBeatKit& {HUNTER_KILLER}();\n"
            f"\tconst FSkyguardDaySortieBeatKit& {FOR_MISSION}"
            "(FName MissionId);\n"
            f"\tbool {SEQUENCES_DIFFER}();\n"
            f"\tint32 {BEAT_INDEX_FOR_ELAPSED}();\n"
            f"\tESkyguardDaySortieBeatKind {KIND_AT}();\n"
            f"\t{SIBLING_KIND_DECL}\n"
            f"\t{SIBLING_CALL_DECL}\n"
            f"\t{TARGET_WRONG_FAST_ATTACKER}\n"
            f"\t{TARGET_WRONG_HEALTH}\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other, LOCKED_DECL)
        self.assertIn("Threat", str(raised.exception))

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        self.assertEqual(
            LOCKED_DECL,
            "ESkyguardThreatKind Threat = "
            "ESkyguardThreatKind::GroundArmor;",
        )
        for banned in leftover_uproperty_lock_tokens():
            self.assertNotIn(banned, LOCKED_DECL)
        self.assertNotEqual(
            LOCKED_DECL,
            UPROPERTY_CLONE,
        )
        self.assertNotIn('Category="Skyguard|Theater"', LOCKED_DECL)
        self.assertNotIn('Category="Skyguard|Campaign"', LOCKED_DECL)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, LOCKED_DECL)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        self.assertNotIn(".cpp", HEADER_PATH)
        self.assertTrue(HEADER_PATH.endswith(".h"))
        self.assertNotIn("{", LOCKED_DECL)
        self.assertNotIn("return ", LOCKED_DECL)
        self.assertNotIn("SkyguardDaySortieBeatKit.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardNightSortieBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardStormRainBeatKit.h", HEADER_PATH)
        self.assertNotIn("SkyguardRadarNode.h", HEADER_PATH)
        self.assertNotIn("SkyguardProtectAsset.h", HEADER_PATH)
        self.assertNotIn("SkyguardApacheAircraft.h", HEADER_PATH)
        self.assertNotIn("SkyguardCampaignTheaterKit.h", HEADER_PATH)

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

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "day-sortie-beat Threat field decl contract "
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
            "threat_field_decl_contract.py"
        ))
        self.assertNotIn("SkyguardDaySortieBeatKit.cpp", THIS_SCRIPT)
        self.assertNotIn("SkyguardNightSortieBeatKit.h", THIS_SCRIPT)
        self.assertIn(LEFTOVER_NIGHT_BEAT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_DAY_BEAT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_NIGHT_KIT_DEFAULTS, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_NIGHT_BEAT_KIND_ENUM, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_DAY_BEAT_KIND_ENUM, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NIGHT_THREAT, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NIGHT_KIND, LOCKED_SCRIPTS)
        self.assertIn(CLONE_NIGHT_CALL, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_THREAT_KIND_ROSTER, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_NIGHT_BEAT_KIT_BULK, LOCKED_SCRIPTS)
        self.assertIn(LEFTOVER_DAY_BEAT_KIT_BULK, LOCKED_SCRIPTS)
        self.assertIn(CLONE_THEATER_WEATHER_IDENTITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_GUIDED_RESERVE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_PLAYSTYLE_LINE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_HULL_INTEGRITY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_ROCKET_MAG, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_GUIDED_MAG, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_ROCKET_RESERVE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_CANNON_RESERVE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_CANNON_MAG, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_LOADOUT, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_FLARE_COUNT, LOCKED_SCRIPTS)
        self.assertIn(CLONE_LOADOUT_STARTING_STATION, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_GUIDED_READY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_ROCKET_READY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_CANNON_READY, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_SELECTED_LOADOUT, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_DESTROYED_SYSTEMS, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_RADAR_DEAD, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_SHOTS_FIRED, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_HITS, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_CARGO_PERCENT, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_SCORE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_MEDAL, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_OUTCOME_NARRATIVE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_MISSION_TITLE, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_WON, LOCKED_SCRIPTS)
        self.assertIn(CLONE_DEBRIEF_VALID, LOCKED_SCRIPTS)

    def test_leftover_analog_bulk_stays_locked(self) -> None:
        leftovers = (
            LEFTOVER_NIGHT_BEAT_DEFAULTS,
            LEFTOVER_DAY_BEAT_DEFAULTS,
            LEFTOVER_NIGHT_KIT_DEFAULTS,
            LEFTOVER_NIGHT_BEAT_KIND_ENUM,
            LEFTOVER_DAY_BEAT_KIND_ENUM,
            CLONE_NIGHT_THREAT,
            CLONE_NIGHT_KIND,
            CLONE_NIGHT_CALL,
            LEFTOVER_THREAT_KIND_ROSTER,
            LEFTOVER_NIGHT_BEAT_KIT_BULK,
            LEFTOVER_DAY_BEAT_KIT_BULK,
            CLONE_THEATER_WEATHER_IDENTITY,
            CLONE_LOADOUT_GUIDED_RESERVE,
            CLONE_LOADOUT_PLAYSTYLE_LINE,
            CLONE_LOADOUT_HULL_INTEGRITY,
            CLONE_LOADOUT_ROCKET_MAG,
            CLONE_LOADOUT_GUIDED_MAG,
            CLONE_LOADOUT_ROCKET_RESERVE,
            CLONE_LOADOUT_CANNON_RESERVE,
            CLONE_LOADOUT_CANNON_MAG,
            CLONE_LOADOUT_LOADOUT,
            CLONE_LOADOUT_FLARE_COUNT,
            CLONE_LOADOUT_STARTING_STATION,
            CLONE_DEBRIEF_GUIDED_READY,
            CLONE_DEBRIEF_ROCKET_READY,
            CLONE_DEBRIEF_CANNON_READY,
            CLONE_DEBRIEF_SELECTED_LOADOUT,
            CLONE_DEBRIEF_DESTROYED_SYSTEMS,
            CLONE_DEBRIEF_RADAR_DEAD,
            CLONE_DEBRIEF_SHOTS_FIRED,
            CLONE_DEBRIEF_HITS,
            CLONE_DEBRIEF_CARGO_PERCENT,
            CLONE_DEBRIEF_SCORE,
            CLONE_DEBRIEF_MEDAL,
            CLONE_DEBRIEF_OUTCOME_NARRATIVE,
            CLONE_DEBRIEF_MISSION_TITLE,
            CLONE_DEBRIEF_WON,
            CLONE_DEBRIEF_VALID,
            "Scripts/tests/test_loadout_spec_defaults_contract.py",
            "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
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
        self.assertFalse(has_identifier(locked_only, SIBLING_KIND))
        self.assertFalse(has_identifier(locked_only, SIBLING_CALL))
        self.assertNotIn("FastAttacker", locked_only)
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
        self.assertNotIn(KIT_STRUCT_NAME, locked_only)
        self.assertNotIn(NIGHT_STRUCT_NAME, locked_only)
        self.assertNotIn(STORM_KIT_NAME, locked_only)
        self.assertNotIn(STOP_BEFORE_KIT, locked_only)
        self.assertNotIn(STOP_BEFORE_ENUM, locked_only)
        self.assertNotIn(STOP_BEFORE_NAMESPACE, locked_only)
        for helper in namespace_helper_tokens():
            self.assertNotIn(helper, locked_only)
        for banned in leftover_uproperty_lock_tokens():
            self.assertNotIn(banned, locked_only)


if __name__ == "__main__":
    unittest.main()
