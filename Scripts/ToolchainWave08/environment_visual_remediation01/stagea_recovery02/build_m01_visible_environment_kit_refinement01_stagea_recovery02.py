from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


GATE = "M01_VISIBLE_ENVIRONMENT_KIT_REFINEMENT01_STAGEA_RECOVERY02"
BASE_SOURCE = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visual_remediation01\build_m01_visible_environment_kit_refinement01_stagea.py"
)
BASE_BYTES = 42238
BASE_SHA256 = "773e67931108a2f199f763a4d3ce94348ba9ed9a403c049b3b8b4409bb06fd12"
OLD_ROUGHNESS_TOKEN = "    rough = np.repeat(rough, size, axis=1)\n"
NEW_ROUGHNESS_TOKEN = (
    "    require(rough.shape == (size, size, 1), "
    "f\"Roughness texture shape drift: {rough.shape}\")\n"
)
OLD_MEASUREMENT_TOKEN = '''def render_and_measure(scene: bpy.types.Scene, path: Path) -> dict[str, float]:
    path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    render = bpy.data.images.get("Render Result")
    require(render is not None, "Render Result is unavailable")
    width, height = render.size
    pixels = np.empty(width * height * 4, dtype=np.float32)
    render.pixels.foreach_get(pixels)
    rgb = pixels.reshape((-1, 4))[:, :3]
    luma = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    return {
        "width": int(width),
        "height": int(height),
        "mean_luma_linear": float(np.mean(luma)),
        "black_fraction_linear_0_01": float(np.mean(luma < 0.01)),
        "max_luma_linear": float(np.max(luma)),
    }
'''
NEW_MEASUREMENT_TOKEN = '''def render_and_measure(scene: bpy.types.Scene, path: Path) -> dict[str, float]:
    path.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    require(path.is_file() and path.stat().st_size > 0, f"Saved render is missing or empty: {path}")
    measured = bpy.data.images.load(str(path), check_existing=False)
    try:
        width, height = measured.size
        require(width > 0 and height > 0, f"Saved render dimensions are invalid: {path} => {width}x{height}")
        expected_values = width * height * 4
        pixels = np.empty(expected_values, dtype=np.float32)
        measured.pixels.foreach_get(pixels)
        require(pixels.size == expected_values and pixels.size > 0, f"Saved render pixel buffer is invalid: {path}")
        rgb = pixels.reshape((-1, 4))[:, :3]
        luma = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        require(luma.size == width * height and luma.size > 0, f"Saved render luminance buffer is invalid: {path}")
        return {
            "width": int(width),
            "height": int(height),
            "mean_luma_linear": float(np.mean(luma)),
            "black_fraction_linear_0_01": float(np.mean(luma < 0.01)),
            "max_luma_linear": float(np.max(luma)),
        }
    finally:
        bpy.data.images.remove(measured)
'''


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_bounded_source() -> tuple[str, dict[str, object]]:
    raw = BASE_SOURCE.read_bytes()
    if len(raw) != BASE_BYTES:
        raise RuntimeError(f"Frozen StageA source byte mismatch: {len(raw)}")
    digest = sha256_bytes(raw)
    if digest != BASE_SHA256:
        raise RuntimeError(f"Frozen StageA source hash mismatch: {digest}")
    source = raw.decode("utf-8")
    roughness_count = source.count(OLD_ROUGHNESS_TOKEN)
    measurement_count = source.count(OLD_MEASUREMENT_TOKEN)
    if roughness_count != 1:
        raise RuntimeError(f"Expected one roughness repeat, found {roughness_count}")
    if measurement_count != 1:
        raise RuntimeError(f"Expected one render measurement block, found {measurement_count}")
    corrected = source.replace(OLD_ROUGHNESS_TOKEN, NEW_ROUGHNESS_TOKEN, 1)
    corrected = corrected.replace(OLD_MEASUREMENT_TOKEN, NEW_MEASUREMENT_TOKEN, 1)
    if OLD_ROUGHNESS_TOKEN in corrected or OLD_MEASUREMENT_TOKEN in corrected:
        raise RuntimeError("One or more bounded Recovery02 tokens remain")
    if corrected.count(NEW_ROUGHNESS_TOKEN) != 1:
        raise RuntimeError("Recovery02 roughness assertion cardinality is not one")
    if corrected.count(NEW_MEASUREMENT_TOKEN) != 1:
        raise RuntimeError("Recovery02 measurement block cardinality is not one")
    receipt = {
        "schema": "skyguard.m01-visible-environment-kit-refinement01-stagea-recovery02.in-memory-patch.v1",
        "gate": GATE,
        "base_source": str(BASE_SOURCE),
        "base_bytes": BASE_BYTES,
        "base_sha256": BASE_SHA256,
        "roughness_token_count": roughness_count,
        "measurement_token_count": measurement_count,
        "behavioral_changes": [
            "preserve Recovery01 roughness allocation correction",
            "measure the freshly written PNG through a temporary Blender image datablock",
            "fail closed on missing image, zero dimensions, or empty pixel and luminance buffers",
            "remove the temporary measurement datablock in finally",
        ],
        "geometry_material_camera_render_export_receipt_changes": 0,
        "passed": True,
    }
    return corrected, receipt


def main() -> int:
    corrected, receipt = load_bounded_source()
    print(json.dumps(receipt, sort_keys=True))
    namespace: dict[str, object] = {
        "__name__": "skyguard_stagea_recovery02_embedded",
        "__file__": str(Path(__file__).resolve()),
        "__package__": None,
    }
    exec(compile(corrected, str(Path(__file__).resolve()), "exec"), namespace)
    embedded_main = namespace.get("main")
    if not callable(embedded_main):
        raise RuntimeError("Frozen StageA main() was not recovered")
    return int(embedded_main())


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(
            json.dumps(
                {
                    "gate": GATE,
                    "status": "FAILED_WITH_EVIDENCE",
                    "error": f"{type(exc).__name__}: {exc}",
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        raise
