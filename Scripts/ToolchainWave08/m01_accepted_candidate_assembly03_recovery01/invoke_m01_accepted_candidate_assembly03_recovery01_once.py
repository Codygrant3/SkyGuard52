"""Recovery01 one-shot binding for the frozen Assembly03 supervisor."""

from __future__ import annotations

import hashlib
from pathlib import Path


BASE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\m01_accepted_candidate_assembly03\invoke_m01_accepted_candidate_assembly03_once.py"
)
BASE_BYTES = 12_561
BASE_SHA256 = "f526c03dc0f822054713e2e6796254623cb1e339068a7bd358cdc9b595787838"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if not BASE.is_file() or BASE.stat().st_size != BASE_BYTES or sha256(BASE) != BASE_SHA256:
    raise RuntimeError("Frozen failed Assembly03 supervisor authority changed")

source = BASE.read_text(encoding="utf-8")
for old, new in (
    (
        "m01_accepted_candidate_assembly03/author_m01_accepted_candidate_assembly03.py",
        "m01_accepted_candidate_assembly03_recovery01/author_m01_accepted_candidate_assembly03_recovery01.py",
    ),
    ("M01_AcceptedCandidateAssembly03", "M01_AcceptedCandidateAssembly03_Recovery01"),
    ("M01_ACCEPTED_CANDIDATE_ASSEMBLY03/attempt_01", "M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01/attempt_01"),
    ("M01_ACCEPTED_CANDIDATE_ASSEMBLY03_TERMINAL_SUPERVISOR", "M01_ACCEPTED_CANDIDATE_ASSEMBLY03_RECOVERY01_TERMINAL_SUPERVISOR"),
    ("ASSEMBLY03_OFFLINE_CONTRACT", "ASSEMBLY03_RECOVERY01_OFFLINE_CONTRACT"),
    ("ASSEMBLY03_SUPERVISOR_OFFLINE_CONTRACT", "ASSEMBLY03_RECOVERY01_SUPERVISOR_OFFLINE_CONTRACT"),
    ("ASSEMBLY03_READY_FOR_STRUCTURAL_ADJUDICATION", "ASSEMBLY03_RECOVERY01_READY_FOR_STRUCTURAL_ADJUDICATION"),
    ("ASSEMBLY03_READY_FOR_MAPPED_VISUAL_PROOF_DESIGN", "ASSEMBLY03_RECOVERY01_READY_FOR_MAPPED_VISUAL_PROOF_DESIGN"),
    ("accepted-candidate-assembly03.supervisor.v1", "accepted-candidate-assembly03-recovery01.supervisor.v1"),
):
    if old not in source:
        raise RuntimeError(f"Recovery01 supervisor token absent: {old}")
    source = source.replace(old, new)

if "Lvl_M01_AcceptedCandidateAssembly03.umap" in source:
    raise RuntimeError("Recovery01 supervisor retains failed output namespace")
if "M01_ACCEPTED_CANDIDATE_ASSEMBLY03/attempt_01" in source:
    raise RuntimeError("Recovery01 supervisor retains failed attempt namespace")

namespace = {"__name__": "__main__", "__file__": __file__}
exec(compile(source, __file__ + "::bound", "exec"), namespace, namespace)
