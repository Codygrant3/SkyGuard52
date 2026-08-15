import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_realism_stack_authoring01_recovery01\author_environment_realism_stack01_recovery01.py")
EXPECTED_SOURCE_BYTES = 25592
EXPECTED_SOURCE_SHA256 = "11a9853988228015ae295baf8335facb8481f8dd3a70393d301af4454556b605"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if not SOURCE.is_file():
    raise RuntimeError(f"Frozen Recovery01 source is missing: {SOURCE}")
if SOURCE.stat().st_size != EXPECTED_SOURCE_BYTES:
    raise RuntimeError("Frozen Recovery01 source byte count changed")
if sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
    raise RuntimeError("Frozen Recovery01 source hash changed")

original = SOURCE.read_text(encoding="utf-8")
if original.count("_RECOVERY01") != 3:
    raise RuntimeError("Unexpected uppercase Recovery01 namespace occurrence count")
if original.count("Recovery01") != 9:
    raise RuntimeError("Unexpected Recovery01 namespace occurrence count")
if original.count('set_property(post, "b_unbound", True)') != 1:
    raise RuntimeError("Unexpected PostProcessVolume compatibility target count")

transformed = original.replace("_RECOVERY01", "_RECOVERY02")
transformed = transformed.replace("Recovery01", "Recovery02")
transformed = transformed.replace('set_property(post, "b_unbound", True)', 'set_property(post, "unbound", True)')

if "Recovery01" in transformed or "_RECOVERY01" in transformed or '"b_unbound"' in transformed:
    raise RuntimeError("Recovery02 transformation left a prohibited Recovery01 token")
if transformed.count('set_property(post, "unbound", True)') != 1:
    raise RuntimeError("Recovery02 transformation did not produce exactly one verified unbound property write")

exec(compile(transformed, str(SOURCE), "exec"), globals(), globals())
