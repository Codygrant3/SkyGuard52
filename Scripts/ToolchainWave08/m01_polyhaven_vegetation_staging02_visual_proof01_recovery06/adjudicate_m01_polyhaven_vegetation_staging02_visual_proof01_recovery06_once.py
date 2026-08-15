"""Bind the clean Stage02 adjudicator to fresh Recovery06 evidence paths."""
from __future__ import annotations
import hashlib
from pathlib import Path
SOURCE=Path(r"D:\Skyguard52\Scripts\ToolchainWave08\m01_polyhaven_vegetation_staging02_visual_proof01\adjudicate_m01_polyhaven_vegetation_staging02_visual_proof01_once.py")
EXPECTED_BYTES=2041
EXPECTED_SHA256="7437136494396f93c956bd7a2d729ba5470fc87dfebf767a0f64024c07593c33"
REPLACEMENTS=(("M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01","M01_POLYHAVEN_VEGETATION_STAGING02_VISUAL_PROOF01_RECOVERY06"),("M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01","M01-POLYHAVEN-VEGETATION-STAGING02-VISUAL-PROOF01-RECOVERY06"),("M01PolyHavenVegetationStaging02VisualProof01.csv","M01PolyHavenVegetationStaging02VisualProof01Recovery06.csv"),("m01_polyhaven_vegetation_staging02_visual_proof01","m01_polyhaven_vegetation_staging02_visual_proof01_recovery06"),("polyhaven-vegetation-staging02-visual-proof01","polyhaven-vegetation-staging02-visual-proof01-recovery06"))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def transform_source():
    if not SOURCE.is_file() or SOURCE.stat().st_size!=EXPECTED_BYTES or sha256(SOURCE)!=EXPECTED_SHA256:raise RuntimeError("Frozen Stage02 adjudicator binder changed")
    namespace={"__name__":"authority","__file__":str(SOURCE)}
    exec(compile(SOURCE.read_text(encoding="utf-8"),str(SOURCE),"exec"),namespace,namespace)
    source=namespace["transform_source"]()
    for old,new in REPLACEMENTS:
        if old not in source:raise RuntimeError(f"Recovery06 adjudicator token absent: {old}")
        source=source.replace(old,new)
    if "RECOVERY06_RECOVERY06" in source or "recovery06_recovery06" in source:raise RuntimeError("Duplicate Recovery06 adjudicator suffix")
    return source
if __name__=="__main__":exec(compile(transform_source(),str(SOURCE)+"::recovery06","exec"),globals(),globals())
