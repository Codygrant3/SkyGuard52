import hashlib
from pathlib import Path


ORIGINAL = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_presentation_refinement01\author_m01_visible_environment_kit_presentation_refinement01.py"
)
EXPECTED_ORIGINAL_SHA256 = "2899658124ce2dbf66d6ac15551b6213745184df02958e835e5bc208d3785d7c"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if sha256(ORIGINAL) != EXPECTED_ORIGINAL_SHA256:
    raise RuntimeError("Frozen PresentationRefinement01 author hash mismatch")

source = ORIGINAL.read_text(encoding="utf-8")
replacements = (
    ("lower_hemisphere_is_solid_color", "lower_hemisphere_is_black", 3),
    ("PresentationRefinement01", "PresentationRefinement01_Recovery01", 5),
    ("PRESENTATION_REFINEMENT01", "PRESENTATION_REFINEMENT01_RECOVERY01", 3),
    ("presentation-refinement01", "presentation-refinement01-recovery01", 1),
)
for old, new, expected_count in replacements:
    actual_count = source.count(old)
    if actual_count != expected_count:
        raise RuntimeError(
            f"Recovery01 binding count changed for {old}: {actual_count} != {expected_count}"
        )
    source = source.replace(old, new)

if "Lvl_M01_VisibleEnvironmentKit02_PresentationRefinement01.umap" in source:
    raise RuntimeError("Recovery01 retains the failed output-map namespace")
if "M01_VISIBLE_ENVIRONMENT_PRESENTATION_REFINEMENT01/attempt_01" in source:
    raise RuntimeError("Recovery01 retains the failed attempt namespace")
if "lower_hemisphere_is_solid_color" in source:
    raise RuntimeError("Recovery01 retains the incompatible UE 5.8 skylight property")

exec(compile(source, str(ORIGINAL) + "::Recovery01", "exec"), globals(), globals())
