# -*- coding: utf-8 -*-
"""R41 채점부(정본 미변경). urllib shim 으로 httpx2 우회."""
import os, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; HARNESS=HERE.parent
sys.path.insert(0,str(HERE)); sys.path.insert(0,str(HARNESS))
from _netfix import neutralize_truststore, export_windows_ca
from _keyutil import load_env, ensure_key
from _shim import AnthropicShim, OpenAIShim

neutralize_truststore(); export_windows_ca()
load_env(HARNESS/".env"); os.environ.setdefault("LLM_BACKEND","api")
ensure_key("ANTHROPIC_API_KEY"); ensure_key("OPENAI_API_KEY")

import judge as J
J._anthropic_client = AnthropicShim()        # 지연 생성 전에 shim 주입
J._openai_client   = OpenAIShim()
J.TRACES = HERE/"traces"; J.EVAL = HERE/"eval"; J.EVAL.mkdir(parents=True, exist_ok=True)
print(f"[R41] TRACES={J.TRACES} EVAL={J.EVAL} JUDGES={J.JUDGE_MODELS}")
J.pointwise()
print("[R41] 채점 완료 → python compare.py")
