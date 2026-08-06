@echo off
setlocal EnableDelayedExpansion
type "D:\Skyguard52\Docs\AAA_Review\luna_farm\P04_weapon_ads.txt" | codex -a never exec -m gpt-5.6-luna -s read-only --json --ephemeral --skip-git-repo-check --output-schema "D:\Skyguard52\Docs\AAA_Review\luna_farm\proposal_wave_schema.json" -o "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave02\canonical\weapon_ads.json" - > "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave02\raw\weapon_ads.jsonl" 2> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave02\logs\weapon_ads.log"
set ERR=!ERRORLEVEL!
echo EXIT=!ERR!> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave02\logs\weapon_ads.exit.txt"
