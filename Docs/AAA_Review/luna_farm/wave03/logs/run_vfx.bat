@echo off
setlocal EnableDelayedExpansion
type "D:\Skyguard52\Docs\AAA_Review\luna_farm\P05_vfx.txt" | codex -a never exec -m gpt-5.6-luna -s read-only --json --ephemeral --skip-git-repo-check --output-schema "D:\Skyguard52\Docs\AAA_Review\luna_farm\proposal_wave_schema.json" -o "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave03\canonical\vfx.json" - > "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave03\raw\vfx.jsonl" 2> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave03\logs\vfx.log"
set ERR=!ERRORLEVEL!
echo EXIT=!ERR!> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave03\logs\vfx.exit.txt"
