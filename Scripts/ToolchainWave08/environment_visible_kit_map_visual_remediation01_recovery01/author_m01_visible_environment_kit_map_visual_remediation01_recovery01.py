import hashlib
from pathlib import Path


ORIGINAL = Path(
    r"D:\Skyguard52\Scripts\ToolchainWave08\environment_visible_kit_map_visual_remediation01\author_m01_visible_environment_kit_map_visual_remediation01.py"
)
EXPECTED_ORIGINAL_SHA256 = "517044b54109fd951b4135594f47cc514047fd60e43254435c1e30913cbce0d2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if sha256(ORIGINAL) != EXPECTED_ORIGINAL_SHA256:
    raise RuntimeError("Frozen VisualRemediation01 author hash mismatch")

source = ORIGINAL.read_text(encoding="utf-8")
replacements = (
    ("lower_hemisphere_is_solid_color", "lower_hemisphere_is_black", 4),
    ("VisualRemediation01", "VisualRemediation01_Recovery01", 5),
    ("VISUAL_REMEDIATION01", "VISUAL_REMEDIATION01_RECOVERY01", 3),
    ("visual-remediation01.authoring.v1", "visual-remediation01-recovery01.authoring.v1", 1),
)
for old, new, expected_count in replacements:
    actual_count = source.count(old)
    if actual_count != expected_count:
        raise RuntimeError(
            f"Recovery01 binding count changed for {old}: {actual_count} != {expected_count}"
        )
    source = source.replace(old, new)

if "Lvl_M01_VisibleEnvironmentKit02_VisualRemediation01.umap" in source:
    raise RuntimeError("Recovery01 retains the failed output-map namespace")
if "M01_VISIBLE_ENVIRONMENT_KIT_MAP_VISUAL_REMEDIATION01/attempt_01" in source:
    raise RuntimeError("Recovery01 retains the failed attempt namespace")

exec(compile(source, str(ORIGINAL) + "::Recovery01", "exec"), globals(), globals())
