from __future__ import annotations

import hashlib
import json
from pathlib import Path

import av
from PIL import Image, ImageDraw


VIDEO = Path(r"C:\Users\chris\Downloads\xdZG_ony6R5pHB4J.mp4")
ROOT = Path(__file__).resolve().parent / "combat_asset_reference_resolution_cycle02_20260805"
FRAMES = ROOT / "frames_full"
CONTACTS = ROOT / "contact_sheets"
MANIFEST = ROOT / "frame_extraction_manifest.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    if ROOT.exists():
        raise RuntimeError(f"Refusing to overwrite existing Cycle02 staging namespace: {ROOT}")
    FRAMES.mkdir(parents=True)
    CONTACTS.mkdir(parents=True)

    container = av.open(str(VIDEO))
    stream = container.streams.video[0]
    records: list[dict[str, object]] = []
    thumbnails: list[tuple[Image.Image, str]] = []
    sample_stride = 15

    for decoded_index, frame in enumerate(container.decode(stream)):
        if decoded_index % sample_stride:
            continue
        timestamp = float(frame.time or 0.0)
        image = frame.to_image()
        name = f"frame_{decoded_index:04d}_{timestamp:08.3f}s.png"
        target = FRAMES / name
        image.save(target, format="PNG", compress_level=6)
        records.append(
            {
                "decoded_frame_index": decoded_index,
                "timestamp_seconds": round(timestamp, 6),
                "width": image.width,
                "height": image.height,
                "path": target.relative_to(ROOT).as_posix(),
                "bytes": target.stat().st_size,
                "sha256": digest(target),
            }
        )
        thumb = image.copy()
        thumb.thumbnail((320, 180))
        thumbnails.append((thumb, f"f{decoded_index}  {timestamp:.3f}s"))
    container.close()

    sheet_records: list[dict[str, object]] = []
    per_sheet = 20
    cols, rows = 5, 4
    cell_w, cell_h = 320, 205
    for start in range(0, len(thumbnails), per_sheet):
        subset = thumbnails[start : start + per_sheet]
        sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
        draw = ImageDraw.Draw(sheet)
        for position, (thumb, label) in enumerate(subset):
            x = (position % cols) * cell_w
            y = (position // cols) * cell_h
            sheet.paste(thumb, (x, y))
            draw.text((x + 4, y + 183), label, fill="black")
        target = CONTACTS / f"contact_{start // per_sheet + 1:02d}.png"
        sheet.save(target, format="PNG", compress_level=6)
        sheet_records.append(
            {
                "path": target.relative_to(ROOT).as_posix(),
                "bytes": target.stat().st_size,
                "sha256": digest(target),
                "first_sample_index": start,
                "sample_count": len(subset),
            }
        )

    payload = {
        "source": {
            "path": str(VIDEO),
            "bytes": VIDEO.stat().st_size,
            "sha256": digest(VIDEO),
        },
        "decoder": {
            "library": "PyAV",
            "version": av.__version__,
            "sample_stride_frames": sample_stride,
            "nominal_sampling_seconds": 0.5,
            "source_stream_width": int(stream.width),
            "source_stream_height": int(stream.height),
            "source_average_rate": str(stream.average_rate),
            "source_frames_reported": int(stream.frames),
        },
        "lossless_original_resolution_frames": records,
        "contact_sheets": sheet_records,
    }
    MANIFEST.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"root": str(ROOT), "frames": len(records), "contact_sheets": len(sheet_records)}, indent=2))


if __name__ == "__main__":
    main()
