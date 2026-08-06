@echo off
setlocal EnableDelayedExpansion
type "D:\Skyguard52\Docs\AAA_Review\luna_farm\P03_city_ocean.txt" | codex -a never exec -m gpt-5.6-luna -s read-only --json --ephemeral --skip-git-repo-check --output-schema "D:\Skyguard52\Docs\AAA_Review\luna_farm\proposal_wave_schema.json" -o "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\canonical\city_ocean.json" - > "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\raw\city_ocean.jsonl" 2> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\logs\city_ocean.log"
set ERR=!ERRORLEVEL!
echo EXIT=!ERR!> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\logs\city_ocean.exit.txt"
