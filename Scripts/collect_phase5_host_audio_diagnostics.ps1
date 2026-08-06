[CmdletBinding()]
param(
    [int]$LookbackHours = 24,
    [string]$ReportPath
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not $ReportPath) {
    $ReportPath = Join-Path $ProjectRoot "Saved\Reports\PHASE5_HOST_AUDIO_DIAGNOSTIC.json"
}

$StartedAt = [DateTime]::UtcNow
$Since = (Get-Date).AddHours(-1 * [Math]::Max(1, $LookbackHours))
$QueryErrors = @()
$ApplicationErrors = @()
try {
    $ApplicationErrors = @(
        Get-WinEvent -FilterHashtable @{
            LogName = "Application"
            Level = 2
            StartTime = $Since
        } -ErrorAction Stop
    )
}
catch {
    $QueryErrors += $_.Exception.Message
}

function Convert-FaultEvidence {
    param([System.Diagnostics.Eventing.Reader.EventRecord]$Event)

    $Message = ""
    try {
        $Message = [string]$Event.FormatDescription()
    }
    catch {
        $Message = [string]$Event.Message
    }
    [ordered]@{
        time_created_utc = if ($Event.TimeCreated) {
            $Event.TimeCreated.ToUniversalTime().ToString("o")
        } else {
            $null
        }
        provider = $Event.ProviderName
        event_id = $Event.Id
        record_id = $Event.RecordId
        message_excerpt = $Message.Substring(
            0,
            [Math]::Min(900, $Message.Length)
        )
    }
}

$NahimicFaults = @(
    $ApplicationErrors |
        Where-Object {
            $Message = ""
            try {
                $Message = [string]$_.FormatDescription()
            }
            catch {
                $Message = [string]$_.Message
            }
            $Message -match "(?i)NahimicSvc32\.exe|DeviceRoutingDaemonModule\.dll"
        } |
        ForEach-Object { Convert-FaultEvidence -Event $_ }
)
$SkyguardFaults = @(
    $ApplicationErrors |
        Where-Object {
            $Message = ""
            try {
                $Message = [string]$_.FormatDescription()
            }
            catch {
                $Message = [string]$_.Message
            }
            $Message -match "(?i)Skyguard52"
        } |
        ForEach-Object { Convert-FaultEvidence -Event $_ }
)

$NahimicProcesses = @(
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object { $_.ProcessName -match "(?i)Nahimic|A-Volute" } |
        ForEach-Object {
            $Path = $null
            $Version = $null
            try {
                $Path = $_.Path
                if ($Path) {
                    $Version = (Get-Item -LiteralPath $Path).VersionInfo.FileVersion
                }
            }
            catch {
                # Protected service processes can deny Path access. That is
                # diagnostic unavailability, not evidence of absence.
            }
            [ordered]@{
                process_name = $_.ProcessName
                pid = $_.Id
                path = $Path
                file_version = $Version
            }
        }
)

$Status = if ($QueryErrors.Count -gt 0) {
    "PARTIAL_EVENT_LOG_QUERY"
}
elseif ($NahimicFaults.Count -gt 0 -and $SkyguardFaults.Count -gt 0) {
    "HOST_MIDDLEWARE_AND_SKYGUARD_FAULTS_DETECTED"
}
elseif ($NahimicFaults.Count -gt 0) {
    "HOST_AUDIO_MIDDLEWARE_FAULTS_DETECTED"
}
elseif ($SkyguardFaults.Count -gt 0) {
    "SKYGUARD_FAULTS_DETECTED"
}
else {
    "NO_RELEVANT_APPLICATION_ERRORS_IN_WINDOW"
}

$Receipt = [ordered]@{
    schema = "skyguard.phase5.host-audio-diagnostic.v1"
    status = $Status
    started_at_utc = $StartedAt.ToString("o")
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
    lookback_hours = [Math]::Max(1, $LookbackHours)
    read_only = $true
    unreal_process_launched = $false
    service_state_modified = $false
    query_errors = $QueryErrors
    nahimic_fault_count = $NahimicFaults.Count
    skyguard_fault_count = $SkyguardFaults.Count
    nahimic_processes = $NahimicProcesses
    nahimic_faults = $NahimicFaults
    skyguard_faults = $SkyguardFaults
    attribution_boundary = @(
        "A Nahimic or DeviceRoutingDaemonModule fault is host middleware evidence, not proof of a Skyguard defect.",
        "A clean Windows event window is not proof that the packaged Skyguard mix is audible or accepted.",
        "Friend-facing acceptance still requires a fresh packaged audible soak on a stable host audio path."
    )
}

$Parent = Split-Path -Parent $ReportPath
New-Item -ItemType Directory -Path $Parent -Force | Out-Null
$Receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $ReportPath -Encoding utf8
$Receipt | ConvertTo-Json -Depth 8
exit 0
