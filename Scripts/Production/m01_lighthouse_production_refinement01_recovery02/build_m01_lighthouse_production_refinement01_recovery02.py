"""Recovery02 pure-PNG luminance wrapper for the frozen lighthouse builder."""

from __future__ import annotations

import importlib.util
import struct
import sys
import zlib
from pathlib import Path

try:
    import bpy
except ModuleNotFoundError:  # Pure PNG fixture tests run outside Blender.
    bpy = None


FROZEN_BUILDER = Path(
    r"D:\Skyguard52\Scripts\Production\m01_lighthouse_production_refinement01\build_m01_lighthouse_production_refinement01.py"
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def load_frozen_builder():
    specification = importlib.util.spec_from_file_location("skyguard_m01_lighthouse_refinement01_frozen", FROZEN_BUILDER)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Unable to load frozen builder: {FROZEN_BUILDER}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def paeth(left: int, up: int, upper_left: int) -> int:
    prediction = left + up - upper_left
    distance_left = abs(prediction - left)
    distance_up = abs(prediction - up)
    distance_upper_left = abs(prediction - upper_left)
    if distance_left <= distance_up and distance_left <= distance_upper_left:
        return left
    if distance_up <= distance_upper_left:
        return up
    return upper_left


def decode_png_rgba8(path: Path) -> tuple[int, int, bytes]:
    payload = path.read_bytes()
    if payload[:8] != PNG_SIGNATURE:
        raise RuntimeError(f"Invalid PNG signature: {path}")
    offset = 8
    width = height = bit_depth = color_type = interlace = None
    compressed = bytearray()
    while offset < len(payload):
        if offset + 12 > len(payload):
            raise RuntimeError(f"Truncated PNG chunk: {path}")
        length = struct.unpack(">I", payload[offset : offset + 4])[0]
        chunk_type = payload[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        if data_end + 4 > len(payload):
            raise RuntimeError(f"Truncated PNG payload: {path}")
        chunk = payload[data_start:data_end]
        expected_crc = struct.unpack(">I", payload[data_end : data_end + 4])[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(chunk, actual_crc) & 0xFFFFFFFF
        if expected_crc != actual_crc:
            raise RuntimeError(f"PNG CRC mismatch for {chunk_type!r}: {path}")
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", chunk)
            if (bit_depth, color_type, compression, filtering, interlace) != (8, 6, 0, 0, 0):
                raise RuntimeError(
                    f"Unsupported PNG format: bit_depth={bit_depth}, color_type={color_type}, "
                    f"compression={compression}, filtering={filtering}, interlace={interlace}"
                )
        elif chunk_type == b"IDAT":
            compressed.extend(chunk)
        elif chunk_type == b"IEND":
            break
        offset = data_end + 4
    if width is None or height is None or not compressed:
        raise RuntimeError(f"PNG missing IHDR or IDAT: {path}")
    raw = zlib.decompress(bytes(compressed))
    bytes_per_pixel = 4
    row_bytes = width * bytes_per_pixel
    expected = height * (row_bytes + 1)
    if len(raw) != expected:
        raise RuntimeError(f"Unexpected PNG scanline bytes: {len(raw)} != {expected}")
    pixels = bytearray(width * height * bytes_per_pixel)
    previous = bytearray(row_bytes)
    source_offset = 0
    target_offset = 0
    for _ in range(height):
        filter_type = raw[source_offset]
        source_offset += 1
        scanline = bytearray(raw[source_offset : source_offset + row_bytes])
        source_offset += row_bytes
        reconstructed = bytearray(row_bytes)
        for index, value in enumerate(scanline):
            left = reconstructed[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            up = previous[index]
            upper_left = previous[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            if filter_type == 0:
                result = value
            elif filter_type == 1:
                result = value + left
            elif filter_type == 2:
                result = value + up
            elif filter_type == 3:
                result = value + ((left + up) // 2)
            elif filter_type == 4:
                result = value + paeth(left, up, upper_left)
            else:
                raise RuntimeError(f"Unsupported PNG filter {filter_type}: {path}")
            reconstructed[index] = result & 0xFF
        pixels[target_offset : target_offset + row_bytes] = reconstructed
        target_offset += row_bytes
        previous = reconstructed
    return width, height, bytes(pixels)


def png_mean_luminance(path: Path) -> float:
    width, height, pixels = decode_png_rgba8(path)
    count = width * height
    stride = max(count // 16384, 1)
    total = 0.0
    samples = 0
    for index in range(0, count, stride):
        offset = index * 4
        red, green, blue = pixels[offset], pixels[offset + 1], pixels[offset + 2]
        total += (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255.0
        samples += 1
    return total / samples


def main() -> int:
    if bpy is None:
        raise RuntimeError("Blender Python API unavailable in production mode")
    frozen = load_frozen_builder()

    def render_view(output: Path, filename: str, location, target, lens: float, mode: str, materials):
        frozen.stage(mode, materials)
        scene = bpy.context.scene
        scene.camera = frozen.review_camera(location, target, lens)
        path = output / filename
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        luminance = png_mean_luminance(path)
        if luminance < 0.08:
            scene.view_settings.exposure += 1.25
            bpy.ops.render.render(write_still=True)
            luminance = png_mean_luminance(path)
        elif luminance > 0.72:
            scene.view_settings.exposure -= 0.85
            bpy.ops.render.render(write_still=True)
            luminance = png_mean_luminance(path)
        frozen.require(path.is_file(), f"Render missing: {path}")
        width, height = frozen.png_dimensions(path)
        frozen.require((width, height) == (2048, 1152), f"Wrong render dimensions: {path} {width}x{height}")
        return {
            **frozen.record(path),
            "mode": mode,
            "mean_luminance": luminance,
            "width": width,
            "height": height,
            "luminance_source": "standard_library_png_decoder",
        }

    frozen.render_view = render_view
    return int(frozen.main())


if __name__ == "__main__":
    raise SystemExit(main())
