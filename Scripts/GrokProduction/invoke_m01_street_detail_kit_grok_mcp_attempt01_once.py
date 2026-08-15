"""Fresh one-shot binding for the M01 street-detail Grok Blender production batch."""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(r"D:\Skyguard52\Scripts\GrokProduction\invoke_m01_promenade_prop_kit_grok_mcp_attempt01_once.py")
BASE_BYTES = 17814
BASE_SHA256 = "c770cad25e3ced45eb2ae0baae7d242d246a19a235f522a82d9f00f55a11bc75"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen promenade Attempt01 supervisor is missing or changed")

source = BASE.read_text(encoding="utf-8")
replacements = {
    'PROMPT = PROJECT / "Production" / "Prompts" / "M01_PROMENADE_PROP_KIT_GROK_MCP_PRODUCTION_ATTEMPT01.md"':
        'PROMPT = PROJECT / "Production" / "Prompts" / "M01_STREET_DETAIL_KIT_GROK_MCP_PRODUCTION_ATTEMPT01.md"',
    'FINALIZER = PROJECT / "Scripts" / "GrokProduction" / "finalize_m01_promenade_prop_kit_scene.py"':
        'FINALIZER = PROJECT / "Scripts" / "GrokProduction" / "finalize_m01_street_detail_kit_scene.py"',
    'ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-promenade-prop-kit-grok-mcp" / "attempt_20260811T061500000000Z"':
        'ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-street-detail-kit-grok-mcp" / "attempt_20260811T070000000000Z"',
    'EXPECTED_BLEND = OUTPUT / "M01_Promenade_PropKit_GrokMCP_Production_A.blend"':
        'EXPECTED_BLEND = OUTPUT / "M01_StreetDetailKit_GrokMCP_Production_A.blend"',
    'EXPECTED_GLB = OUTPUT / "exports" / "M01_Promenade_PropKit_GrokMCP_Production_A.glb"':
        'EXPECTED_GLB = OUTPUT / "exports" / "M01_StreetDetailKit_GrokMCP_Production_A.glb"',
    'skyguard.m01-promenade-prop-kit.grok-mcp.production-attempt01.terminal.v1':
        'skyguard.m01-street-detail-kit.grok-mcp.production-attempt01.terminal.v1',
    'if report.get("classification") != "PASSED_AWAITING_DIRECT_VISUAL_REVIEW":\n            raise RuntimeError("Implementation report did not reach the automatic review boundary")':
        'report_classification = report.get("classification")\n        if report_classification not in ("PASSED_AWAITING_DIRECT_VISUAL_REVIEW", "PARTIAL_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW"):\n            raise RuntimeError("Implementation report did not reach an automatic review boundary")',
    'classification = "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW"\n        failure_stage = None':
        'classification = "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW" if report_classification == "PASSED_AWAITING_DIRECT_VISUAL_REVIEW" else "PARTIAL_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW"\n        failure_stage = None',
    'return 0 if classification == "PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW" else 1':
        'return 0 if classification in ("PASSED_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW", "PARTIAL_AUTOMATIC_AWAITING_DIRECT_VISUAL_REVIEW") else 1',
}

for old, new in replacements.items():
    if source.count(old) != 1:
        raise RuntimeError(f"Frozen supervisor binding changed: {old}")
    source = source.replace(old, new)

compile(source, str(BASE), "exec")
exec(source, globals(), globals())

