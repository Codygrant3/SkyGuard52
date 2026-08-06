# Phase 2 Slice 01 Recovery04 readiness

Status: `PASS_RECOVERY04_READY_NOT_RUN`.

Recovery03 is terminal and hash-bound. Recovery04 preserves all prior bytes and applies three proven Blender 5.2 migrations in a distinct source, output, and attempt namespace:

- `CROSS` → `PLAIN_AXES`;
- `BLENDER_EEVEE_NEXT` → `BLENDER_EEVEE`;
- if factory startup leaves `scene.world` unset, create `WORLD_R4S01_Recovery04` and assign it before frozen render configuration.

The new launch wrapper writes checksum entries through a typed string list and `WriteAllLines`, guaranteeing one digest and filename per line. No Blender, Unreal, build, output, import, or promotion occurred.
