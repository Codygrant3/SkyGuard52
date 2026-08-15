"""Bind the clean Stage02 proof executor to fresh Recovery06 evidence paths."""
from __future__ import annotations
import hashlib
from pathlib import Path
SOURCE=Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\capture_m01_polyhaven_vegetation_staging02_visual_proof01.py")
EXPECTED_BYTES=6895
EXPECTED_SHA256="0b2f184a3937bf87c56127957bd36101ae633e3ab3f252beb916291bd6851f96"
REPLACEMENTS=(("M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01","M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY06"),("M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01","M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY06"),("M01PolyHavenVegetationStaging02VisualProof01.csv","M01PolyHavenVegetationStaging02VisualProof01Recovery06.csv"))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def transform_source():
    if not SOURCE.is_file() or SOURCE.stat().st_size!=EXPECTED_BYTES or sha256(SOURCE)!=EXPECTED_SHA256:raise RuntimeError("Frozen Stage02 executor binder changed")
    namespace={"__name__":"authority","__file__":str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"),str(SOURCE),"exec"),namespace,namespace)
    source=namespace["transform_source"]()
    for old,new in REPLACEMENTS:
        if old not in source:raise RuntimeError(f"Recovery06 executor token absent: {old}")
        source=source.replace(old,new)
    if "RECOVERY06_RECOVERY06" in source:raise RuntimeError("Duplicate Recovery06 executor suffix")
    return source
if __name__=="__main__":exec(compile(transform_source(),str(SOURCE)+"::recovery06","exec"),globals(),globals())
