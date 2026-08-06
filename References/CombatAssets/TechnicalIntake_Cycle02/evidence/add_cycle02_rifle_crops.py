from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent / "combat_asset_reference_resolution_cycle02_20260805"
CROPS = ROOT / "rifle_crops"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if CROPS.exists():
        raise RuntimeError(f"Refusing to overwrite crop namespace: {CROPS}")
    CROPS.mkdir()
    selections = [
        ("frame_0000_0000.000s.png", (230, 270, 880, 720), "top rail, muzzle, support hand"),
        ("frame_0435_0014.500s.png", (480, 0, 1120, 720), "tan handguard and muzzle"),
        ("frame_0450_0015.000s.png", (520, 0, 1120, 720), "tan handguard, barrel and open-tine muzzle"),
        ("frame_0480_0016.000s.png", (480, 0, 1100, 720), "handguard vent pattern and rail"),
        ("frame_0510_0017.000s.png", (380, 0, 930, 720), "handguard close view"),
        ("frame_0675_0022.500s.png", (250, 20, 1160, 720), "dark-lighting weapon view and rear rail"),
    ]
    records = []
    for source_name, box, observation in selections:
        source = ROOT / "frames_full" / source_name
        if not source.is_file():
            raise FileNotFoundError(source)
        with Image.open(source) as image:
            crop = image.crop(box)
            target = CROPS / source_name.replace(".png", "_rifle_crop.png")
            crop.save(target, format="PNG", compress_level=6)
        records.append(
            {
                "source": source.relative_to(ROOT).as_posix(),
                "crop_box_xyxy": list(box),
                "observation_scope": observation,
                "path": target.relative_to(ROOT).as_posix(),
                "width": crop.width,
                "height": crop.height,
                "bytes": target.stat().st_size,
                "sha256": digest(target),
            }
        )
    manifest = ROOT / "rifle_crop_manifest.json"
    manifest.write_text(json.dumps({"lossless_crops": records}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"crops": len(records), "manifest": str(manifest)}, indent=2))


if __name__ == "__main__":
    main()
