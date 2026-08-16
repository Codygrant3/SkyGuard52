from __future__ import annotations

import copy
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

VALIDATOR_PATH = TEST_DIR.parent / "validate_skyguard_production.py"
VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "validate_skyguard_production",
    VALIDATOR_PATH,
)
assert VALIDATOR_SPEC and VALIDATOR_SPEC.loader
VALIDATOR = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(VALIDATOR)


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
            ids[:7],
            [
                "core-apache-cockpit",
                "core-apache-cockpit-station-detail01",
                "core-apache-cockpit-station-model01",
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
        registered_workers = {
            "core-apache-cockpit": r"Scripts\Workers\worker_core_apache_cockpit.py",
            "core-apache-cockpit-station-detail01": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_detail01.py"
            ),
            "core-apache-cockpit-station-model01": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model01.py"
            ),
        }
        for asset in nxt[:7]:
            self.assertEqual(asset["lane"], "P0-apache-cpg-hero-slice")
            self.assertEqual(asset["status"], "queued")
            expected_worker = registered_workers.get(asset["id"])
            if expected_worker:
                self.assertEqual(asset["worker"]["script"], expected_worker)
            else:
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

    def test_apache_p0_cockpit_registers_real_queued_worker(self) -> None:
        worker_path = (
            PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_cockpit.py"
        )
        self.assertTrue(worker_path.is_file(), worker_path)
        source = worker_path.read_text(encoding="utf-8")
        self.assertIn("from skyguard_blender_worker_sdk import", source)
        self.assertIn("run_worker", source)
        self.assertIn("create_socket", source)
        self.assertIn("def build_asset(", source)
        self.assertNotIn("nuke()", source)
        self.assertNotIn("APACHE_CPG_COCKPIT_BLOCKOUT01", source)
        self.assertNotIn("Yak", source)
        self.assertNotIn("Igla", source)
        self.assertNotIn("rifle", source.lower())
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertIn("0.85", after_gate)

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        cockpit = by_id["core-apache-cockpit"]
        self.assertEqual(cockpit["status"], "queued")
        self.assertEqual(cockpit["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(
            cockpit["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit.py",
        )
        self.assertEqual(
            cockpit["worker"]["arguments"],
            ["--output", "{output_dir}", "--asset-id", "core-apache-cockpit"],
        )
        self.assertEqual(cockpit["worker"]["minimum_renders"], 6)
        self.assertEqual(
            cockpit["worker"]["postflight"]["script"],
            r"Scripts\adjudicate_ready_blender_asset_attempt_v2.py",
        )
        self.assertTrue(cockpit["worker"]["postflight"]["visual_review_still_required"])
        self.assertFalse(cockpit.get("existing"))
        for asset_id in VALIDATOR.APACHE_P0_IDS:
            asset = by_id[asset_id]
            self.assertEqual(asset["status"], "queued", asset_id)
            self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
            if asset_id not in {
                "core-apache-cockpit",
                "core-apache-cockpit-station-detail01",
                "core-apache-cockpit-station-model01",
            }:
                self.assertFalse(asset.get("worker"), asset_id)
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])

    def test_apache_p0_station_detail01_registers_queued_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_detail01.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_detail01_once.ps1"
        )
        self.assertTrue(worker_path.is_file(), worker_path)
        self.assertTrue(supervisor_path.is_file(), supervisor_path)
        source = worker_path.read_text(encoding="utf-8")
        supervisor = supervisor_path.read_text(encoding="utf-8")
        self.assertIn("from skyguard_blender_worker_sdk import", source)
        self.assertIn("run_station_detail_worker", source)
        self.assertNotIn("run_worker(", source)
        self.assertIn("create_socket", source)
        self.assertIn("configure_scene", source)
        self.assertIn("validate_asset", source)
        self.assertIn("render_review_views", source)
        self.assertIn("export_asset", source)
        self.assertIn("bpy.ops.render.render(write_still=True)", source)
        self.assertIn("eye_forward.png", source)
        self.assertIn("eye_down_tedac.png", source)
        self.assertNotIn("import numpy", source)
        self.assertNotIn("from numpy", source)
        self.assertNotIn("Render Result", source)
        self.assertNotIn('empty_display_type = "CROSS"', source)
        self.assertNotIn("Yak", source)
        self.assertNotIn("Igla", source)
        self.assertNotIn("rifle", source.lower())
        self.assertNotIn("Stage 7B", source)
        self.assertNotIn("APACHE_CPG_STATION_DETAIL01", source)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-detail01"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(asset["supersedes_only_after_acceptance"], "core-apache-cockpit")
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_detail01.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-detail01",
            ],
        )
        self.assertEqual(asset["worker"]["minimum_renders"], 8)
        self.assertEqual(
            asset["worker"]["postflight"]["script"],
            r"Scripts\adjudicate_ready_blender_asset_attempt_v2.py",
        )
        self.assertTrue(asset["worker"]["postflight"]["visual_review_still_required"])
        self.assertIn("core-apache-cockpit-station-detail01", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-detail01"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_detail01_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-detail01.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-detail01.glb")
        self.assertEqual(len(contract["render_groups"]), 1)
        self.assertEqual(contract["render_groups"][0]["count"], 8)
        self.assertEqual(contract["render_groups"][0]["width"], 1920)
        self.assertEqual(contract["render_groups"][0]["height"], 1080)
        self.assertEqual(
            contract["required_json"]["artifact_receipt.json"],
            "skyguard.blender-worker-receipt.v1",
        )
        self.assertEqual(contract["minimum_meshes"], 1)
        for record in contract["authorities"]:
            path = PIPELINE.ROOT / record["path"].replace("\\", "/")
            self.assertEqual(record["bytes"], path.stat().st_size, record["path"])
            self.assertEqual(record["sha256"], PIPELINE.sha256(path), record["path"])
        cockpit = by_id["core-apache-cockpit"]
        self.assertEqual(cockpit["status"], "queued")
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_station_model01_registers_queued_bmesh_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model01.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model01_once.ps1"
        )
        self.assertTrue(worker_path.is_file(), worker_path)
        self.assertTrue(supervisor_path.is_file(), supervisor_path)
        source = worker_path.read_text(encoding="utf-8")
        supervisor = supervisor_path.read_text(encoding="utf-8")
        self.assertIn("from skyguard_blender_worker_sdk import", source)
        self.assertIn("create_socket", source)
        self.assertIn("pbr_material", source)
        self.assertIn("configure_scene", source)
        self.assertIn("create_collection", source)
        self.assertIn("validate_asset", source)
        self.assertIn("render_review_views", source)
        self.assertIn("export_asset", source)
        self.assertIn("parse_worker_args", source)
        self.assertIn("WorkerError", source)
        self.assertIn("sha256", source)
        self.assertIn("now_utc", source)
        self.assertIn("SDK_VERSION", source)
        self.assertIn("run_station_model_worker", source)
        self.assertNotIn("run_worker(", source)
        self.assertTrue("import bmesh" in source or "bmesh.from_mesh" in source)
        self.assertIn("bmesh.ops", source)
        self.assertIn("bmesh.ops.extrude_face_region", source)
        self.assertIn("bmesh.ops.inset_region", source)
        self.assertIn("bmesh.ops.solidify", source)
        self.assertIn("bmesh.ops.bridge_loops", source)
        self.assertIn("bmesh.ops.spin", source)
        self.assertIn("bpy.ops.render.render(write_still=True)", source)
        self.assertIn("eye_forward.png", source)
        self.assertIn("eye_down_tedac.png", source)
        self.assertIn("(0.42, 0.55, 0.62)", source)
        self.assertNotIn("primitive_cube_add", source)
        self.assertNotIn("def add_box", source)
        self.assertNotIn("import numpy", source)
        self.assertNotIn("from numpy", source)
        self.assertNotIn("Render Result", source)
        self.assertNotIn('empty_display_type = "CROSS"', source)
        self.assertNotIn("Yak", source)
        self.assertNotIn("Igla", source)
        self.assertNotIn("rifle", source.lower())
        self.assertNotIn("Stage 7B", source)
        self.assertNotIn("APACHE_CPG_STATION_DETAIL01", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL01", source)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model01", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model01"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-detail01",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model01.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model01",
            ],
        )
        self.assertEqual(asset["worker"]["minimum_renders"], 8)
        self.assertEqual(
            asset["worker"]["postflight"]["script"],
            r"Scripts\adjudicate_ready_blender_asset_attempt_v2.py",
        )
        self.assertTrue(asset["worker"]["postflight"]["visual_review_still_required"])
        self.assertIn("blend", asset["required"])
        self.assertIn("glb", asset["required"])
        self.assertIn("6_renders", asset["required"])
        self.assertIn("cpg_eyepoint_renders", asset["required"])
        self.assertIn("uvs", asset["required"])
        self.assertIn("pbr", asset["required"])
        self.assertIn("pivots", asset["required"])
        self.assertIn("sockets", asset["required"])
        self.assertIn("full_resolution_visual_review", asset["required"])
        self.assertIn("core-apache-cockpit-station-model01", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model01"),
            ids.index("core-apache-cockpit-station-detail01") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model01"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model01_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model01.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model01.glb")
        self.assertEqual(len(contract["render_groups"]), 1)
        self.assertEqual(contract["render_groups"][0]["count"], 8)
        self.assertEqual(contract["render_groups"][0]["width"], 1920)
        self.assertEqual(contract["render_groups"][0]["height"], 1080)
        self.assertEqual(
            contract["required_json"]["artifact_receipt.json"],
            "skyguard.blender-worker-receipt.v1",
        )
        self.assertEqual(contract["minimum_meshes"], 1)
        check_paths = {item["path"]: item for item in contract["checks"]}
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model01")
        self.assertEqual(check_paths["sdk_version"]["value"], "1.0.0")
        self.assertEqual(
            check_paths["validation.required_sockets"]["op"],
            "contains_all",
        )
        self.assertEqual(
            check_paths["validation.required_sockets"]["value"],
            [
                "SOCKET_Origin",
                "SOCKET_CPG_Eye",
                "SOCKET_TEDAC",
                "SOCKET_MPD_L",
                "SOCKET_MPD_R",
                "SOCKET_Collective",
                "SOCKET_Cyclic",
            ],
        )
        self.assertEqual(
            check_paths["eyepoint_renders"]["op"],
            "contains_all",
        )
        self.assertEqual(
            check_paths["eyepoint_renders"]["value"],
            ["eye_forward.png", "eye_down_tedac.png"],
        )
        for record in contract["authorities"]:
            path = PIPELINE.ROOT / record["path"].replace("\\", "/")
            self.assertEqual(record["bytes"], path.stat().st_size, record["path"])
            self.assertEqual(record["sha256"], PIPELINE.sha256(path), record["path"])
        self.assertEqual(by_id["core-apache-cockpit"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-detail01"]["status"], "queued")
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_rejects_phantom_worker_path(self) -> None:
        manifest = copy.deepcopy(PIPELINE.load_manifest())
        cockpit = PIPELINE.asset_index(manifest)["core-apache-cockpit"]
        cockpit["worker"] = {
            "script": r"Scripts\Workers\worker_core_apache_cockpit_does_not_exist.py",
            "arguments": [],
        }
        errors = VALIDATOR.apache_p0_contract_errors(manifest)
        self.assertTrue(
            any("phantom worker" in error and "core-apache-cockpit" in error for error in errors),
            errors,
        )

    def test_apache_p0_accepts_real_worker_and_ready_status(self) -> None:
        manifest = copy.deepcopy(PIPELINE.load_manifest())
        cockpit = PIPELINE.asset_index(manifest)["core-apache-cockpit"]
        cockpit["status"] = "ready"
        cockpit["worker"] = {
            "script": r"Scripts\skyguard_production.py",
            "arguments": [],
        }
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])
        live = PIPELINE.asset_index(PIPELINE.load_manifest())["core-apache-cockpit"]
        self.assertEqual(live["status"], "queued")
        self.assertEqual(
            live["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit.py",
        )


if __name__ == "__main__":
    unittest.main()
