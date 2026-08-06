@echo off
setlocal EnableDelayedExpansion
type "D:\Skyguard52\Docs\AAA_Review\true_art_track\terra_prompt.txt" | codex -a never exec -m gpt-5.6-terra -c model_reasoning_effort="high" -s read-only --json --ephemeral --skip-git-repo-check --output-schema "D:\Skyguard52\Docs\AAA_Review\true_art_track\terra_true_art_schema.json" -o "D:\Skyguard52\Docs\AAA_Review\true_art_track\terra_true_art_plan.json" - > "D:\Skyguard52\Docs\AAA_Review\true_art_track\logs\terra_raw.jsonl" 2> "D:\Skyguard52\Docs\AAA_Review\true_art_track\logs\terra.log"
set ERR=!ERRORLEVEL!
echo EXIT=!ERR!> "D:\Skyguard52\Docs\AAA_Review\true_art_track\logs\terra.exit.txt"
