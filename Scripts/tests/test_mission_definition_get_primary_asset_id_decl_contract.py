from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardMissionDefinition.h"
CLASS_NAME = "USkyguardMissionDefinition"
# Declaration presence only. Do not invent INDEX_NONE,
# a returned asset id, or lock the GetPrimaryAssetId body
# in the .cpp. origin/main is one line
# (`virtual FPrimaryAssetId GetPrimaryAssetId() const override;`);
# accept that form, other split-line wraps, and an inline
# body without locking the body.
# This is USkyguardMissionDefinition::GetPrimaryAssetId, not
# USkyguardCampaignDefinition::GetPrimaryAssetId (#339).
GET_PRIMARY_ASSET_ID = (
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;"
)
UFUNCTION_VALIDATE = 'UFUNCTION(BlueprintCallable, Category = "Mission")'
# Leftover #56–#64 plus MissionDefinition production files.
# This lane only adds an isolated Python GetPrimaryAssetId
# declaration contract. Stay off MissionId #350, DisplayName
# #351, CampaignOrder #352, MissionMap #353, Route #354,
# Objectives #355, Waves #356, Weather #357, Boss #358,
# Presentation #359, ScoreRules, PrerequisiteMissionIds
# (in-flight sibling), RequiredCampaignMedals (in-flight
# sibling), ValidateDefinition, and FindObjective on this
# class. Stay off leftover campaign-definition
# GetPrimaryAssetId #339, leftover campaign-roster lookup,
# leftover campaign-save empty-fail-closed, leftover
# objective / route / weather / boss / wave / presentation /
# score-rules defaults, leftover CPG debrief, leftover
# Gunner helpers, leftover Harbor clocks, leftover
# theater-kit / flare / HUD, leftover drafts #56–#64,
# leftover ApacheSystem / weapon stations / pilot commands
# / loadout / lock-phase, leftover settings invert-look /
# ApplySettings broadcast, leftover bind-hud-host, leftover
# objective-runtime fail-closed, leftover route-runtime
# fail-closed, leftover pilot line / confirm / warn /
# call-probe / duration drafts, leftover gun-fire camera
# shake, leftover mission-weather enum, leftover mission 0N
# integration readiness, and dirty workspace paths.
LOCKED = {
    "SkyguardMissionDefinition.h",
    "SkyguardMissionDefinition.cpp",
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
# campaign-definition GetPrimaryAssetId, leftover
# campaign-roster lookup, leftover campaign-save
# empty-fail-closed, leftover objective / route /
# mission-score / weather / boss / wave / presentation
# defaults, leftover route-definition fields, leftover
# campaign definition CampaignId / DisplayName / Missions,
# leftover CPG debrief, leftover objective-runtime /
# route-runtime fail-closed, leftover theater-kit / Harbor /
# flare / HUD, leftover ApacheSystem / weapon stations /
# pilot commands / loadout, leftover settings invert-look,
# leftover bind-hud-host, leftover pilot drafts, leftover
# gun-fire camera shake, leftover mission-weather enum,
# and in-flight MissionId stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
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
    "Scripts/tests/test_campaign_roster_lookup_contract.py",
    "Scripts/tests/test_campaign_roster_lookup_tests.py",
    "Scripts/tests/test_campaign_roster_contract.py",
    "Scripts/tests/test_campaign_roster_get_decl_contract.py",
    "Scripts/tests/test_campaign_roster_id_at_decl_contract.py",
    "Scripts/tests/test_campaign_roster_num_missions_decl_contract.py",
    "Scripts/tests/test_campaign_roster_loadout_label_decl_contract.py",
    "Scripts/tests/test_campaign_roster_weather_enum_label_decl_contract.py",
    "Scripts/tests/test_campaign_save_empty_fail_closed.py",
    "Scripts/tests/test_objective_definition_defaults_contract.py",
    "Scripts/tests/test_enemy_wave_defaults_contract.py",
    "Scripts/tests/test_boss_definition_defaults_contract.py",
    "Scripts/tests/test_weather_profile_defaults_contract.py",
    "Scripts/tests/test_mission_presentation_defaults_contract.py",
    "Scripts/tests/test_mission_score_rules_defaults_contract.py",
    "Scripts/tests/test_route_definition_fields_contract.py",
    "Scripts/tests/test_campaign_definition_campaign_id_decl_contract.py",
    "Scripts/tests/test_campaign_definition_display_name_decl_contract.py",
    "Scripts/tests/test_campaign_definition_missions_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_campaign_save_campaign_id_decl_contract.py",
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
)
# Neighbors in the same public section. Presence is not locked
# here. MissionId #350 / DisplayName #351 / CampaignOrder
# #352 / MissionMap #353 / Route #354 / Objectives #355 /
# Waves #356 / Weather #357 / Boss #358 / Presentation #359 /
# ScoreRules / PrerequisiteMissionIds /
# RequiredCampaignMedals / ValidateDefinition /
# FindObjective stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "FName MissionId",
    "FText DisplayName",
    "int32 CampaignOrder = 1;",
    "TSoftObjectPtr<UWorld> MissionMap",
    "FSkyguardRouteDefinition Route",
    "TArray<FSkyguardObjectiveDefinition> Objectives",
    "TArray<FSkyguardEnemyWaveDefinition> Waves",
    "FSkyguardBossDefinition Boss",
    "FSkyguardWeatherProfile Weather",
    "FSkyguardMissionPresentation Presentation",
    "FSkyguardMissionScoreRules ScoreRules",
    "TArray<FName> PrerequisiteMissionIds",
    "int32 RequiredCampaignMedals = 0;",
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
    "const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;",
)
MISSION_ID_NOT_LOCKED = ("FName MissionId",)
DISPLAY_NAME_NOT_LOCKED = ("FText DisplayName",)
CAMPAIGN_ORDER_NOT_LOCKED = ("int32 CampaignOrder = 1;",)
MISSION_MAP_NOT_LOCKED = ("TSoftObjectPtr<UWorld> MissionMap",)
ROUTE_NOT_LOCKED = ("FSkyguardRouteDefinition Route",)
OBJECTIVES_NOT_LOCKED = (
    "TArray<FSkyguardObjectiveDefinition> Objectives",
)
WAVES_NOT_LOCKED = ("TArray<FSkyguardEnemyWaveDefinition> Waves",)
BOSS_NOT_LOCKED = ("FSkyguardBossDefinition Boss",)
WEATHER_NOT_LOCKED = ("FSkyguardWeatherProfile Weather",)
PRESENTATION_NOT_LOCKED = ("FSkyguardMissionPresentation Presentation",)
SCORE_RULES_NOT_LOCKED = ("FSkyguardMissionScoreRules ScoreRules",)
PREREQUISITE_NOT_LOCKED = ("TArray<FName> PrerequisiteMissionIds",)
MEDALS_NOT_LOCKED = ("int32 RequiredCampaignMedals = 0;",)
VALIDATE_DEFINITION_NOT_LOCKED = (
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
)
FIND_OBJECTIVE_NOT_LOCKED = (
    "const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;",
)
# USkyguardCampaignDefinition::GetPrimaryAssetId (#339) stays
# unlocked. This lane is GetPrimaryAssetId on
# USkyguardMissionDefinition only.
CAMPAIGN_PRIMARY_ASSET_NOT_LOCKED = (
    "USkyguardCampaignDefinition",
    "test_get_primary_asset_id_decl_contract.py",
)
DEFINITION_NOT_LOCKED = (
    'FName CampaignId = TEXT("Skyguard52MainCampaign");',
    "USkyguardCampaignDefinition",
    "TArray<TObjectPtr<USkyguardMissionDefinition>> Missions",
)
# Invented GetPrimaryAssetId return values stay unlocked.
# Do not invent a returned asset id or lock the .cpp body.
RETURNED_ASSET_ID_NOT_LOCKED = (
    'TEXT("SkyguardMission")',
    "MissionId.IsNone()",
    "GetFName()",
    "return FPrimaryAssetId",
)
# Leftover struct-default drafts stay unlocked. Those
# leftover drafts lock struct defaults, not this class
# declaration.
LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED = (
    "test_objective_definition_defaults_contract.py",
    "test_enemy_wave_defaults_contract.py",
    "test_boss_definition_defaults_contract.py",
    "test_weather_profile_defaults_contract.py",
    "test_mission_presentation_defaults_contract.py",
    "test_mission_score_rules_defaults_contract.py",
    "test_route_definition_fields_contract.py",
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
# .cpp GetPrimaryAssetId body / invented returned asset ids
# stay unlocked. Do not invent INDEX_NONE or lock the
# cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return FPrimaryAssetId",
    'TEXT("SkyguardMission")',
    "MissionId.IsNone()",
    "GetFName()",
    "USkyguardMissionDefinition::GetPrimaryAssetId",
    "SkyguardMissionDefinition.cpp",
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


def leftover_live_copy_tokens() -> tuple[str, ...]:
    return ("ig" + "la", "ya" + "k", "ri" + "fle")


def leftover_readiness_tokens() -> tuple[str, ...]:
    return (
        "b" + "Ya" + "kRuntimeReady",
        "ASkyguard" + "Ig" + "la" + "Missile",
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


class MissionDefinitionGetPrimaryAssetIdDeclContractTests(unittest.TestCase):
    def test_mission_definition_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, GET_PRIMARY_ASSET_ID), section)

    def test_missing_class_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            class_body(
                "class SKYGUARD52_API USkyguardUnrelatedMission "
                ": public UPrimaryDataAsset\n{\n};\n"
            )
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_other_class_does_not_satisfy(self) -> None:
        other = (
            "class SKYGUARD52_API UOtherMissionDefinition "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "public:\n"
            f"\t{GET_PRIMARY_ASSET_ID}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(other)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_campaign_definition_class_does_not_satisfy(self) -> None:
        definition = (
            "class SKYGUARD52_API USkyguardCampaignDefinition "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "public:\n"
            f"\t{GET_PRIMARY_ASSET_ID}\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(definition)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "private:\n"
            f"\t{GET_PRIMARY_ASSET_ID}\n"
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
            ": public UPrimaryDataAsset\n"
            "{\n"
            "public:\n"
            "\tFName MissionId;\n"
            "private:\n"
            f"\t{GET_PRIMARY_ASSET_ID}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, GET_PRIMARY_ASSET_ID)
        self.assertIn("GetPrimaryAssetId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, GET_PRIMARY_ASSET_ID))

    def test_missing_get_primary_asset_id_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tFName MissionId;\n"
            "\tFText DisplayName;\n"
            "\tint32 CampaignOrder = 1;\n"
            "\tTSoftObjectPtr<UWorld> MissionMap;\n"
            "\tFSkyguardRouteDefinition Route;\n"
            "\tTArray<FSkyguardObjectiveDefinition> Objectives;\n"
            "\tTArray<FSkyguardEnemyWaveDefinition> Waves;\n"
            "\tFSkyguardBossDefinition Boss;\n"
            "\tFSkyguardWeatherProfile Weather;\n"
            "\tFSkyguardMissionPresentation Presentation;\n"
            "\tFSkyguardMissionScoreRules ScoreRules;\n"
            "\tTArray<FName> PrerequisiteMissionIds;\n"
            "\tint32 RequiredCampaignMedals = 0;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, GET_PRIMARY_ASSET_ID)
        self.assertIn("GetPrimaryAssetId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_ufunction_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UFUNCTION_VALIDATE}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, GET_PRIMARY_ASSET_ID)
        self.assertIn("GetPrimaryAssetId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_declaration_includes_virtual_const_override(self) -> None:
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, GET_PRIMARY_ASSET_ID), section)
        self.assertTrue(
            GET_PRIMARY_ASSET_ID.startswith("virtual "),
            GET_PRIMARY_ASSET_ID,
        )
        self.assertIn(" const ", GET_PRIMARY_ASSET_ID)
        self.assertTrue(
            GET_PRIMARY_ASSET_ID.endswith("override;"),
            GET_PRIMARY_ASSET_ID,
        )
        self.assertNotIn("UFUNCTION", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("BlueprintCallable", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("BlueprintPure", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("Category", GET_PRIMARY_ASSET_ID)

    def test_neighbor_helpers_do_not_satisfy(self) -> None:
        other_helpers = (
            "\tFName MissionId;\n"
            "\tFText DisplayName;\n"
            "\tint32 CampaignOrder = 1;\n"
            "\tTSoftObjectPtr<UWorld> MissionMap;\n"
            "\tFSkyguardRouteDefinition Route;\n"
            "\tTArray<FSkyguardObjectiveDefinition> Objectives;\n"
            "\tTArray<FSkyguardEnemyWaveDefinition> Waves;\n"
            "\tFSkyguardBossDefinition Boss;\n"
            "\tFSkyguardWeatherProfile Weather;\n"
            "\tFSkyguardMissionPresentation Presentation;\n"
            "\tFSkyguardMissionScoreRules ScoreRules;\n"
            "\tTArray<FName> PrerequisiteMissionIds;\n"
            "\tint32 RequiredCampaignMedals = 0;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_helpers, GET_PRIMARY_ASSET_ID)
        self.assertIn("GetPrimaryAssetId", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        missing_virtual = (
            "\tFPrimaryAssetId GetPrimaryAssetId() const override;\n"
        )
        missing_const = (
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() override;\n"
        )
        missing_override = (
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() const;\n"
        )
        wrong_return = (
            "\tvirtual void GetPrimaryAssetId() const override;\n"
        )
        extra_arg = (
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId("
            "FName AssetType) const override;\n"
        )
        for region in (
            missing_virtual,
            missing_const,
            missing_override,
            wrong_return,
            extra_arg,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, GET_PRIMARY_ASSET_ID)
            self.assertIn("GetPrimaryAssetId", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_get_primary_asset_id_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, GET_PRIMARY_ASSET_ID),
            GET_PRIMARY_ASSET_ID,
        )
        self.assertTrue(has_declaration(section, GET_PRIMARY_ASSET_ID))
        self.assertEqual(
            declaration_count(section, GET_PRIMARY_ASSET_ID),
            1,
        )
        self.assertTrue(
            GET_PRIMARY_ASSET_ID.startswith("virtual "),
            GET_PRIMARY_ASSET_ID,
        )
        self.assertTrue(
            GET_PRIMARY_ASSET_ID.endswith("override;"),
            GET_PRIMARY_ASSET_ID,
        )
        self.assertIn("FPrimaryAssetId", GET_PRIMARY_ASSET_ID)
        self.assertIn("GetPrimaryAssetId()", GET_PRIMARY_ASSET_ID)
        self.assertIn(" const ", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("INDEX_NONE", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("{", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("}", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("return ", GET_PRIMARY_ASSET_ID)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_virtual = (
            "public:\n"
            "\tvirtual\n"
            "\tFPrimaryAssetId GetPrimaryAssetId() const override;\n"
            "private:\n"
            "};\n"
        )
        wrap_type = (
            "public:\n"
            "\tvirtual FPrimaryAssetId\n"
            "\tGetPrimaryAssetId() const override;\n"
            "private:\n"
            "};\n"
        )
        wrap_name = (
            "public:\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId(\n"
            "\t\t) const override;\n"
            "};\n"
        )
        wrap_const = (
            "public:\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId()\n"
            "\tconst override;\n"
            "};\n"
        )
        wrap_override = (
            "public:\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() const\n"
            "\toverride;\n"
            "};\n"
        )
        header_wrap_virtual = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_virtual}"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_type}"
        )
        header_wrap_name = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_name}"
        )
        header_wrap_const = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_const}"
        )
        header_wrap_override = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_override}"
        )
        for header in (
            header_wrap_virtual,
            header_wrap_type,
            header_wrap_name,
            header_wrap_const,
            header_wrap_override,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, GET_PRIMARY_ASSET_ID),
                section,
            )
            self.assertEqual(
                require_declaration(section, GET_PRIMARY_ASSET_ID),
                GET_PRIMARY_ASSET_ID,
            )
            self.assertEqual(
                declaration_count(section, GET_PRIMARY_ASSET_ID),
                1,
            )
        one_line = f"{{\npublic:\n\t{GET_PRIMARY_ASSET_ID}\n}}\n"
        self.assertTrue(has_declaration(one_line, GET_PRIMARY_ASSET_ID))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, GET_PRIMARY_ASSET_ID), section)
        self.assertEqual(
            require_declaration(section, GET_PRIMARY_ASSET_ID),
            GET_PRIMARY_ASSET_ID,
        )

    def test_declaration_accepts_inline_body_without_locking_it(self) -> None:
        inline = (
            "public:\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() const override\n"
            "\t{\n"
            "\t\treturn FPrimaryAssetId();\n"
            "\t}\n"
            "};\n"
        )
        header = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{inline}"
        )
        section = public_section(header)
        self.assertTrue(has_declaration(section, GET_PRIMARY_ASSET_ID), section)
        self.assertEqual(
            require_declaration(section, GET_PRIMARY_ASSET_ID),
            GET_PRIMARY_ASSET_ID,
        )
        self.assertEqual(
            declaration_count(section, GET_PRIMARY_ASSET_ID),
            1,
        )
        self.assertNotIn("{", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("}", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("return ", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("return FPrimaryAssetId", GET_PRIMARY_ASSET_ID)

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", GET_PRIMARY_ASSET_ID)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_returned_asset_id(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        self.assertNotIn("return ", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("return FPrimaryAssetId", GET_PRIMARY_ASSET_ID)
        self.assertNotIn('TEXT("SkyguardMission")', GET_PRIMARY_ASSET_ID)
        self.assertNotIn("MissionId.IsNone()", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("GetFName()", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("TEXT(", GET_PRIMARY_ASSET_ID)
        self.assertNotIn('"', GET_PRIMARY_ASSET_ID)
        for token in RETURNED_ASSET_ID_NOT_LOCKED:
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, locked_only)
        section = public_section(origin_main_header())
        self.assertNotIn('TEXT("SkyguardMission")', section)
        self.assertNotIn("MissionId.IsNone()", section)
        self.assertNotIn("GetFName()", section)
        self.assertNotIn("return FPrimaryAssetId", section)

    def test_contract_does_not_lock_get_primary_asset_id_cpp_body(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        self.assertNotIn("{", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("}", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("return ", GET_PRIMARY_ASSET_ID)
        self.assertNotIn(
            "USkyguardMissionDefinition::GetPrimaryAssetId",
            GET_PRIMARY_ASSET_ID,
        )
        self.assertNotIn(
            "SkyguardMissionDefinition.cpp",
            GET_PRIMARY_ASSET_ID,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", locked_only)
        self.assertNotIn("return FPrimaryAssetId", GET_PRIMARY_ASSET_ID)
        self.assertNotIn('TEXT("SkyguardMission")', GET_PRIMARY_ASSET_ID)
        self.assertNotIn("MissionId.IsNone()", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("GetFName()", GET_PRIMARY_ASSET_ID)

    def test_contract_does_not_relock_mission_id(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in MISSION_ID_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FName MissionId", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FName MissionId", locked_only)

    def test_contract_does_not_relock_display_name(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in DISPLAY_NAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("DisplayName", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("FText", GET_PRIMARY_ASSET_ID)

    def test_contract_does_not_relock_campaign_order(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in CAMPAIGN_ORDER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("CampaignOrder", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("CampaignOrder", locked_only)

    def test_contract_does_not_relock_mission_map(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in MISSION_MAP_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("MissionMap", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("TSoftObjectPtr", GET_PRIMARY_ASSET_ID)

    def test_contract_does_not_relock_route(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in ROUTE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardRouteDefinition", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardRouteDefinition", locked_only)

    def test_contract_does_not_relock_objectives(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("Objectives", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("Objectives", locked_only)
        self.assertNotIn("FSkyguardObjectiveDefinition", GET_PRIMARY_ASSET_ID)

    def test_contract_does_not_relock_waves(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in WAVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("Waves", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("Waves", locked_only)
        self.assertNotIn("FSkyguardEnemyWaveDefinition", GET_PRIMARY_ASSET_ID)

    def test_contract_does_not_relock_boss(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in BOSS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardBossDefinition", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardBossDefinition", locked_only)

    def test_contract_does_not_relock_weather(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in WEATHER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardWeatherProfile", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardWeatherProfile", locked_only)

    def test_contract_does_not_relock_presentation(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in PRESENTATION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardMissionPresentation", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardMissionPresentation", locked_only)

    def test_contract_does_not_relock_score_rules(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in SCORE_RULES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardMissionScoreRules", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardMissionScoreRules", locked_only)

    def test_contract_does_not_relock_prerequisite_mission_ids(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in PREREQUISITE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("PrerequisiteMissionIds", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)

    def test_contract_does_not_relock_required_campaign_medals(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in MEDALS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("RequiredCampaignMedals", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("RequiredCampaignMedals", locked_only)

    def test_contract_does_not_relock_validate_definition(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in VALIDATE_DEFINITION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("ValidateDefinition", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("OutErrors", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("BlueprintCallable", GET_PRIMARY_ASSET_ID)

    def test_contract_does_not_relock_find_objective(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in FIND_OBJECTIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FindObjective", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("ObjectiveId", GET_PRIMARY_ASSET_ID)

    def test_contract_does_not_relock_campaign_definition_get_primary_asset_id(
        self,
    ) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        section = public_section(origin_main_header())
        for token in CAMPAIGN_PRIMARY_ASSET_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, section)
        for token in DEFINITION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, section)
        self.assertNotIn("USkyguardCampaignDefinition", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("Skyguard52MainCampaign", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)

    def test_contract_does_not_relock_leftover_struct_default_drafts(
        self,
    ) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for token in LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("defaults_contract", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("defaults_contract", locked_only)

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FillResultCombatStats", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("ASkyguardGunner", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FillAndFinalize", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FillAndFail", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("ApplyHydraForClusters", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        self.assertEqual(
            require_declaration(locked_only, GET_PRIMARY_ASSET_ID),
            GET_PRIMARY_ASSET_ID,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FName MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("RequiredCampaignMedals", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("return FPrimaryAssetId", section)
        self.assertNotIn('TEXT("SkyguardMission")', section)
        self.assertNotIn("MissionId.IsNone()", section)
        self.assertNotIn("GetFName()", section)
        self.assertNotIn("OutErrors.Reset", section)
        self.assertNotIn("AddError", section)
        self.assertEqual(
            require_declaration(section, GET_PRIMARY_ASSET_ID),
            GET_PRIMARY_ASSET_ID,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::GetPrimaryAssetId",
            section,
        )

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::GetPrimaryAssetId",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("}", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("return FPrimaryAssetId", GET_PRIMARY_ASSET_ID)
        self.assertNotIn('TEXT("SkyguardMission")', GET_PRIMARY_ASSET_ID)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        section = public_section(origin_main_header())
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, section)
            self.assertNotIn(token, file_text)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "mission GetPrimaryAssetId contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, GET_PRIMARY_ASSET_ID.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"mission GetPrimaryAssetId contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, GET_PRIMARY_ASSET_ID.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, GET_PRIMARY_ASSET_ID)

    def test_contract_is_get_primary_asset_id_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, GET_PRIMARY_ASSET_ID),
            GET_PRIMARY_ASSET_ID,
        )
        locked_only = f"{GET_PRIMARY_ASSET_ID}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, GET_PRIMARY_ASSET_ID)
        self.assertNotIn("FName MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("RequiredCampaignMedals", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        for token in RETURNED_ASSET_ID_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, GET_PRIMARY_ASSET_ID)
            self.assertNotIn(token, section)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, GET_PRIMARY_ASSET_ID.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("{", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("return FPrimaryAssetId", GET_PRIMARY_ASSET_ID)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertTrue(GET_PRIMARY_ASSET_ID.startswith("virtual "))
        self.assertTrue(GET_PRIMARY_ASSET_ID.endswith("override;"))

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
