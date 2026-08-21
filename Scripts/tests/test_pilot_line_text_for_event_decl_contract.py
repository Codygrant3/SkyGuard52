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
# values, or the actual line strings.
LINE_TEXT_FOR_EVENT = "FString LineTextForEvent(ESkyguardPilotLine Line);"
# Leftover #56–#64 plus PilotVoice production sources/tests.
# This lane only adds an isolated Python LineTextForEvent
# declaration contract. Stay off leftover Harbor #6/#8/#9,
# leftover #16 Harbor pilot commands, leftover #58 CPG HUD
# pilot confirm, leftover theater-kit #59, and leftover
# flare/HUD #57/#61/#62.
LOCKED = {
    "SkyguardPilotVoice.h",
    "SkyguardPilotVoice.cpp",
    "SkyguardPilotVoiceDurationTests.cpp",
    "SkyguardPilotVoiceCallProbeTests.cpp",
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
# Isolated-test drafts stay off this lane. ConfirmLineForCommand
# strings (#120), LineDurationForEvent (#117), WarnOffAxis /
# CallLock / CallReload strings (#129), ResetCallProbe /
# CallEvent (#128), ESkyguardPilotLine enum (#170), and
# leftover ESkyguardPilotCommand roster (#152) stay sibling-only.
LOCKED_SCRIPTS = (
    "Scripts/tests/test_pilot_confirm_line_contract.py",
    "Scripts/tests/test_pilot_warn_lock_reload_contract.py",
    "Scripts/tests/test_pilot_line_enum_contract.py",
    "Scripts/tests/test_pilot_command_roster_contract.py",
    "Scripts/tests/test_campaign_theater_kit_contract.py",
)
# Neighbors in the same namespace. Presence is not locked here.
UNLOCKED_NEIGHBORS = (
    "FString ConfirmLineForCommand(ESkyguardPilotCommand Command);",
    "float LineDurationForEvent(ESkyguardPilotLine Line);",
    "FSkyguardRadioLine MakeRadioLine(ESkyguardPilotLine Line);",
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
CONFIRM_LINE_NOT_LOCKED = (
    "FString ConfirmLineForCommand(ESkyguardPilotCommand Command);"
)
DURATION_NOT_LOCKED = "float LineDurationForEvent(ESkyguardPilotLine Line);"
WARN_LOCK_RELOAD_NOT_LOCKED = (
    "void WarnOffAxis(UObject* WorldContext);",
    "void CallLock(UObject* WorldContext);",
    "void CallReload(UObject* WorldContext, const TCHAR* Station);",
)
CALL_PROBE_NOT_LOCKED = (
    "void ResetCallProbe();",
    "void CallEvent(UObject* WorldContext, ESkyguardPilotLine Line);",
)
NEIGHBOR_HELPERS_NOT_LOCKED = (
    "FSkyguardRadioLine MakeRadioLine(ESkyguardPilotLine Line);",
    "void ConfirmCommand(UObject* WorldContext, ESkyguardPilotCommand Command);",
    "ESkyguardPilotLine GetLastCalledLine();",
    "FString GetLastCalledText();",
    "int32 GetCalledEventCount();",
)
# .cpp TEXT payloads / confirm strings stay unlocked. Do not
# invent the actual line strings.
LINE_STRINGS_NOT_LOCKED = (
    "Radar just lit us",
    "Cargo is taking hits",
    "That hull is on fire",
    "Missile inbound",
    "Flares good",
    "Blackout. Thermal",
    "Winchester-safe",
    "Pick a loadout",
    "Coming left. Holding the circle.",
    "Coming right. Holding the circle.",
    "Rolling in.",
    "Breaking off.",
    "Opening the range.",
    "Holding station.",
    "Popping up.",
    "Dropping behind cover.",
    "Coming onto your target.",
    "Staying in the fight.",
    "Break the glass",
    "Good lock. Missile is yours.",
    "Reloading %s.",
    'return TEXT("',
    "TEXT(",
)
# #170 enumerators stay unlocked. Parse the namespace, not the enum.
PILOT_LINE_ENUM_NOT_LOCKED = (
    "enum class ESkyguardPilotLine",
    "RadarLit",
    "CargoHit",
    "CargoCritical",
    "ShipRadarDown",
    "ShipEnginesDown",
    "ShipLauncherDown",
    "ShipCannonDown",
    "ShipDeckDown",
    "ShipDead",
    "Inbound",
    "FlaresGood",
    "Choice",
    "Extract",
    "GoThermal",
    "Win",
    "Fail",
    "LoadoutPrompt",
)
# Leftover #152 command roster stays unlocked.
PILOT_COMMAND_ROSTER_NOT_LOCKED = (
    "enum class ESkyguardPilotCommand",
    "OrbitLeft",
    "OrbitRight",
    "AttackRun",
    "Break",
    "Extend",
    "Hold",
    "Climb",
    "Descend",
    "FaceTarget",
    "Pursuit",
)
# #117 durations stay unlocked.
DURATION_VALUES_NOT_LOCKED = (
    "3.2f",
    "3.0f",
    "2.8f",
    "2.6f",
    "2.4f",
    "2.2f",
    "2.0f",
    "4.0f",
    "return 3.2f",
    "return 2.4f",
)
SIBLING_TYPES = (
    "enum class ESkyguardPilotLine",
    "enum class ESkyguardPilotCommand",
    "struct FSkyguardRadioLine",
    "FSkyguardMission0NIntegrationReadiness",
    "bYakRuntimeReady",
)
# .cpp bodies / invented return values / line tables stay unlocked.
CPP_AND_INVENTED = (
    "return ",
    "INDEX_NONE",
    "NAME_None",
    "return 0",
    "return -1",
    "return INDEX_NONE",
    "return FString()",
    "return TEXT(",
    "switch (Line)",
    "default:",
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
    compact = re.sub(r"\s+", " ", text).strip()
    compact = re.sub(r"\s*\(\s*", "(", compact)
    compact = re.sub(r"\s*\)\s*", ")", compact)
    compact = re.sub(r"\s*,\s*", ",", compact)
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


def namespace_body(header: str) -> str:
    match = NAMESPACE_RE.search(header)
    if match is None:
        raise AssertionError(
            f"namespace {NAMESPACE_NAME} is missing from "
            f"origin/main:{HEADER_PATH}"
        )
    start = match.start()
    brace = header.index("{", start)
    finish = header.index("}", brace)
    return header[brace : finish + 1]


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


class PilotLineTextForEventDeclContractTests(unittest.TestCase):
    def test_pilot_voice_namespace_exists(self) -> None:
        header = origin_main_header()
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        body = namespace_body(header)
        self.assertTrue(has_declaration(body, LINE_TEXT_FOR_EVENT), body)
        self.assertTrue(body.startswith("{"), body)
        self.assertTrue(body.endswith("}"), body)

    def test_missing_namespace_fails_closed(self) -> None:
        with self.assertRaises(AssertionError) as raised:
            namespace_body(
                "namespace SkyguardUnrelatedPilotVoice\n{\n};\n"
            )
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_enum_alone_does_not_satisfy_namespace(self) -> None:
        enum_only = (
            "enum class ESkyguardPilotLine : uint8\n"
            "{\n"
            "\tRadarLit,\n"
            "\tLoadoutPrompt\n"
            "};\n"
            "enum class ESkyguardPilotCommand : uint8\n"
            "{\n"
            "\tOrbitLeft,\n"
            "\tPursuit\n"
            "};\n"
        )
        with self.assertRaises(AssertionError) as raised:
            namespace_body(enum_only)
        self.assertIn(NAMESPACE_NAME, str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())

    def test_missing_line_text_declaration_fails_closed(self) -> None:
        neighbors_only = (
            "{\n"
            "\tFString ConfirmLineForCommand(ESkyguardPilotCommand Command);\n"
            "\tfloat LineDurationForEvent(ESkyguardPilotLine Line);\n"
            "\tFSkyguardRadioLine MakeRadioLine(ESkyguardPilotLine Line);\n"
            "\tvoid ConfirmCommand(UObject* WorldContext, "
            "ESkyguardPilotCommand Command);\n"
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
        with self.assertRaises(AssertionError) as raised:
            require_declaration(neighbors_only, LINE_TEXT_FOR_EVENT)
        self.assertIn("LineTextForEvent", str(raised.exception))
        self.assertIn("missing", str(raised.exception).lower())
        self.assertIn(NAMESPACE_NAME, str(raised.exception))

    def test_line_text_declaration_matches_origin_main(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertEqual(
            require_declaration(body, LINE_TEXT_FOR_EVENT),
            LINE_TEXT_FOR_EVENT,
        )
        self.assertTrue(has_declaration(body, LINE_TEXT_FOR_EVENT))
        self.assertEqual(declaration_count(body, LINE_TEXT_FOR_EVENT), 1)
        self.assertTrue(LINE_TEXT_FOR_EVENT.endswith(";"), LINE_TEXT_FOR_EVENT)
        self.assertNotIn("INDEX_NONE", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("return ", LINE_TEXT_FOR_EVENT)

    def test_declaration_accepts_origin_main_split_line_forms(self) -> None:
        wrap_type = (
            "{\n"
            "\tFString\n"
            "\tLineTextForEvent(ESkyguardPilotLine Line);\n"
            "}\n"
        )
        wrap_args = (
            "{\n"
            "\tFString LineTextForEvent(\n"
            "\t\tESkyguardPilotLine Line);\n"
            "}\n"
        )
        self.assertTrue(has_declaration(wrap_type, LINE_TEXT_FOR_EVENT), wrap_type)
        self.assertTrue(has_declaration(wrap_args, LINE_TEXT_FOR_EVENT), wrap_args)
        self.assertEqual(
            require_declaration(wrap_type, LINE_TEXT_FOR_EVENT),
            LINE_TEXT_FOR_EVENT,
        )
        self.assertEqual(
            require_declaration(wrap_args, LINE_TEXT_FOR_EVENT),
            LINE_TEXT_FOR_EVENT,
        )
        self.assertEqual(declaration_count(wrap_type, LINE_TEXT_FOR_EVENT), 1)
        self.assertEqual(declaration_count(wrap_args, LINE_TEXT_FOR_EVENT), 1)
        one_line = f"{{\n\t{LINE_TEXT_FOR_EVENT}\n}}\n"
        self.assertTrue(has_declaration(one_line, LINE_TEXT_FOR_EVENT))
        body = namespace_body(origin_main_header())
        self.assertTrue(has_declaration(body, LINE_TEXT_FOR_EVENT), body)
        self.assertEqual(
            require_declaration(body, LINE_TEXT_FOR_EVENT),
            LINE_TEXT_FOR_EVENT,
        )

    def test_declaration_does_not_invent_index_none_or_return_values(
        self,
    ) -> None:
        body = namespace_body(origin_main_header())
        self.assertTrue(LINE_TEXT_FOR_EVENT.endswith(";"), LINE_TEXT_FOR_EVENT)
        self.assertNotIn("return ", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("INDEX_NONE", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("NAME_None", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("{", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("}", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("return ", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("return INDEX_NONE", body)
        self.assertNotIn("return 0", body)
        self.assertNotIn("return -1", body)
        self.assertNotIn("return FString()", body)
        self.assertNotIn("= INDEX_NONE", body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LINE_TEXT_FOR_EVENT)
            if token != "return ":
                self.assertNotIn(token, body)

    def test_declaration_does_not_invent_line_strings(self) -> None:
        body = namespace_body(origin_main_header())
        locked_only = f"{LINE_TEXT_FOR_EVENT}\n"
        for token in LINE_STRINGS_NOT_LOCKED:
            self.assertNotIn(token, LINE_TEXT_FOR_EVENT)
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, body)
        self.assertNotIn("TEXT(", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("TEXT(", body)
        self.assertNotIn('return TEXT("', body)
        self.assertNotEqual(LINE_TEXT_FOR_EVENT, "Radar just lit us")
        self.assertNotEqual(LINE_TEXT_FOR_EVENT, "Missile inbound")

    def test_contract_does_not_relock_confirm_line_for_command(self) -> None:
        locked_only = f"{LINE_TEXT_FOR_EVENT}\n"
        self.assertEqual(
            require_declaration(locked_only, LINE_TEXT_FOR_EVENT),
            LINE_TEXT_FOR_EVENT,
        )
        self.assertNotIn(CONFIRM_LINE_NOT_LOCKED, locked_only)
        self.assertNotIn(CONFIRM_LINE_NOT_LOCKED, LINE_TEXT_FOR_EVENT)
        self.assertNotIn("ConfirmLineForCommand", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("ConfirmLineForCommand", locked_only)
        for token in (
            "Coming left. Holding the circle.",
            "Staying in the fight.",
            "Rolling in.",
        ):
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LINE_TEXT_FOR_EVENT)

    def test_contract_does_not_relock_line_duration(self) -> None:
        locked_only = f"{LINE_TEXT_FOR_EVENT}\n"
        self.assertNotIn(DURATION_NOT_LOCKED, locked_only)
        self.assertNotIn("LineDurationForEvent", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("LineDurationForEvent", locked_only)
        for token in DURATION_VALUES_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LINE_TEXT_FOR_EVENT)
        self.assertNotIn(
            "float LineDurationForEvent(ESkyguardPilotLine Line);",
            (LINE_TEXT_FOR_EVENT,),
        )

    def test_contract_does_not_relock_warn_lock_reload(self) -> None:
        locked_only = f"{LINE_TEXT_FOR_EVENT}\n"
        for neighbor in WARN_LOCK_RELOAD_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LINE_TEXT_FOR_EVENT)
        self.assertNotIn("WarnOffAxis", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("CallLock", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("CallReload", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("Break the glass", locked_only)
        self.assertNotIn("Good lock. Missile is yours.", locked_only)
        self.assertNotIn("Reloading %s.", locked_only)

    def test_contract_does_not_relock_call_probe(self) -> None:
        locked_only = f"{LINE_TEXT_FOR_EVENT}\n"
        for neighbor in CALL_PROBE_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LINE_TEXT_FOR_EVENT)
        self.assertNotIn("ResetCallProbe", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("CallEvent", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("ResetCallProbe", locked_only)
        self.assertNotIn("CallEvent", locked_only)

    def test_contract_does_not_relock_pilot_line_enum(self) -> None:
        locked_only = f"{LINE_TEXT_FOR_EVENT}\n"
        body = namespace_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardPilotLine", locked_only)
        self.assertNotIn("enum class ESkyguardPilotLine", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("enum class ESkyguardPilotLine", body)
        for name in PILOT_LINE_ENUM_NOT_LOCKED:
            if name == "enum class ESkyguardPilotLine":
                continue
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, LINE_TEXT_FOR_EVENT)
            self.assertNotIn(name, body)

    def test_contract_does_not_relock_pilot_command_roster(self) -> None:
        locked_only = f"{LINE_TEXT_FOR_EVENT}\n"
        body = namespace_body(origin_main_header())
        self.assertNotIn("enum class ESkyguardPilotCommand", locked_only)
        self.assertNotIn("enum class ESkyguardPilotCommand", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("enum class ESkyguardPilotCommand", body)
        for name in PILOT_COMMAND_ROSTER_NOT_LOCKED:
            if name == "enum class ESkyguardPilotCommand":
                continue
            self.assertNotIn(name, locked_only)
            self.assertNotIn(name, LINE_TEXT_FOR_EVENT)
            self.assertNotIn(name, body)

    def test_contract_does_not_relock_neighbor_helpers(self) -> None:
        locked_only = f"{LINE_TEXT_FOR_EVENT}\n"
        self.assertEqual(
            require_declaration(locked_only, LINE_TEXT_FOR_EVENT),
            LINE_TEXT_FOR_EVENT,
        )
        for neighbor in NEIGHBOR_HELPERS_NOT_LOCKED:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LINE_TEXT_FOR_EVENT)
        self.assertNotIn("MakeRadioLine", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("ConfirmCommand", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("GetLastCalledLine", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("GetLastCalledText", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("GetCalledEventCount", LINE_TEXT_FOR_EVENT)
        self.assertNotIn("MakeRadioLine", locked_only)
        self.assertNotIn("ConfirmCommand", locked_only)
        self.assertNotIn("GetLastCalledLine", locked_only)
        self.assertNotIn("GetLastCalledText", locked_only)
        self.assertNotIn("GetCalledEventCount", locked_only)

    def test_contract_parses_namespace_not_enum_or_cpp(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertNotIn("enum class ESkyguardPilotLine", body)
        self.assertNotIn("enum class ESkyguardPilotCommand", body)
        self.assertNotIn("struct FSkyguardRadioLine", body)
        self.assertEqual(
            require_declaration(body, LINE_TEXT_FOR_EVENT),
            LINE_TEXT_FOR_EVENT,
        )
        self.assertNotIn("SkyguardPilotVoice.cpp", body)
        self.assertNotIn("TEXT(", body)

    def test_contract_does_not_read_cpp_or_line_tables(self) -> None:
        body = namespace_body(origin_main_header())
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LINE_TEXT_FOR_EVENT)
        self.assertNotIn("SkyguardPilotVoice.cpp", body)
        self.assertNotIn("SkyguardPilotVoice::LineTextForEvent", body)
        self.assertNotIn("switch (Line)", body)
        self.assertNotIn("return TEXT(", body)
        self.assertNotIn("return FString()", body)

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

    def test_contract_does_not_require_rifle_or_igla(self) -> None:
        body = namespace_body(origin_main_header())
        self.assertNotIn("Rifle", body)
        self.assertNotIn("Igla", body)
        self.assertNotIn("Yak", body)
        self.assertNotEqual(LINE_TEXT_FOR_EVENT, "Rifle")
        self.assertNotEqual(LINE_TEXT_FOR_EVENT, "Igla")
        self.assertNotIn("FireIgla", body)
        self.assertNotIn("FireRifle", body)
        self.assertNotIn("YakSpawnLocation", body)
        self.assertNotIn("bYakRuntimeReady", body)
        self.assertNotIn("FSkyguardMission0NIntegrationReadiness", body)

    def test_declaration_bans_igla_yak_rifle(self) -> None:
        body = namespace_body(origin_main_header())
        lowered = body.lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"pilot LineTextForEvent contains {banned}; "
                "declaration is Apache CPG 30 mm / Hydra / Hellfire, "
                "not Yak",
            )
            self.assertNotIn(banned, LINE_TEXT_FOR_EVENT.lower())

    def test_contract_is_line_text_for_event_declaration_only(self) -> None:
        header = origin_main_header()
        body = namespace_body(header)
        self.assertIn(f"namespace {NAMESPACE_NAME}", header)
        self.assertEqual(
            require_declaration(body, LINE_TEXT_FOR_EVENT),
            LINE_TEXT_FOR_EVENT,
        )
        locked_only = f"{LINE_TEXT_FOR_EVENT}\n"
        for neighbor in UNLOCKED_NEIGHBORS:
            self.assertNotIn(neighbor, locked_only)
            self.assertNotIn(neighbor, LINE_TEXT_FOR_EVENT)
        self.assertNotIn("ConfirmLineForCommand", locked_only)
        self.assertNotIn("LineDurationForEvent", locked_only)
        self.assertNotIn("WarnOffAxis", locked_only)
        self.assertNotIn("CallLock", locked_only)
        self.assertNotIn("CallReload", locked_only)
        self.assertNotIn("ResetCallProbe", locked_only)
        self.assertNotIn("CallEvent", locked_only)
        self.assertNotIn("MakeRadioLine", locked_only)
        self.assertNotIn("ConfirmCommand", locked_only)
        self.assertNotIn("GetLastCalledLine", locked_only)
        self.assertNotIn("GetLastCalledText", locked_only)
        self.assertNotIn("GetCalledEventCount", locked_only)
        for token in LINE_STRINGS_NOT_LOCKED:
            self.assertNotIn(token, locked_only)
            self.assertNotIn(token, LINE_TEXT_FOR_EVENT)
        for token in SIBLING_TYPES:
            self.assertNotIn(token, body)
        for token in CPP_AND_INVENTED:
            self.assertNotIn(token, LINE_TEXT_FOR_EVENT)
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
        self.assertNotIn("TEXT(", body)
        self.assertNotEqual(LINE_TEXT_FOR_EVENT, "Rifle")
        self.assertNotEqual(LINE_TEXT_FOR_EVENT, "Igla")

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
