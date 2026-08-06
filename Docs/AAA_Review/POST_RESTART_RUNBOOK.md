# POST-RESTART RUNBOOK — Skyguard52 AAA

Updated: 2026-07-31T16:55:45

## What happened
PC froze under load (multiple UAC/install prompts + Unreal automation).
User will restart, re-launch install prompts, and approve UAC.

## Goal status
ACTIVE — critic still FAIL vs AAA. Not complete.
Live project: `D:\Skyguard52`
Engine: `D:\UE_5.8`
Map: `/Game/Skyguard/Maps/Lvl_SkyguardCoast`

## After reboot: approve these installs first
1. **.NET Framework 4.8.1 Developer Pack** (PRIMARY blocker for Unreal C++ editor module)
   - Installer on disk: `D:\Skyguard52\Saved\NDP481-DevPack-ENU.exe`
   - If no window: double-click that file, accept UAC, Install
   - Success proof:
     - `C:\Program Files (x86)\Microsoft SDKs\NETFXSDK` exists
     - `C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.8` exists

2. **Visual Studio Build Tools component modify** (if prompted)
   - May appear as VS Installer / setup.exe modify for:
     - Microsoft.Net.Component.4.8.SDK
     - Microsoft.Net.Component.4.8.TargetingPack
     - Microsoft.Net.ComponentGroup.4.8.DeveloperTools
   - Approve UAC and let it finish

3. Ignore/close duplicate stuck NetFx windows if several appear; keep ONE successful install.

## After NetFx succeeds — tell Codex
Say: **"NetFx installed, resume Skyguard AAA"**

Codex will then:
1. Verify NETFXSDK + v4.8 refs
2. Re-enable Modules in `Skyguard52.uproject`
3. Build editor-loadable Skyguard52 module / place C++ gunner+spawner
4. Continue Loop8 densify + harsh critic (still FAIL until AAA blind win)
5. Fab/Bridge hero import if available

## Current verified progress (pre-freeze)
- Loop7 complete: densified coast map ~8.05MB
- Hero meshes: 18 under `Content/Skyguard/Meshes/Hero/`
- New Loop8 procedural OBJs ready (gunner station, glove arm, heavy shahed, ruined tower, pier)
- Loop8 world script may be partial on disk; re-run after reboot
- C++ game target builds: `Binaries/Win64/Skyguard52.exe` exists
- Critic docs: `Docs/AAA_Review/CRITIC_FAIL_loop7.md` — overall FAIL vs AAA
- NetFx was stuck at: "Launching elevated engine process" waiting for UAC

## Do NOT
- Do not delete `D:\Skyguard52`
- Do not use OneDrive Unreal path (spaces/colon crash UE)
- Do not mark goal complete

## Quick launch after reboot (optional)
```powershell
# 1) Install NetFx if not done
Start-Process "D:\Skyguard52\Saved\NDP481-DevPack-ENU.exe"

# 2) After install, verify
Test-Path "C:\Program Files (x86)\Microsoft SDKs\NETFXSDK"
Test-Path "C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.8"

# 3) Open project
Start-Process "D:\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe" "D:\Skyguard52\Skyguard52.uproject"
```
