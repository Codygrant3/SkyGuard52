@echo off
setlocal EnableDelayedExpansion
type "D:\Skyguard52\Docs\AAA_Review\luna_farm\P02_aircraft.txt" | codex -a never exec -m gpt-5.6-luna -s read-only --json --ephemeral --skip-git-repo-check --output-schema "D:\Skyguard52\Docs\AAA_Review\luna_farm\proposal_wave_schema.json" -o "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave01\canonical\aircraft.json" - > "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave01\raw\aircraft.jsonl" 2> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave01\logs\aircraft.log"
set ERR=!ERRORLEVEL!
echo EXIT=!ERR!> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave01\logs\aircraft.exit.txt"
