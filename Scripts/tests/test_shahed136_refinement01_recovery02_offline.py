from __future__ import annotations

import ast
import unittest

from Scripts.Workers import worker_core_shahed136_refinement01_recovery02 as subject


class ShahedRecovery02CompatibilityTests(unittest.TestCase):
    def test_frozen_source_receives_only_required_compatibility_bindings(self) -> None:
        source = subject.build_patched_source()
        ast.parse(source)
        self.assertNotIn("rig.animation_data.action.fcurves", source)
        self.assertNotIn(subject.LEGACY_LIGHT_ENERGY, source)
        self.assertEqual(source.count(subject.BLENDER52_LIGHT_ENERGY), 1)
        self.assertIn('scene.render.engine = "BLENDER_EEVEE"', source)

    def test_patched_namespace_exposes_main_without_importing_bpy(self) -> None:
        namespace = subject.load_patched_namespace()
        self.assertTrue(callable(namespace.get("main")))


if __name__ == "__main__":
    unittest.main()
