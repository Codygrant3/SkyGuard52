"""Build an immutable provenance receipt for every local Poly Haven texture.

This performs metadata-only HEAD requests against the canonical Poly Haven
download host. It never replaces local art. A record is accepted only when the
official URL responds successfully and its declared byte length matches the
hashed local file.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(r"D:\Skyguard52")
POLY_ROOT = ROOT / "Content" / "Skyguard" / "Textures" / "PolyHaven"
LEGACY_MANIFEST = POLY_ROOT / "surface-build-manifest.json"
OUTPUT = POLY_ROOT / "polyhaven-provenance-manifest.json"
BASE_URL = "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_url(family: str, filename: str, known: dict[tuple[str, str], str]) -> str:
    if (family, filename) in known:
        return known[(family, filename)]
    return f"{BASE_URL}/{family}/{filename}"


def head_receipt(url: str) -> tuple[int | None, int | None, str | None]:
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            length = response.headers.get("Content-Length")
            return response.status, int(length) if length else None, response.headers.get("ETag")
    except Exception as error:  # receipt records the limitation; it never guesses
        return None, None, f"{type(error).__name__}: {error}"


def main() -> int:
    legacy = json.loads(LEGACY_MANIFEST.read_text(encoding="utf-8"))
    known: dict[tuple[str, str], str] = {}
    for source in legacy.get("sources", []):
        known[(source["asset"], Path(source["cached_path"]).name)] = source["source_url"]

    records = []
    for family_dir in sorted(path for path in POLY_ROOT.iterdir() if path.is_dir()):
        for path in sorted(file for file in family_dir.iterdir() if file.is_file()):
            url = canonical_url(family_dir.name, path.name, known)
            status, remote_bytes, etag_or_error = head_receipt(url)
            local_bytes = path.stat().st_size
            verified = status == 200 and remote_bytes == local_bytes
            records.append(
                {
                    "family": family_dir.name,
                    "file": path.name,
                    "path": str(path),
                    "source_url": url,
                    "source": "Poly Haven",
                    "license": "CC0-1.0",
                    "license_url": "https://polyhaven.com/license",
                    "local_bytes": local_bytes,
                    "local_sha256": sha256_file(path),
                    "head_status": status,
                    "remote_content_length": remote_bytes,
                    "remote_etag_or_error": etag_or_error,
                    "canonical_url_and_length_verified": verified,
                }
            )

    failed = [record for record in records if not record["canonical_url_and_length_verified"]]
    receipt = {
        "schema": "skyguard.polyhaven-provenance-manifest.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Poly Haven",
        "source_url": "https://polyhaven.com/",
        "license": "CC0-1.0",
        "license_url": "https://polyhaven.com/license",
        "record_count": len(records),
        "verified_record_count": len(records) - len(failed),
        "failed_records": [
            {"family": item["family"], "file": item["file"]} for item in failed
        ],
        "records": records,
        "gate": "PASS" if records and not failed else "FAIL",
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "gate": receipt["gate"], "records": len(records)}))
    return 0 if receipt["gate"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
