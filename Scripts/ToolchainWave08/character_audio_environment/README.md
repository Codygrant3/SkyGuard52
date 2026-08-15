# Skyguard Toolchain Wave 08: character, audio, environment

This namespace contains deterministic, offline-first tooling for three isolated
Unreal Engine 5.8 capability gates. Nothing here modifies the canonical
`Skyguard52.uproject`, canonical Config, canonical Content, or production
plugins.

The three later preparation commands are:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\ToolchainWave08\character_audio_environment\prepare_character_view_once.ps1 -AuthorizeSinglePrepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\ToolchainWave08\character_audio_environment\prepare_audio_view_once.ps1 -AuthorizeSinglePrepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Skyguard52\Scripts\ToolchainWave08\character_audio_environment\prepare_environment_view_once.ps1 -AuthorizeSinglePrepare
```

Each command creates one fresh root and one immutable attempt namespace. It
never launches Unreal, Blender, AutomationTool, UBT, a compiler, or an asset
generator. Character and audio views contain empty Content directories. The
environment view receives a byte-for-byte Content copy because links could
allow an isolated editor to mutate canonical packages.

Run the offline verifier before authorizing any preparation:

```powershell
python D:\Skyguard52\Scripts\ToolchainWave08\character_audio_environment\verify_offline.py
```
