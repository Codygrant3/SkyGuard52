param(
    [switch]$AuthorizeSinglePrepare,
    [switch]$OfflineContractTest
)
. (Join-Path $PSScriptRoot 'common.ps1')
$contract = 'D:\Skyguard52\Docs\Toolchain\ToolchainWave08\character_prototype_contract.json'
exit (Invoke-IsolatedViewPreparation -ContractPath $contract -Authorized $AuthorizeSinglePrepare.IsPresent -OfflineContractTest $OfflineContractTest.IsPresent)
