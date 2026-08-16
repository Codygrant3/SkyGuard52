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
            17,
        )
        ids = [asset["id"] for asset in nxt]
        self.assertEqual(
            ids[:17],
            [
                "core-apache-cockpit",
                "core-apache-cockpit-station-detail01",
                "core-apache-cockpit-station-model01",
                "core-apache-cockpit-station-model02",
                "core-apache-cockpit-station-model03",
                "core-apache-cockpit-station-model04",
                "core-apache-cockpit-station-model05",
                "core-apache-cockpit-station-model06",
                "core-apache-cockpit-station-model07",
                "core-apache-cockpit-station-model08",
                "core-apache-cockpit-station-model09",
                "core-apache-cockpit-station-model10",
                "core-apache-cockpit-station-model11",
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
            "core-apache-cockpit-station-model02": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model02.py"
            ),
            "core-apache-cockpit-station-model03": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model03.py"
            ),
            "core-apache-cockpit-station-model04": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model04.py"
            ),
            "core-apache-cockpit-station-model05": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model05.py"
            ),
            "core-apache-cockpit-station-model06": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model06.py"
            ),
            "core-apache-cockpit-station-model07": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model07.py"
            ),
            "core-apache-cockpit-station-model08": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model08.py"
            ),
            "core-apache-cockpit-station-model09": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model09.py"
            ),
            "core-apache-cockpit-station-model10": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model10.py"
            ),
            "core-apache-cockpit-station-model11": (
                r"Scripts\Workers\worker_core_apache_cockpit_station_model11.py"
            ),
            "core-apache-30mm": r"Scripts\Workers\worker_core_apache_30mm.py",
            "core-apache-hydra": r"Scripts\Workers\worker_core_apache_hydra.py",
        }
        for asset in nxt[:17]:
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
                "core-apache-cockpit-station-model02",
                "core-apache-cockpit-station-model03",
                "core-apache-cockpit-station-model04",
                "core-apache-cockpit-station-model05",
                "core-apache-cockpit-station-model06",
                "core-apache-cockpit-station-model07",
                "core-apache-cockpit-station-model08",
                "core-apache-cockpit-station-model09",
                "core-apache-cockpit-station-model10",
                "core-apache-cockpit-station-model11",
                "core-apache-30mm",
                "core-apache-hydra",
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

    def test_apache_p0_station_model02_registers_queued_clear_greenhouse_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model02.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model02_once.ps1"
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
        self.assertIn("0.2 <= world.x <= 0.85", source)
        self.assertIn("abs(world.y) < 0.20", source)
        self.assertIn("1.05 <= world.z <= 1.35", source)
        self.assertIn("add_explicit_hood", source)
        self.assertIn("hood verts are missing", source)
        greenhouse = source.split("def build_greenhouse", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("GEO_BowFrame", greenhouse)
        self.assertNotIn("GEO_BowFrame", source)
        self.assertIn("GEO_Rail_L", greenhouse)
        self.assertIn("GEO_Rail_R", greenhouse)
        self.assertIn("GEO_Sill_L", greenhouse)
        self.assertIn("GEO_Sill_R", greenhouse)
        self.assertIn("GEO_AftFrame", greenhouse)
        self.assertIn("0.38", greenhouse)
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
        self.assertNotIn("APACHE_CPG_STATION_MODEL02", source)
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model02", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model02"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-model01",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model02.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model02",
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
        self.assertIn("core-apache-cockpit-station-model02", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model02"),
            ids.index("core-apache-cockpit-station-model01") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model02"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model02_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model02.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model02.glb")
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
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model02")
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
        self.assertEqual(by_id["core-apache-cockpit-station-model01"]["status"], "queued")
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_station_model03_registers_queued_formed_station_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model03.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model03_once.ps1"
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
        self.assertIn("0.2 <= world.x <= 0.85", source)
        self.assertIn("abs(world.y) < 0.20", source)
        self.assertIn("1.05 <= world.z <= 1.35", source)
        self.assertIn("add_explicit_hood", source)
        self.assertIn("hood verts are missing", source)
        self.assertIn("GEO_SeatBack", source)
        self.assertIn("GEO_SeatHeadrest", source)
        self.assertIn("GEO_APillar_L", source)
        self.assertIn("GEO_APillar_R", source)
        self.assertIn("GEO_KneePanel_L", source)
        self.assertIn("GEO_KneePanel_R", source)
        greenhouse = source.split("def build_greenhouse", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("GEO_BowFrame", greenhouse)
        self.assertNotIn("GEO_BowFrame", source)
        self.assertIn("GEO_Rail_L", greenhouse)
        self.assertIn("GEO_Rail_R", greenhouse)
        self.assertIn("GEO_Sill_L", greenhouse)
        self.assertIn("GEO_Sill_R", greenhouse)
        self.assertIn("GEO_AftFrame", greenhouse)
        self.assertIn("0.38", greenhouse)
        self.assertNotIn("primitive_cylinder_add", source)
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
        self.assertNotIn("APACHE_CPG_STATION_MODEL02", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL03", source)
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model03", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model03"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertIsNone(asset.get("blocker"))
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-model02",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model03.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model03",
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
        self.assertIn("core-apache-cockpit-station-model03", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])
        self.assertEqual(
            asset["state_reason"],
            (
                "Queued Apache CPG P0 station-model03 method; formed seat/canopy/knobs; "
                "worker and contract registered; not launched; not ready; does not "
                "supersede model02 until accepted; visual review still required; "
                "Unreal import forbidden until accepted."
            ),
        )

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model03"),
            ids.index("core-apache-cockpit-station-model02") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model03"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model03_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model03.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model03.glb")
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
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model03")
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
        self.assertEqual(by_id["core-apache-cockpit-station-model01"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model02"]["status"], "queued")
        self.assertEqual(by_id["core-apache-30mm"]["status"], "queued")
        self.assertEqual(by_id["core-apache-hydra"]["status"], "queued")
        self.assertEqual(
            by_id["core-apache-30mm"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_30mm.py",
        )
        self.assertEqual(
            by_id["core-apache-hydra"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_hydra.py",
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_30mm.py").is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_hydra.py").is_file()
        )
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_station_model04_registers_queued_readable_station_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model04.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model04_once.ps1"
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
        self.assertIn("SOCKET_CPG_Eye", source)
        self.assertIn("(0.42, 0.55, 0.62)", source)
        self.assertIn("0.2 <= world.x <= 0.85", source)
        self.assertIn("abs(world.y) < 0.20", source)
        self.assertIn("1.05 <= world.z <= 1.35", source)
        self.assertIn("add_explicit_hood", source)
        self.assertIn("hood verts are missing", source)
        self.assertIn("GEO_SeatBack", source)
        self.assertIn("GEO_SeatHeadrest", source)
        self.assertIn("GEO_APillar_L", source)
        self.assertIn("GEO_APillar_R", source)
        self.assertIn("GEO_KneePanel_L", source)
        self.assertIn("GEO_KneePanel_R", source)
        self.assertIn("abs(world.y) < 0.16", source)
        self.assertIn("z <= 0.86", source)
        self.assertIn("GEO_TEDAC has no emit faces", source)
        greenhouse = source.split("def build_greenhouse", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("GEO_BowFrame", greenhouse)
        self.assertNotIn("GEO_BowFrame", source)
        self.assertIn("GEO_Rail_L", greenhouse)
        self.assertIn("GEO_Rail_R", greenhouse)
        self.assertIn("GEO_Sill_L", greenhouse)
        self.assertIn("GEO_Sill_R", greenhouse)
        self.assertIn("GEO_AftFrame", greenhouse)
        self.assertIn("0.38", greenhouse)
        self.assertNotIn("primitive_cylinder_add", source)
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
        self.assertNotIn("APACHE_CPG_STATION_MODEL02", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL03", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL04", source)
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model04", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model04"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertIsNone(asset.get("blocker"))
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-model03",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model04.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model04",
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
        self.assertIn("core-apache-cockpit-station-model04", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])
        self.assertEqual(
            asset["state_reason"],
            (
                "Queued Apache CPG P0 station-model04 method; restore TEDAC/MPD "
                "readability from the eye; keep formed seat; worker registered; "
                "not launched; not ready; does not supersede model03 until accepted; "
                "visual review still required; Unreal import forbidden until accepted."
            ),
        )

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model04"),
            ids.index("core-apache-cockpit-station-model03") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model04"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model04_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model04.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model04.glb")
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
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model04")
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
        self.assertEqual(by_id["core-apache-cockpit-station-model01"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model02"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model03"]["status"], "queued")
        self.assertEqual(by_id["core-apache-30mm"]["status"], "queued")
        self.assertEqual(by_id["core-apache-hydra"]["status"], "queued")
        self.assertEqual(
            by_id["core-apache-cockpit-station-model03"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model03.py",
        )
        self.assertEqual(
            by_id["core-apache-30mm"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_30mm.py",
        )
        self.assertEqual(
            by_id["core-apache-hydra"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_hydra.py",
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model03.py"
            ).is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_30mm.py").is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_hydra.py").is_file()
        )
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_station_model05_registers_queued_formed_canopy_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model05.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model05_once.ps1"
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
        self.assertIn("SOCKET_CPG_Eye", source)
        self.assertIn("(0.42, 0.55, 0.62)", source)
        self.assertIn("0.2 <= world.x <= 0.85", source)
        self.assertIn("abs(world.y) < 0.20", source)
        self.assertIn("1.05 <= world.z <= 1.35", source)
        self.assertIn("add_explicit_hood", source)
        self.assertIn("hood verts are missing", source)
        self.assertIn("GEO_SeatBack", source)
        self.assertIn("GEO_SeatHeadrest", source)
        self.assertIn("GEO_APillar_L", source)
        self.assertIn("GEO_APillar_R", source)
        self.assertIn("GEO_KneePanel_L", source)
        self.assertIn("GEO_KneePanel_R", source)
        self.assertIn("abs(world.y) < 0.16", source)
        self.assertIn("z <= 0.86", source)
        self.assertIn("GEO_TEDAC has no emit faces", source)
        self.assertIn("def assert_tedac_readable_from_eye", source)
        self.assertIn("thumb_face = bm.faces.new(thumb)", source)
        greenhouse = source.split("def build_greenhouse", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("GEO_BowFrame", greenhouse)
        self.assertNotIn("GEO_BowFrame", source)
        self.assertIn("GEO_Rail_L", greenhouse)
        self.assertIn("GEO_Rail_R", greenhouse)
        self.assertIn("GEO_Sill_L", greenhouse)
        self.assertIn("GEO_Sill_R", greenhouse)
        self.assertIn("GEO_AftFrame", greenhouse)
        self.assertIn("0.38", greenhouse)
        self.assertIn("section_along", greenhouse)
        self.assertNotIn("pipe_along", greenhouse)
        self.assertIn("GEO_CanopyGlass", greenhouse)
        self.assertIn("def section_along", source)
        self.assertIn("formed rectangular", source.lower())
        seat_fn = source.split("def build_seat", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("GEO_Seat", seat_fn)
        self.assertIn("GEO_SeatBolster_L", seat_fn)
        self.assertIn("GEO_SeatHeadrest", seat_fn)
        self.assertNotIn("primitive_cylinder_add", source)
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
        self.assertNotIn("APACHE_CPG_STATION_MODEL02", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL03", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL04", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL05", source)
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model05", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model05"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertIsNone(asset.get("blocker"))
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-model04",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model05.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model05",
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
        self.assertIn("core-apache-cockpit-station-model05", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])
        self.assertEqual(
            asset["state_reason"],
            (
                "Queued Apache CPG P0 station-model05 method; formed greenhouse "
                "canopy frame instead of pipe kit; keep TEDAC/MPD readability; "
                "deeper bucket seat; worker registered; not launched; not ready; "
                "does not supersede model04 until accepted; visual review still "
                "required; Unreal import forbidden until accepted."
            ),
        )

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model05"),
            ids.index("core-apache-cockpit-station-model04") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model05"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model05_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model05.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model05.glb")
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
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model05")
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
        self.assertEqual(by_id["core-apache-cockpit-station-model01"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model02"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model03"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model04"]["status"], "queued")
        self.assertEqual(by_id["core-apache-30mm"]["status"], "queued")
        self.assertEqual(by_id["core-apache-hydra"]["status"], "queued")
        self.assertEqual(
            by_id["core-apache-cockpit-station-model04"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model04.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model02"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model02.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model03"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model03.py",
        )
        self.assertEqual(
            by_id["core-apache-30mm"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_30mm.py",
        )
        self.assertEqual(
            by_id["core-apache-hydra"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_hydra.py",
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model04.py"
            ).is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_30mm.py").is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_hydra.py").is_file()
        )
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_station_model06_registers_queued_canopy_skin_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model06.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model06_once.ps1"
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
        self.assertIn("SOCKET_CPG_Eye", source)
        self.assertIn("(0.42, 0.55, 0.62)", source)
        self.assertIn("0.2 <= world.x <= 0.85", source)
        self.assertIn("abs(world.y) < 0.20", source)
        self.assertIn("1.05 <= world.z <= 1.35", source)
        self.assertIn("add_explicit_hood", source)
        self.assertIn("hood verts are missing", source)
        self.assertIn("GEO_SeatBack", source)
        self.assertIn("GEO_SeatHeadrest", source)
        self.assertIn("GEO_APillar_L", source)
        self.assertIn("GEO_APillar_R", source)
        self.assertIn("GEO_KneePanel_L", source)
        self.assertIn("GEO_KneePanel_R", source)
        self.assertIn("abs(world.y) < 0.16", source)
        self.assertIn("z <= 0.86", source)
        self.assertIn("GEO_TEDAC has no emit faces", source)
        self.assertIn("def assert_tedac_readable_from_eye", source)
        self.assertIn("thumb_face = bm.faces.new(thumb)", source)
        self.assertIn("(0.545, 0.0, 0.748)", source)
        greenhouse = source.split("def build_greenhouse", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("GEO_BowFrame", greenhouse)
        self.assertNotIn("GEO_BowFrame", source)
        self.assertIn("GEO_Rail_L", greenhouse)
        self.assertIn("GEO_Rail_R", greenhouse)
        self.assertIn("GEO_Sill_L", greenhouse)
        self.assertIn("GEO_Sill_R", greenhouse)
        self.assertIn("GEO_AftFrame", greenhouse)
        self.assertIn("0.38", greenhouse)
        self.assertIn("section_along", greenhouse)
        self.assertNotIn("pipe_along", greenhouse)
        self.assertIn("GEO_CanopyGlass", greenhouse)
        self.assertIn("def section_along", source)
        self.assertIn("formed rectangular", source.lower())
        self.assertIn("def loft_canopy_skin", source)
        self.assertIn("canopy skin", source.lower())
        self.assertIn("enclosure", source.lower())
        skin_fn = source.split("def loft_canopy_skin", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", skin_fn)
        self.assertNotIn("pipe_along", skin_fn)
        self.assertIn("faces.new", skin_fn)
        self.assertIn("solidify", skin_fn)
        self.assertIn("-0.20", skin_fn)
        self.assertIn("0.70", skin_fn)
        self.assertIn("0.20", skin_fn)
        self.assertNotIn("thicker tube", source.lower())
        seat_fn = source.split("def build_seat", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("GEO_Seat", seat_fn)
        self.assertIn("GEO_SeatBolster_L", seat_fn)
        self.assertIn("GEO_SeatHeadrest", seat_fn)
        self.assertIn("dish", seat_fn)
        self.assertIn("bucket", seat_fn.lower())
        self.assertNotIn("primitive_cylinder_add", source)
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
        self.assertNotIn("APACHE_CPG_STATION_MODEL02", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL03", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL04", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL05", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL06", source)
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model06", supervisor)
        self.assertNotIn("core-apache-cockpit-station-model05", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model06"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertIsNone(asset.get("blocker"))
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-model05",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model06.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model06",
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
        self.assertIn("core-apache-cockpit-station-model06", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(
            list(VALIDATOR.APACHE_P0_IDS),
            [
                "core-apache-cockpit",
                "core-apache-cockpit-station-detail01",
                "core-apache-cockpit-station-model01",
                "core-apache-cockpit-station-model02",
                "core-apache-cockpit-station-model03",
                "core-apache-cockpit-station-model04",
                "core-apache-cockpit-station-model05",
                "core-apache-cockpit-station-model06",
                "core-apache-cockpit-station-model07",
                "core-apache-cockpit-station-model08",
                "core-apache-cockpit-station-model09",
                "core-apache-cockpit-station-model10",
                "core-apache-cockpit-station-model11",
                "core-apache-30mm",
                "core-apache-hydra",
                "core-apache-hellfire",
                "core-apache-airframe",
            ],
        )
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])
        self.assertEqual(
            asset["state_reason"],
            (
                "Queued Apache CPG P0 station-model06 method; filled canopy skin "
                "between sill and rail so the greenhouse reads as an enclosure; "
                "keep TEDAC/MPD readability; bucket seat; worker registered; "
                "not launched; not ready; does not supersede model05 until "
                "accepted; visual review still required; Unreal import forbidden "
                "until accepted."
            ),
        )

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model06"),
            ids.index("core-apache-cockpit-station-model05") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model06"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model06_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model06.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model06.glb")
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
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model06")
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
        self.assertEqual(by_id["core-apache-cockpit-station-model01"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model02"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model03"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model04"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model05"]["status"], "queued")
        self.assertEqual(by_id["core-apache-30mm"]["status"], "queued")
        self.assertEqual(by_id["core-apache-hydra"]["status"], "queued")
        self.assertEqual(
            by_id["core-apache-cockpit-station-model05"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model05.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model04"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model04.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model02"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model02.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model03"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model03.py",
        )
        self.assertEqual(
            by_id["core-apache-30mm"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_30mm.py",
        )
        self.assertEqual(
            by_id["core-apache-hydra"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_hydra.py",
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model05.py"
            ).is_file()
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model04.py"
            ).is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_30mm.py").is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_hydra.py").is_file()
        )
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_station_model07_registers_queued_overhead_brow_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model07.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model07_once.ps1"
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
        self.assertIn("SOCKET_CPG_Eye", source)
        self.assertIn("(0.42, 0.55, 0.62)", source)
        self.assertIn("0.2 <= world.x <= 0.85", source)
        self.assertIn("abs(world.y) < 0.20", source)
        self.assertIn("1.05 <= world.z <= 1.35", source)
        self.assertIn("add_explicit_hood", source)
        self.assertIn("hood verts are missing", source)
        self.assertIn("GEO_SeatBack", source)
        self.assertIn("GEO_SeatHeadrest", source)
        self.assertIn("GEO_APillar_L", source)
        self.assertIn("GEO_APillar_R", source)
        self.assertIn("GEO_KneePanel_L", source)
        self.assertIn("GEO_KneePanel_R", source)
        self.assertIn("abs(world.y) < 0.16", source)
        self.assertIn("z <= 0.86", source)
        self.assertIn("GEO_TEDAC has no emit faces", source)
        self.assertIn("def assert_tedac_readable_from_eye", source)
        self.assertIn("thumb_face = bm.faces.new(thumb)", source)
        self.assertIn("(0.545, 0.0, 0.748)", source)
        greenhouse = source.split("def build_greenhouse", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("GEO_BowFrame", greenhouse)
        self.assertNotIn("GEO_BowFrame", source)
        self.assertIn("GEO_Rail_L", greenhouse)
        self.assertIn("GEO_Rail_R", greenhouse)
        self.assertIn("GEO_Sill_L", greenhouse)
        self.assertIn("GEO_Sill_R", greenhouse)
        self.assertIn("GEO_AftFrame", greenhouse)
        self.assertIn("0.38", greenhouse)
        self.assertIn("section_along", greenhouse)
        self.assertNotIn("pipe_along", greenhouse)
        self.assertIn("GEO_CanopyGlass", greenhouse)
        self.assertIn("def section_along", source)
        self.assertIn("formed rectangular", source.lower())
        self.assertIn("def loft_canopy_skin", source)
        self.assertIn("canopy skin", source.lower())
        self.assertIn("enclosure", source.lower())
        skin_fn = source.split("def loft_canopy_skin", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", skin_fn)
        self.assertNotIn("pipe_along", skin_fn)
        self.assertIn("faces.new", skin_fn)
        self.assertIn("solidify", skin_fn)
        self.assertIn("-0.20", skin_fn)
        self.assertIn("0.70", skin_fn)
        self.assertIn("0.20", skin_fn)
        self.assertNotIn("thicker tube", source.lower())
        self.assertIn("def loft_overhead_brow", source)
        self.assertIn("GEO_OverheadBrow", source)
        self.assertIn("GEO_ForwardBrow", source)
        self.assertIn("1.36", source)
        overhead_fn = source.split("def loft_overhead_brow", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", overhead_fn)
        self.assertNotIn("pipe_along", overhead_fn)
        self.assertIn("faces.new", overhead_fn)
        self.assertIn("solidify", overhead_fn)
        self.assertIn("GEO_OverheadBrow", overhead_fn)
        self.assertIn("GEO_ForwardBrow", overhead_fn)
        self.assertIn("-0.15", overhead_fn)
        self.assertIn("0.55", overhead_fn)
        self.assertIn("1.36", overhead_fn)
        self.assertIn("loft_overhead_brow", greenhouse)
        seat_fn = source.split("def build_seat", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("GEO_Seat", seat_fn)
        self.assertIn("GEO_SeatBolster_L", seat_fn)
        self.assertIn("GEO_SeatHeadrest", seat_fn)
        self.assertIn("dish", seat_fn)
        self.assertIn("bucket", seat_fn.lower())
        self.assertIn("0.168", seat_fn)
        self.assertIn("(0.032, 0.026, 0.020, 1.0)", source)
        self.assertIn("(0.18, 0.20, 0.12, 1.0)", source)
        self.assertNotIn("primitive_cylinder_add", source)
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
        self.assertNotIn("APACHE_CPG_STATION_MODEL02", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL03", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL04", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL05", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL06", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL07", source)
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model07", supervisor)
        self.assertNotIn("core-apache-cockpit-station-model06", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model07"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertIsNone(asset.get("blocker"))
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-model06",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model07.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model07",
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
        self.assertIn("core-apache-cockpit-station-model07", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(
            list(VALIDATOR.APACHE_P0_IDS),
            [
                "core-apache-cockpit",
                "core-apache-cockpit-station-detail01",
                "core-apache-cockpit-station-model01",
                "core-apache-cockpit-station-model02",
                "core-apache-cockpit-station-model03",
                "core-apache-cockpit-station-model04",
                "core-apache-cockpit-station-model05",
                "core-apache-cockpit-station-model06",
                "core-apache-cockpit-station-model07",
                "core-apache-cockpit-station-model08",
                "core-apache-cockpit-station-model09",
                "core-apache-cockpit-station-model10",
                "core-apache-cockpit-station-model11",
                "core-apache-30mm",
                "core-apache-hydra",
                "core-apache-hellfire",
                "core-apache-airframe",
            ],
        )
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])
        self.assertEqual(
            asset["state_reason"],
            (
                "Queued Apache CPG P0 station-model07 method; lofted overhead "
                "brow connecting left and right rails above the look-out; keep "
                "TEDAC/MPD readability and side canopy skins; darker bucket "
                "seat; worker registered; not launched; not ready; does not "
                "supersede model06 until accepted; visual review still "
                "required; Unreal import forbidden until accepted."
            ),
        )

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model07"),
            ids.index("core-apache-cockpit-station-model06") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model07"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model07_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model07.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model07.glb")
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
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model07")
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
        self.assertEqual(by_id["core-apache-cockpit-station-model01"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model02"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model03"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model04"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model05"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model06"]["status"], "queued")
        self.assertEqual(by_id["core-apache-30mm"]["status"], "queued")
        self.assertEqual(by_id["core-apache-hydra"]["status"], "queued")
        self.assertEqual(
            by_id["core-apache-cockpit-station-model06"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model06.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model05"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model05.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model04"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model04.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model02"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model02.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model03"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model03.py",
        )
        self.assertEqual(
            by_id["core-apache-30mm"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_30mm.py",
        )
        self.assertEqual(
            by_id["core-apache-hydra"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_hydra.py",
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model06.py"
            ).is_file()
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model05.py"
            ).is_file()
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model04.py"
            ).is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_30mm.py").is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_hydra.py").is_file()
        )
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_station_model08_registers_queued_glass_brow_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model08.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model08_once.ps1"
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
        self.assertIn("SOCKET_CPG_Eye", source)
        self.assertIn("(0.42, 0.55, 0.62)", source)
        self.assertIn("0.2 <= world.x <= 0.85", source)
        self.assertIn("abs(world.y) < 0.20", source)
        self.assertIn("1.05 <= world.z <= 1.35", source)
        self.assertIn("add_explicit_hood", source)
        self.assertIn("hood verts are missing", source)
        self.assertIn("GEO_SeatBack", source)
        self.assertIn("GEO_SeatHeadrest", source)
        self.assertIn("GEO_APillar_L", source)
        self.assertIn("GEO_APillar_R", source)
        self.assertIn("GEO_KneePanel_L", source)
        self.assertIn("GEO_KneePanel_R", source)
        self.assertIn("abs(world.y) < 0.16", source)
        self.assertIn("z <= 0.86", source)
        self.assertIn("GEO_TEDAC has no emit faces", source)
        self.assertIn("def assert_tedac_readable_from_eye", source)
        self.assertIn("thumb_face = bm.faces.new(thumb)", source)
        self.assertIn("(0.545, 0.0, 0.748)", source)
        greenhouse = source.split("def build_greenhouse", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("GEO_BowFrame", greenhouse)
        self.assertNotIn("GEO_BowFrame", source)
        self.assertIn("GEO_Rail_L", greenhouse)
        self.assertIn("GEO_Rail_R", greenhouse)
        self.assertIn("GEO_Sill_L", greenhouse)
        self.assertIn("GEO_Sill_R", greenhouse)
        self.assertIn("GEO_AftFrame", greenhouse)
        self.assertIn("0.38", greenhouse)
        self.assertIn("section_along", greenhouse)
        self.assertNotIn("pipe_along", greenhouse)
        self.assertIn("GEO_CanopyGlass", greenhouse)
        self.assertIn("def section_along", source)
        self.assertIn("formed rectangular", source.lower())
        self.assertIn("def loft_canopy_skin", source)
        self.assertIn("canopy skin", source.lower())
        self.assertIn("enclosure", source.lower())
        skin_fn = source.split("def loft_canopy_skin", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", skin_fn)
        self.assertNotIn("pipe_along", skin_fn)
        self.assertIn("faces.new", skin_fn)
        self.assertIn("solidify", skin_fn)
        self.assertIn("-0.20", skin_fn)
        self.assertIn("0.70", skin_fn)
        self.assertIn("0.20", skin_fn)
        self.assertNotIn("thicker tube", source.lower())
        self.assertIn("def loft_overhead_brow", source)
        self.assertIn("GEO_OverheadBrow", source)
        self.assertIn("GEO_ForwardBrow", source)
        self.assertIn("1.36", source)
        overhead_fn = source.split("def loft_overhead_brow", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", overhead_fn)
        self.assertNotIn("pipe_along", overhead_fn)
        self.assertIn("faces.new", overhead_fn)
        self.assertIn("solidify", overhead_fn)
        self.assertIn("GEO_OverheadBrow", overhead_fn)
        self.assertIn("GEO_ForwardBrow", overhead_fn)
        self.assertIn("-0.15", overhead_fn)
        self.assertIn("0.55", overhead_fn)
        self.assertIn("1.36", overhead_fn)
        self.assertIn("glass", overhead_fn.lower())
        self.assertIn("loft_overhead_brow", greenhouse)
        self.assertIn("loft_overhead_brow(collection, glass)", greenhouse)
        self.assertNotIn("loft_overhead_brow(collection, rail)", greenhouse)
        self.assertIn("MAT_CPG_CanopyGlass", source)
        seat_fn = source.split("def build_seat", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("GEO_Seat", seat_fn)
        self.assertIn("GEO_SeatBolster_L", seat_fn)
        self.assertIn("GEO_SeatHeadrest", seat_fn)
        self.assertIn("dish", seat_fn)
        self.assertIn("bucket", seat_fn.lower())
        self.assertIn("0.228", seat_fn)
        self.assertIn("1.055", seat_fn)
        self.assertIn("1.018", seat_fn)
        self.assertIn("(0.032, 0.026, 0.020, 1.0)", source)
        self.assertIn("(0.014, 0.011, 0.009, 1.0)", source)
        self.assertIn("(0.18, 0.20, 0.12, 1.0)", source)
        self.assertIn("MAT_CPG_SeatWell", source)
        self.assertNotIn("primitive_cylinder_add", source)
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
        self.assertNotIn("APACHE_CPG_STATION_MODEL02", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL03", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL04", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL05", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL06", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL07", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL08", source)
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model08", supervisor)
        self.assertNotIn("core-apache-cockpit-station-model07", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model08"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertIsNone(asset.get("blocker"))
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-model07",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model08.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model08",
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
        self.assertIn("core-apache-cockpit-station-model08", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(
            list(VALIDATOR.APACHE_P0_IDS),
            [
                "core-apache-cockpit",
                "core-apache-cockpit-station-detail01",
                "core-apache-cockpit-station-model01",
                "core-apache-cockpit-station-model02",
                "core-apache-cockpit-station-model03",
                "core-apache-cockpit-station-model04",
                "core-apache-cockpit-station-model05",
                "core-apache-cockpit-station-model06",
                "core-apache-cockpit-station-model07",
                "core-apache-cockpit-station-model08",
                "core-apache-cockpit-station-model09",
                "core-apache-cockpit-station-model10",
                "core-apache-cockpit-station-model11",
                "core-apache-30mm",
                "core-apache-hydra",
                "core-apache-hellfire",
                "core-apache-airframe",
            ],
        )
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])
        self.assertEqual(
            asset["state_reason"],
            (
                "Queued Apache CPG P0 station-model08 method; glass overhead "
                "brow so eye_forward is an open look-out; keep TEDAC/MPD "
                "readability and side canopy skins; deeper bucket seat; "
                "worker registered; not launched; not ready; does not "
                "supersede model07 until accepted; visual review still "
                "required; Unreal import forbidden until accepted."
            ),
        )

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model08"),
            ids.index("core-apache-cockpit-station-model07") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model08"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model08_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model08.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model08.glb")
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
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model08")
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
        self.assertEqual(by_id["core-apache-cockpit-station-model01"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model02"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model03"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model04"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model05"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model06"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model07"]["status"], "queued")
        self.assertEqual(by_id["core-apache-30mm"]["status"], "queued")
        self.assertEqual(by_id["core-apache-hydra"]["status"], "queued")
        self.assertEqual(
            by_id["core-apache-cockpit-station-model07"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model07.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model06"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model06.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model05"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model05.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model04"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model04.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model02"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model02.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model03"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model03.py",
        )
        self.assertEqual(
            by_id["core-apache-30mm"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_30mm.py",
        )
        self.assertEqual(
            by_id["core-apache-hydra"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_hydra.py",
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model07.py"
            ).is_file()
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model06.py"
            ).is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_30mm.py").is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_hydra.py").is_file()
        )
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_station_model09_registers_queued_bucket_seat_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model09.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model09_once.ps1"
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
        self.assertIn("SOCKET_CPG_Eye", source)
        self.assertIn("(0.42, 0.55, 0.62)", source)
        self.assertIn("0.2 <= world.x <= 0.85", source)
        self.assertIn("abs(world.y) < 0.20", source)
        self.assertIn("1.05 <= world.z <= 1.35", source)
        self.assertIn("add_explicit_hood", source)
        self.assertIn("hood verts are missing", source)
        self.assertIn("GEO_SeatBack", source)
        self.assertIn("GEO_SeatHeadrest", source)
        self.assertIn("GEO_APillar_L", source)
        self.assertIn("GEO_APillar_R", source)
        self.assertIn("GEO_KneePanel_L", source)
        self.assertIn("GEO_KneePanel_R", source)
        self.assertIn("abs(world.y) < 0.16", source)
        self.assertIn("z <= 0.86", source)
        self.assertIn("GEO_TEDAC has no emit faces", source)
        self.assertIn("def assert_tedac_readable_from_eye", source)
        self.assertIn("thumb_face = bm.faces.new(thumb)", source)
        self.assertIn("(0.545, 0.0, 0.748)", source)
        greenhouse = source.split("def build_greenhouse", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("GEO_BowFrame", greenhouse)
        self.assertNotIn("GEO_BowFrame", source)
        self.assertIn("GEO_Rail_L", greenhouse)
        self.assertIn("GEO_Rail_R", greenhouse)
        self.assertIn("GEO_Sill_L", greenhouse)
        self.assertIn("GEO_Sill_R", greenhouse)
        self.assertIn("GEO_AftFrame", greenhouse)
        self.assertIn("0.38", greenhouse)
        self.assertIn("section_along", greenhouse)
        self.assertNotIn("pipe_along", greenhouse)
        self.assertIn("GEO_CanopyGlass", greenhouse)
        self.assertIn("def section_along", source)
        self.assertIn("formed rectangular", source.lower())
        self.assertIn("def loft_canopy_skin", source)
        self.assertIn("canopy skin", source.lower())
        self.assertIn("enclosure", source.lower())
        skin_fn = source.split("def loft_canopy_skin", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", skin_fn)
        self.assertNotIn("pipe_along", skin_fn)
        self.assertIn("faces.new", skin_fn)
        self.assertIn("solidify", skin_fn)
        self.assertIn("-0.20", skin_fn)
        self.assertIn("0.70", skin_fn)
        self.assertIn("0.20", skin_fn)
        self.assertNotIn("thicker tube", source.lower())
        self.assertIn("def loft_overhead_brow", source)
        self.assertIn("GEO_OverheadBrow", source)
        self.assertIn("GEO_ForwardBrow", source)
        self.assertIn("1.36", source)
        overhead_fn = source.split("def loft_overhead_brow", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", overhead_fn)
        self.assertNotIn("pipe_along", overhead_fn)
        self.assertIn("faces.new", overhead_fn)
        self.assertIn("solidify", overhead_fn)
        self.assertIn("GEO_OverheadBrow", overhead_fn)
        self.assertIn("GEO_ForwardBrow", overhead_fn)
        self.assertIn("-0.15", overhead_fn)
        self.assertIn("0.55", overhead_fn)
        self.assertIn("1.36", overhead_fn)
        self.assertIn("glass", overhead_fn.lower())
        self.assertIn("loft_overhead_brow", greenhouse)
        self.assertIn("loft_overhead_brow(collection, glass)", greenhouse)
        self.assertNotIn("loft_overhead_brow(collection, rail)", greenhouse)
        self.assertIn("MAT_CPG_CanopyGlass", source)
        seat_fn = source.split("def build_seat", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("GEO_Seat", seat_fn)
        self.assertIn("GEO_SeatBolster_L", seat_fn)
        self.assertIn("GEO_SeatBolster_R", seat_fn)
        self.assertIn("GEO_SeatBack", seat_fn)
        self.assertIn("GEO_SeatHeadrest", seat_fn)
        self.assertIn("dish", seat_fn)
        self.assertIn("bucket", seat_fn.lower())
        self.assertIn("cheeks", seat_fn.lower())
        self.assertIn("cupped", seat_fn.lower())
        self.assertIn("pan well", seat_fn.lower())
        self.assertIn("0.318", seat_fn)
        self.assertIn("1.168", seat_fn)
        self.assertIn("1.128", seat_fn)
        self.assertIn("0.056", seat_fn)
        self.assertIn("0.612", seat_fn)
        self.assertNotIn("0.228", seat_fn)
        self.assertNotIn("1.055", seat_fn)
        self.assertNotIn("1.018", seat_fn)
        self.assertNotIn("(-0.205, -0.175, 0.620)", seat_fn)
        self.assertNotIn("(-0.248, 0.155, 1.015)", seat_fn)
        self.assertIn("(0.032, 0.026, 0.020, 1.0)", source)
        self.assertIn("(0.014, 0.011, 0.009, 1.0)", source)
        self.assertIn("(0.18, 0.20, 0.12, 1.0)", source)
        self.assertIn("MAT_CPG_SeatWell", source)
        self.assertNotIn("primitive_cylinder_add", source)
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
        self.assertNotIn("APACHE_CPG_STATION_MODEL02", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL03", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL04", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL05", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL06", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL07", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL08", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL09", source)
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model09", supervisor)
        self.assertNotIn("core-apache-cockpit-station-model08", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model09"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertIsNone(asset.get("blocker"))
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-model08",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model09.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model09",
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
        self.assertIn("core-apache-cockpit-station-model09", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(
            list(VALIDATOR.APACHE_P0_IDS),
            [
                "core-apache-cockpit",
                "core-apache-cockpit-station-detail01",
                "core-apache-cockpit-station-model01",
                "core-apache-cockpit-station-model02",
                "core-apache-cockpit-station-model03",
                "core-apache-cockpit-station-model04",
                "core-apache-cockpit-station-model05",
                "core-apache-cockpit-station-model06",
                "core-apache-cockpit-station-model07",
                "core-apache-cockpit-station-model08",
                "core-apache-cockpit-station-model09",
                "core-apache-cockpit-station-model10",
                "core-apache-cockpit-station-model11",
                "core-apache-30mm",
                "core-apache-hydra",
                "core-apache-hellfire",
                "core-apache-airframe",
            ],
        )
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])
        self.assertEqual(
            asset["state_reason"],
            (
                "Queued Apache CPG P0 station-model09 method; keep glass "
                "overhead brow and TEDAC/MPD readability; bucket seat with "
                "visible pan well, tall inner bolster cheeks, and cupped "
                "back; worker registered; not launched; not ready; does not "
                "supersede model08 until accepted; visual review still "
                "required; Unreal import forbidden until accepted."
            ),
        )

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model09"),
            ids.index("core-apache-cockpit-station-model08") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model09"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model09_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model09.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model09.glb")
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
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model09")
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
        self.assertEqual(by_id["core-apache-cockpit-station-model01"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model02"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model03"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model04"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model05"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model06"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model07"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model08"]["status"], "queued")
        self.assertEqual(by_id["core-apache-30mm"]["status"], "queued")
        self.assertEqual(by_id["core-apache-hydra"]["status"], "queued")
        self.assertEqual(
            by_id["core-apache-cockpit-station-model08"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model08.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model07"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model07.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model06"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model06.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model05"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model05.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model04"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model04.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model02"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model02.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model03"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model03.py",
        )
        self.assertEqual(
            by_id["core-apache-30mm"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_30mm.py",
        )
        self.assertEqual(
            by_id["core-apache-hydra"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_hydra.py",
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model08.py"
            ).is_file()
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model07.py"
            ).is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_30mm.py").is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_hydra.py").is_file()
        )
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_station_model10_registers_queued_formed_enclosure_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model10.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model10_once.ps1"
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
        self.assertIn("SOCKET_CPG_Eye", source)
        self.assertIn("(0.42, 0.55, 0.62)", source)
        self.assertIn("0.2 <= world.x <= 0.85", source)
        self.assertIn("abs(world.y) < 0.20", source)
        self.assertIn("1.05 <= world.z <= 1.35", source)
        self.assertIn("add_explicit_hood", source)
        self.assertIn("hood verts are missing", source)
        self.assertIn("GEO_SeatBack", source)
        self.assertIn("GEO_SeatHeadrest", source)
        self.assertIn("GEO_APillar_L", source)
        self.assertIn("GEO_APillar_R", source)
        self.assertIn("GEO_KneePanel_L", source)
        self.assertIn("GEO_KneePanel_R", source)
        self.assertIn("abs(world.y) < 0.16", source)
        self.assertIn("z <= 0.86", source)
        self.assertIn("GEO_TEDAC has no emit faces", source)
        self.assertIn("def assert_tedac_readable_from_eye", source)
        self.assertIn("thumb_face = bm.faces.new(thumb)", source)
        self.assertIn("(0.545, 0.0, 0.748)", source)
        greenhouse = source.split("def build_greenhouse", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("GEO_BowFrame", greenhouse)
        self.assertNotIn("GEO_BowFrame", source)
        self.assertIn("GEO_Rail_L", greenhouse)
        self.assertIn("GEO_Rail_R", greenhouse)
        self.assertIn("GEO_Sill_L", greenhouse)
        self.assertIn("GEO_Sill_R", greenhouse)
        self.assertIn("GEO_AftFrame", greenhouse)
        self.assertIn("0.38", greenhouse)
        self.assertIn("section_along", greenhouse)
        self.assertNotIn("pipe_along", greenhouse)
        self.assertIn("GEO_CanopyGlass", greenhouse)
        self.assertIn("def section_along", source)
        self.assertIn("formed rectangular", source.lower())
        self.assertIn("sill plate", greenhouse.lower())
        self.assertIn("formed pillar", greenhouse.lower())
        self.assertIn("rail cap", greenhouse.lower())
        self.assertIn("0.052", greenhouse)
        self.assertIn("0.062", greenhouse)
        self.assertIn("0.038", greenhouse)
        self.assertNotIn("0.018", greenhouse)
        self.assertIn("def loft_canopy_skin", source)
        self.assertIn("canopy skin", source.lower())
        self.assertIn("enclosure", source.lower())
        skin_fn = source.split("def loft_canopy_skin", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", skin_fn)
        self.assertNotIn("pipe_along", skin_fn)
        self.assertIn("faces.new", skin_fn)
        self.assertIn("solidify", skin_fn)
        self.assertIn("-0.20", skin_fn)
        self.assertIn("0.70", skin_fn)
        self.assertIn("0.20", skin_fn)
        self.assertNotIn("thicker tube", source.lower())
        self.assertIn("def loft_overhead_brow", source)
        self.assertIn("GEO_OverheadBrow", source)
        self.assertIn("GEO_ForwardBrow", source)
        self.assertIn("1.36", source)
        overhead_fn = source.split("def loft_overhead_brow", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", overhead_fn)
        self.assertNotIn("pipe_along", overhead_fn)
        self.assertIn("faces.new", overhead_fn)
        self.assertIn("solidify", overhead_fn)
        self.assertIn("GEO_OverheadBrow", overhead_fn)
        self.assertIn("GEO_ForwardBrow", overhead_fn)
        self.assertIn("-0.15", overhead_fn)
        self.assertIn("0.55", overhead_fn)
        self.assertIn("1.36", overhead_fn)
        self.assertIn("glass", overhead_fn.lower())
        self.assertIn("loft_overhead_brow", greenhouse)
        self.assertIn("loft_overhead_brow(collection, glass)", greenhouse)
        self.assertNotIn("loft_overhead_brow(collection, rail)", greenhouse)
        self.assertIn("MAT_CPG_CanopyGlass", source)
        seat_fn = source.split("def build_seat", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("GEO_Seat", seat_fn)
        self.assertIn("GEO_SeatBolster_L", seat_fn)
        self.assertIn("GEO_SeatBolster_R", seat_fn)
        self.assertIn("GEO_SeatBack", seat_fn)
        self.assertIn("GEO_SeatHeadrest", seat_fn)
        self.assertIn("dish", seat_fn)
        self.assertIn("bucket", seat_fn.lower())
        self.assertIn("cheeks", seat_fn.lower())
        self.assertIn("cupped", seat_fn.lower())
        self.assertIn("pan well", seat_fn.lower())
        self.assertIn("0.318", seat_fn)
        self.assertIn("1.168", seat_fn)
        self.assertIn("1.128", seat_fn)
        self.assertIn("0.056", seat_fn)
        self.assertIn("0.612", seat_fn)
        self.assertNotIn("0.228", seat_fn)
        self.assertNotIn("1.055", seat_fn)
        self.assertNotIn("1.018", seat_fn)
        self.assertNotIn("(-0.205, -0.175, 0.620)", seat_fn)
        self.assertNotIn("(-0.248, 0.155, 1.015)", seat_fn)
        self.assertIn("(0.032, 0.026, 0.020, 1.0)", source)
        self.assertIn("(0.014, 0.011, 0.009, 1.0)", source)
        self.assertIn("(0.18, 0.20, 0.12, 1.0)", source)
        self.assertIn("MAT_CPG_SeatWell", source)
        tedac_fn = source.split("def build_tedac", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("formed_bezel", tedac_fn)
        self.assertIn("corner_cut", tedac_fn)
        self.assertIn("GEO_TEDAC", tedac_fn)
        self.assertIn("pipe_along", tedac_fn)
        self.assertNotIn("primitive_cylinder_add", source)
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
        self.assertNotIn("APACHE_CPG_STATION_MODEL02", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL03", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL04", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL05", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL06", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL07", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL08", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL09", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL10", source)
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model10", supervisor)
        self.assertNotIn("core-apache-cockpit-station-model09", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model10"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertIsNone(asset.get("blocker"))
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-model09",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model10.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model10",
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
        self.assertIn("core-apache-cockpit-station-model10", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(
            list(VALIDATOR.APACHE_P0_IDS),
            [
                "core-apache-cockpit",
                "core-apache-cockpit-station-detail01",
                "core-apache-cockpit-station-model01",
                "core-apache-cockpit-station-model02",
                "core-apache-cockpit-station-model03",
                "core-apache-cockpit-station-model04",
                "core-apache-cockpit-station-model05",
                "core-apache-cockpit-station-model06",
                "core-apache-cockpit-station-model07",
                "core-apache-cockpit-station-model08",
                "core-apache-cockpit-station-model09",
                "core-apache-cockpit-station-model10",
                "core-apache-cockpit-station-model11",
                "core-apache-30mm",
                "core-apache-hydra",
                "core-apache-hellfire",
                "core-apache-airframe",
            ],
        )
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])
        self.assertEqual(
            asset["state_reason"],
            (
                "Queued Apache CPG P0 station-model10 method; formed plate "
                "greenhouse (sill plates, formed A-pillars, rail caps — not "
                "tube sticks); keep glass overhead brow, TEDAC/MPD "
                "readability, and model09 bucket seat; worker registered; "
                "not launched; not ready; does not supersede model09 until "
                "accepted; visual review still required; Unreal import "
                "forbidden until accepted."
            ),
        )

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model10"),
            ids.index("core-apache-cockpit-station-model09") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model10"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model10_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model10.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model10.glb")
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
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model10")
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
        self.assertEqual(by_id["core-apache-cockpit-station-model01"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model02"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model03"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model04"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model05"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model06"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model07"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model08"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model09"]["status"], "queued")
        self.assertEqual(by_id["core-apache-30mm"]["status"], "queued")
        self.assertEqual(by_id["core-apache-hydra"]["status"], "queued")
        self.assertEqual(
            by_id["core-apache-cockpit-station-model09"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model09.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model08"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model08.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model07"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model07.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model06"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model06.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model05"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model05.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model04"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model04.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model02"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model02.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model03"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model03.py",
        )
        self.assertEqual(
            by_id["core-apache-30mm"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_30mm.py",
        )
        self.assertEqual(
            by_id["core-apache-hydra"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_hydra.py",
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model09.py"
            ).is_file()
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model08.py"
            ).is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_30mm.py").is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_hydra.py").is_file()
        )
        self.assertNotIn("harbor-threat-kit01", by_id)
        self.assertNotIn("core-radar-van-kit01", by_id)

    def test_apache_p0_station_model11_registers_queued_dark_formed_greenhouse_method(self) -> None:
        worker_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "Workers"
            / "worker_core_apache_cockpit_station_model11.py"
        )
        supervisor_path = (
            PIPELINE.ROOT
            / "Scripts"
            / "invoke_core_apache_cockpit_station_model11_once.ps1"
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
        self.assertIn("SOCKET_CPG_Eye", source)
        self.assertIn("(0.42, 0.55, 0.62)", source)
        self.assertIn("0.2 <= world.x <= 0.85", source)
        self.assertIn("abs(world.y) < 0.20", source)
        self.assertIn("1.05 <= world.z <= 1.35", source)
        self.assertIn("add_explicit_hood", source)
        self.assertIn("hood verts are missing", source)
        self.assertIn("GEO_SeatBack", source)
        self.assertIn("GEO_SeatHeadrest", source)
        self.assertIn("GEO_APillar_L", source)
        self.assertIn("GEO_APillar_R", source)
        self.assertIn("GEO_KneePanel_L", source)
        self.assertIn("GEO_KneePanel_R", source)
        self.assertIn("abs(world.y) < 0.16", source)
        self.assertIn("z <= 0.86", source)
        self.assertIn("GEO_TEDAC has no emit faces", source)
        self.assertIn("def assert_tedac_readable_from_eye", source)
        self.assertIn("thumb_face = bm.faces.new(thumb)", source)
        self.assertIn("(0.545, 0.0, 0.748)", source)
        greenhouse = source.split("def build_greenhouse", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("GEO_BowFrame", greenhouse)
        self.assertNotIn("GEO_BowFrame", source)
        self.assertIn("GEO_Rail_L", greenhouse)
        self.assertIn("GEO_Rail_R", greenhouse)
        self.assertIn("GEO_Sill_L", greenhouse)
        self.assertIn("GEO_Sill_R", greenhouse)
        self.assertIn("GEO_AftFrame", greenhouse)
        self.assertIn("0.38", greenhouse)
        self.assertIn("section_along", greenhouse)
        self.assertNotIn("pipe_along", greenhouse)
        self.assertIn("GEO_CanopyGlass", greenhouse)
        self.assertIn("def section_along", source)
        self.assertIn("formed rectangular", source.lower())
        self.assertIn("sill plate", greenhouse.lower())
        self.assertIn("formed pillar", greenhouse.lower())
        self.assertIn("rail cap", greenhouse.lower())
        self.assertIn("0.052", greenhouse)
        self.assertIn("0.062", greenhouse)
        self.assertIn("0.038", greenhouse)
        self.assertNotIn("0.018", greenhouse)
        self.assertIn("def loft_canopy_skin", source)
        self.assertIn("canopy skin", source.lower())
        self.assertIn("enclosure", source.lower())
        self.assertIn("dark formed", source.lower())
        self.assertIn("joint plate", source.lower())
        self.assertIn("GEO_JointPlate", greenhouse)
        self.assertIn("|y| >= 0.38", greenhouse)
        joint_fn = source.split("def formed_joint_plate", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("faces.new", joint_fn)
        self.assertNotIn("section_along", joint_fn)
        self.assertNotIn("pipe_along", joint_fn)
        self.assertNotIn("GEO_BowFrame", joint_fn)
        self.assertIn("0.38", joint_fn)
        skin_fn = source.split("def loft_canopy_skin", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", skin_fn)
        self.assertNotIn("pipe_along", skin_fn)
        self.assertIn("faces.new", skin_fn)
        self.assertIn("solidify", skin_fn)
        self.assertIn("-0.20", skin_fn)
        self.assertIn("0.70", skin_fn)
        self.assertIn("0.20", skin_fn)
        self.assertNotIn("thicker tube", source.lower())
        self.assertIn("def loft_overhead_brow", source)
        self.assertIn("GEO_OverheadBrow", source)
        self.assertIn("GEO_ForwardBrow", source)
        self.assertIn("1.36", source)
        overhead_fn = source.split("def loft_overhead_brow", 1)[1].split("\ndef ", 1)[0]
        self.assertNotIn("section_along", overhead_fn)
        self.assertNotIn("pipe_along", overhead_fn)
        self.assertIn("faces.new", overhead_fn)
        self.assertIn("solidify", overhead_fn)
        self.assertIn("GEO_OverheadBrow", overhead_fn)
        self.assertIn("GEO_ForwardBrow", overhead_fn)
        self.assertIn("-0.15", overhead_fn)
        self.assertIn("0.55", overhead_fn)
        self.assertIn("1.36", overhead_fn)
        self.assertIn("glass", overhead_fn.lower())
        self.assertIn("loft_overhead_brow", greenhouse)
        self.assertIn("loft_overhead_brow(collection, glass)", greenhouse)
        self.assertNotIn("loft_overhead_brow(collection, rail)", greenhouse)
        self.assertIn("MAT_CPG_CanopyGlass", source)
        self.assertIn("MAT_CPG_CanopyRail", source)
        self.assertIn("(0.035, 0.038, 0.032, 1.0)", source)
        self.assertNotIn("(0.12, 0.13, 0.1, 1.0)", source)
        self.assertNotIn("(0.12, 0.13, 0.1)", source)
        seat_fn = source.split("def build_seat", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("GEO_Seat", seat_fn)
        self.assertIn("GEO_SeatBolster_L", seat_fn)
        self.assertIn("GEO_SeatBolster_R", seat_fn)
        self.assertIn("GEO_SeatBack", seat_fn)
        self.assertIn("GEO_SeatHeadrest", seat_fn)
        self.assertIn("dish", seat_fn)
        self.assertIn("bucket", seat_fn.lower())
        self.assertIn("cheeks", seat_fn.lower())
        self.assertIn("cupped", seat_fn.lower())
        self.assertIn("pan well", seat_fn.lower())
        self.assertIn("0.318", seat_fn)
        self.assertIn("1.168", seat_fn)
        self.assertIn("1.128", seat_fn)
        self.assertIn("0.056", seat_fn)
        self.assertIn("0.612", seat_fn)
        self.assertNotIn("0.228", seat_fn)
        self.assertNotIn("1.055", seat_fn)
        self.assertNotIn("1.018", seat_fn)
        self.assertNotIn("(-0.205, -0.175, 0.620)", seat_fn)
        self.assertNotIn("(-0.248, 0.155, 1.015)", seat_fn)
        self.assertIn("(0.032, 0.026, 0.020, 1.0)", source)
        self.assertIn("(0.014, 0.011, 0.009, 1.0)", source)
        self.assertIn("(0.18, 0.20, 0.12, 1.0)", source)
        self.assertIn("MAT_CPG_SeatWell", source)
        tedac_fn = source.split("def build_tedac", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("formed_bezel", tedac_fn)
        self.assertIn("corner_cut", tedac_fn)
        self.assertGreater(
            float(
                tedac_fn.split("corner_cut=", 1)[1]
                .split(",", 1)[0]
                .split(")", 1)[0]
                .strip()
            ),
            0.022,
        )
        self.assertIn("GEO_TEDAC", tedac_fn)
        self.assertIn("pipe_along", tedac_fn)
        self.assertNotIn("primitive_cylinder_add", source)
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
        self.assertNotIn("APACHE_CPG_STATION_MODEL02", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL03", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL04", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL05", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL06", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL07", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL08", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL09", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL10", source)
        self.assertNotIn("APACHE_CPG_STATION_MODEL11", source)
        emit_fn = source.split("def emit_material", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("if alpha < 1.0:", emit_fn)
        before_gate, after_gate = emit_fn.split("if alpha < 1.0:", 1)
        self.assertNotIn("Transmission", before_gate)
        self.assertNotIn("BLEND", before_gate)
        self.assertIn("Transmission Weight", after_gate)
        self.assertIn("BLEND", after_gate)
        self.assertEqual(supervisor.count("$CyclePath run $AssetId"), 1)
        self.assertIn("core-apache-cockpit-station-model11", supervisor)
        self.assertNotIn("core-apache-cockpit-station-model10", supervisor)
        self.assertIn("OfflineContractTest", supervisor)
        self.assertIn("ExecuteOnce", supervisor)
        self.assertIn("StandingAuthority", supervisor)
        self.assertNotIn("Start-Process", supervisor)
        self.assertNotIn("blender.exe", supervisor.lower())

        manifest = PIPELINE.load_manifest()
        by_id = PIPELINE.asset_index(manifest)
        asset = by_id["core-apache-cockpit-station-model11"]
        self.assertEqual(asset["status"], "queued")
        self.assertNotEqual(asset["status"], "ready")
        self.assertNotEqual(asset["status"], "accepted")
        self.assertIsNone(asset.get("blocker"))
        self.assertEqual(asset["lane"], VALIDATOR.APACHE_P0_LANE)
        self.assertEqual(asset["priority"], 1)
        self.assertEqual(
            asset["supersedes_only_after_acceptance"],
            "core-apache-cockpit-station-model10",
        )
        self.assertEqual(
            asset["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model11.py",
        )
        self.assertEqual(
            asset["worker"]["arguments"],
            [
                "--output",
                "{output_dir}",
                "--asset-id",
                "core-apache-cockpit-station-model11",
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
        self.assertIn("core-apache-cockpit-station-model11", VALIDATOR.APACHE_P0_IDS)
        self.assertEqual(
            list(VALIDATOR.APACHE_P0_IDS),
            [
                "core-apache-cockpit",
                "core-apache-cockpit-station-detail01",
                "core-apache-cockpit-station-model01",
                "core-apache-cockpit-station-model02",
                "core-apache-cockpit-station-model03",
                "core-apache-cockpit-station-model04",
                "core-apache-cockpit-station-model05",
                "core-apache-cockpit-station-model06",
                "core-apache-cockpit-station-model07",
                "core-apache-cockpit-station-model08",
                "core-apache-cockpit-station-model09",
                "core-apache-cockpit-station-model10",
                "core-apache-cockpit-station-model11",
                "core-apache-30mm",
                "core-apache-hydra",
                "core-apache-hellfire",
                "core-apache-airframe",
            ],
        )
        self.assertEqual(VALIDATOR.apache_p0_contract_errors(manifest), [])
        self.assertEqual(
            asset["state_reason"],
            (
                "Queued Apache CPG P0 station-model11 method; dark formed "
                "greenhouse (dark canopy-rail value plus formed joint plates "
                "at rail/sill and rail/A-pillar — not a white kit, not tubes); "
                "keep glass overhead brow, TEDAC/MPD readability, and model10 "
                "bucket seat; worker registered; not launched; not ready; does "
                "not supersede model10 until accepted; visual review still "
                "required; Unreal import forbidden until accepted."
            ),
        )

        ids = [item["id"] for item in manifest["assets"]]
        self.assertEqual(
            ids.index("core-apache-cockpit-station-model11"),
            ids.index("core-apache-cockpit-station-model10") + 1,
        )

        contracts = PIPELINE.load_json(
            PIPELINE.PRODUCTION / "ready_blender_output_contracts.json"
        )["contracts"]
        contract = contracts["core-apache-cockpit-station-model11"]
        self.assertEqual(contract["worker_script"], asset["worker"]["script"])
        self.assertEqual(
            contract["supervisor_script"],
            r"Scripts\invoke_core_apache_cockpit_station_model11_once.ps1",
        )
        self.assertEqual(contract["blend"], "core-apache-cockpit-station-model11.blend")
        self.assertEqual(contract["glb"], "core-apache-cockpit-station-model11.glb")
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
        self.assertEqual(check_paths["asset_id"]["value"], "core-apache-cockpit-station-model11")
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
        self.assertEqual(by_id["core-apache-cockpit-station-model01"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model02"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model03"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model04"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model05"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model06"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model07"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model08"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model09"]["status"], "queued")
        self.assertEqual(by_id["core-apache-cockpit-station-model10"]["status"], "queued")
        self.assertEqual(by_id["core-apache-30mm"]["status"], "queued")
        self.assertEqual(by_id["core-apache-hydra"]["status"], "queued")
        self.assertEqual(
            by_id["core-apache-cockpit-station-model10"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model10.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model09"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model09.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model08"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model08.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model07"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model07.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model06"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model06.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model05"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model05.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model04"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model04.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model02"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model02.py",
        )
        self.assertEqual(
            by_id["core-apache-cockpit-station-model03"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_cockpit_station_model03.py",
        )
        self.assertEqual(
            by_id["core-apache-30mm"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_30mm.py",
        )
        self.assertEqual(
            by_id["core-apache-hydra"]["worker"]["script"],
            r"Scripts\Workers\worker_core_apache_hydra.py",
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model10.py"
            ).is_file()
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model09.py"
            ).is_file()
        )
        self.assertTrue(
            (
                PIPELINE.ROOT
                / "Scripts"
                / "Workers"
                / "worker_core_apache_cockpit_station_model08.py"
            ).is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_30mm.py").is_file()
        )
        self.assertTrue(
            (PIPELINE.ROOT / "Scripts" / "Workers" / "worker_core_apache_hydra.py").is_file()
        )
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
