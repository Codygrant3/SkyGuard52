from __future__ import annotations

"""Postflight render-source binding for the Recovery02 facade worker.

The governed worker delegates rendering to its frozen harness.  This inert
binding exposes the same disk-backed Blender render operation to the central
source audit without creating a second execution path.
"""

from pathlib import Path

import bpy


def write_review_frame(path: Path) -> None:
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
