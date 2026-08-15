# Skyguard 52

Unreal Engine 5.8 and Blender 5.2 AAA production project.

Canonical project root:

`D:\Skyguard52`

Current state:

- ten-mission gameplay engineering and boss architecture exists;
- 39 of 39 accepted mission integration tests passed;
- a packaged engineering baseline exists;
- Recovery05 plugin build and runtime binding are accepted;
- production art is behind engineering;
- no production hero-asset set or production campaign map is fully accepted;
- the project is not yet a release candidate.

Start here:

- `Production\production_manifest.json` — canonical asset queue and status;
- `Production\README.md` — production-controller commands;
- `Docs\AAA_Review\SKYGUARD52_FULL_PRODUCTION_AUDIT_2026-08-06.md` — current
  audit and remediation plan;
- `AGENTS.md` — mandatory project boundaries.

Validate the control plane:

```powershell
python .\Scripts\skyguard_production.py audit
python .\Scripts\skyguard_production.py preflight
python .\Scripts\validate_skyguard_production.py
```

The old Three.js prototype is retired and is not a project authority.
