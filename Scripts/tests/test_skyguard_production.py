from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
CONTROLLER = TEST_DIR.parent / "skyguard_production.py"
if not CONTROLLER.is_file():
    CONTROLLER = TEST_DIR / "skyguard_production.py"
SPEC = importlib.util.spec_from_file_location("skyguard_production", CONTROLLER)
assert SPEC and SPEC.loader
PIPELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PIPELINE)


class ProductionPipelineTests(unittest.TestCase):
    def test_sha256_and_atomic_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.txt"
            source.write_text("skyguard", encoding="utf-8")
            self.assertEqual(
                PIPELINE.sha256(source),
                "b9c8934f436ed52282dc31928efd349e7f1327b1822c7094035c6c34b86bb8ea",
            )
            target = root / "receipt.json"
            PIPELINE.atomic_write_json(target, {"ok": True})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"ok": True})
            self.assertFalse(target.with_name(target.name + ".tmp").exists())

    def test_transitions_reject_skipping_review(self) -> None:
        asset = {"id": "test", "status": "ready"}
        with self.assertRaises(PIPELINE.PipelineError):
            PIPELINE.transition(asset, "accepted", "not allowed")
        PIPELINE.transition(asset, "running", "launch")
        PIPELINE.transition(asset, "awaiting_review", "complete")
        PIPELINE.transition(asset, "accepted", "reviewed")
        self.assertEqual(asset["status"], "accepted")

    def test_output_checks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "asset.blend").write_bytes(b"blend")
            (root / "asset.glb").write_bytes(b"glb")
            for index in range(3):
                (root / f"render_{index}.png").write_bytes(b"png")
            passed, errors = PIPELINE.output_checks(root, {"minimum_renders": 3})
            self.assertTrue(passed, errors)

    def test_duplicate_ids_fail_manifest(self) -> None:
        manifest = {
            "schema": "skyguard.production-manifest.v1",
            "project": {"root": str(PIPELINE.ROOT)},
            "policies": {"accepted_states": ["queued"]},
            "toolchain": {},
            "assets": [
                {"id": "same", "status": "queued", "priority": 1},
                {"id": "same", "status": "queued", "priority": 2},
            ],
        }
        errors = PIPELINE.validate_manifest(manifest, check_files=False)
        self.assertTrue(any("Duplicate asset ids" in error for error in errors))

    def test_canonical_manifest_has_active_standing_authorization(self) -> None:
        manifest = PIPELINE.load_manifest()
        errors = PIPELINE.validate_manifest(manifest)
        self.assertEqual(errors, [])
        policies = manifest["policies"]
        self.assertTrue(policies["standing_blender_unreal_authorization"])
        self.assertFalse(policies["per_run_user_authorization_required"])

    def test_manifest_rejects_return_to_per_run_authorization(self) -> None:
        manifest = PIPELINE.load_manifest()
        manifest["policies"]["per_run_user_authorization_required"] = True
        errors = PIPELINE.validate_manifest(manifest, check_files=False)
        self.assertIn(
            "Per-run Blender/Unreal user authorization must be disabled.",
            errors,
        )

    def test_visual_feedback_guard_blocks_the_rejected_strategy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            memory_path = Path(directory) / "feedback.json"
            memory_path.write_text(
                json.dumps(
                    {
                        "schema": "skyguard.visual-feedback-memory.v1",
                        "updated_at_utc": None,
                        "policy": {
                            "pivot_threshold": 2,
                            "same_source_hash_is_idempotent": True,
                            "automatic_visual_acceptance": False,
                            "cosmetic_retry_after_pivot": False,
                        },
                        "reviews": [],
                        "lanes": {
                            "m01_environment": {
                                "classification": "PIVOT_REQUIRED",
                                "required_strategy_tags": ["asset_specific"],
                                "forbidden_strategy_tags": ["lighting_only_recovery"],
                                "repeated_categories": ["architecture"],
                                "next_work_requirements": [],
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            rejected = {
                "id": "rejected",
                "feedback_guard_required": True,
                "feedback_lane": "m01_environment",
                "strategy_tags": ["lighting_only_recovery"],
            }
            errors = PIPELINE.visual_feedback_guard_errors(rejected, memory_path)
            self.assertEqual(len(errors), 1)
            self.assertIn("strategy blocked", errors[0])

            accepted = {
                "id": "accepted",
                "feedback_guard_required": True,
                "feedback_lane": "m01_environment",
                "strategy_tags": ["asset_specific"],
            }
            self.assertEqual(
                PIPELINE.visual_feedback_guard_errors(accepted, memory_path),
                [],
            )

    def test_canonical_execution_order_starts_with_apache_cpg_p0(self) -> None:
        manifest = PIPELINE.load_manifest()
        self.assertEqual(
            manifest["execution_order"][0],
            "P0-apache-cpg-hero-slice",
        )
        self.assertLess(
            manifest["execution_order"].index("P0-apache-cpg-hero-slice"),
            manifest["execution_order"].index("P0-cockpit-combat-vertical-slice"),
        )
        self.assertLess(
            manifest["execution_order"].index("P0-apache-cpg-hero-slice"),
            manifest["execution_order"].index("P0-mission01-visual-slice"),
        )

    def test_next_surfaces_apache_p0_and_skips_deferred_yak_lane(self) -> None:
        manifest = PIPELINE.load_manifest()
        nxt = PIPELINE.select_next_assets(
            manifest,
            set(PIPELINE.DEFAULT_NEXT_STATES.split(",")),
            15,
        )
        ids = [asset["id"] for asset in nxt]
        self.assertEqual(
            ids[:5],
            [
                "core-apache-cockpit",
                "core-apache-30mm",
                "core-apache-hydra",
                "core-apache-hellfire",
                "core-apache-airframe",
            ],
        )
        forbidden_prefixes = (
            "core-yak52-",
            "core-pilot",
            "core-rear",
            "core-hand-forearm",
            "core-rifle",
            "core-igla-",
            "core-shahed",
        )
        leaked = [
            asset_id
            for asset_id in ids
            if asset_id.startswith(forbidden_prefixes)
        ]
        self.assertEqual(leaked, [])
        for asset in nxt[:5]:
            self.assertEqual(asset["lane"], "P0-apache-cpg-hero-slice")
            self.assertEqual(asset["status"], "queued")
            self.assertFalse(asset.get("worker"))

    def test_archived_p0_hero_assets_are_deferred_not_deleted(self) -> None:
        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        deferred = [
            "core-yak52-airframe",
            "core-yak52-airframe-recovery01",
            "core-yak52-airframe-artist-grade-method02",
            "core-yak52-airframe-artist-grade-method02-plus",
            "core-yak52-cockpit",
            "core-pilot",
            "core-rear-gunner",
            "core-hand-forearm",
            "core-reargunner-character-refinement01",
            "core-reargunner-hand-forearm-refinement01",
            "core-rifle",
            "core-rifle-method05-stagea",
            "core-igla-launcher",
            "core-igla-missile",
            "core-shahed136",
            "core-shahed-heavy",
        ]
        note = (
            "Deferred because the live fantasy is Apache CPG (2026-08-16) "
            "and Stage 7B / Yak-Igla hero loops are archived."
        )
        for asset_id in deferred:
            asset = by_id[asset_id]
            self.assertEqual(asset["status"], "deferred", asset_id)
            self.assertIn(note, asset.get("state_reason", ""), asset_id)
            self.assertEqual(asset["lane"], "P0-cockpit-combat-vertical-slice")

    def test_accepted_and_vegetation_assets_were_not_flipped(self) -> None:
        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        accepted = [
            "support-rail-coupon",
            "m01-lighthouse",
            "m01-coastal-facade-bay-production01-recovery02",
            "m01-coastal-corridor-correction06-recovery01",
            "m01-coastal-corridor-correction06-recovery01-unrealready01",
            "m01-prewar-window-eevee-glazing-transmission-coupon-a01",
        ]
        for asset_id in accepted:
            self.assertEqual(by_id[asset_id]["status"], "accepted", asset_id)
        self.assertEqual(by_id["shared-vegetation-kit"]["status"], "blocked_reference")
        baseline = manifest["baseline"]
        self.assertEqual(baseline["production_hero_assets_accepted"], 0)
        self.assertEqual(baseline["production_campaign_maps_accepted"], 0)
        self.assertFalse(baseline["clean_machine_release_candidate"])
        self.assertTrue(manifest["policies"]["visual_review_required"])
        self.assertTrue(manifest["policies"]["unreal_import_requires_acceptance"])


if __name__ == "__main__":
    unittest.main()
