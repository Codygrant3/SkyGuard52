import hashlib
from pathlib import Path


SOURCE = Path(r"D:\Skyguard52\Scripts\ToolchainWave08\environment_authoring01_recovery07_mapped_visual_proof01_recovery04\capture_recovery07_mapped_visual_proof01_recovery04.py")
EXPECTED_SOURCE_BYTES = 32325
EXPECTED_SOURCE_SHA256 = "589198baa1cbe4c13b0ba79d7af8c71d422d5a5f825b23d1d6a6e8fcfbbb5cc1"
OLD_PREFIX = "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_MAPPED_VISUAL_PROOF01_RECOVERY04"
NEW_PREFIX = "M01_ENVIRONMENT_REALISM_STACK_VISUAL_PROOF01"
OLD_PREFIX_HEAD = "TOOLCHAIN_WAVE08_M01_ENVIRONMENT_AUTHORING01_RECOVERY07_"
OLD_PREFIX_TAIL = "MAPPED_VISUAL_PROOF01_RECOVERY04"
NEW_PREFIX_HEAD = "M01_ENVIRONMENT_REALISM_STACK_"
NEW_PREFIX_TAIL = "VISUAL_PROOF01"
OLD_CONTRACT_ID = "T08-M01-ENV-AUTH01-RECOVERY07-MAPPED-VISUAL-PROOF01-RECOVERY04"
NEW_CONTRACT_ID = "M01-ENVIRONMENT-REALISM-STACK-VISUAL-PROOF01"
OLD_MAP = "Lvl_M01_T08_EnvironmentAuthoring01_Recovery07"
NEW_MAP = "Lvl_M01_T08_EnvironmentRealismStack01_Recovery02"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def transform_source() -> str:
    if not SOURCE.is_file() or SOURCE.stat().st_size != EXPECTED_SOURCE_BYTES or sha256(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("Frozen Recovery04 mapped-proof executor authority changed")

    original = SOURCE.read_text(encoding="utf-8")
    required_fragments = (
        OLD_PREFIX_HEAD,
        OLD_PREFIX_TAIL,
        OLD_CONTRACT_ID,
        OLD_MAP,
        'governed = [actor for actor in actors if actor.get_actor_label() in expected_set]',
        'if label in expected_set:',
        'if actor.get_actor_label().startswith("M01_A01_")',
    )
    for fragment in required_fragments:
        if fragment not in original:
            raise RuntimeError(f"Frozen executor transformation target is missing: {fragment}")

    transformed = original.replace(OLD_PREFIX_HEAD, NEW_PREFIX_HEAD)
    transformed = transformed.replace(OLD_PREFIX_TAIL, NEW_PREFIX_TAIL)
    transformed = transformed.replace(OLD_CONTRACT_ID, NEW_CONTRACT_ID)
    transformed = transformed.replace(OLD_MAP, NEW_MAP)
    transformed = transformed.replace("Recovery07MappedVisualProof01Recovery04.csv", "M01EnvironmentRealismStackVisualProof01.csv")
    transformed = transformed.replace("recovery07_mapped_visual_proof01_recovery04", "m01_environment_realism_stack_visual_proof01")
    transformed = transformed.replace(
        'if actor.get_actor_label().startswith("M01_A01_")',
        'if actor.get_actor_label().startswith(("M01_A01_", "M01_RS01_"))',
    )
    transformed = transformed.replace(
        'governed = [actor for actor in actors if actor.get_actor_label() in expected_set]',
        'governed = [actor for actor in actors if actor.get_actor_label() in expected_set or any(actor.get_actor_label().startswith(prefix) for prefix in contract["world"]["expected_prefix_counts"])]',
    )
    transformed = transformed.replace(
        'if label in expected_set:',
        'if label in expected_set or any(label.startswith(prefix) for prefix in contract["world"]["expected_prefix_counts"]):',
    )
    transformed = transformed.replace(
        'is_governed = label.startswith("M01_A01_") or any(',
        'is_governed = label.startswith(("M01_A01_", "M01_RS01_")) or any(',
    )
    transformed = transformed.replace(
        'or tag.startswith("Skyguard.Environment.Mission01")',
        'or tag.startswith("Skyguard.Environment.Mission01")\n            or tag == "Skyguard.RealismStack01"\n            or tag.startswith("Skyguard.RealismStack01.")',
    )

    for stale in (OLD_PREFIX_HEAD, OLD_PREFIX_TAIL, OLD_CONTRACT_ID, OLD_MAP, "Recovery07MappedVisualProof01Recovery04.csv"):
        if stale in transformed:
            raise RuntimeError(f"Visual-proof transformation left stale token: {stale}")
    if transformed.count('startswith(("M01_A01_", "M01_RS01_"))') < 2:
        raise RuntimeError("Visual-proof transformation did not govern both actor namespaces")
    return transformed


if __name__ == "__main__":
    exec(compile(transform_source(), str(SOURCE), "exec"), globals(), globals())
