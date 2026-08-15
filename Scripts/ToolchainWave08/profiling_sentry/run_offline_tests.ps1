[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = (Resolve-Path (Join-Path $Root '..\..\..')).Path

$scripts = Get-ChildItem -LiteralPath $Root -Filter '*.py' -File
foreach ($script in $scripts) {
    & python -m py_compile $script.FullName
    if ($LASTEXITCODE -ne 0) { throw "Python syntax failed: $($script.FullName)" }
}

$jsonFiles = @(
    (Join-Path $ProjectRoot 'Production\Templates\PBR\skyguard_pbr_export_template_v1.json'),
    (Join-Path $ProjectRoot 'Production\Templates\PBR\skyguard_pbr_manifest_v1.schema.json'),
    (Join-Path $ProjectRoot 'Production\Templates\PBR\example_pbr_manifest.json'),
    (Join-Path $Root 'skyguard_profiling_receipt_v1.schema.json'),
    (Join-Path $Root 'profiling_profile_v1.json'),
    (Join-Path $Root 'sentry_readiness_v1.schema.json'),
    (Join-Path $Root 'sentry_readiness.json')
)
foreach ($path in $jsonFiles) {
    $null = Get-Content -LiteralPath $path -Raw | ConvertFrom-Json
}

& python (Join-Path $Root 'test_toolchain_wave08.py')
if ($LASTEXITCODE -ne 0) { throw 'Wave 08 unit tests failed.' }

& python (Join-Path $Root 'validate_pbr_manifest.py') --manifest (Join-Path $ProjectRoot 'Production\Templates\PBR\example_pbr_manifest.json')
if ($LASTEXITCODE -ne 0) { throw 'PBR example validation failed.' }

& python (Join-Path $Root 'validate_sentry_readiness.py') --readiness (Join-Path $Root 'sentry_readiness.json')
if ($LASTEXITCODE -ne 0) { throw 'Sentry readiness validation failed.' }

Write-Output 'PASSED_TOOLCHAIN_WAVE08_OFFLINE_TESTS'
