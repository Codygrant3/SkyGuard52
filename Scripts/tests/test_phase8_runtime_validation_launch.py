from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUPERVISOR = PROJECT_ROOT / "Scripts" / "run_skyguard_phase8_runtime_validation.ps1"
PSO_WORKFLOW = PROJECT_ROOT / "Scripts" / "run_skyguard_phase8_pso_workflow.ps1"
RELEASE_GATE = PROJECT_ROOT / "Scripts" / "run_skyguard_phase8_release_gate.ps1"


class Phase8RuntimeValidationLaunchTests(unittest.TestCase):
    def test_hidden_packaged_runtime_uses_offscreen_rendering(self) -> None:
        script = SUPERVISOR.read_text(encoding="utf-8")
        self.assertIn('"-RenderOffscreen", "-ResX=1280", "-ResY=720"', script)
        self.assertNotIn('"-windowed", "-ResX=1280", "-ResY=720"', script)
        self.assertIn("-WindowStyle Hidden", script)

    def test_runtime_validation_remains_d3d12_sm6(self) -> None:
        script = SUPERVISOR.read_text(encoding="utf-8")
        self.assertIn('"-d3d12", "-sm6", "-NoVSync"', script)

    def test_hidden_pso_capture_uses_offscreen_rendering(self) -> None:
        script = PSO_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn(
            '[string]$mission.map, "-RenderOffscreen", "-d3d12", "-sm6", "-logPSO"',
            script,
        )

    def test_hidden_mission_soaks_and_shipping_smoke_use_offscreen_rendering(
        self,
    ) -> None:
        script = RELEASE_GATE.read_text(encoding="utf-8")
        self.assertIn(
            '"-RenderOffscreen", "-ResX=1920", "-ResY=1080", "-d3d12", "-sm6"',
            script,
        )
        self.assertNotIn(
            '"-windowed", "-ResX=1920", "-ResY=1080", "-d3d12", "-sm6"',
            script,
        )
        self.assertGreaterEqual(script.count('"-RenderOffscreen"'), 2)


if __name__ == "__main__":
    unittest.main()
