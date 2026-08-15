from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\GrokProduction\recover_m01_utility_cabinet_recovery02_scene.py")
SOURCE_BYTES = 9122
SOURCE_SHA256 = "543de177dffc3392550273d59471960b4216dbd109c57a62e79a11d0507d84ce"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


if SOURCE.stat().st_size != SOURCE_BYTES or sha256(SOURCE) != SOURCE_SHA256:
    raise RuntimeError("Recovery02 source authority changed")

text = SOURCE.read_text(encoding="utf-8")
replacements = {
    '"m01-utility-cabinet-deterministic-recovery02"': '"m01-utility-cabinet-deterministic-recovery03"',
    '"attempt_20260811T093000000000Z"': '"attempt_20260811T094000000000Z"',
    '"M01_Promenade_UtilityCabinet_Recovery02.blend"': '"M01_Promenade_UtilityCabinet_Recovery03.blend"',
    '"M01_Promenade_UtilityCabinet_Recovery02.glb"': '"M01_Promenade_UtilityCabinet_Recovery03.glb"',
    'if left_min[0] >= -0.500:': 'if left_min[0] >= -0.465:',
    'if right_max[0] <= 0.500:': 'if right_max[0] <= 0.465:',
    'skyguard.m01-utility-cabinet.deterministic-recovery02.report.v1': 'skyguard.m01-utility-cabinet.deterministic-recovery03.report.v1',
}
for old, new in replacements.items():
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one governed replacement for {old!r}, found {count}")
    text = text.replace(old, new, 1)

namespace = {"__name__": "__main__", "__file__": str(SOURCE)}
exec(compile(text, str(SOURCE), "exec"), namespace, namespace)
