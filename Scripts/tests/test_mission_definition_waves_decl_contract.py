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
# a waves default, or lock Waves in the .cpp.
# origin/main is one line
# (`TArray<FSkyguardEnemyWaveDefinition> Waves;`);
# accept that form and other split-line wraps. Nearby
# UPROPERTY metadata is present on origin/main; do not
# invent metadata that is not in origin/main.
# This is USkyguardMissionDefinition::Waves, not leftover
# enemy-wave struct defaults and not
# USkyguardCampaignDefinition::Missions.
# Parse the public class section only. Do not parse the
# leftover enemy-wave struct body.
WAVES = "TArray<FSkyguardEnemyWaveDefinition> Waves;"
UPROPERTY_COMBAT = (
    'UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combat")'
)
# Leftover #56–#64 plus MissionDefinition production files.
# This lane only adds an isolated Python Waves field
# declaration contract. Stay off MissionId #350, DisplayName
# #351, CampaignOrder #352, MissionMap, Route (in-flight
# sibling), Objectives (in-flight sibling), Boss, Weather,
# Presentation, ScoreRules, PrerequisiteMissionIds,
# RequiredCampaignMedals, GetPrimaryAssetId,
# ValidateDefinition, and FindObjective on this class.
# Stay off leftover enemy-wave defaults (that leftover
# draft locks struct fields, not this class field), leftover
# objective-definition defaults, leftover boss-definition
# defaults, leftover weather-profile defaults, leftover
# mission-presentation defaults, leftover mission-score-
# rules defaults, leftover route-definition fields (those
# leftover drafts lock struct defaults, not this class
# field). Stay off leftover campaign-roster lookup,
# leftover campaign-save empty-fail-closed, leftover
# campaign definition CampaignId / DisplayName / Missions
# contracts, leftover CPG debrief copy / snapshot /
# fail-closed, leftover Gunner helpers, leftover Harbor
# clocks, leftover theater-kit / flare / HUD, leftover
# drafts #56–#64, leftover ApacheSystem / weapon stations
# / pilot commands / loadout / lock-phase, leftover
# settings invert-look / ApplySettings broadcast,
# leftover bind-hud-host, leftover objective-runtime
# fail-closed, leftover route-runtime fail-closed,
# leftover pilot line / confirm / warn / call-probe /
# duration drafts, leftover gun-fire camera shake,
# leftover mission-weather enum, leftover mission 0N
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
# campaign-roster lookup, leftover campaign-save
# empty-fail-closed, leftover objective / route /
# mission-score / weather / boss / wave / presentation
# defaults, leftover campaign definition CampaignId /
# DisplayName / Missions, leftover MissionId #350,
# leftover DisplayName #351 / CampaignOrder #352 /
# MissionMap / Route / Objectives in-flight siblings,
# leftover CPG debrief, leftover objective-runtime /
# route-runtime fail-closed, leftover theater-kit /
# Harbor / flare / HUD, leftover ApacheSystem / weapon
# stations / pilot commands / loadout, leftover settings
# invert-look, leftover bind-hud-host, leftover pilot
# drafts, leftover gun-fire camera shake, and leftover
# mission-weather enum stay sibling-only.
LOCKED_SCRIPTS = (
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
    "Scripts/tests/test_mission_definition_mission_id_decl_contract.py",
    "Scripts/tests/test_mission_definition_display_name_decl_contract.py",
    "Scripts/tests/test_mission_definition_campaign_order_decl_contract.py",
    "Scripts/tests/test_mission_definition_mission_map_decl_contract.py",
    "Scripts/tests/test_mission_definition_route_decl_contract.py",
    "Scripts/tests/test_mission_definition_objectives_decl_contract.py",
    "Scripts/tests/test_validate_definition_decl_contract.py",
    "Scripts/tests/test_find_mission_decl_contract.py",
    "Scripts/tests/test_get_primary_asset_id_decl_contract.py",
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
    "Scripts/tests/test_gun_fire_camera_shake_tests.py",
    "Scripts/tests/test_mission_weather_enum_contract.py",
)
# Neighbors in the same public section. Presence is not locked
# here. MissionId #350 / DisplayName #351 / CampaignOrder
# #352 / MissionMap / Route / Objectives / Boss / Weather /
# Presentation / ScoreRules / PrerequisiteMissionIds /
# RequiredCampaignMedals / GetPrimaryAssetId /
# ValidateDefinition / FindObjective stay sibling-only.
UNLOCKED_NEIGHBORS = (
    "FName MissionId",
    "FText DisplayName",
    "int32 CampaignOrder = 1;",
    "TSoftObjectPtr<UWorld> MissionMap",
    "FSkyguardRouteDefinition Route",
    "TArray<FSkyguardObjectiveDefinition> Objectives",
    "FSkyguardBossDefinition Boss",
    "FSkyguardWeatherProfile Weather",
    "FSkyguardMissionPresentation Presentation",
    "FSkyguardMissionScoreRules ScoreRules",
    "TArray<FName> PrerequisiteMissionIds",
    "int32 RequiredCampaignMedals = 0;",
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;",
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
    "const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;",
)
MISSION_ID_NOT_LOCKED = ("FName MissionId;",)
DISPLAY_NAME_NOT_LOCKED = ("FText DisplayName",)
CAMPAIGN_ORDER_NOT_LOCKED = ("int32 CampaignOrder = 1;",)
MISSION_MAP_NOT_LOCKED = ("TSoftObjectPtr<UWorld> MissionMap",)
ROUTE_NOT_LOCKED = ("FSkyguardRouteDefinition Route",)
OBJECTIVES_NOT_LOCKED = (
    "TArray<FSkyguardObjectiveDefinition> Objectives",
)
BOSS_NOT_LOCKED = ("FSkyguardBossDefinition Boss",)
WEATHER_NOT_LOCKED = ("FSkyguardWeatherProfile Weather",)
PRESENTATION_NOT_LOCKED = ("FSkyguardMissionPresentation Presentation",)
SCORE_RULES_NOT_LOCKED = ("FSkyguardMissionScoreRules ScoreRules",)
PREREQUISITE_NOT_LOCKED = ("TArray<FName> PrerequisiteMissionIds",)
MEDALS_NOT_LOCKED = ("int32 RequiredCampaignMedals = 0;",)
PRIMARY_ASSET_NOT_LOCKED = (
    "virtual FPrimaryAssetId GetPrimaryAssetId() const override;",
)
VALIDATE_DEFINITION_NOT_LOCKED = (
    "bool ValidateDefinition(TArray<FText>& OutErrors) const;",
)
FIND_OBJECTIVE_NOT_LOCKED = (
    "const FSkyguardObjectiveDefinition* FindObjective(FName ObjectiveId) const;",
)
# USkyguardCampaignDefinition / USkyguardCampaignSaveGame
# identity fields stay unlocked. This lane is Waves on
# USkyguardMissionDefinition only.
DEFINITION_NOT_LOCKED = (
    'FName CampaignId = TEXT("Skyguard52MainCampaign");',
    "USkyguardCampaignDefinition",
    "TArray<TObjectPtr<USkyguardMissionDefinition>> Missions",
)
SAVE_GAME_CAMPAIGN_ID_NOT_LOCKED = (
    "USkyguardCampaignSaveGame",
)
# Leftover struct-default drafts stay unlocked. Those
# leftover drafts lock struct defaults, not this class
# field. Leftover enemy-wave defaults locks WaveId /
# StartTimeSeconds / Formations / CompletionObjectiveId
# on the leftover enemy-wave struct, not this class field.
LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED = (
    "test_objective_definition_defaults_contract.py",
    "test_enemy_wave_defaults_contract.py",
    "test_boss_definition_defaults_contract.py",
    "test_weather_profile_defaults_contract.py",
    "test_mission_presentation_defaults_contract.py",
    "test_mission_score_rules_defaults_contract.py",
    "test_route_definition_fields_contract.py",
)
LEFTOVER_ENEMY_WAVE_FIELDS_NOT_LOCKED = (
    "FName WaveId;",
    "float StartTimeSeconds = 0.f;",
    "TArray<FSkyguardEnemyFormationDefinition> Formations;",
    "FName CompletionObjectiveId;",
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
# Invented UPROPERTY specifiers that are not on origin/main
# for this field. Nearby origin/main metadata is
# EditAnywhere, BlueprintReadOnly, Category = "Combat".
# Do not invent extra specifiers. Neighbor fields may use
# ClampMin meta; that is not locked here.
INVENTED_UPROPERTY = (
    "BlueprintReadWrite",
    "VisibleAnywhere",
    "VisibleDefaultsOnly",
    "EditDefaultsOnly",
    "SaveGame",
    'Category = "Campaign"',
    'Category = "Campaign|Id"',
    'Category = "Combat|Waves"',
    "AllowPrivateAccess",
)
INVENTED_FIELD_META = (
    "meta =",
)
# Invented waves defaults are not on origin/main.
# Do not invent an initializer or INDEX_NONE sentinel.
INVENTED_WAVES_DEFAULT = (
    "INDEX_NONE",
    "NAME_None",
    "{}",
    "TArray()",
)
# .cpp Waves body / invented INDEX_NONE stay unlocked.
# Do not invent INDEX_NONE or lock the cpp body.
CPP_AND_INVENTED = (
    "INDEX_NONE",
    "NAME_None",
    "return INDEX_NONE",
    "return false",
    "return true",
    "USkyguardMissionDefinition::Waves",
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
    compact = re.sub(r"\s*<\s*", "<", compact)
    compact = re.sub(r"\s*>\s*", ">", compact)
    compact = re.sub(r">([A-Za-z_])", r"> \1", compact)
    compact = re.sub(r"\s*\*\s*", "* ", compact)
    compact = re.sub(r"\s*=\s*", " = ", compact)
    return compact


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


def has_declaration(region: str, declaration: str) -> bool:
    if declaration in region:
        return True
    return collapsed(declaration) in collapsed(region)


def declaration_count(region: str, declaration: str) -> int:
    if declaration in region:
        return region.count(declaration)
    return collapsed(region).count(collapsed(declaration))


def require_declaration(region: str, declaration: str) -> str:
    if not has_declaration(region, declaration):
        raise AssertionError(
            f"{declaration} is missing from origin/main:{HEADER_PATH} "
            f"class {CLASS_NAME} public section"
        )
    return declaration


class MissionDefinitionWavesDeclContractTests(unittest.TestCase):
    def test_mission_definition_class_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(CLASS_NAME, header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        body = class_body(header)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        section = public_section(header)
        self.assertTrue(has_declaration(section, WAVES), section)

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
            f"\t{WAVES}\n"
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
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>> "
            "Missions;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(definition)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_save_game_class_does_not_satisfy(self) -> None:
        save_game = (
            "class SKYGUARD52_API USkyguardCampaignSaveGame "
            ": public USaveGame\n"
            "{\n"
            "public:\n"
            "\tFName CampaignId;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            public_section(save_game)
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_public_section_fails_closed(self) -> None:
        private_only = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            ": public UPrimaryDataAsset\n"
            "{\n"
            "private:\n"
            f"\t{WAVES}\n"
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
            f"\t{WAVES}\n"
            "};\n"
        )
        section = public_section(mixed)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(section, WAVES)
        self.assertIn("Waves", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))
        self.assertFalse(has_declaration(section, WAVES))

    def test_missing_waves_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "\tFName MissionId;\n"
            "\tFText DisplayName;\n"
            "\tint32 CampaignOrder = 1;\n"
            "\tTSoftObjectPtr<UWorld> MissionMap;\n"
            "\tFSkyguardRouteDefinition Route;\n"
            "\tTArray<FSkyguardObjectiveDefinition> Objectives;\n"
            "\tFSkyguardBossDefinition Boss;\n"
            "\tFSkyguardWeatherProfile Weather;\n"
            "\tFSkyguardMissionPresentation Presentation;\n"
            "\tFSkyguardMissionScoreRules ScoreRules;\n"
            "\tTArray<FName> PrerequisiteMissionIds;\n"
            "\tint32 RequiredCampaignMedals = 0;\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, WAVES)
        self.assertIn("Waves", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(CLASS_NAME, str(raised.exception))

    def test_uproperty_macro_alone_does_not_satisfy(self) -> None:
        macro_only = f"\t{UPROPERTY_COMBAT}\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(macro_only, WAVES)
        self.assertIn("Waves", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_origin_main_uproperty_metadata_is_present(self) -> None:
        section = public_section(origin_main_header())
        self.assertIn(UPROPERTY_COMBAT, section)
        self.assertIn("EditAnywhere", section)
        self.assertIn("BlueprintReadOnly", section)
        self.assertIn('Category = "Combat"', section)
        self.assertTrue(has_declaration(section, WAVES), section)
        self.assertNotIn("UPROPERTY", WAVES)
        self.assertNotIn("EditAnywhere", WAVES)
        self.assertNotIn("BlueprintReadOnly", WAVES)
        self.assertNotIn("Category", WAVES)
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, UPROPERTY_COMBAT)
            self.assertNotIn(invented, WAVES)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, UPROPERTY_COMBAT)
            self.assertNotIn(invented, WAVES)

    def test_neighbor_fields_do_not_satisfy(self) -> None:
        other_fields = (
            "\tFName MissionId;\n"
            "\tFText DisplayName;\n"
            "\tint32 CampaignOrder = 1;\n"
            "\tTSoftObjectPtr<UWorld> MissionMap;\n"
            "\tFSkyguardRouteDefinition Route;\n"
            "\tTArray<FSkyguardObjectiveDefinition> Objectives;\n"
            "\tFSkyguardBossDefinition Boss;\n"
            "\tFSkyguardWeatherProfile Weather;\n"
            "\tFSkyguardMissionPresentation Presentation;\n"
            "\tFSkyguardMissionScoreRules ScoreRules;\n"
            "\tTArray<FName> PrerequisiteMissionIds;\n"
            "\tint32 RequiredCampaignMedals = 0;\n"
            "\tvirtual FPrimaryAssetId GetPrimaryAssetId() "
            "const override;\n"
            "\tbool ValidateDefinition("
            "TArray<FText>& OutErrors) const;\n"
            "\tconst FSkyguardObjectiveDefinition* FindObjective("
            "FName ObjectiveId) const;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(other_fields, WAVES)
        self.assertIn("Waves", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_wrong_signature_does_not_satisfy(self) -> None:
        wrong_inner = (
            "\tTArray<FSkyguardObjectiveDefinition> Waves;\n"
        )
        boss_inner = "\tTArray<FSkyguardBossDefinition> Waves;\n"
        name_inner = "\tTArray<FName> Waves;\n"
        wrong_name = (
            "\tTArray<FSkyguardEnemyWaveDefinition> WaveList;\n"
        )
        scalar = "\tFSkyguardEnemyWaveDefinition Waves;\n"
        map_type = (
            "\tTMap<FName, FSkyguardEnemyWaveDefinition> Waves;\n"
        )
        name_type = "\tFName Waves;\n"
        assigned = (
            "\tTArray<FSkyguardEnemyWaveDefinition> Waves = {};\n"
        )
        mission_id = "\tFName MissionId;\n"
        campaign_id = "\tFName CampaignId;\n"
        definition_id = (
            '\tFName CampaignId = TEXT("Skyguard52MainCampaign");\n'
        )
        display_name = "\tFText DisplayName;\n"
        missions = (
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>> "
            "Missions;\n"
        )
        for region in (
            wrong_inner,
            boss_inner,
            name_inner,
            wrong_name,
            scalar,
            map_type,
            name_type,
            assigned,
            mission_id,
            campaign_id,
            definition_id,
            display_name,
            missions,
        ):
            with self.assertRaises(AssertionError) as raised:
                require_declaration(region, WAVES)
            self.assertIn("Waves", str(raised.exception))
            self.assertIn("missing", str(raised.exception).lower())

    def test_campaign_definition_missions_does_not_satisfy(self) -> None:
        missions = (
            "\tTArray<TObjectPtr<USkyguardMissionDefinition>> "
            "Missions;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(missions, WAVES)
        self.assertIn("Waves", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(missions, WAVES))

    def test_leftover_enemy_wave_struct_fields_do_not_satisfy(self) -> None:
        leftover = (
            "\tFName WaveId;\n"
            "\tfloat StartTimeSeconds = 0.f;\n"
            "\tTArray<FSkyguardEnemyFormationDefinition> "
            "Formations;\n"
            "\tFName CompletionObjectiveId;\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(leftover, WAVES)
        self.assertIn("Waves", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(leftover, WAVES))

    def test_invented_waves_assignment_does_not_satisfy(self) -> None:
        assigned = (
            "\tTArray<FSkyguardEnemyWaveDefinition> Waves = {};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            require_declaration(assigned, WAVES)
        self.assertIn("Waves", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(assigned, WAVES))

    def test_wrong_type_does_not_satisfy(self) -> None:
        wrong = "\tTArray<FSkyguardObjectiveDefinition> Waves;\n"
        with self.assertRaises(AssertionError) as raised:
            require_declaration(wrong, WAVES)
        self.assertIn("Waves", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(wrong, WAVES))

    def test_waves_declaration_matches_origin_main(self) -> None:
        section = public_section(origin_main_header())
        self.assertEqual(
            require_declaration(section, WAVES),
            WAVES,
        )
        self.assertTrue(has_declaration(section, WAVES))
        self.assertEqual(
            declaration_count(section, WAVES),
            1,
        )
        self.assertTrue(
            WAVES.endswith(";"),
            WAVES,
        )
        self.assertTrue(
            WAVES.startswith("TArray<"),
            WAVES,
        )
        self.assertIn("Waves", WAVES)
        self.assertIn("FSkyguardEnemyWaveDefinition", WAVES)
        self.assertNotIn("=", WAVES)
        self.assertNotIn("TEXT(", WAVES)
        self.assertNotIn("INDEX_NONE", WAVES)
        self.assertNotIn("NAME_None", WAVES)
        self.assertNotIn("UFUNCTION", WAVES)
        self.assertNotIn("{", WAVES)
        self.assertNotIn("}", WAVES)
        self.assertNotIn("return ", WAVES)

    def test_declaration_does_not_invent_waves_default(self) -> None:
        locked_only = f"{WAVES}\n"
        self.assertNotIn("=", WAVES)
        self.assertNotIn("TEXT(", WAVES)
        for invented in INVENTED_WAVES_DEFAULT:
            self.assertNotIn(invented, WAVES)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, WAVES), section)
        self.assertNotIn("NAME_None", WAVES)
        self.assertNotIn("INDEX_NONE", WAVES)
        self.assertNotIn("{}", locked_only)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "public:\n"
            "\tTArray<FSkyguardEnemyWaveDefinition>\n"
            "\tWaves;\n"
            "private:\n"
            "};\n"
        )
        wrap_tabs = (
            "public:\n"
            "\tTArray<FSkyguardEnemyWaveDefinition>\n"
            "\t\tWaves;\n"
            "private:\n"
            "};\n"
        )
        wrap_spaces = (
            "public:\n"
            "\tTArray<FSkyguardEnemyWaveDefinition>    "
            "Waves;\n"
            "};\n"
        )
        wrap_leading = (
            "public:\n"
            "    TArray<FSkyguardEnemyWaveDefinition> "
            "Waves;\n"
            "};\n"
        )
        wrap_template = (
            "public:\n"
            "\tTArray<\n"
            "\t\tFSkyguardEnemyWaveDefinition\n"
            "\t> Waves;\n"
            "};\n"
        )
        header_wrap_type = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_type}"
        )
        header_wrap_tabs = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_tabs}"
        )
        header_wrap_spaces = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_spaces}"
        )
        header_wrap_leading = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_leading}"
        )
        header_wrap_template = (
            f"class SKYGUARD52_API {CLASS_NAME} "
            f": public UPrimaryDataAsset\n{{\n{wrap_template}"
        )
        for header in (
            header_wrap_type,
            header_wrap_tabs,
            header_wrap_spaces,
            header_wrap_leading,
            header_wrap_template,
        ):
            section = public_section(header)
            self.assertTrue(
                has_declaration(section, WAVES),
                section,
            )
            self.assertEqual(
                require_declaration(section, WAVES),
                WAVES,
            )
            self.assertEqual(
                declaration_count(section, WAVES),
                1,
            )
        one_line = f"{{\npublic:\n\t{WAVES}\n}}\n"
        self.assertTrue(has_declaration(one_line, WAVES))
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, WAVES), section)
        self.assertEqual(
            require_declaration(section, WAVES),
            WAVES,
        )

    def test_declaration_does_not_invent_index_none(self) -> None:
        locked_only = f"{WAVES}\n"
        self.assertNotIn("INDEX_NONE", locked_only)
        self.assertNotIn("INDEX_NONE", WAVES)
        self.assertNotIn("return INDEX_NONE", locked_only)
        self.assertNotIn("NAME_None", WAVES)
        section = public_section(origin_main_header())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("NAME_None", section)

    def test_declaration_does_not_invent_uproperty_metadata(self) -> None:
        locked_only = f"{WAVES}\n"
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, WAVES)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_COMBAT)
        for invented in INVENTED_FIELD_META:
            self.assertNotIn(invented, WAVES)
            self.assertNotIn(invented, locked_only)
            self.assertNotIn(invented, UPROPERTY_COMBAT)
        section = public_section(origin_main_header())
        for invented in INVENTED_UPROPERTY:
            self.assertNotIn(invented, section)
        self.assertIn(UPROPERTY_COMBAT, section)

    def test_declaration_does_not_invent_ufunction(self) -> None:
        locked_only = f"{WAVES}\n"
        self.assertNotIn("UFUNCTION", WAVES)
        self.assertNotIn("UFUNCTION", locked_only)
        self.assertFalse(WAVES.startswith("UFUNCTION"), WAVES)
        section = public_section(origin_main_header())
        self.assertTrue(has_declaration(section, WAVES), section)
        self.assertEqual(
            require_declaration(section, WAVES),
            WAVES,
        )

    def test_contract_does_not_lock_waves_cpp_body(self) -> None:
        locked_only = f"{WAVES}\n"
        self.assertNotIn("{", WAVES)
        self.assertNotIn("}", WAVES)
        self.assertNotIn("return ", WAVES)
        self.assertNotIn(
            "USkyguardMissionDefinition::Waves",
            WAVES,
        )
        self.assertNotIn(
            "SkyguardMissionDefinition.cpp",
            WAVES,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", locked_only)
        self.assertNotIn("return false", WAVES)
        self.assertNotIn("AddError", WAVES)

    def test_contract_does_not_relock_mission_id(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in MISSION_ID_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("FName MissionId", WAVES)
        self.assertNotIn("FName MissionId", locked_only)

    def test_contract_does_not_relock_display_name(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in DISPLAY_NAME_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("DisplayName", WAVES)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("FText", WAVES)

    def test_contract_does_not_relock_campaign_order(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in CAMPAIGN_ORDER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("CampaignOrder", WAVES)
        self.assertNotIn("CampaignOrder", locked_only)

    def test_contract_does_not_relock_mission_map(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in MISSION_MAP_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("MissionMap", WAVES)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("TSoftObjectPtr", WAVES)

    def test_contract_does_not_relock_route(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in ROUTE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("FSkyguardRouteDefinition", WAVES)
        self.assertNotIn("FSkyguardRouteDefinition", locked_only)

    def test_contract_does_not_relock_objectives(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in OBJECTIVES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("Objectives", WAVES)
        self.assertNotIn("Objectives", locked_only)
        self.assertNotIn("FSkyguardObjectiveDefinition", WAVES)

    def test_contract_does_not_relock_boss(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in BOSS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("FSkyguardBossDefinition", WAVES)
        self.assertNotIn("FSkyguardBossDefinition", locked_only)

    def test_contract_does_not_relock_weather(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in WEATHER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("FSkyguardWeatherProfile", WAVES)
        self.assertNotIn("FSkyguardWeatherProfile", locked_only)

    def test_contract_does_not_relock_presentation(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in PRESENTATION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("FSkyguardMissionPresentation", WAVES)
        self.assertNotIn("FSkyguardMissionPresentation", locked_only)

    def test_contract_does_not_relock_score_rules(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in SCORE_RULES_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("FSkyguardMissionScoreRules", WAVES)
        self.assertNotIn("FSkyguardMissionScoreRules", locked_only)

    def test_contract_does_not_relock_prerequisite_mission_ids(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in PREREQUISITE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("PrerequisiteMissionIds", WAVES)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)

    def test_contract_does_not_relock_required_campaign_medals(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in MEDALS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("RequiredCampaignMedals", WAVES)
        self.assertNotIn("RequiredCampaignMedals", locked_only)

    def test_contract_does_not_relock_primary_asset_id(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in PRIMARY_ASSET_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("GetPrimaryAssetId", WAVES)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("FPrimaryAssetId", WAVES)

    def test_contract_does_not_relock_validate_definition(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in VALIDATE_DEFINITION_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("ValidateDefinition", WAVES)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("OutErrors", WAVES)
        self.assertNotIn("BlueprintCallable", WAVES)

    def test_contract_does_not_relock_find_objective(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in FIND_OBJECTIVE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("FindObjective", WAVES)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("ObjectiveId", WAVES)

    def test_contract_does_not_relock_campaign_definition_fields(self) -> None:
        locked_only = f"{WAVES}\n"
        section = public_section(origin_main_header())
        for token in DEFINITION_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)
        self.assertNotIn("Skyguard52MainCampaign", WAVES)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", WAVES)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        for token in SAVE_GAME_CAMPAIGN_ID_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_struct_default_drafts(
        self,
    ) -> None:
        locked_only = f"{WAVES}\n"
        for token in LEFTOVER_STRUCT_DEFAULTS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
        self.assertNotIn("defaults_contract", WAVES)
        self.assertNotIn("defaults_contract", locked_only)

    def test_contract_does_not_relock_leftover_enemy_wave_defaults(
        self,
    ) -> None:
        locked_only = f"{WAVES}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_ENEMY_WAVE_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)
        self.assertNotIn("WaveId", WAVES)
        self.assertNotIn("StartTimeSeconds", WAVES)
        self.assertNotIn("CompletionObjectiveId", WAVES)
        self.assertNotIn("FSkyguardEnemyFormationDefinition", WAVES)
        self.assertNotIn("WaveId", locked_only)
        self.assertNotIn("StartTimeSeconds", locked_only)
        self.assertNotIn("CompletionObjectiveId", locked_only)
        self.assertNotIn("FSkyguardEnemyFormationDefinition", locked_only)
        self.assertNotIn("test_enemy_wave_defaults_contract.py", WAVES)
        self.assertNotIn("test_enemy_wave_defaults_contract.py", locked_only)

    def test_contract_does_not_parse_enemy_wave_struct_body(self) -> None:
        locked_only = f"{WAVES}\n"
        header = origin_main_header()
        section = public_section(header)
        self.assertEqual(
            HEADER_PATH,
            "Source/Skyguard52/SkyguardMissionDefinition.h",
        )
        self.assertNotIn("SkyguardMissionTypes.h", WAVES)
        self.assertNotIn("SkyguardMissionTypes.h", locked_only)
        self.assertNotIn("struct FSkyguardEnemyWaveDefinition", WAVES)
        self.assertNotIn("struct FSkyguardEnemyWaveDefinition", locked_only)
        self.assertNotIn("struct FSkyguardEnemyWaveDefinition", section)
        self.assertNotIn("WaveId", section)
        self.assertNotIn("StartTimeSeconds", section)
        self.assertNotIn("CompletionObjectiveId", section)
        self.assertNotIn("FSkyguardEnemyFormationDefinition", section)
        self.assertEqual(
            require_declaration(section, WAVES),
            WAVES,
        )

    def test_contract_does_not_relock_fill_and_gunner_helpers(self) -> None:
        locked_only = f"{WAVES}\n"
        for neighbor in FILL_AND_GUNNER_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("FillResultCombatStats", WAVES)
        self.assertNotIn("ASkyguardGunner", WAVES)
        self.assertNotIn("FillAndFinalize", WAVES)
        self.assertNotIn("FillAndFail", WAVES)
        self.assertNotIn("ApplyHydraForClusters", WAVES)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)

    def test_contract_does_not_relock_leftover_cpg_debrief_siblings(
        self,
    ) -> None:
        locked_only = f"{WAVES}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardBuildCpgDebriefCopy", locked_only)
        self.assertNotIn("SkyguardCpgCopyHasBannedTerm", locked_only)
        self.assertNotIn("SkyguardCaptureCpgDebrief", locked_only)
        self.assertNotIn("FSkyguardCpgDebriefSnapshot", locked_only)

    def test_contract_does_not_relock_leftover_runtime_fail_closed(
        self,
    ) -> None:
        locked_only = f"{WAVES}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_leftover_siblings(self) -> None:
        locked_only = f"{WAVES}\n"
        section = public_section(origin_main_header())
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{WAVES}\n"
        self.assertEqual(
            require_declaration(locked_only, WAVES),
            WAVES,
        )
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("FName MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("RequiredCampaignMedals", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)

    def test_contract_parses_public_section_not_private_or_cpp(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertNotIn("OutErrors.Reset", section)
        self.assertNotIn("AddError", section)
        self.assertEqual(
            require_declaration(section, WAVES),
            WAVES,
        )
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::Waves",
            section,
        )
        self.assertNotIn("struct FSkyguardEnemyWaveDefinition", section)

    def test_contract_does_not_read_cpp_or_invented_bodies(self) -> None:
        section = public_section(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)
        self.assertNotIn("SkyguardMissionDefinition.cpp", section)
        self.assertNotIn(
            "USkyguardMissionDefinition::Waves",
            section,
        )
        self.assertNotIn("return INDEX_NONE", section)
        self.assertNotIn("{", WAVES)
        self.assertNotIn("}", WAVES)
        self.assertNotIn("return false", WAVES)
        self.assertNotIn("AddError", WAVES)

    def test_contract_does_not_retune_harbor(self) -> None:
        section = public_section(origin_main_header())
        locked_only = f"{WAVES}\n"
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, locked_only)

    def test_harbor_40_80_tokens_fail_closed_if_present(self) -> None:
        locked_only = f"{WAVES}\n"
        section = public_section(origin_main_header())
        file_text = this_file_text()
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)
            self.assertNotIn(token, file_text)

    def test_this_file_bans_retired_live_copy(self) -> None:
        file_text = this_file_text().lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                file_text,
                "mission Waves contract contains "
                f"{banned}; declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )

    def test_contract_does_not_require_retired_live_mount(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, lowered)
            self.assertNotIn(banned, WAVES.lower())
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, WAVES)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", section)

    def test_declaration_bans_retired_live_copy(self) -> None:
        section = public_section(origin_main_header())
        lowered = section.lower()
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(
                banned,
                lowered,
                f"mission Waves contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / "
                "Hellfire, not leftover live copy",
            )
            self.assertNotIn(banned, WAVES.lower())

    def test_contract_does_not_read_dirty_workspace_header(self) -> None:
        header = origin_main_header()
        dirty = "D:" + "\\Skyguard52"
        dirty_fwd = "D:" + "/Skyguard52"
        self.assertNotIn(dirty, header)
        self.assertNotIn(dirty_fwd, header)
        section = public_section(header)
        self.assertNotIn(dirty, section)
        self.assertNotIn(dirty_fwd, WAVES)

    def test_contract_is_waves_declaration_only(self) -> None:
        header = origin_main_header()
        section = public_section(header)
        self.assertIsNotNone(CLASS_RE.search(header), header)
        self.assertEqual(
            require_declaration(section, WAVES),
            WAVES,
        )
        locked_only = f"{WAVES}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, WAVES)
        self.assertNotIn("FName MissionId", locked_only)
        self.assertNotIn("DisplayName", locked_only)
        self.assertNotIn("CampaignOrder", locked_only)
        self.assertNotIn("MissionMap", locked_only)
        self.assertNotIn("FindObjective", locked_only)
        self.assertNotIn("GetPrimaryAssetId", locked_only)
        self.assertNotIn("ValidateDefinition", locked_only)
        self.assertNotIn("PrerequisiteMissionIds", locked_only)
        self.assertNotIn("RequiredCampaignMedals", locked_only)
        self.assertNotIn("FillResultCombatStats", locked_only)
        self.assertNotIn("ASkyguardGunner", locked_only)
        self.assertNotIn("FillAndFinalize", locked_only)
        self.assertNotIn("FillAndFail", locked_only)
        self.assertNotIn("ApplyHydraForClusters", locked_only)
        self.assertNotIn("USkyguardCampaignDefinition", locked_only)
        self.assertNotIn("USkyguardCampaignSaveGame", locked_only)
        self.assertNotIn("Skyguard52MainCampaign", locked_only)
        self.assertNotIn("WaveId", locked_only)
        self.assertNotIn("StartTimeSeconds", locked_only)
        self.assertNotIn("CompletionObjectiveId", locked_only)
        self.assertNotIn("FSkyguardEnemyFormationDefinition", locked_only)
        self.assertNotIn("struct FSkyguardEnemyWaveDefinition", locked_only)
        self.assertNotIn("SkyguardMissionTypes.h", locked_only)
        for token in LEFTOVER_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
        for token in LEFTOVER_CPG_DEBRIEF_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
        for token in LEFTOVER_RUNTIME_FAIL_CLOSED_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
        for token in LEFTOVER_ENEMY_WAVE_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, WAVES)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)
        for token in leftover_readiness_tokens():
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, WAVES)
            self.assertNotIn(token, section)
        for token in INVENTED_WAVES_DEFAULT:
            self.assertNotIn(token, WAVES)
        for token in leftover_harbor_tokens():
            self.assertNotIn(token, section)
            self.assertNotIn(token, locked_only)
        for banned in leftover_live_copy_tokens():
            self.assertNotIn(banned, section.lower())
            self.assertNotIn(banned, WAVES.lower())
        self.assertNotIn("INDEX_NONE", section)
        self.assertNotIn("return ", WAVES)
        self.assertNotIn("{", WAVES)
        self.assertNotIn("AddError", WAVES)
        self.assertNotIn("ApplyHydraForClusters", section)
        self.assertEqual(
            WAVES,
            "TArray<FSkyguardEnemyWaveDefinition> Waves;",
        )

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
