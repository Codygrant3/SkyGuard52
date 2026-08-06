# Recovery04 Representative Visual Proof — Full-Resolution Inspection

Automatic verification does not establish visual acceptance. A reviewer must inspect all eight original 2560×1440 PNGs at full resolution.

## Required frames

- `C01_REAR_GUNNER_PORT`
- `C02_REAR_GUNNER_STARBOARD`
- `C03_SHORELINE_APPROACH`
- `C04_ROUTE_EXTERIOR`
- `C05_CITY_INLAND`
- `T01_ROUTE_ENTRY`
- `T02_ROUTE_MID`
- `T03_ROUTE_EXIT`

## Reject the proof if any frame shows

- diagnostic color blocks;
- floating or disconnected geometry;
- buildings without grounded terrain;
- visible tiling or repeating placeholder structures;
- overexposure or crushed shadows;
- missing water and shore contact;
- obvious low-poly hero silhouettes;
- unstable clouds, water, foliage, or world geometry;
- camera clipping;
- world-fixed elements moving with the camera;
- unacceptable traversal hitching in the temporal sequence.

## Required feature presence

- `C01_REAR_GUNNER_PORT`: coast, beach, terrain, city, vegetation.
- `C02_REAR_GUNNER_STARBOARD`: ocean, shore contact, atmosphere.
- `C03_SHORELINE_APPROACH`: waterline, beach, terrain transition, skyline.
- `C04_ROUTE_EXTERIOR`: route silhouette, city massing, vegetation distribution.
- `C05_CITY_INLAND`: grounded buildings, roads, urban infrastructure, terrain.

## Decision

Record each camera as `PASS` or `FAIL_WITH_EVIDENCE`. No average score may conceal a failed camera. Visual acceptance requires all eight frames, all required features, and no rejection condition.
