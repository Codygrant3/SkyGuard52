from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "verify_skyguard_phase1_insights_review.py"
)
SPEC = importlib.util.spec_from_file_location("phase1_insights_review", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_csv(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def make_manifest(tmp_path: Path) -> Path:
    trace = tmp_path / "accepted.utrace"
    trace.write_bytes(b"trace")
    contract = tmp_path / "contract.txt"
    contract.write_text("contract", encoding="utf-8")
    log = tmp_path / "insights.log"
    log.write_text(
        "Analysis has completed\n"
        "Application is closing because it was started with the AutoQuit "
        "parameter and session analysis is complete.\n",
        encoding="utf-8",
    )
    write_csv(tmp_path / "threads.csv", "Id,Name,Group\n1,GameThread,CPU\n")
    write_csv(tmp_path / "timers.csv", "Id,Type,Name,File,Line\n1,CPU,LoadPackage,,0\n")
    write_csv(
        tmp_path / "stats.csv",
        "Name,Count,Incl,I.Max\nLoadPackage,1,0.25,0.25\nNiagara,1,0.01,0.01\n",
    )
    write_csv(
        tmp_path / "loading.csv",
        "ThreadName,TimerName,StartTime,EndTime,Duration,Depth\n"
        "GameThread,LoadPackage,20,20.25,0.25,1\n",
    )
    write_csv(
        tmp_path / "shader.csv",
        "ThreadName,TimerName,StartTime,EndTime,Duration,Depth\n"
        "GameThread,CompileShader,21,21.12,0.12,1\n",
    )
    write_csv(
        tmp_path / "niagara.csv",
        "ThreadName,TimerName,StartTime,EndTime,Duration,Depth\n"
        "GameThread,Niagara,22,22.01,0.01,1\n",
    )
    bindings = []
    for label, path in (("trace", trace), ("contract", contract)):
        bindings.append(
            {
                "label": label,
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": MODULE.sha256(path),
            }
        )
    manifest = {
        "schema": "skyguard.phase1.insights-review-run.v1",
        "attempt_id": "attempt_20260802T120000000Z",
        "requested_channels": ["cpu", "gpu", "loadtime"],
        "bindings": bindings,
        "execution": {
            "exit_code": 0,
            "timed_out": False,
            "log_path": str(log),
        },
        "exports": {
            "threads": str(tmp_path / "threads.csv"),
            "timers": str(tmp_path / "timers.csv"),
            "timer_statistics": str(tmp_path / "stats.csv"),
            "loading_streaming_events": str(tmp_path / "loading.csv"),
            "shader_pso_events": str(tmp_path / "shader.csv"),
            "niagara_events": str(tmp_path / "niagara.csv"),
        },
    }
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


class InsightsReviewVerifierTests(unittest.TestCase):
    def test_readable_headless_export_does_not_promote_p1_4(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            report = MODULE.verify(make_manifest(tmp_path))
            self.assertEqual(report["headless_export_gate"], "PASS")
            self.assertEqual(report["terminal_state"], "EXECUTION_COMPLETE")
            self.assertEqual(
                report["p1_4_disposition"], "INSUFFICIENT_EVIDENCE"
            )
            self.assertEqual(
                report["domains"]["memory_vram"]["status"], "NOT_CAPTURED"
            )
            self.assertEqual(
                report["domains"]["loading_streaming"][
                    "max_observed_duration_seconds"
                ],
                0.25,
            )
            self.assertEqual(
                report["domains"]["shader_pso"][
                    "max_observed_duration_seconds"
                ],
                0.12,
            )

    def test_binding_tamper_fails_headless_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            manifest = make_manifest(tmp_path)
            (tmp_path / "accepted.utrace").write_bytes(b"tampered")
            report = MODULE.verify(manifest)
            self.assertEqual(report["headless_export_gate"], "FAIL")
            self.assertEqual(report["terminal_state"], "EXECUTION_FAILED")
            self.assertFalse(report["bindings"][0]["hash_matches"])


if __name__ == "__main__":
    unittest.main()
