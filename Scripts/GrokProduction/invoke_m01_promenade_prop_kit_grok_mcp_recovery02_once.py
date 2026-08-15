"""Fresh Recovery02 binding for the frozen promenade-kit production supervisor."""

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
    raise RuntimeError("Frozen Attempt01 supervisor is missing or changed")

source = BASE.read_text(encoding="utf-8")
replacements = {
    'SOURCE = PROJECT / "Content" / "Skyguard" / "Meshes" / "Source" / "Mission01" / "Coastal_Production_001" / "BLD_M01_COAST_PROD_001_MASTER.blend"':
        'SOURCE = Path(r"D:\\Skyguard52\\Production\\Attempts\\m01-promenade-prop-kit-grok-mcp-recovery01\\attempt_20260811T063000000000Z\\output\\M01_Promenade_PropKit_GrokMCP_Production_A.blend")',
    'SOURCE_BYTES = 201985': 'SOURCE_BYTES = 660949',
    'SOURCE_SHA = "4cb6bc2acc06310c4328687d65c808db6adfe5b1c5e49774a81bec60bf4a08cb"':
        'SOURCE_SHA = "78a788384768da87253f0b78e5ca3c33d1274cccea6a27facae218ad95fbec29"',
    'PROMPT = PROJECT / "Production" / "Prompts" / "M01_PROMENADE_PROP_KIT_GROK_MCP_PRODUCTION_ATTEMPT01.md"':
        'PROMPT = PROJECT / "Production" / "Prompts" / "M01_PROMENADE_PROP_KIT_GROK_MCP_PRODUCTION_RECOVERY02.md"',
    'FINALIZER = PROJECT / "Scripts" / "GrokProduction" / "finalize_m01_promenade_prop_kit_scene.py"':
        'FINALIZER = PROJECT / "Scripts" / "GrokProduction" / "finalize_m01_promenade_prop_kit_scene_recovery02.py"',
    'ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-promenade-prop-kit-grok-mcp" / "attempt_20260811T061500000000Z"':
        'ATTEMPT = PROJECT / "Production" / "Attempts" / "m01-promenade-prop-kit-grok-mcp-recovery02" / "attempt_20260811T064500000000Z"',
    'skyguard.m01-promenade-prop-kit.grok-mcp.production-attempt01.terminal.v1':
        'skyguard.m01-promenade-prop-kit.grok-mcp.production-recovery02.terminal.v1',
}

for old, new in replacements.items():
    if source.count(old) != 1:
        raise RuntimeError(f"Frozen Attempt01 supervisor binding changed: {old}")
    source = source.replace(old, new)

compile(source, str(BASE), "exec")
exec(source, globals(), globals())
