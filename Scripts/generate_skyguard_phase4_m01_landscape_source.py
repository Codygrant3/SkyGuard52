"""Generate the governed deterministic Mission 1 Landscape height source.

This creates source data only. It does not launch Unreal, create a Landscape
actor, serialize a PCG graph, import licensed content, or claim visual quality.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any


SCHEMA = "skyguard.phase4.m01-landscape-source-manifest.v1"
WIDTH = 505
HEIGHT = 127
COMPONENTS_X = 8
COMPONENTS_Y = 2
SECTIONS_PER_COMPONENT = 1
QUADS_PER_SECTION = 63
SEED = 5201


def _hash_noise(x: int, y: int, seed: int = SEED) -> float:
    value = (
        (x * 0x1F123BB5)
        ^ (y * 0x5F356495)
        ^ (seed * 0x6C8E9CF5)
    ) & 0xFFFFFFFF
    value ^= value >> 15
    value = (value * 0x2C1B3C6D) & 0xFFFFFFFF
    value ^= value >> 12
    return (value / 0xFFFFFFFF) * 2.0 - 1.0


def generate_samples(width: int = WIDTH, height: int = HEIGHT) -> list[int]:
    if width != WIDTH or height != HEIGHT:
        raise ValueError(f"governed Landscape size is exactly {WIDTH}x{HEIGHT}")

    samples: list[int] = []
    for y in range(height):
        coast_alpha = y / (height - 1)
        dune_envelope = math.exp(-((coast_alpha - 0.16) / 0.13) ** 2)
        inland_rise = 150.0 * coast_alpha
        for x in range(width):
            along = x / (width - 1)
            macro = (
                math.sin(along * math.tau * 2.15 + coast_alpha * 1.8) * 52.0
                + math.sin(along * math.tau * 0.47 - coast_alpha * 3.1) * 34.0
            )
            dunes = dune_envelope * (
                94.0
                + math.sin(along * math.tau * 7.0 + coast_alpha * 9.0) * 36.0
            )
            micro = _hash_noise(x // 2, y // 2) * 13.0
            height_value = 32768.0 + inland_rise + macro + dunes + micro
            samples.append(max(0, min(65535, round(height_value))))
    return samples


def write_source(
    output_path: Path,
    manifest_path: Path,
    root: Path | None = None,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    samples = generate_samples()
    payload = struct.pack(f"<{len(samples)}H", *samples)
    output_path.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    logical_path = output_path.as_posix()
    if root is not None:
        try:
            logical_path = output_path.resolve().relative_to(
                root.resolve()
            ).as_posix()
        except ValueError:
            pass
    manifest = {
        "schema": SCHEMA,
        "generator": "Scripts/generate_skyguard_phase4_m01_landscape_source.py",
        "seed": SEED,
        "path": logical_path,
        "width": WIDTH,
        "height": HEIGHT,
        "sample_count": len(samples),
        "bytes": len(payload),
        "encoding": "little-endian-uint16",
        "sha256": digest,
        "minimum_sample": min(samples),
        "maximum_sample": max(samples),
        "components_x": COMPONENTS_X,
        "components_y": COMPONENTS_Y,
        "sections_per_component": SECTIONS_PER_COMPONENT,
        "quads_per_section": QUADS_PER_SECTION,
        "claim": "deterministic source-only Landscape height data",
        "serialized_landscape_created": False,
        "visible_quality_accepted": False,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(r"D:\Skyguard52"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--manifest", type=Path)
    args = parser.parse_args()

    output = args.output or (
        args.root
        / "Content/Skyguard/Environment/Source/Mission01"
        / "HM_M01_CoastalProduction_505x127.r16"
    )
    manifest = args.manifest or (
        args.root
        / "Saved/Reports/PHASE4_M01_LANDSCAPE_SOURCE_MANIFEST.json"
    )
    result = write_source(output.resolve(), manifest.resolve(), args.root)
    print("[SkyguardPhase4LandscapeSource] " + json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
