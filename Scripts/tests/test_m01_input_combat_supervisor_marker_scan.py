from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "run_skyguard_m01_input_combat_performance_gate.ps1"
)
MARKER = "skyguard.m01.input-combat.runtime-receipt.v1"
BUFFER_BYTES = 1_048_576


def ps_literal(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


class M01InputCombatSupervisorMarkerScanTests(unittest.TestCase):
    def test_supervisor_uses_bounded_streaming_scan(self) -> None:
        source = SCRIPT_PATH.read_text(encoding="utf-8-sig")

        self.assertNotIn("ReadAllBytes", source)
        self.assertNotIn("GetString($bytes)", source)
        self.assertIn("[System.IO.File]::Open(", source)
        self.assertIn("$stream.Read($buffer, $carryBytes, $bufferBytes)", source)
        self.assertIn("$bufferBytes = 1048576", source)
        self.assertIn("$overlapBytes", source)

    def test_streaming_scan_detects_ascii_utf16_and_chunk_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            marker_ascii = MARKER.encode("ascii")
            marker_utf16 = MARKER.encode("utf-16-le")
            fixtures = {
                "ascii": b"prefix-" + marker_ascii + b"-suffix",
                "utf16": b"prefix--" + marker_utf16 + b"-suffix",
                "ascii_boundary": (
                    b"A" * (BUFFER_BYTES - 7) + marker_ascii + b"-suffix"
                ),
                "utf16_boundary": (
                    b"A" * (BUFFER_BYTES - 8) + marker_utf16 + b"-suffix"
                ),
                "utf16_misaligned": b"A" + marker_utf16 + b"-suffix",
                "missing": b"A" * (BUFFER_BYTES * 2 + 113),
            }
            paths: dict[str, Path] = {}
            for name, payload in fixtures.items():
                path = root / f"{name}.bin"
                path.write_bytes(payload)
                paths[name] = path

            test_calls = "\n".join(
                f"    {name} = Test-PackagedRuntimeHook -LiteralPath "
                f"{ps_literal(path)}"
                for name, path in paths.items()
            )
            command = f"""
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
    {ps_literal(SCRIPT_PATH)},
    [ref]$tokens,
    [ref]$parseErrors
)
if ($parseErrors.Count -ne 0) {{
    throw ($parseErrors | ForEach-Object Message | Out-String)
}}
$wanted = @('Test-PackagedRuntimeHook')
$definitions = $ast.FindAll(
    {{
        param($node)
        $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $wanted -contains $node.Name
    }},
    $true
)
foreach ($definition in $definitions) {{
    Invoke-Expression $definition.Extent.Text
}}
$results = [ordered]@{{
{test_calls}
}}
$results | ConvertTo-Json -Compress
"""
            completed = subprocess.run(
                [
                    "powershell.exe",
                    "-NoLogo",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    command,
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            self.assertEqual(
                0,
                completed.returncode,
                msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
            )
            results = json.loads(completed.stdout.strip())
            self.assertTrue(results["ascii"])
            self.assertTrue(results["utf16"])
            self.assertTrue(results["ascii_boundary"])
            self.assertTrue(results["utf16_boundary"])
            self.assertFalse(results["utf16_misaligned"])
            self.assertFalse(results["missing"])


if __name__ == "__main__":
    unittest.main()
