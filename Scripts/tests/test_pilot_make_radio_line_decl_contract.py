from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_PATH = "Source/Skyguard52/SkyguardPilotVoice.h"
NAMESPACE_NAME = "SkyguardPilotVoice"
# Declaration presence only. Do not invent INDEX_NONE, return
# values, or radio-line field contents.
# origin/main may split the factory as
# FSkyguardRadioLine /
# MakeRadioLine(ESkyguardPilotLine Line);
MAKE_RADIO_LINE = "FSkyguardRadioLine MakeRadioLine(ESkyguardPilotLine Line);"
MAKE_RADIO_LINE_HEAD = "MakeRadioLine("
LOCKED_DECLARATION = MAKE_RADIO_LINE
LOCKED_DECLARATIONS = (MAKE_RADIO_LINE,)
# Leftover #56–#64 plus PilotVoice production sources. This lane
# only adds an isolated Python MakeRadioLine declaration contract.
# Stay off leftover Harbor #6/#8/#9, leftover theater-kit #59,
# flare/HUD #57/#61/#62, leftover #58 CPG HUD pilot confirm,
# leftover #16 Harbor pilot commands, CPG mesh/art, Harbor
# IncomingRadar 40/80, and FSkyguardMission0NIntegrationReadiness
# (bYakRuntimeReady).
LOCKED = {
    "SkyguardPilotVoice.h",
    "SkyguardPilotVoice.cpp",
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
# Isolated-test drafts stay off this lane. LineTextForEvent is the
# sibling in-flight declaration. ConfirmLineForCommand strings
# (#120), LineDurationForEvent (#117), WarnOffAxis / CallLock /
# CallReload strings (#129), ResetCallProbe / CallEvent (#128),
# ESkyguardPilotLine enum (#170), leftover ESkyguardPilotCommand
# roster (#152), leftover theater-kit #59, and radio-line field
# defaults (#172) stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_pilot_line_text_for_event_decl_contract.py",
    "Scripts/tests/test_pilot_confirm_line_contract.py",
    "Scripts/tests/test_pilot_warn_lock_reload_contract.py",
    "Scripts/tests/test_pilot_line_enum_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_radio_line_defaults_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "FString ConfirmLineForCommand(ESkyguardPilotCommand Command);",
    "FString LineTextForEvent(ESkyguardPilotLine Line);",
    "float LineDurationForEvent(ESkyguardPilotLine Line);",
    "void ConfirmCommand(UObject* WorldContext, ESkyguardPilotCommand Command);",
    "void WarnOffAxis(UObject* WorldContext);",
    "void CallLock(UObject* WorldContext);",
    "void CallReload(UObject* WorldContext, const TCHAR* Station);",
    "void CallEvent(UObject* WorldContext, ESkyguardPilotLine Line);",
    "void ResetCallProbe();",
    "ESkyguardPilotLine GetLastCalledLine();",
    "FString GetLastCalledText();",
    "int32 GetCalledEventCount();",
)
LINE_TEXT_NOT_LOCKED = "FString LineTextForEvent(ESkyguardPilotLine Line);"
CONFIRM_LINE_NOT_LOCKED = (
    "FString ConfirmLineForCommand(ESkyguardPilotCommand Command);"
)
LINE_DURATION_NOT_LOCKED = (
    "float LineDurationForEvent(ESkyguardPilotLine Line);"
)
WARN_LOCK_RELOAD_NOT_LOCKED = (
    "void WarnOffAxis(UObject* WorldContext);",
    "void CallLock(UObject* WorldContext);",
    "void CallReload(UObject* WorldContext, const TCHAR* Station);",
)
PROBE_NOT_LOCKED = (
    "void ResetCallProbe();",
    "void CallEvent(UObject* WorldContext, ESkyguardPilotLine Line);",
)
GETTERS_NOT_LOCKED = (
    "void ConfirmCommand(UObject* WorldContext, ESkyguardPilotCommand Command);",
    "ESkyguardPilotLine GetLastCalledLine();",
    "FString GetLastCalledText();",
    "int32 GetCalledEventCount();",
)
# Do not invent FSkyguardRadioLine field contents. Those stay in
# leftover #172 radio-line defaults.
RADIO_LINE_FIELDS_NOT_LOCKED = (
    "FName LineId;",
    "FText Speaker;",
    "FText Subtitle;",
    "TSoftObjectPtr<USoundBase> Sound;",
    "int32 Priority = 50;",
    "float EstimatedDurationSeconds = 2.f;",
    "float CooldownSeconds = 0.f;",
)
# #170 / leftover #152 enumerators stay unlocked. Names are
# documentary only — this contract does not lock the roster.
PILOT_LINE_ENUMERATORS_NOT_LOCKED = (
    "enum class ESkyguardPilotLine",
    "RadarLit",
    "CargoHit",
    "Inbound",
    "FlaresGood",
    "Win",
    "Fail",
    "LoadoutPrompt",
)
PILOT_COMMAND_ENUMERATORS_NOT_LOCKED = (
    "enum class ESkyguardPilotCommand",
    "OrbitLeft",
    "OrbitRight",
    "AttackRun",
    "FaceTarget",
    "Pursuit",
    "Break",
)
SIBLING_TYPES = (
    "enum class ESkyguardPilotLine",
    "enum class ESkyguardPilotCommand",
    "struct FSkyguardRadioLine",
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
)
# .cpp bodies / invented return values / radio-line tables stay
# unlocked.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
    "LineTextForEvent(Line)",
    "ConfirmLineForCommand",
)
BANNED = ("igla", "yak", "rifle")
HARBOR_INCOMING = "IncomingRadar"
HARBOR_CLOCKS = (
    "IncomingRadarLiveIntervalSeconds",
    "IncomingRadarDownIntervalSeconds",
)
HARBOR_TUNING = ("40.f", "80.f")
NAMESPACE_RE = re.compile(rf"namespace\s+{re.escape(NAMESPACE_NAME)}\b")


def collapsed(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text)
    normalized = re.sub(r"\s*\(\s*", "(", normalized)
    normalized = re.sub(r"\s*\)\s*", ")", normalized)
    return normalized.strip()


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


def namespace_body(header: str) -> str:
    """Parse namespace SkyguardPilotVoice only, not sibling types."""
    match = NAMESPACE_RE.search(header)
    if match is None:
        raise AssertionError(
            f"namespace {NAMESPACE_NAME} is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = match.start()
    brace = header.index("{", start)
    depth = 0
    for index, char in enumerate(header[brace:], start=brace):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return header[brace : index + 1]
    raise AssertionError(
        f"namespace {NAMESPACE_NAME} body is unclosed in "
        f"origin/main:{HEADER_PATH}"
    )


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
            f"namespace {NAMESPACE_NAME}"
        )
    return declaration


class PilotMakeRadioLineDeclContractTests(unittest.TestCase):
    def test_pilot_voice_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertTrue(has_declaration(body, MAKE_RADIO_LINE), body)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)
        self.assertNotIn("enum class ESkyguardPilotLine", body)
        self.assertNotIn("enum class ESkyguardPilotCommand", body)
        self.assertNotIn("struct FSkyguardRadioLine", body)

    def test_missing_namespace_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            namespace_body(
                "namespace SkyguardUnrelatedVoice\n{\n};\n"
            )
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enum_or_struct_alone_does_not_satisfy_namespace(self) -> None:
        enum_and_struct = (
            "enum class ESkyguardPilotLine : uint8\n"
            "{\n"
            "\tRadarLit,\n"
            "\tWin,\n"
            "\tFail\n"
            "};\n"
            "struct FSkyguardRadioLine\n"
            "{\n"
            "\tFName LineId;\n"
            "\tint32 Priority = 50;\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            namespace_body(enum_and_struct)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_make_radio_line_declaration_fails_closed(self) -> None:
        neighbors_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tFString ConfirmLineForCommand(ESkyguardPilotCommand Command);\n"
            "\tFString LineTextForEvent(ESkyguardPilotLine Line);\n"
            "\tfloat LineDurationForEvent(ESkyguardPilotLine Line);\n"
            "\tvoid ConfirmCommand(UObject* WorldContext, ESkyguardPilotCommand Command);\n"
            "\tvoid WarnOffAxis(UObject* WorldContext);\n"
            "\tvoid CallLock(UObject* WorldContext);\n"
            "\tvoid CallReload(UObject* WorldContext, const TCHAR* Station);\n"
            "\tvoid CallEvent(UObject* WorldContext, ESkyguardPilotLine Line);\n"
            "\tvoid ResetCallProbe();\n"
            "\tESkyguardPilotLine GetLastCalledLine();\n"
            "\tFString GetLastCalledText();\n"
            "\tint32 GetCalledEventCount();\n"
            "}\n"
        )
        body = namespace_body(neighbors_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(body, MAKE_RADIO_LINE)
        self.assertIn("MakeRadioLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_neighbors_do_not_satisfy_make_radio_line(self) -> None:
        neighbors_only = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tFString ConfirmLineForCommand(ESkyguardPilotCommand Command);\n"
            "\tFString LineTextForEvent(ESkyguardPilotLine Line);\n"
            "\tfloat LineDurationForEvent(ESkyguardPilotLine Line);\n"
            "\tvoid WarnOffAxis(UObject* WorldContext);\n"
            "\tvoid CallLock(UObject* WorldContext);\n"
            "\tvoid CallReload(UObject* WorldContext, const TCHAR* Station);\n"
            "\tvoid CallEvent(UObject* WorldContext, ESkyguardPilotLine Line);\n"
            "\tvoid ResetCallProbe();\n"
            "}\n"
        )
        body = namespace_body(neighbors_only)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(body, MAKE_RADIO_LINE)
        self.assertIn("MakeRadioLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertFalse(has_declaration(body, MAKE_RADIO_LINE))
        self.assertIn("LineTextForEvent", body)
        self.assertIn("ConfirmLineForCommand", body)
        self.assertIn("LineDurationForEvent", body)
        self.assertIn("WarnOffAxis", body)
        self.assertIn("CallEvent", body)
        self.assertIn("ResetCallProbe", body)

    def test_wrong_signature_does_not_satisfy(self) -> None:
        wrong = (
            f"namespace {NAMESPACE_NAME}\n"
            "{\n"
            "\tvoid MakeRadioLine(ESkyguardPilotLine Line);\n"
            "\tFSkyguardRadioLine MakeRadioLine();\n"
            "\tFSkyguardRadioLine MakeRadioLine(ESkyguardPilotCommand Command);\n"
            "\tFString MakeRadioLine(ESkyguardPilotLine Line);\n"
            "\tFSkyguardRadioLine LineTextForEvent(ESkyguardPilotLine Line);\n"
            "}\n"
        )
        body = namespace_body(wrong)
        with self.assertRaises(AssertionError) as raised:
            require_declaration(body, MAKE_RADIO_LINE)
        self.assertIn("MakeRadioLine", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn("MakeRadioLine", body)
        self.assertFalse(has_declaration(body, MAKE_RADIO_LINE))

    def test_origin_main_split_line_form_is_accepted(self) -> None:
        split_return = (
            "{\n"
            "\tFSkyguardRadioLine\n"
            "\tMakeRadioLine(ESkyguardPilotLine Line);\n"
            "}\n"
        )
        split_parens = (
            "{\n"
            "\tFSkyguardRadioLine MakeRadioLine(\n"
            "\t\tESkyguardPilotLine Line);\n"
            "}\n"
        )
        one_line = "{\n\t" + MAKE_RADIO_LINE + "\n}\n"
        self.assertTrue(
            has_declaration(split_return, MAKE_RADIO_LINE),
            split_return,
        )
        self.assertEqual(
            require_declaration(split_return, MAKE_RADIO_LINE),
            MAKE_RADIO_LINE,
        )
        self.assertEqual(declaration_count(split_return, MAKE_RADIO_LINE), 1)
        self.assertEqual(
            require_declaration(split_parens, MAKE_RADIO_LINE),
            MAKE_RADIO_LINE,
        )
        self.assertEqual(
            require_declaration(one_line, MAKE_RADIO_LINE),
            MAKE_RADIO_LINE,
        )
        self.assertIn(MAKE_RADIO_LINE_HEAD, split_return)
        self.assertIn(MAKE_RADIO_LINE_HEAD, split_parens)
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, MAKE_RADIO_LINE),
            MAKE_RADIO_LINE,
        )
        self.assertIn(MAKE_RADIO_LINE_HEAD, body)

    def test_make_radio_line_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, MAKE_RADIO_LINE),
            MAKE_RADIO_LINE,
        )
        self.assertEqual(LOCKED_DECLARATIONS, (MAKE_RADIO_LINE,))
        self.assertEqual(LOCKED_DECLARATION, MAKE_RADIO_LINE)
        self.assertTrue(has_declaration(body, MAKE_RADIO_LINE), body)
        self.assertEqual(declaration_count(body, MAKE_RADIO_LINE), 1)
        self.assertTrue(MAKE_RADIO_LINE.endswith(";"), MAKE_RADIO_LINE)
        self.assertNotIn("INDEX_NONE", MAKE_RADIO_LINE)
        self.assertNotIn("return ", MAKE_RADIO_LINE)
        self.assertNotIn("LineTextForEvent", MAKE_RADIO_LINE)
        self.assertNotIn("ConfirmLineForCommand", MAKE_RADIO_LINE)
        self.assertNotIn("LineDurationForEvent", MAKE_RADIO_LINE)
        self.assertNotIn("WarnOffAxis", MAKE_RADIO_LINE)
        self.assertNotIn("CallLock", MAKE_RADIO_LINE)
        self.assertNotIn("CallReload", MAKE_RADIO_LINE)
        self.assertNotIn("ResetCallProbe", MAKE_RADIO_LINE)
        self.assertNotIn("CallEvent", MAKE_RADIO_LINE)

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        for declaration in LOCKED_DECLARATIONS:
            self.assertTrue(declaration.endswith(";"), declaration)
            self.assertNotIn("return ", declaration)
            self.assertNotIn("INDEX_NONE", declaration)
            self.assertNotIn("NAME_None", declaration)
            self.assertNotIn("{", declaration)
            self.assertNotIn("}", declaration)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MAKE_RADIO_LINE)
            if token not in ("return ", "ConfirmLineForCommand"):
                self.assertNotIn(token, body)
        self.assertNotIn("return ", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("= INDEX_NONE", body)

    def test_declaration_does_not_invent_radio_line_field_contents(
        self,
    ) -> None:
        locked_only = f"{MAKE_RADIO_LINE}\n"
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(locked_only, MAKE_RADIO_LINE),
            MAKE_RADIO_LINE,
        )
        for token in RADIO_LINE_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAKE_RADIO_LINE)
            self.assertNotIn(token, body)
        self.assertNotIn("Priority = 50", MAKE_RADIO_LINE)
        self.assertNotIn("EstimatedDurationSeconds", MAKE_RADIO_LINE)
        self.assertNotIn("CooldownSeconds", MAKE_RADIO_LINE)
        self.assertNotIn("LineId", MAKE_RADIO_LINE)
        self.assertNotIn("Speaker", MAKE_RADIO_LINE)
        self.assertNotIn("Subtitle", MAKE_RADIO_LINE)
        self.assertIn(
            "Scripts/tests/test_radio_line_defaults_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_line_text_for_event(self) -> None:
        locked_only = f"{MAKE_RADIO_LINE}\n"
        self.assertEqual(
            require_declaration(locked_only, MAKE_RADIO_LINE),
            MAKE_RADIO_LINE,
        )
        self.assertNotIn(LINE_TEXT_NOT_LOCKED, locked_only)
        self.assertNotIn(LINE_TEXT_NOT_LOCKED, MAKE_RADIO_LINE)
        self.assertNotIn(LINE_TEXT_NOT_LOCKED, LOCKED_DECLARATIONS)
        self.assertNotIn("LineTextForEvent", MAKE_RADIO_LINE)
        self.assertNotIn("LineTextForEvent", locked_only)
        self.assertIn(
            "Scripts/tests/test_pilot_line_text_for_event_decl_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_confirm_line_for_command(self) -> None:
        locked_only = f"{MAKE_RADIO_LINE}\n"
        self.assertNotIn(CONFIRM_LINE_NOT_LOCKED, locked_only)
        self.assertNotIn(CONFIRM_LINE_NOT_LOCKED, LOCKED_DECLARATIONS)
        self.assertNotIn("ConfirmLineForCommand", MAKE_RADIO_LINE)
        self.assertNotIn("ConfirmLineForCommand", locked_only)
        self.assertNotIn("Coming left. Holding the circle.", MAKE_RADIO_LINE)
        self.assertNotIn("Rolling in.", MAKE_RADIO_LINE)
        self.assertIn(
            "Scripts/tests/test_pilot_confirm_line_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_line_duration_for_event(self) -> None:
        locked_only = f"{MAKE_RADIO_LINE}\n"
        self.assertNotIn(LINE_DURATION_NOT_LOCKED, locked_only)
        self.assertNotIn(LINE_DURATION_NOT_LOCKED, LOCKED_DECLARATIONS)
        self.assertNotIn("LineDurationForEvent", MAKE_RADIO_LINE)
        self.assertNotIn("LineDurationForEvent", locked_only)
        self.assertNotIn("float LineDurationForEvent", LOCKED_DECLARATIONS)

    def test_contract_does_not_relock_warn_lock_or_reload(self) -> None:
        locked_only = f"{MAKE_RADIO_LINE}\n"
        for token in WARN_LOCK_RELOAD_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAKE_RADIO_LINE)
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn("WarnOffAxis", MAKE_RADIO_LINE)
        self.assertNotIn("CallLock", MAKE_RADIO_LINE)
        self.assertNotIn("CallReload", MAKE_RADIO_LINE)
        self.assertIn(
            "Scripts/tests/test_pilot_warn_lock_reload_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_reset_call_probe_or_call_event(
        self,
    ) -> None:
        locked_only = f"{MAKE_RADIO_LINE}\n"
        for token in PROBE_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAKE_RADIO_LINE)
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn("ResetCallProbe", MAKE_RADIO_LINE)
        self.assertNotIn("CallEvent", MAKE_RADIO_LINE)
        self.assertNotIn("CallEvent", locked_only)

    def test_contract_does_not_relock_confirm_or_last_called_getters(
        self,
    ) -> None:
        locked_only = f"{MAKE_RADIO_LINE}\n"
        for token in GETTERS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, MAKE_RADIO_LINE)
            self.assertNotIn(token, LOCKED_DECLARATIONS)
        self.assertNotIn("ConfirmCommand", MAKE_RADIO_LINE)
        self.assertNotIn("GetLastCalledLine", MAKE_RADIO_LINE)
        self.assertNotIn("GetLastCalledText", MAKE_RADIO_LINE)
        self.assertNotIn("GetCalledEventCount", MAKE_RADIO_LINE)

    def test_contract_does_not_relock_pilot_line_enum(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardPilotLine", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("UENUM(", body)
        for name in PILOT_LINE_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, MAKE_RADIO_LINE)
        self.assertNotIn("ESkyguardPilotLine::RadarLit", body)
        self.assertNotIn("ESkyguardPilotLine::RadarLit", MAKE_RADIO_LINE)
        self.assertIn(
            "Scripts/tests/test_pilot_line_enum_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_does_not_relock_pilot_command_roster(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardPilotCommand", body)
        for name in PILOT_COMMAND_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, MAKE_RADIO_LINE)
            if name != "enum class ESkyguardPilotCommand":
                self.assertNotIn(name, body)
        self.assertNotIn("ESkyguardPilotCommand::OrbitLeft", body)
        self.assertNotIn("ESkyguardPilotCommand::OrbitLeft", MAKE_RADIO_LINE)
        self.assertIn(
            "Scripts/tests/test_pilot_command_roster_contract.py",
            LOCKED_SCRIPTS,
        )

    def test_contract_parses_namespace_not_struct_or_enum(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertNotIn("enum class ESkyguardPilotLine", body)
        self.assertNotIn("enum class ESkyguardPilotCommand", body)
        self.assertNotIn("struct FSkyguardRadioLine", body)
        self.assertTrue(has_declaration(body, MAKE_RADIO_LINE), body)
        for token in RADIO_LINE_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, body)

    def test_contract_does_not_read_cpp_or_radio_line_tables(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MAKE_RADIO_LINE)
        self.assertNotIn("SkyguardPilotVoice.cpp", body)
        self.assertNotIn("SkyguardPilotVoice::MakeRadioLine", body)
        self.assertNotIn("LineTextForEvent(Line)", body)
        self.assertNotIn("return ", body)

    def test_contract_does_not_retune_harbor(self) -> None:
        body = namespace_body(origin_main_header())
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("IncomingRadarLiveIntervalSeconds", body)
        self.assertNotIn("IncomingRadarDownIntervalSeconds", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", body)

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(LOCKED_DECLARATIONS, ("Rifle", "Igla"))
        self.assertNotEqual(MAKE_RADIO_LINE, "Rifle")
        self.assertNotEqual(MAKE_RADIO_LINE, "Igla")
        self.assertNotIn("ESkyguardGunshipWeapon::Igla", body)
        self.assertNotIn("ESkyguardGunshipWeapon::Rifle", body)
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)
        self.assertNotIn("YakSpawnLocation", body)

    def test_namespace_bans_igla_yak_rifle(self) -> None:
        body = namespace_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"namespace {NAMESPACE_NAME} contains {banned}; "
                "MakeRadioLine is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, MAKE_RADIO_LINE.lower())

    def test_contract_is_make_radio_line_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(LOCKED_DECLARATIONS, (MAKE_RADIO_LINE,))
        self.assertEqual(
            require_declaration(body, MAKE_RADIO_LINE),
            MAKE_RADIO_LINE,
        )
        locked_only = f"{MAKE_RADIO_LINE}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, MAKE_RADIO_LINE)
            self.assertNotIn(neighbor, LOCKED_DECLARATIONS)
        for token in RADIO_LINE_FIELDS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, body)
        self.assertNotIn("LineTextForEvent", locked_only)
        self.assertNotIn("ConfirmLineForCommand", locked_only)
        self.assertNotIn("LineDurationForEvent", locked_only)
        self.assertNotIn("WarnOffAxis", locked_only)
        self.assertNotIn("CallLock", locked_only)
        self.assertNotIn("CallReload", locked_only)
        self.assertNotIn("ResetCallProbe", locked_only)
        self.assertNotIn("CallEvent", locked_only)
        self.assertNotIn("ConfirmCommand", locked_only)
        self.assertNotIn("GetLastCalledLine", locked_only)
        self.assertNotIn("GetLastCalledText", locked_only)
        self.assertNotIn("GetCalledEventCount", locked_only)
        for name in SIBLING_TYPES:
            self.assertNotIn(name, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, MAKE_RADIO_LINE)
        for token in HARBOR_CLOCKS:
            self.assertNotIn(token, body)
        for token in HARBOR_TUNING:
            self.assertNotIn(token, body)
        self.assertNotIn("40.f, 80.f", body)
        self.assertNotIn(HARBOR_INCOMING, body)
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("return ", body)
        self.assertNotIn("enum class", body)
        self.assertNotIn("struct FSkyguardRadioLine", body)
        self.assertNotIn("LineTextForEvent", LOCKED_DECLARATIONS)
        self.assertNotIn("ConfirmLineForCommand", LOCKED_DECLARATIONS)
        self.assertNotIn("LineDurationForEvent", LOCKED_DECLARATIONS)
        self.assertNotIn("WarnOffAxis", LOCKED_DECLARATIONS)
        self.assertNotIn("CallEvent", LOCKED_DECLARATIONS)
        self.assertNotIn("ResetCallProbe", LOCKED_DECLARATIONS)
        self.assertNotEqual(list(LOCKED_DECLARATIONS), ["Rifle", "Igla"])
        self.assertIn(
            "Scripts/tests/test_pilot_line_text_for_event_decl_contract.py",
            LOCKED_SCRIPTS,
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
