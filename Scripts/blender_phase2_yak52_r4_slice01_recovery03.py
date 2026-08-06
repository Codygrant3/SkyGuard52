"""Recovery03: Blender 5.2 compatibility entrypoint, never executed on import."""
from __future__ import annotations
import copy, importlib.util, json
from pathlib import Path
from typing import Any

BUILD_ID="BLD-M01-YAK-FINAL-ART-R4-S01-RECOVERY03"
DATUM_EMPTY_DISPLAY_TYPE="PLAIN_AXES"
RENDER_ENGINE="BLENDER_EEVEE"
ROOT=Path(__file__).resolve().parents[1]
SCRIPT_PATH=Path(__file__).resolve()
FROZEN=ROOT/"Scripts/blender_phase2_yak52_r4_slice01_silhouette.py"
CONTRACT=ROOT/"Docs/AAA_Review/PHASE2_YAK52_R4_SLICE01_RECOVERY03_OUTPUT_CONTRACT.json"
OUTPUT_DIR=ROOT/"Content/Skyguard/Meshes/Source/Mission01/Yak52_FinalArt_R4/Slice01_Recovery03"
BLEND_PATH=OUTPUT_DIR/"BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY03_MASTER.blend"
GLB_PATH=OUTPUT_DIR/"bld_m01_yak_final_art_r4_s01_recovery03.glb"
MANIFEST_PATH=ROOT/"Saved/Reports/BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY03_MANIFEST.json"
SCREENSHOT_DIR=ROOT/"Saved/Screenshots/BLD_M01_YAK_FINAL_ART_R4_S01_RECOVERY03"

def load()->Any:
    spec=importlib.util.spec_from_file_location("skyguard_slice01_frozen_r03",FROZEN)
    if spec is None or spec.loader is None:raise RuntimeError("frozen source load failed")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def datums(m:Any,collection:Any,length:float)->None:
    half=length/2
    for name,loc in (("DATUM_R4S01_AircraftOrigin",(0,0,0)),("DATUM_R4S01_TailExtreme",(-half,0,.34)),("DATUM_R4S01_PropellerPlane",(half,0,.13)),("DATUM_R4S01_WingReference",(0,0,0))):
        o=m.bpy.data.objects.new(name,None);o.empty_display_type=DATUM_EMPTY_DISPLAY_TYPE;o.empty_display_size=.25;o.location=loc;m.link_object(o,collection)
def main()->None:
    c=json.loads(CONTRACT.read_text(encoding="utf-8-sig"))
    for key in ("build_id","authority_inputs","authoring_script","outputs","claims"):
        if key not in c:raise RuntimeError(f"Recovery03 contract missing {key}")
    m=load();m.BUILD_ID=BUILD_ID;m.OUTPUT_CONTRACT_PATH=CONTRACT;m.SCRIPT_PATH=SCRIPT_PATH
    m.OUTPUT_DIR=OUTPUT_DIR;m.BLEND_PATH=BLEND_PATH;m.GLB_PATH=GLB_PATH;m.MANIFEST_PATH=MANIFEST_PATH;m.SCREENSHOT_DIR=SCREENSHOT_DIR
    m.create_datums=lambda collection,length:datums(m,collection,length)
    original=m.configure_render
    def configure(manifest:dict[str,Any])->None:
        patched=copy.deepcopy(manifest)
        if patched["render_contract"]["engine"]!="BLENDER_EEVEE_NEXT":raise RuntimeError("unexpected frozen render token")
        patched["render_contract"]["engine"]=RENDER_ENGINE
        original(patched)
    m.configure_render=configure
    m.main()
if __name__=="__main__":main()
