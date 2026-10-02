# -*- coding: utf-8 -*-
"""Q03 corrected-rubric Table X reproduction (no API), package-relative.
Runs the corrected analyzer on outputs/confirm_v2/rubric_sensitivity/q03_pointwise.json."""
import os, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
os.environ["EVAL_DIR"]=str(ROOT/"outputs"/"confirm_v2"/"rubric_sensitivity")
os.environ["POINTWISE_NAME"]="q03_pointwise.json"
os.environ["OUT_NAME"]="q03_analysis.json"
sys.path.insert(0,str(ROOT/"analysis"))
import analyze as A
print("[Q03] corrected-rubric re-analysis (324/324) ->", A.EVAL/"q03_analysis.json")
A.main()
