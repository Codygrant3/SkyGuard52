[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$secretPath = 'C:\Users\chris\.codex\codex-router\caller-secret'
$nodePath = 'C:\Program Files\nodejs\node.exe'
$codexPath = 'C:\Users\chris\AppData\Roaming\npm\node_modules\@openai\codex\bin\codex.js'
$projectRoot = 'D:\Skyguard52'

$secret = (Get-Content -LiteralPath $secretPath -Raw).Trim()
if ($secret.Length -lt 32) {
    throw 'The local router caller capability is missing or invalid.'
}

$baseUrl = "http://127.0.0.1:4102/_codex-router/$secret/v1"
$startInfo = [System.Diagnostics.ProcessStartInfo]::new()
$startInfo.FileName = $nodePath
$startInfo.WorkingDirectory = $projectRoot
$startInfo.UseShellExecute = $false
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true

$arguments = @(
    $codexPath,
    'exec',
    '--ephemeral',
    '--ignore-user-config',
    '--dangerously-bypass-approvals-and-sandbox',
    '--json',
    '-m', 'grok-oauth/grok-4.5',
    '-C', $projectRoot,
    '-c', 'model_provider="skyguard_router"',
    '-c', 'model_reasoning_effort="low"',
    '-c', 'model_providers.skyguard_router.name="Skyguard Router"',
    '-c', "model_providers.skyguard_router.base_url=`"$baseUrl`"",
    '-c', 'model_providers.skyguard_router.env_key="SKYGUARD_ROUTER_SECRET"',
    '-c', 'model_providers.skyguard_router.wire_api="responses"',
    'Respond with exactly ROUTER_OK and nothing else.'
)

foreach ($argument in $arguments) {
    [void]$startInfo.ArgumentList.Add($argument)
}

$startInfo.Environment['SKYGUARD_ROUTER_SECRET'] = $secret
[void]$startInfo.Environment.Remove('XAI_API_KEY')

$process = [System.Diagnostics.Process]::Start($startInfo)
$stdoutTask = $process.StandardOutput.ReadToEndAsync()
$stderrTask = $process.StandardError.ReadToEndAsync()
$process.WaitForExit()
$process.Refresh()

$stdout = $stdoutTask.Result.Replace($secret, '[REDACTED]')
$stderr = $stderrTask.Result.Replace($secret, '[REDACTED]')
$passed = $process.ExitCode -eq 0 -and $stdout -match 'ROUTER_OK'

[pscustomobject]@{
    classification = if ($passed) { 'PASSED_GROK_OAUTH_ROUTER_SMOKE' } else { 'FAILED_GROK_OAUTH_ROUTER_SMOKE' }
    exit_code = [int]$process.ExitCode
    exit_code_type = $process.ExitCode.GetType().FullName
    xai_api_key_removed_from_child = $true
    router_endpoint = 'authenticated caller-capability route on 127.0.0.1:4102'
    output_contains_router_ok = [bool]($stdout -match 'ROUTER_OK')
    stderr_summary = @($stderr -split "`r?`n" | Where-Object { $_ -match 'ERROR|WARN|401|400|failed' } | Select-Object -Last 8)
} | ConvertTo-Json -Depth 4

if (-not $passed) {
    exit 1
}

exit 0
