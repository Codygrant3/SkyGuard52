@echo off
setlocal EnableDelayedExpansion
type "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\max_refine\max_refine_prompt.txt" | codex -a never exec -m gpt-5.6-luna -c model_reasoning_effort="max" -s read-only --json --ephemeral --skip-git-repo-check --output-schema "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\max_refine\refine_schema.json" -o "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\max_refine\refined_selected.json" - > "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\max_refine\raw.jsonl" 2> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\max_refine\max_refine.log"
set ERR=!ERRORLEVEL!
echo EXIT=!ERR!> "D:\Skyguard52\Docs\AAA_Review\luna_farm\wave04\max_refine\exit.txt"
