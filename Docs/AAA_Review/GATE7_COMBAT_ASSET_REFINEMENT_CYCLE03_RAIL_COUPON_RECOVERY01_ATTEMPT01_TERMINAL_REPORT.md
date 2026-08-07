# Rail Coupon Recovery01 Attempt01 Terminal Report

Classification: `FAILED_WITH_EVIDENCE`

The single authorized Blender 5.2 execution launched once and was not retried. The frozen offline verifier had passed all thirteen authorities, both governed namespaces were absent, and the heavy-process count was zero before launch.

Blender terminated during the generated-coupon dimensional guard before rendering or export:

`RuntimeError: Rail coupon bounding dimensions failed authority validation`

The failure occurred at line 569 of the frozen execution source after `collection_bbox(collection)` and `validate_dimensions(bbox)`. Consequently, the attempt produced no governed `.blend`, GLB, dimension receipt, GLB-structure receipt, or review PNG. The output namespace contains only an empty `exports` directory.

The supervisor returned exit code `1` without writing its required terminal supervisor manifest. The preflight receipt, copied source and contract, stdout, and stderr remain preserved in the immutable failed attempt namespace.

No Unreal process ran. No automatic retry occurred. No Method 04 prompt was created because the measured rail dependency did not pass.

The next executable gate is a separately authorized offline-only recovery design addressing both the construction-versus-bounds mismatch and the missing terminal-manifest lifecycle. This failed namespace must never be reused.
