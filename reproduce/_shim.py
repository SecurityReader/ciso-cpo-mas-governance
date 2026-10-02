# -*- coding: utf-8 -*-
"""httpx2(회사 포크) 우회용 stdlib(urllib+ssl) API shim.
anthropic.Anthropic / openai.OpenAI 와 '하네스가 쓰는 부분만' 동일한 인터페이스 제공.
corp_ca.pem(corporate root CA included)으로 TLS 검증 → 순수 소켓 TLS가 이미 성공했으므로 동작 보장.
"""
import os, json, ssl, time, urllib.request, urllib.error
from pathlib import Path
CA_PEM = Path(__file__).resolve().parent / "corp_ca.pem"

def _ctx():
    return ssl.create_default_context(cafile=str(CA_PEM))

def _post(url, headers, body, timeout=600):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, context=_ctx(), timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"HTTP {e.code}: {msg}") from e   # 메시지에 param명 포함(폴백 트리거용)

# ---- Anthropic ----
class _Blk:
    def __init__(self, text): self.type, self.text = "text", text
class _Usage:
    def __init__(self, i, o): self.input_tokens, self.output_tokens = i, o
class _AResp:
    def __init__(self, content, usage, rid): self.content, self.usage, self.id = content, usage, rid
class _AMessages:
    def create(self, model, max_tokens, messages, system=None, temperature=None, **kw):
        body = {"model": model, "max_tokens": max_tokens, "messages": messages}
        if system is not None: body["system"] = system
        if temperature is not None: body["temperature"] = temperature
        d = _post("https://api.anthropic.com/v1/messages",
                  {"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                   "anthropic-version": "2023-06-01", "content-type": "application/json"},
                  body)
        blks = [_Blk(b.get("text", "")) for b in d.get("content", []) if b.get("type") == "text"]
        u = d.get("usage", {}) or {}
        return _AResp(blks, _Usage(u.get("input_tokens", 0), u.get("output_tokens", 0)), d.get("id", ""))
class AnthropicShim:
    def __init__(self): self.messages = _AMessages()

# ---- OpenAI (chat.completions) ----
class _Msg:
    def __init__(self, content): self.content = content
class _Choice:
    def __init__(self, content): self.message = _Msg(content)
class _OResp:
    def __init__(self, choices, rid): self.choices, self.id = choices, rid
class _Completions:
    def create(self, model, messages, temperature=None, max_tokens=None, response_format=None, **kw):
        body = {"model": model, "messages": messages}
        if temperature is not None: body["temperature"] = temperature
        if max_tokens is not None: body["max_tokens"] = max_tokens
        if response_format is not None: body["response_format"] = response_format
        d = _post("https://api.openai.com/v1/chat/completions",
                  {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"],
                   "content-type": "application/json"},
                  body)
        ch = [_Choice((c.get("message", {}) or {}).get("content", "")) for c in d.get("choices", [])]
        return _OResp(ch, d.get("id", ""))
class _Chat:
    def __init__(self): self.completions = _Completions()
class OpenAIShim:
    def __init__(self): self.chat = _Chat()
