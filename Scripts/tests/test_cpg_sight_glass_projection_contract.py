from __future__ import annotations

import math
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Source" / "Skyguard52"


def horizontal_fov_to_vertical(horizontal_fov_degrees: float, aspect: float) -> float:
    """VFov = 2 * atan( tan(HFov * 0.5) / Aspect ). Camera FOV is horizontal."""
    half = math.tan(math.radians(horizontal_fov_degrees * 0.5))
    return math.degrees(2.0 * math.atan(half / aspect))


def project_world_to_eye(
    world: tuple[float, float, float],
    bounds_radius: float,
    eye: tuple[float, float, float],
    fov_degrees: float,
    aspect: float,
) -> tuple[bool, float, float, float]:
    """Identity-eye subset of SkyguardCpgProjectWorldToEye (Unreal X-forward)."""
    local_x = world[0] - eye[0]
    local_y = world[1] - eye[1]
    local_z = world[2] - eye[2]
    if local_x <= 1e-4:
        return False, 0.0, 0.0, 0.0
    tan_half = math.tan(math.radians(fov_degrees * 0.5))
    depth = local_x * tan_half
    if depth <= 1e-4:
        return False, 0.0, 0.0, 0.0
    return True, local_y / (depth * aspect), local_z / depth, max(bounds_radius, 0.0) / depth


def ndc_to_absolute(
    ndc: tuple[float, float],
    abs_min: tuple[float, float],
    abs_max: tuple[float, float],
) -> tuple[float, float]:
    size_x = abs_max[0] - abs_min[0]
    size_y = abs_max[1] - abs_min[1]
    return (
        abs_min[0] + (ndc[0] * 0.5 + 0.5) * size_x,
        abs_min[1] + (0.5 - ndc[1] * 0.5) * size_y,
    )


def absolute_to_local(
    absolute: tuple[float, float],
    abs_min: tuple[float, float],
    local_size: tuple[float, float],
    abs_max: tuple[float, float],
) -> tuple[float, float]:
    size_x = abs_max[0] - abs_min[0]
    size_y = abs_max[1] - abs_min[1]
    return (
        (absolute[0] - abs_min[0]) / size_x * local_size[0],
        (absolute[1] - abs_min[1]) / size_y * local_size[1],
    )


def text(name: str) -> str:
    return (SOURCE / name).read_text(encoding="utf-8-sig")


class CpgSightGlassProjectionContractTests(unittest.TestCase):
    def test_hud_declares_bounds_radius_eye_projection_helpers(self) -> None:
        header = text("SkyguardCpgHud.h")
        for token in (
            "BoundsRadius",
            "FSkyguardCpgSightEyeProject",
            "FSkyguardCpgProjectedSightMark",
            "SkyguardCpgProjectWorldToEye",
            "SkyguardCpgHorizontalFovToVertical",
            "VerticalFovDegrees",
            "SkyguardCpgEyeNdcToAbsolute",
            "SkyguardCpgEyeRadiusToAbsolute",
            "SkyguardCpgAbsoluteToLocal",
            "EyeLocation",
            "EyeRotation",
            "EyeFovDegrees",
            "EyeAspectRatio",
            "SightMarks",
            "ContactMarks",
        ):
            self.assertIn(token, header)

    def test_native_paint_and_snapshot_call_the_helper(self) -> None:
        paint = text("SkyguardCpgSightHud.cpp")
        snapshot = text("SkyguardGunner.cpp")
        self.assertIn("SkyguardCpgProjectWorldToEye", paint)
        self.assertIn("SkyguardCpgHorizontalFovToVertical", paint)
        self.assertIn("SkyguardCpgEyeNdcToAbsolute", paint)
        self.assertIn("AbsoluteToLocal", paint)
        self.assertIn("SkyguardCpgProjectWorldToEye", snapshot)
        self.assertIn("SkyguardCpgHorizontalFovToVertical", snapshot)
        self.assertIn("BuildCpgHudSnapshot", snapshot)
        self.assertNotIn("ProjectWorldLocationToScreen", paint)
        self.assertRegex(
            snapshot,
            r"SkyguardCpgProjectWorldToEye\([\s\S]*?SkyguardCpgHorizontalFovToVertical\(\s*Snap\.EyeFovDegrees",
            "snapshot must convert camera HFOV before the vertical helper",
        )
        self.assertRegex(
            paint,
            r"SkyguardCpgProjectWorldToEye\([\s\S]*?SkyguardCpgHorizontalFovToVertical\(\s*Cached\.EyeFovDegrees",
            "NativePaint must convert camera HFOV before the vertical helper",
        )

    def test_native_tick_does_not_project_in_screen_space(self) -> None:
        hud = text("SkyguardCpgSightHud.cpp")
        tick = hud.split("int32 USkyguardCpgSightHud::NativePaint")[0]
        self.assertIn("BuildCpgHudSnapshot", tick)
        self.assertNotIn("ProjectWorldLocationToScreen", tick)
        paint = hud.split("int32 USkyguardCpgSightHud::NativePaint", 1)[1]
        self.assertIn("SkyguardCpgProjectWorldToEye", paint)
        self.assertIn("Cached.ContactMarks", paint)

    def test_gunner_exposes_cpg_eye_getters_used_by_snapshot(self) -> None:
        header = text("SkyguardGunner.h")
        impl = text("SkyguardGunner.cpp")
        for token in (
            "GetCpgEyeLocation",
            "GetCpgEyeRotation",
            "GetCpgEyeFovDegrees",
            "GetCpgEyeAspectRatio",
        ):
            self.assertIn(token, header)
            self.assertIn(token, impl)
        snapshot = impl.split("FSkyguardCpgHudSnapshot ASkyguardGunner::BuildCpgHudSnapshot")[1]
        snapshot = snapshot.split("void ASkyguardGunner::CollectCpgContactMarks")[0]
        self.assertIn("GetCpgEyeLocation()", snapshot)
        self.assertIn("SkyguardCpgProjectWorldToEye", snapshot)
        self.assertIn("SightMarks", snapshot)
        self.assertIn("BoundsRadius", snapshot)

    def test_collect_marks_fill_bounds_radius(self) -> None:
        impl = text("SkyguardGunner.cpp")
        collect = impl.split("void ASkyguardGunner::CollectCpgContactMarks")[1]
        collect = collect.split("void ASkyguardGunner::UpdateCpgHud")[0]
        self.assertIn("BoundsRadius", collect)
        self.assertRegex(collect, r"GetSimpleCollisionRadius|Bounds\.SphereRadius")

    def test_automation_covers_the_projection_helper(self) -> None:
        tests = text("SkyguardCpgHudTests.cpp")
        self.assertIn("FSkyguardCpgSightProjectsBoundsRadiusToGlassTest", tests)
        self.assertIn("FSkyguardCpgSightConvertsHorizontalFovAtWideAspectTest", tests)
        self.assertIn("SkyguardCpgProjectWorldToEye", tests)
        self.assertIn("SkyguardCpgHorizontalFovToVertical", tests)
        self.assertIn("SkyguardCpgAbsoluteToLocal", tests)
        self.assertIn("BoundsRadius", tests)
        self.assertIn("snapshot reuses the eye-projection helper", tests)
        self.assertIn("HFOV edge lands at NDC X = +1 after H to V conversion", tests)
        self.assertIn("RadiusNdc uses the vertical half-angle, not raw HFOV", tests)

    def test_helper_math_puts_bounds_radius_marks_on_the_glass(self) -> None:
        ahead = project_world_to_eye((1000.0, 0.0, 0.0), 100.0, (0.0, 0.0, 0.0), 90.0, 1.0)
        self.assertEqual(ahead, (True, 0.0, 0.0, 0.1))
        right = project_world_to_eye((1000.0, 200.0, 0.0), 50.0, (0.0, 0.0, 0.0), 90.0, 1.0)
        self.assertTrue(right[0])
        self.assertAlmostEqual(right[1], 0.2)
        self.assertAlmostEqual(right[2], 0.0)
        self.assertLess(right[3], ahead[3])
        behind = project_world_to_eye((-400.0, 0.0, 0.0), 80.0, (0.0, 0.0, 0.0), 90.0, 1.0)
        self.assertFalse(behind[0])
        center_abs = ndc_to_absolute((ahead[1], ahead[2]), (100.0, 50.0), (2020.0, 1130.0))
        self.assertAlmostEqual(center_abs[0], 1060.0)
        self.assertAlmostEqual(center_abs[1], 590.0)
        center_local = absolute_to_local(center_abs, (100.0, 50.0), (1920.0, 1080.0), (2020.0, 1130.0))
        self.assertAlmostEqual(center_local[0], 960.0)
        self.assertAlmostEqual(center_local[1], 540.0)
        abs_radius = abs(ahead[3]) * abs(1130.0 - 50.0)
        self.assertAlmostEqual(abs_radius, 108.0)

    def test_wide_aspect_converts_camera_hfov_before_vertical_projection(self) -> None:
        hfov = 90.0
        aspect = 16.0 / 9.0
        depth = 1000.0
        radius = 100.0
        tan_half_h = math.tan(math.radians(hfov * 0.5))
        vfov = horizontal_fov_to_vertical(hfov, aspect)
        tan_half_v = math.tan(math.radians(vfov * 0.5))
        self.assertLess(vfov, hfov)
        self.assertAlmostEqual(tan_half_v, tan_half_h / aspect)

        ahead = project_world_to_eye((depth, 0.0, 0.0), radius, (0.0, 0.0, 0.0), vfov, aspect)
        self.assertEqual(ahead[0], True)
        self.assertAlmostEqual(ahead[1], 0.0)
        self.assertAlmostEqual(ahead[2], 0.0)

        h_edge = project_world_to_eye(
            (depth, depth * tan_half_h, 0.0), radius, (0.0, 0.0, 0.0), vfov, aspect
        )
        self.assertAlmostEqual(h_edge[1], 1.0)

        old = project_world_to_eye(
            (depth, depth * tan_half_h, 0.0), radius, (0.0, 0.0, 0.0), hfov, aspect
        )
        self.assertNotAlmostEqual(old[1], 1.0)

        v_edge = project_world_to_eye(
            (depth, 0.0, depth * tan_half_v), radius, (0.0, 0.0, 0.0), vfov, aspect
        )
        self.assertAlmostEqual(v_edge[2], 1.0)
        self.assertAlmostEqual(ahead[3], radius / (depth * tan_half_v))
        self.assertNotAlmostEqual(ahead[3], radius / (depth * tan_half_h))

    def test_runtime_mesh_catalog_preferred_stays_empty(self) -> None:
        catalog = text("SkyguardRuntimeMeshCatalog.cpp")
        self.assertIn("Preferred stays empty", catalog)
        for slot in (
            "Gunner.Cockpit",
            "Apache.Airframe",
            "Gunner.Rifle",
            "Drone.Body",
        ):
            pattern = rf'TEXT\("{re.escape(slot)}"\),\s*TEXT\(""\)'
            self.assertRegex(catalog, pattern, f"{slot} Preferred must stay empty")
        self.assertNotIn(
            'TEXT("Gunner.Cockpit"),\n\t\t\tTEXT("/Game/',
            catalog,
        )


if __name__ == "__main__":
    unittest.main()
