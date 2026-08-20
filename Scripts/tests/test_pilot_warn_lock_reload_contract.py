from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
VOICE_H = "SkyguardPilotVoice.h"
VOICE_CPP = "SkyguardPilotVoice.cpp"
LOCKED = {
    "SkyguardPilotVoice.cpp",
    "SkyguardPilotVoice.h",
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
    "SkyguardCampaignDefinitionTests.cpp",
    "SkyguardCampaignSubsystemTests.cpp",
    "SkyguardMissionDefinitionTests.cpp",
    "SkyguardDroneThreatKindTests.cpp",
    "SkyguardCampaignRosterLookupTests.cpp",
    "SkyguardSortiePresentationFailClosedTests.cpp",
    "SkyguardApacheChinMuzzleTests.cpp",
    "SkyguardGunshipTypesLoadoutTests.cpp",
    "SkyguardMissionDirectorPresentationHelpersTests.cpp",
    "SkyguardAudioAcceptanceHarnessFailClosedTests.cpp",
    "SkyguardObjectiveRuntimeFailClosedTests.cpp",
    "SkyguardRadioChatterEmptyLineTests.cpp",
    "SkyguardRouteRuntimeFailClosedTests.cpp",
    "SkyguardPauseHostFailClosedTests.cpp",
    "SkyguardMissionBriefingFailClosedTests.cpp",
    "SkyguardArcadeLookFailClosedTests.cpp",
    "SkyguardAudioDirectorWorldEventFailClosedTests.cpp",
}

WARN_OFF_AXIS = "Break the glass — threat off your sensor."
CALL_LOCK = "Good lock. Missile is yours."
CALL_RELOAD = "Reloading %s."
BANNED = ("igla", "yak", "rifle")


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


def between(source: str, start: str, end: str) -> str:
    begin = source.index(start)
    finish = source.index(end, begin)
    return source[begin:finish]


def warn_off_axis_body(impl: str) -> str:
    return between(
        impl,
        "void SkyguardPilotVoice::WarnOffAxis",
        "void SkyguardPilotVoice::CallLock",
    )


def call_lock_body(impl: str) -> str:
    return between(
        impl,
        "void SkyguardPilotVoice::CallLock",
        "void SkyguardPilotVoice::CallReload",
    )


def call_reload_body(impl: str) -> str:
    return between(
        impl,
        "void SkyguardPilotVoice::CallReload",
        "void SkyguardPilotVoice::CallEvent",
    )


def live_text_payloads(block: str) -> list[str]:
    return re.findall(r'TEXT\("([^"]*)"\)', block)


class PilotWarnLockReloadContractTests(unittest.TestCase):
    def test_warn_lock_reload_functions_exist_in_header(self) -> None:
        header = text(VOICE_H)
        self.assertIn("void WarnOffAxis(UObject* WorldContext);", header)
        self.assertIn("void CallLock(UObject* WorldContext);", header)
        self.assertIn(
            "void CallReload(UObject* WorldContext, const TCHAR* Station);",
            header,
        )

    def test_warn_off_axis_payload_and_duration(self) -> None:
        body = warn_off_axis_body(text(VOICE_CPP))
        self.assertIn(f'TEXT("{WARN_OFF_AXIS}")', body)
        self.assertIn("3.2f", body)
        self.assertIn(
            f'Say(WorldContext, TEXT("{WARN_OFF_AXIS}"), 3.2f)',
            body,
        )

    def test_call_lock_payload_and_duration(self) -> None:
        body = call_lock_body(text(VOICE_CPP))
        self.assertIn(f'TEXT("{CALL_LOCK}")', body)
        self.assertIn("2.4f", body)
        self.assertIn(
            f'Say(WorldContext, TEXT("{CALL_LOCK}"), 2.4f)',
            body,
        )
        self.assertIn("Missile is yours", body)

    def test_call_reload_payload_duration_and_station_ternary(self) -> None:
        body = call_reload_body(text(VOICE_CPP))
        self.assertIn(f'TEXT("{CALL_RELOAD}")', body)
        self.assertIn("2.2f", body)
        self.assertIn('Station ? Station : TEXT("guns")', body)
        self.assertIn(
            f'*FString::Printf(TEXT("{CALL_RELOAD}"), Station ? Station : TEXT("guns"))',
            body,
        )

    def test_live_warn_lock_reload_strings_ban_igla_yak_rifle(self) -> None:
        impl = text(VOICE_CPP)
        payloads = (
            live_text_payloads(warn_off_axis_body(impl))
            + live_text_payloads(call_lock_body(impl))
            + live_text_payloads(call_reload_body(impl))
        )
        self.assertIn(WARN_OFF_AXIS, payloads)
        self.assertIn(CALL_LOCK, payloads)
        self.assertIn(CALL_RELOAD, payloads)
        self.assertIn("guns", payloads)
        for payload in payloads:
            lowered = payload.lower()
            for banned in BANNED:
                self.assertNotIn(banned, lowered, payload)

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        existing.append("Scripts/tests/test_pilot_confirm_line_contract.py")
        existing.append("Scripts/tests/test_apache_cpg_feel_contract.py")
        existing.append("Scripts/tests/test_threat_kind_roster_contract.py")
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
