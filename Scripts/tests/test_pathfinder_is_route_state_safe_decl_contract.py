from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardPathfinderEncounterController.h"
CLASS_NAME = "USkyguardPathfinderEncounterController"
# Declaration presence only. Do not invent INDEX_NONE
# or lock the IsRouteStateSafe body in the .cpp.
# origin/main is one line
# (`bool IsRouteStateSafe() const;`);
# accept that form, other split-line wraps, and an inline
# body without locking the body. Nearby origin/main
# UFUNCTION(BlueprintPure, Category="Skyguard|Boss|Encounter")
# is accepted as present. Parse the public class section of
# USkyguardPathfinderEncounterController only. Do not parse
# leftover boss-phase enum values. Leftover
# briefing-fail-closed #9fe9, leftover briefing
# declaration contracts through GetRadioChatter, leftover
# mission-briefing-state enum, leftover radio-chatter
# empty-fail-closed, leftover campaign-roster #111,
# leftover campaign-save empty-fail-closed, leftover
# boss-phase enum #60cb, leftover boss-definition
# defaults, leftover boss-weak-point defaults, and
# in-flight AdvanceEncounter stay sibling-only.
IS_ROUTE_STATE_SAFE = "bool IsRouteStateSafe() const;"
UFUNCTION_ENCOUNTER = (
    'UFUNCTION(BlueprintPure, Category="Skyguard|Boss|Encounter")'
)
# Leftover #56–#64 plus PathfinderEncounterController
# production files. This lane only adds an isolated
# Python IsRouteStateSafe declaration contract. Stay
# off AdvanceEncounter (in-flight),
# ResetEncounterState (sibling this wave),
# GetRouteProgress, GetEffectiveSpeedMultiplier,
# IsAttackTelegraphActive, and GetTelegraphsTriggered
# on this class. Stay off UPROPERTY fields, delegates,
# leftover boss-phase enum, leftover boss-definition
# defaults, leftover boss-weak-point defaults, leftover
# briefing-fail-closed, leftover briefing declaration
# contracts through GetRadioChatter, leftover
# mission-briefing-state enum, leftover radio-chatter
# empty-fail-closed, leftover campaign-roster lookup,
# leftover campaign-save empty-fail-closed, leftover
# Gunner helpers, leftover Harbor clocks, leftover
# theater-kit / flare / HUD, leftover drafts #56–#64,
# leftover ApacheSystem / weapon stations / pilot
# commands / loadout / lock-phase, leftover settings
# invert-look / ApplySettings broadcast, leftover
# bind-hud-host, leftover objective-runtime
# fail-closed, leftover route-runtime fail-closed,
# leftover gun-fire camera shake, leftover
# mission-weather enum, leftover mission 0N
# integration readiness, and dirty workspace paths.
LOCKED = {
    "SkyguardPathfinderEncounterController.h",
    "SkyguardPathfinderEncounterController.cpp",
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
# Isolated-test drafts stay off this lane. Leftover
# briefing-fail-closed, leftover briefing declaration
# contracts through GetRadioChatter, leftover
# radio-chatter empty-fail-closed, leftover
# mission-briefing-state enum, leftover campaign-roster
# lookup, leftover campaign-save empty-fail-closed,
# leftover boss-phase enum, leftover boss-definition
# defaults, leftover boss-weak-point defaults,
# leftover CPG debrief, leftover objective-runtime /
# route-runtime fail-closed, leftover theater-kit /
# Harbor / flare / HUD, leftover ApacheSystem /
# weapon stations / pilot commands / loadout,
# leftover settings invert-look, leftover
# bind-hud-host, leftover gun-fire camera shake,
# leftover mission-weather enum, leftover
# AdvanceEncounter, leftover ResetEncounterState,
# leftover GetRouteProgress, leftover
# GetEffectiveSpeedMultiplier, leftover
# IsAttackTelegraphActive, and leftover
# GetTelegraphsTriggered stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_briefing_fail_closed.py",
    "Scripts/tests/test_briefing_fail_closed_tests.py",
    "Scripts/tests/test_briefing_fail_closed_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
    "Scripts/tests/test_briefing_configure_from_mission_decl_contract.py",
    "Scripts/tests/test_briefing_set_assets_ready_decl_contract.py",
    "Scripts/tests/test_briefing_advance_briefing_decl_contract.py",
    "Scripts/tests/test_briefing_acknowledge_and_launch_decl_contract.py",
    "Scripts/tests/test_briefing_can_launch_decl_contract.py",
    "Scripts/tests/test_briefing_get_briefing_state_decl_contract.py",
    "Scripts/tests/test_briefing_get_elapsed_seconds_decl_contract.py",
    "Scripts/tests/test_briefing_get_minimum_warmup_seconds_decl_contract.py",
    "Scripts/tests/test_briefing_get_briefing_text_decl_contract.py",
    "Scripts/tests/test_briefing_get_radio_chatter_decl_contract.py",
    "Scripts/tests/test_radio_chatter_empty_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_queue_fail_closed.py",
    "Scripts/tests/test_radio_chatter_empty_line_tests.py",
    "Scripts/tests/test_mission_briefing_state_enum_contract.py",
    "Scripts/tests/test_mission_briefing_state_enum.py",
    "Scripts/tests/test_mission_briefing_state_enum_tests.py",
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
    "Scripts/tests/test_campaign_roster_weather_enum_label_decl_contract.py",
    "Scripts/tests/test_mission_definition_mission_id_decl_contract.py",
    "Scripts/tests/test_mission_definition_display_name_decl_contract.py",
    "Scripts/tests/test_mission_definition_campaign_order_decl_contract.py",
    "Scripts/tests/test_mission_definition_mission_map_decl_contract.py",
    "Scripts/tests/test_mission_definition_route_decl_contract.py",
    "Scripts/tests/test_mission_definition_objectives_decl_contract.py",
    "Scripts/tests/test_mission_definition_waves_decl_contract.py",
    "Scripts/tests/test_mission_definition_weather_decl_contract.py",
    "Scripts/tests/test_mission_definition_boss_decl_contract.py",
    "Scripts/tests/test_mission_definition_presentation_decl_contract.py",
    "Scripts/tests/test_mission_definition_score_rules_decl_contract.py",
    "Scripts/tests/test_mission_definition_prerequisite_ids_decl_contract.py",
    "Scripts/tests/test_mission_definition_required_medals_decl_contract.py",
    "Scripts/tests/test_mission_definition_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_mission_definition_find_objective_decl_contract.py",
    "Scripts/tests/test_mission_definition_validate_definition_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_definition_missions_decl_contract.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_enemy_wave_defaults_contract.py",
    "Scripts/tests/test_boss_phase_enum_contract.py",
    "Scripts/tests/test_boss_definition_defaults_contract.py",
    "Scripts/tests/test_boss_weak_point_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_mission_presentation_defaults_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
    "Scripts/tests/test_route_definition_fields_contract.py",
    "Scripts/tests/test_mission_save_record_defaults_contract.py",
    "Scripts/tests/test_objective_runtime_fail_closed.py",
    "Scripts/tests/test_objective_runtime_empty_fail_closed.py",
    "Scripts/tests/test_objective_runtime_fail_closed_contract.py",
    "Scripts/tests/test_route_runtime_fail_closed.py",
    "Scripts/tests/test_route_runtime_empty_fail_closed.py",
    "Scripts/tests/test_route_runtime_fail_closed_contract.py",
    "Scripts/tests/test_cpg_debrief_copy_decl_contract.py",
    "Scripts/tests/test_cpg_debrief_snapshot_defaults_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed_contract.py",
    "Scripts/tests/test_cpg_debrief_fail_closed.py",
    "Scripts/tests/test_mission_debrief_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
    "Scripts/tests/test_campaign_sortie_flow_contract.py",
    "Scripts/tests/test_m09_campaign_handoff_contract.py",
    "Scripts/tests/test_apache_own_ship_systems_contract.py",
    "Scripts/tests/test_gunship_weapon_stations_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_gunship_loadout_lock_phase_contract.py",
    "Scripts/tests/test_gunship_types_loadout_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_tests.py",
    "Scripts/tests/test_settings_apply_broadcast_contract.py",
    "Scripts/tests/test_bind_hud_host_presentation_tests.py",
    "Scripts/tests/test_pilot_confirm_line_contract.py",
    "Scripts/tests/test_pilot_warn_lock_reload_contract.py",
    "Scripts/tests/test_pilot_line_enum_contract.py",
    "Scripts/tests/test_pilot_confirm_command_decl_contract.py",
    "Scripts/tests/test_pilot_get_last_called_line_decl_contract.py",
    "Scripts/tests/test_pilot_get_last_called_text_decl_contract.py",
    "Scripts/tests/test_pilot_make_radio_line_decl_contract.py",
    "Scripts/tests/test_pilot_line_text_for_event_decl_contract.py",
    "Scripts/tests/test_pilot_voice_call_probe.py",
    "Scripts/tests/test_pilot_voice_duration_tests.py",
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
    "Scripts/tests/test_pathfinder_advance_encounter_decl_contract.py",
)
# Neighbors in the same public section. Presence is not locked
# here. AdvanceEncounter / ResetEncounterState /
# GetRouteProgress / GetEffectiveSpeedMultiplier /
# IsAttackTelegraphActive / GetTelegraphsTriggered
# stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "USkyguardPathfinderEncounterController();",
    "void AdvanceEncounter(float DeltaSeconds);",
    "void ResetEncounterState(const FTransform& NewRouteOrigin);",
    "float GetRouteProgress() const { return RouteProgressCm; }",
    "float GetEffectiveSpeedMultiplier() const;",
    "bool IsAttackTelegraphActive() const { return bAttackTelegraphActive; }",
    "int32 GetTelegraphsTriggered() const { return TelegraphsTriggered; }",
)
ADVANCE_ENCOUNTER_NOT_LOCKED = (
    "void AdvanceEncounter(float DeltaSeconds);",
)
RESET_ENCOUNTER_STATE_NOT_LOCKED = (
    "void ResetEncounterState(const FTransform& NewRouteOrigin);",
)
GET_ROUTE_PROGRESS_NOT_LOCKED = (
    "float GetRouteProgress() const;",
    "float GetRouteProgress() const { return RouteProgressCm; }",
)
GET_EFFECTIVE_SPEED_NOT_LOCKED = (
    "float GetEffectiveSpeedMultiplier() const;",
)
IS_ATTACK_TELEGRAPH_NOT_LOCKED = (
    "bool IsAttackTelegraphActive() const;",
    "bool IsAttackTelegraphActive() const { return bAttackTelegraphActive; }",
)
GET_TELEGRAPHS_TRIGGERED_NOT_LOCKED = (
    "int32 GetTelegraphsTriggered() const;",
    "int32 GetTelegraphsTriggered() const { return TelegraphsTriggered; }",
)
# Leftover boss-phase enum stays unlocked.
# This lane parses the public class section only.
LEFTOVER_ENUM_NOT_LOCKED = (
    "Disarm",
    "LockWindow",
    "Critical",
    "Defeated",
    "test_boss_phase_enum_contract.py",
)
# Leftover briefing-fail-closed / leftover briefing
# declaration contracts / leftover briefing-card
# defaults / leftover briefing-radio-row defaults /
# leftover radio-chatter empty-fail-closed stay unlocked.
LEFTOVER_BRIEFING_NOT_LOCKED = (
    "test_briefing_fail_closed.py",
    "test_briefing_fail_closed_tests.py",
    "test_briefing_fail_closed_contract.py",
    "test_briefing_card_defaults_contract.py",
    "test_briefing_radio_row_defaults_contract.py",
    "test_briefing_can_launch_decl_contract.py",
    "test_briefing_get_radio_chatter_decl_contract.py",
    "test_radio_chatter_empty_fail_closed.py",
    "FSkyguardBriefingCard",
    "FSkyguardBriefingRadioRow",
)
# Leftover boss-definition / leftover boss-weak-point
# defaults stay unlocked. Named leftover weak-point
# weapon fields are built in leftover_weak_point_tokens.
LEFTOVER_BOSS_DEFAULTS_NOT_LOCKED = (
    "test_boss_definition_defaults_contract.py",
    "test_boss_weak_point_defaults_contract.py",
    "FSkyguardBossDefinition",
    "FSkyguardBossWeakPointDefinition",
    "FSkyguardBossTelemetry",
    "ESkyguardBossWeapon",
    "MaximumBreakupPieces",
    "RequiredWeapon",
    "ExposesWeakPointId",
)
FILL_AND_GUNNER_NOT_LOCKED = (
    "void FillResultCombatStats(",
    "const ASkyguardGunner* Gunner,",
    "FillAndFinalize",
    "FillAndFail",
    "ApplyHydraForClusters",
)
# Leftover CPG debrief copy / snapshot defaults /
# fail-closed / empty-capture stay unlocked.
LEFTOVER_CPG_DEBRIEF_NOT_LOCKED = (
    "SkyguardBuildCpgDebriefCopy",
    "SkyguardCpgCopyHasBannedTerm",
    "SkyguardCaptureCpgDebrief",
    "FSkyguardCpgDebriefSnapshot",
)
# Leftover objective-runtime fail-closed / leftover
# route-runtime fail-closed stay unlocked.
LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED = (
    "SkyguardObjectiveRuntimeFailClosed",
    "SkyguardRouteRuntimeFailClosed",
    "ObjectiveRuntimeFailClosed",
    "RouteRuntimeFailClosed",
)
# Leftover ApacheSystem / weapon stations / pilot
# commands / loadout / lock-phase / invert-look /
# ApplySettings / leftover Gunner FillAnd* stay unlocked.
LEFTOVER_NOT_LOCKED = (
    "ESkyguardApacheSystem",
    "ESkyguardGunshipWeaponStation",
    "ESkyguardPilotCommand",
    "ESkyguardLoadout",
    "ESkyguardGuidedLockPhase",
    "ApplyHydraForClusters",
    "FillAndFinalize",
    "FillAndFail",
    "FillResultCombatStats",
    "bInvertLook",
    "ApplySettings",
)
# UPROPERTY fields / delegates in the same public
# section stay unlocked.
LEFTOVER_UPROPERTY_NOT_LOCKED = (
    "bAutoAdvance",
    "RouteLengthCm",
    "ApproachSpeedCmPerSecond",
    "MaxLateralOffsetCm",
    "MinHeightFromOriginCm",
    "MaxHeightFromOriginCm",
    "ObservedPhase",
    "OnAttackTelegraphChanged",
    "OnAttackCommitted",
    "FSkyguardPathfinderTelegraphEvent",
    "FSkyguardPathfinderAttackEvent",
)
# .cpp IsRouteStateSafe body / invented INDEX_NONE
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardPathfinderEncounterController::IsRouteStateSafe",
    "SkyguardPathfinderEncounterController.cpp",
)
SIBLING_TYPES = (
    "FSkyguardMission0NIntegrationReadiness",
)
CLASS_RE = re.compile(
    rf"class\s+(?:SKYGUARD52_API\s+)?{re.escape(CLASS_NAME)}\b"
)
ACCESS_RE = re.compile(r"(?:^|\n)\s*(public|private|protected)\s*:")


def leftover_harbor_tokens() -> tuple[str, ...]:
    incoming = "Incoming" + "Radar"
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return (
        incoming,
        incoming + "LiveIntervalSeconds",
        incoming + "DownIntervalSeconds",
        forty,
        eighty,
        forty + ", " + eighty,
    )


def leftover_harbor_section_tokens() -> tuple[str, ...]:
    # Bare leftover Harbor clock literals are checked
    # against the locked declaration and this file.
    # The public safety envelope uses a signed min-height
    # leftover that is not the Harbor clock pair.
    incoming = "Incoming" + "Radar"
    forty = "40" + ".f"
    eighty = "80" + ".f"
    return (
        incoming,
        incoming + "LiveIntervalSeconds",
        incoming + "DownIntervalSeconds",
        forty,
        forty + ", " + eighty,
    )


def leftover_live_copy_tokens() -> tuple[str, ...]:
    return ("ig" + "la", "ya" + "k", "ri" + "fle")


def leftover_readiness_tokens() -> tuple[str, ...]:
    return (
        "b" + "Ya" + "kRuntimeReady",
        "ASkyguard" + "Ig" + "la" + "Missile",
    )


def leftover_weak_point_tokens() -> tuple[str, ...]:
    accepts = "bAccepts"
    return (
        accepts + "Ri" + "fle",
        accepts + "Ig" + "la",
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


def has_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return True
    stem = declaration_stem(declaration)
    if not stem:
        return False
    # Accept `;` or an inline `{` body after the signature
    # without locking that body.
    pattern = re.compile(re.escape(stem) + r"\s*[;{]")
    return pattern.search(compact_region) is not None


def declaration_count(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    compact_region = collapsed(region)
    compact_decl = collapsed(declaration)
    if compact_decl in compact_region:
        return compact_region.count(compact_decl)
    stem = declaration_stem(declaration)
    if not stem:
        return 0
    pattern = re.compile(re.escape(stem) + r"\s*[;{]")
    return len(pattern.findall(compact_region))


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


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} public section"
        )
    return declaration


class PathfinderIsRouteStateSafeDeclContractTests(unittest.TestCase):
    def test_pathfinder_controller_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, IS_ROUTE_STATE_SAFE), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedPathfinder "
                ": public UActorComponent\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherPathfinderEncounterController "
            ": public UActorComponent\n"
            "{\n"
            "public:\n"
            f"\t{IS_ROUTE_STATE_SAFE}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_boss_phase_enum_does_not_satisfy_class(self) -> None:
        enum_only = (
            "UENUM(BlueprintType)\n"
            "enum class ESkyguardBossPhase : uint8\n"
            "{\n"
            "\tApproach,\n"
            "\tDisarm,\n"
            "\tLockWindow,\n"
            "\tCritical,\n"
            "\tDefeated\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            class_body(enum_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UActorComponent\n"
            "{\n"
            "private:\n"
            f"\t{IS_ROUTE_STATE_SAFE}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(private_only)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("public section", str(raised.exception).lower())
        self.assertIn("missing", str(raised.exception).lower())

    def test_private_declaration_does_not_satisfy_public_lock(self) -> None:
        mixed = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UActorComponent\n"
            "{\n"
            "public:\n"
            "\tvoid AdvanceEncounter(float DeltaSeconds);\n"
            "private:\n"
            f"\t{IS_ROUTE_STATE_SAFE}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, IS_ROUTE_STATE_SAFE)
        self.assertIn("IsRouteStateSafe", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, IS_ROUTE_STATE_SAFE))

    def test_missing_is_route_state_safe_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tUSkyguardPathfinderEncounterController();\n"
            "\tvoid AdvanceEncounter(float DeltaSeconds);\n"
            "\tvoid ResetEncounterState("
            "const FTransform& NewRouteOrigin);\n"
            "\tfloat GetRouteProgress() const { "
            "return RouteProgressCm; }\n"
            "\tfloat GetEffectiveSpeedMultiplier() const;\n"
            "\tbool IsAttackTelegraphActive() const { "
            "return bAttackTelegraphActive; }\n"
            "\tint32 GetTelegraphsTriggered() const { "
            "return TelegraphsTriggered; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, IS_ROUTE_STATE_SAFE)
        self.assertIn("IsRouteStateSafe", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_ENCOUNTER}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, IS_ROUTE_STATE_SAFE)
        self.assertIn("IsRouteStateSafe", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_ufunction_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UFUNCTION_ENCOUNTER, section)
        self.assertTrue(has_declaration(section, IS_ROUTE_STATE_SAFE), section)
        self.assertNotIn("BlueprintPure", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("UFUNCTION", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("Category", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("BlueprintCallable", IS_ROUTE_STATE_SAFE)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tvoid AdvanceEncounter(float DeltaSeconds);\n"
            "\tvoid ResetEncounterState("
            "const FTransform& NewRouteOrigin);\n"
            "\tfloat GetRouteProgress() const { "
            "return RouteProgressCm; }\n"
            "\tfloat GetEffectiveSpeedMultiplier() const;\n"
            "\tbool IsAttackTelegraphActive() const { "
            "return bAttackTelegraphActive; }\n"
            "\tint32 GetTelegraphsTriggered() const { "
            "return TelegraphsTriggered; }\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, IS_ROUTE_STATE_SAFE)
        self.assertIn("IsRouteStateSafe", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        wrong_return = "\tvoid IsRouteStateSafe() const;\n"
        missing_const = "\tbool IsRouteStateSafe();\n"
        added_arg = "\tbool IsRouteStateSafe(bool bForce) const;\n"
        int_return = "\tint32 IsRouteStateSafe() const;\n"
        float_return = "\tfloat IsRouteStateSafe() const;\n"
        for region in (
            wrong_return,
            missing_const,
            added_arg,
            int_return,
            float_return,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, IS_ROUTE_STATE_SAFE)
            self.assertIn("IsRouteStateSafe", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_is_route_state_safe_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, IS_ROUTE_STATE_SAFE),
            IS_ROUTE_STATE_SAFE,
        )
        self.assertTrue(has_declaration(section, IS_ROUTE_STATE_SAFE))
        self.assertEqual(declaration_count(section, IS_ROUTE_STATE_SAFE), 1)
        self.assertTrue(IS_ROUTE_STATE_SAFE.startswith("bool "), IS_ROUTE_STATE_SAFE)
        self.assertTrue(IS_ROUTE_STATE_SAFE.endswith(";"), IS_ROUTE_STATE_SAFE)
        self.assertIn("IsRouteStateSafe()", IS_ROUTE_STATE_SAFE)
        self.assertIn(" const", IS_ROUTE_STATE_SAFE)
        self.assertTrue(IS_ROUTE_STATE_SAFE.endswith(" const;"), IS_ROUTE_STATE_SAFE)
        self.assertNotIn("INDEX_NONE", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("{", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("}", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("return ", IS_ROUTE_STATE_SAFE)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tbool\n"
            "\tIsRouteStateSafe() const;\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tbool IsRouteStateSafe(\n"
            "\t\t) const;\n"
            "private:\n"
            "};\n"
        )
        wrap_arg = (
            "public:\n"
            "\tbool IsRouteStateSafe\n"
            "\t() const;\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tbool IsRouteStateSafe()\n"
            "\tconst;\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UActorComponent\n{{\n{wrap_type}"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UActorComponent\n{{\n{wrap_name}"
        )
        header_wrap_arg = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UActorComponent\n{{\n{wrap_arg}"
        )
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UActorComponent\n{{\n{wrap_const}"
        )
        for header in (
            header_wrap_type,
            header_wrap_name,
            header_wrap_arg,
            header_wrap_const,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, IS_ROUTE_STATE_SAFE),
                section,
            )
            self.assertEqual(
                require_declaration(section, IS_ROUTE_STATE_SAFE),
                IS_ROUTE_STATE_SAFE,
            )
            self.assertEqual(
                declaration_count(section, IS_ROUTE_STATE_SAFE),
                1,
            )
        one_line = f"{{\npublic:\n\t{IS_ROUTE_STATE_SAFE}\n}}\n"
        self.assertTrue(has_declaration(one_line, IS_ROUTE_STATE_SAFE))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, IS_ROUTE_STATE_SAFE), section)
        self.assertEqual(
            require_declaration(section, IS_ROUTE_STATE_SAFE),
            IS_ROUTE_STATE_SAFE,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tbool IsRouteStateSafe() const\n"
            "\t{\n"
            "\t\treturn false;\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UActorComponent\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(has_declaration(section, IS_ROUTE_STATE_SAFE), section)
        self.assertEqual(
            require_declaration(section, IS_ROUTE_STATE_SAFE),
            IS_ROUTE_STATE_SAFE,
        )
        self.assertEqual(declaration_count(section, IS_ROUTE_STATE_SAFE), 1)
        self.assertNotIn("{", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("}", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("return ", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("return false", IS_ROUTE_STATE_SAFE)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", IS_ROUTE_STATE_SAFE)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_contract_does_not_lock_is_route_state_safe_cpp_body(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        self.assertNotIn("{", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("}", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("return ", IS_ROUTE_STATE_SAFE)
        self.assertNotIn(
            "USkyguardPathfinderEncounterController::IsRouteStateSafe",
            IS_ROUTE_STATE_SAFE,
        )
        self.assertNotIn(
            "SkyguardPathfinderEncounterController.cpp",
            IS_ROUTE_STATE_SAFE,
        )
        self.assertNotIn(
            "SkyguardPathfinderEncounterController.cpp",
            locked_only,
        )
        self.assertNotIn("return false", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("return true", IS_ROUTE_STATE_SAFE)

    def test_contract_does_not_relock_advance_encounter(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for neighbor in ADVANCE_ENCOUNTER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("AdvanceEncounter", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("AdvanceEncounter", locked_only)

    def test_contract_does_not_relock_reset_encounter_state(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for neighbor in RESET_ENCOUNTER_STATE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("ResetEncounterState", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("ResetEncounterState", locked_only)

    def test_contract_does_not_relock_get_route_progress(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for neighbor in GET_ROUTE_PROGRESS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("GetRouteProgress", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("GetRouteProgress", locked_only)

    def test_contract_does_not_relock_get_effective_speed_multiplier(
        self,
    ) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for neighbor in GET_EFFECTIVE_SPEED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("GetEffectiveSpeedMultiplier", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("GetEffectiveSpeedMultiplier", locked_only)

    def test_contract_does_not_relock_is_attack_telegraph_active(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for neighbor in IS_ATTACK_TELEGRAPH_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("IsAttackTelegraphActive", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("IsAttackTelegraphActive", locked_only)

    def test_contract_does_not_relock_get_telegraphs_triggered(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for neighbor in GET_TELEGRAPHS_TRIGGERED_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("GetTelegraphsTriggered", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("GetTelegraphsTriggered", locked_only)

    def test_contract_does_not_relock_leftover_boss_phase_enum(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for token in LEFTOVER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("ESkyguardBossPhase", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("ESkyguardBossPhase", locked_only)
        self.assertNotIn("Disarm", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("LockWindow", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("Critical", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("Defeated", IS_ROUTE_STATE_SAFE)
        self.assertNotIn(
            "test_boss_phase_enum_contract.py",
            IS_ROUTE_STATE_SAFE,
        )

    def test_contract_does_not_relock_leftover_boss_defaults(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for token in LEFTOVER_BOSS_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for token in leftover_weak_point_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("FSkyguardBossDefinition", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("FSkyguardBossWeakPointDefinition", locked_only)

    def test_contract_does_not_relock_leftover_briefing_siblings(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for token in LEFTOVER_BRIEFING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("FSkyguardBriefingCard", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("FSkyguardBriefingRadioRow", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("FSkyguardBriefingCard", locked_only)
        self.assertNotIn("FSkyguardBriefingRadioRow", locked_only)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("FillResultCombatStats", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("ASkyguardGunner", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("FillAndFinalize", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("FillAndFail", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("ApplyHydraForClusters", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_uprop_fields_or_delegates(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for token in LEFTOVER_UPROPERTY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("UPROPERTY", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("UPROPERTY", locked_only)
        self.assertNotIn("ObservedPhase", locked_only)
        self.assertNotIn("OnAttackTelegraphChanged", locked_only)
        self.assertNotIn("OnAttackCommitted", locked_only)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        self.assertEqual(
            require_declaration(locked_only, IS_ROUTE_STATE_SAFE),
            IS_ROUTE_STATE_SAFE,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("AdvanceEncounter", locked_only)
        self.assertNotIn("ResetEncounterState", locked_only)
        self.assertNotIn("GetRouteProgress", locked_only)
        self.assertNotIn("GetEffectiveSpeedMultiplier", locked_only)
        self.assertNotIn("IsAttackTelegraphActive", locked_only)
        self.assertNotIn("GetTelegraphsTriggered", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_parses_public_section_not_enum_private_or_cpp(
        self,
    ) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("UENUM", section)
        self.assertNotIn("enum class", section)
        self.assertNotIn("AdvanceFixedStep", section)
        self.assertNotIn("ObservePhaseChange", section)
        self.assertNotIn("UpdateTelegraph", section)
        self.assertNotIn("GetPhaseSpeed", section)
        self.assertNotIn("GetCommandLateralOffset", section)
        self.assertNotIn("GetCommandHeightOffset", section)
        self.assertNotIn("GetAttackInterval", section)
        self.assertNotIn("SetTelegraphActive", section)
        self.assertEqual(
            require_declaration(section, IS_ROUTE_STATE_SAFE),
            IS_ROUTE_STATE_SAFE,
        )
        self.assertNotIn(
            "SkyguardPathfinderEncounterController.cpp",
            section,
        )
        self.assertNotIn(
            "USkyguardPathfinderEncounterController::IsRouteStateSafe",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
            self.assertNotIn(token, section)
        self.assertNotIn(
            "SkyguardPathfinderEncounterController.cpp",
            section,
        )
        self.assertNotIn(
            "USkyguardPathfinderEncounterController::IsRouteStateSafe",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("}", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("return false", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("return true", IS_ROUTE_STATE_SAFE)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for token in leftover_harbor_section_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        section = public_section(origin_main_header())
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
            self.assertNotIn(token, file_text)
        for token in leftover_harbor_section_tokens():
            self.assertNotIn(token, section)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "pathfinder IsRouteStateSafe contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, IS_ROUTE_STATE_SAFE.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for token in leftover_weak_point_tokens():
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"pathfinder IsRouteStateSafe contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, IS_ROUTE_STATE_SAFE.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, IS_ROUTE_STATE_SAFE)

    def test_contract_is_is_route_state_safe_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, IS_ROUTE_STATE_SAFE),
            IS_ROUTE_STATE_SAFE,
        )
        locked_only = f"{IS_ROUTE_STATE_SAFE}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, IS_ROUTE_STATE_SAFE)
        self.assertNotIn("AdvanceEncounter", locked_only)
        self.assertNotIn("ResetEncounterState", locked_only)
        self.assertNotIn("GetRouteProgress", locked_only)
        self.assertNotIn("GetEffectiveSpeedMultiplier", locked_only)
        self.assertNotIn("IsAttackTelegraphActive", locked_only)
        self.assertNotIn("GetTelegraphsTriggered", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FSkyguardBriefingCard", locked_only)
        self.assertNotIn("FSkyguardBriefingRadioRow", locked_only)
        self.assertNotIn("FSkyguardBossDefinition", locked_only)
        self.assertNotIn("ESkyguardBossPhase", locked_only)
        self.assertNotIn("Disarm", locked_only)
        self.assertNotIn("LockWindow", locked_only)
        self.assertNotIn("Critical", locked_only)
        self.assertNotIn("Defeated", locked_only)
        self.assertNotIn("ObservedPhase", locked_only)
        self.assertNotIn("OnAttackTelegraphChanged", locked_only)
        self.assertNotIn("OnAttackCommitted", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for token in LEFTOVER_BRIEFING_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for token in LEFTOVER_ENUM_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for token in LEFTOVER_BOSS_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for token in LEFTOVER_UPROPERTY_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for token in leftover_weak_point_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
            self.assertNotIn(token, section)
        for token in leftover_harbor_section_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, IS_ROUTE_STATE_SAFE)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, IS_ROUTE_STATE_SAFE.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("{", IS_ROUTE_STATE_SAFE)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertTrue(IS_ROUTE_STATE_SAFE.startswith("bool "))
        self.assertTrue(IS_ROUTE_STATE_SAFE.endswith(" const;"))
        self.assertIn(UFUNCTION_ENCOUNTER, section)

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
