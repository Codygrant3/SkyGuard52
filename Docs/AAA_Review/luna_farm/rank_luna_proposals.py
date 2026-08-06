#!/usr/bin/env python3
"""Rank Luna Skyguard proposals under L52 capture-safe rules."""
from __future__ import annotations
import json, sys, csv, re
from pathlib import Path

KNOWN = {"Prop","PropHub","PropNose","YakBeauty","Cockpit","ADS","City","Combat","Harbor","Ocean","Wide"}
PLACEMENT = {"behind_wall","additive_emissive","unlit_hf_only"}
PILLAR_NEED = {
    "materials": 1.0,
    "aircraft": 1.0,
    "city_ocean": 0.9,
    "weapon_ads": 0.9,
    "vfx": 1.0,
}

def hard_reject(p: dict) -> str | None:
    if p.get("placement") not in PLACEMENT:
        return "bad_placement"
    stages = set(p.get("stage_targets") or [])
    if not stages or not stages.issubset(KNOWN):
        return "bad_stages"
    change = (p.get("change") or "").strip().lower()
    if len(change) < 12 or change in {"make better", "more realistic", "improve quality"}:
        return "vague_change"
    if not (p.get("acceptance_test") or "").strip():
        return "no_acceptance_test"
    blob = json.dumps(p).lower()
    if any(x in blob for x in ["extreme sun", "sky intensity 40", "dark pbr in fov", "replace hf densify", "remove checker"]):
        return "unsafe_phrase"
    if p.get("effort") == "L" and p.get("risk") == "high":
        return "too_hard_risky"
    return None

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))

def score(p: dict) -> tuple[float, dict]:
    pillar = p.get("pillar") or ""
    placement = p.get("placement")
    effort = p.get("effort") or "M"
    risk = p.get("risk") or "med"
    notes = (p.get("implementation_notes") or "") + " " + (p.get("capture_safe_reason") or "")
    assets = p.get("assets") or {}
    has_assets = any(assets.get(k) for k in ("meshes","materials","textures","niagara"))

    pillar_need = PILLAR_NEED.get(pillar, 0.5)
    capture_safety = {"behind_wall": 1.0, "additive_emissive": 0.95, "unlit_hf_only": 0.55}.get(placement, 0.0)
    implementability = 1.0 if effort == "S" and has_assets else 0.7 if effort in {"S","M"} else 0.35
    asset_readiness = 1.0 if has_assets else 0.3
    visual_roi = 0.8 if any(k in notes.lower() for k in ["panel", "weather", "muzzle", "facade", "foam", "normal", "roughness"]) else 0.55
    em = p.get("expected_metric_effect") or {}
    upside = 0.0
    upside += 0.4 if em.get("uniq_delta") == "up" else 0.0
    upside += 0.3 if em.get("edge_delta") == "up" else 0.0
    upside += 0.3 if em.get("black_delta") in {"down", "flat"} else 0.0
    metric_upside = clamp01(upside if upside else 0.4)
    regression_risk = {"low": 0.1, "med": 0.45, "high": 0.9}.get(risk, 0.5)
    if len(p.get("stage_targets") or []) >= 4:
        regression_risk = min(1.0, regression_risk + 0.2)
    complexity_penalty = {"S": 0.0, "M": 0.45, "L": 1.0}.get(effort, 0.5)

    parts = {
        "pillar_need": pillar_need,
        "visual_roi": visual_roi,
        "capture_safety": capture_safety,
        "implementability": implementability,
        "asset_readiness": asset_readiness,
        "metric_upside": metric_upside,
        "regression_risk": regression_risk,
        "complexity_penalty": complexity_penalty,
    }
    total = (
        25 * parts["pillar_need"]
        + 20 * parts["visual_roi"]
        + 20 * parts["capture_safety"]
        + 15 * parts["implementability"]
        + 10 * parts["asset_readiness"]
        + 10 * parts["metric_upside"]
        - 25 * parts["regression_risk"]
        - 10 * parts["complexity_penalty"]
    )
    return total, parts

def band(total: float, p: dict, parts: dict) -> str:
    if total >= 75 and parts["capture_safety"] >= 0.8 and p.get("risk") in {"low", "med"}:
        return "A"
    if total >= 60:
        return "B"
    if total >= 45:
        return "C"
    return "D"

def load_proposals(path: Path):
    raw = path.read_text(encoding="utf-8-sig").strip()
    # tolerate accidental fences
    raw = re.sub(r"^```(?:json)?\n|\n```$", "", raw).strip()
    data = json.loads(raw)
    if isinstance(data, dict) and "proposals" in data:
        data = data["proposals"]
    if not isinstance(data, list):
        raise SystemExit("root must be list")
    return data

def main():
    if len(sys.argv) < 3:
        print("usage: rank_luna_proposals.py input.jsonl_or_json out_csv")
        return 2
    inp = Path(sys.argv[1])
    out = Path(sys.argv[2])
    text = inp.read_text(encoding="utf-8")
    proposals = []
    if inp.suffix.lower() == ".jsonl":
        for line in text.splitlines():
            line=line.strip()
            if not line:
                continue
            obj=json.loads(line)
            if isinstance(obj, list):
                proposals.extend(obj)
            else:
                proposals.append(obj)
    else:
        proposals = load_proposals(inp)

    rows = []
    for p in proposals:
        why = hard_reject(p)
        if why:
            rows.append({
                "id": p.get("id",""),
                "pillar": p.get("pillar",""),
                "title": p.get("title",""),
                "score": -1,
                "band": "D",
                "risk": p.get("risk",""),
                "effort": p.get("effort",""),
                "placement": p.get("placement",""),
                "stage_targets": "|".join(p.get("stage_targets") or []),
                "status": f"rejected_{why}",
            })
            continue
        total, parts = score(p)
        rows.append({
            "id": p.get("id",""),
            "pillar": p.get("pillar",""),
            "title": p.get("title",""),
            "score": round(total, 2),
            "band": band(total, p, parts),
            "risk": p.get("risk",""),
            "effort": p.get("effort",""),
            "placement": p.get("placement",""),
            "stage_targets": "|".join(p.get("stage_targets") or []),
            "capture_safety": parts["capture_safety"],
            "visual_roi": parts["visual_roi"],
            "implementability": parts["implementability"],
            "asset_readiness": parts["asset_readiness"],
            "metric_upside": parts["metric_upside"],
            "regression_risk": parts["regression_risk"],
            "complexity_penalty": parts["complexity_penalty"],
            "status": "candidate",
        })
    rows.sort(key=lambda r: r.get("score", -1), reverse=True)
    fields = sorted({k for r in rows for k in r.keys()})
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    a = sum(1 for r in rows if r.get("band") == "A")
    print(f"wrote {out} rows={len(rows)} A-band={a}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
