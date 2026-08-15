"""Bind the frozen Stage02 proof executor to fresh Recovery05 evidence paths."""
from __future__ import annotations
import hashlib
from pathlib import Path
SOURCE=Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\capture_m01_polyhaven_vegetation_staging02_visual_proof01.py");EXPECTED_BYTES=6_895;EXPECTED_SHA256="0b2f184a3937bf87c56127957bd36101ae633e3ab3f252beb916291bd6851f96";REPLACEMENTS=(("M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01","M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY05"),("M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01","M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY05"),("M01PolyHavenVegetationStaging02VisualProof01.csv","M01PolyHavenVegetationStaging02VisualProof01Recovery05.csv"))
def sha256(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def transform_source():
    if not SOURCE.is_file() or SOURCE.stat().st_size!=EXPECTED_BYTES or sha256(SOURCE)!=EXPECTED_SHA256:raise RuntimeError("Frozen Stage02 executor binder changed")
    n={"__name__":"authority","__file__":str(SOURCE)};exec(compile(SOURCE.read_text(encoding="utf-8"),str(SOURCE),"exec"),n,n);s=n["transform_source"]()
    for old,new in REPLACEMENTS:
        if old not in s:raise RuntimeError(f"Recovery05 executor token absent: {old}")
        s=s.replace(old,new)
    return s
if __name__=="__main__":exec(compile(transform_source(),str(SOURCE)+"::recovery05","exec"),globals(),globals())
