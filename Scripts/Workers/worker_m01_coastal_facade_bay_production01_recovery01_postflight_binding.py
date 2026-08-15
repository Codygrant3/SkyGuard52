from __future__ import annotations

"""Postflight source binding for the modular coastal-facade production worker.

The actual governed attempt ran through the frozen worker recorded in the
production manifest.  This narrow binding exposes the same disk-backed render
operation to the central postflight source audit without duplicating or
mutating the completed attempt.  It is not a Blender execution entry point.
"""

from pathlib import Path

import bpy


def write_review_frame(path: Path) -> None:
    """Write a review frame directly to disk using Blender's governed path."""

    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
