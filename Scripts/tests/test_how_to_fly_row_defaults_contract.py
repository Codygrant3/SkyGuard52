from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"
HEADER_NAME = "SkyguardSortiePresentationComponent.h"
LOCKED = {
    "SkyguardSortiePresentationComponent.h",
    "SkyguardSortiePresentationComponent.cpp",
    "SkyguardSortiePresentationTests.cpp",
    "SkyguardSortiePresentationFailClosedTests.cpp",
    "SkyguardSortiePresentationWidgets.h",
    "SkyguardSortiePresentationWidgets.cpp",
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
SIBLING_CONTRACTS = (
    "Scripts/tests/test_sortie_presentation_state_enum_contract.py",
    "Scripts/tests/test_sortie_presentation_contract.py",
    "Scripts/tests/test_briefing_card_defaults_contract.py",
    "Scripts/tests/test_briefing_radio_row_defaults_contract.py",
)
PUBLIC_FIELDS = (
    "FName StepId;",
    "FText InputHint;",
    "FText Instruction;",
    "ESkyguardBriefingPictogram Pictogram =\n"
    "\t\tESkyguardBriefingPictogram::Mission;",
)
IN_CLASS_DEFAULTS = {
    "Pictogram": "ESkyguardBriefingPictogram::Mission",
}
BANNED = ("igla", "yak", "rifle")
# Historical Rifle / Igla names stay on ESkyguardBriefingPictogram. This
# contract locks only the FSkyguardHowToFlyRow Mission default.
PICTOGRAM_ENUMERATORS_NOT_LOCKED = (
    "Route",
    "DroneSwarm",
    "ProtectedAsset",
    "Boss",
    "Rifle",
    "Igla",
    "Weather",
    "Radio",
)
# ESkyguardSortiePresentationState belongs to #173.
PRESENTATION_STATES_NOT_RELOCKED = (
    "Unconfigured",
    "SortieActive",
    "DebriefReady",
    "SaveFailure",
    "TravelReady",
    "TravelBlocked",
    "CampaignComplete",
)
# FSkyguardBriefingCard belongs to #178. A sibling may lock
# FSkyguardBriefingRadioRow in a different file.
SIBLING_STRUCTS_NOT_RELOCKED = (
    "FSkyguardBriefingCard",
    "FSkyguardBriefingRadioRow",
)


def origin_main(name: str) -> str:
    result = subprocess.run(
        ["git", "show", f"origin/main:Source/Skyguard52/{name}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def how_to_fly_row_body(header: str) -> str:
    start = header.index("struct FSkyguardHowToFlyRow")
    brace = header.index("{", start)
    finish = header.index("};", brace)
    return header[brace : finish + 2]


def in_class_defaults(body: str) -> dict[str, str]:
    return {
        name: value.strip()
        for name, value in re.findall(
            r"(?:ESkyguardBriefingPictogram)\s+(\w+)\s*=\s*([^;]+);",
            body,
        )
    }


class HowToFlyRowDefaultsContractTests(unittest.TestCase):
    def test_how_to_fly_row_struct_exists(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn("struct FSkyguardHowToFlyRow", header)
        self.assertIn("USTRUCT(BlueprintType)", header)
        self.assertIn("GENERATED_BODY()", how_to_fly_row_body(header))

    def test_public_fields_match_origin_main_in_order(self) -> None:
        body = how_to_fly_row_body(origin_main(HEADER_NAME))
        positions = [body.index(field) for field in PUBLIC_FIELDS]
        self.assertEqual(positions, sorted(positions), PUBLIC_FIELDS)
        for field in PUBLIC_FIELDS:
            self.assertIn(field, body)
        self.assertIn("StepId", body)
        self.assertIn("InputHint", body)
        self.assertIn("Instruction", body)
        self.assertIn("Pictogram", body)
        self.assertEqual(body.count("UPROPERTY("), 4)
        self.assertEqual(
            len(
                re.findall(
                    r"^\tUPROPERTY\(VisibleAnywhere, BlueprintReadOnly\)$",
                    body,
                    flags=re.MULTILINE,
                )
            ),
            3,
        )
        self.assertIn(
            'UPROPERTY(VisibleAnywhere, BlueprintReadOnly, meta=(MultiLine="true"))',
            body,
        )
        self.assertEqual(body.count('meta=(MultiLine="true")'), 1)

    def test_in_class_defaults_match_origin_main(self) -> None:
        body = how_to_fly_row_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        self.assertEqual(
            defaults.get("Pictogram"),
            "ESkyguardBriefingPictogram::Mission",
        )
        self.assertIn(
            "ESkyguardBriefingPictogram Pictogram =\n"
            "\t\tESkyguardBriefingPictogram::Mission;",
            body,
        )
        self.assertEqual(
            re.findall(r"ESkyguardBriefingPictogram::(\w+)", body),
            ["Mission"],
        )

    def test_public_get_how_to_fly_rows_returns_the_struct(self) -> None:
        header = origin_main(HEADER_NAME)
        self.assertIn(
            "TArray<FSkyguardHowToFlyRow> GetHowToFlyRows() const",
            header,
        )
        self.assertIn(
            'UFUNCTION(BlueprintPure, Category="Skyguard|Sortie Presentation")',
            header,
        )
        self.assertIn(
            "TArray<FSkyguardHowToFlyRow> HowToFlyRows;",
            header,
        )

    def test_struct_does_not_invent_index_none_or_name_none(self) -> None:
        body = how_to_fly_row_body(origin_main(HEADER_NAME))
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        self.assertNotIn("StepId =", body)
        self.assertNotIn("InputHint =", body)
        self.assertNotIn("Instruction =", body)

    def test_contract_does_not_lock_briefing_pictogram_enumerators(self) -> None:
        body = how_to_fly_row_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardBriefingPictogram", body)
        self.assertIn("ESkyguardBriefingPictogram::Mission", body)
        for name in PICTOGRAM_ENUMERATORS_NOT_LOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(f"ESkyguardBriefingPictogram::{name}", body)

    def test_contract_does_not_relock_sortie_presentation_state(self) -> None:
        body = how_to_fly_row_body(origin_main(HEADER_NAME))
        self.assertNotIn("enum class ESkyguardSortiePresentationState", body)
        self.assertNotIn("ESkyguardSortiePresentationState", body)
        for name in PRESENTATION_STATES_NOT_RELOCKED:
            self.assertNotIn(name, body)
            self.assertNotIn(
                f"ESkyguardSortiePresentationState::{name}",
                body,
            )

    def test_contract_is_how_to_fly_row_defaults_only(self) -> None:
        body = how_to_fly_row_body(origin_main(HEADER_NAME))
        defaults = in_class_defaults(body)
        self.assertEqual(defaults, IN_CLASS_DEFAULTS)
        for name in SIBLING_STRUCTS_NOT_RELOCKED:
            self.assertNotIn(f"struct {name}", body)
            self.assertNotIn(name, body)
        self.assertNotIn("ESkyguardBriefingPictogram::Radio", body)
        self.assertNotIn("GetBriefingCards", body)
        self.assertNotIn("GetRadioRows", body)
        self.assertNotIn("GetPresentationState", body)
        self.assertNotIn("CardId", body)
        self.assertNotIn("Priority", body)
        self.assertNotIn("LineId", body)
        self.assertNotIn("Speaker", body)
        self.assertNotIn("Subtitle", body)
        self.assertNotIn("40.f", body)
        self.assertNotIn("80.f", body)
        self.assertNotIn("INDEX_NONE", body)
        self.assertNotIn("NAME_None", body)
        for banned in ("Rifle", "Igla", "Yak"):
            self.assertNotIn(banned, body)
            self.assertNotIn(banned, defaults)
        self.assertNotEqual(list(defaults), ["Rifle", "Igla"])

    def test_struct_bans_igla_yak_rifle(self) -> None:
        lowered = how_to_fly_row_body(origin_main(HEADER_NAME)).lower()
        for banned in BANNED:
            self.assertNotIn(
                banned,
                lowered,
                f"FSkyguardHowToFlyRow contains {banned}",
            )

    def test_locked_files_were_not_the_edit_surface(self) -> None:
        existing = [
            f"Source/Skyguard52/{name}"
            for name in LOCKED
            if (SOURCE / name).exists()
        ]
        for sibling in (
            *SIBLING_CONTRACTS,
            "Scripts/tests/test_storm_rain_beat_kit_contract.py",
            "Scripts/tests/test_campaign_theater_kit_contract.py",
            "Scripts/tests/test_day_sortie_beat_kit_contract.py",
            "Scripts/tests/test_night_sortie_beat_kit_contract.py",
        ):
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
