#!/usr/bin/env python3
"""Validate that the Sentry gate remains honest and contains no secret value."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECRET_PATTERNS = [re.compile(r"https://[^\s\"']+@[^\s\"']+/\d+"), re.compile(r"(?i)(auth[_-]?token|secret[_-]?key)\s*[:=]\s*[^\s,}]+")]


def validate(data: object, raw: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict): return ["root must be object"]
    if data.get("schema") != "skyguard.sentry-readiness.v1": errors.append("schema mismatch")
    if data.get("network_calls_performed") is not False: errors.append("offline gate must perform zero network calls")
    if data.get("secrets_persisted") is not False: errors.append("secrets_persisted must be false")
    for pattern in SECRET_PATTERNS:
        if pattern.search(raw): errors.append("possible secret or DSN persisted")
    plugin = data.get("plugin", {})
    package = data.get("package", {})
    credentials = data.get("credentials", {})
    privacy = data.get("privacy", {})
    prerequisites = bool(plugin.get("installed") and package.get("passing_clean_machine_package_available") and credentials.get("dsn_available_at_execution") and privacy.get("crash_data_policy_approved") and privacy.get("pii_scrubbing_defined") and privacy.get("user_consent_defined"))
    if not prerequisites and data.get("classification") != "BLOCKED_PREREQUISITES": errors.append("classification must remain blocked while a prerequisite is false")
    if prerequisites and data.get("classification") == "BLOCKED_PREREQUISITES": errors.append("completed prerequisites require a new explicit gate classification")
    if not isinstance(data.get("required_next_gate"), list) or not data["required_next_gate"]: errors.append("required_next_gate must be nonempty")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--readiness", required=True); args = parser.parse_args()
    try:
        raw = Path(args.readiness).read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception as exc:
        print(json.dumps({"result": "FAIL", "errors": [str(exc)]}, indent=2)); return 2
    errors = validate(data, raw)
    print(json.dumps({"result": "PASS" if not errors else "FAIL", "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__": sys.exit(main())

