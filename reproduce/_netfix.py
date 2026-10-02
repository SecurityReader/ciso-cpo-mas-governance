# -*- coding: utf-8 -*-
"""R41 네트워크 수정: truststore(httpx 충돌) 우회 + Windows 신뢰저장소 → PEM.
- truststore.inject_into_ssl 을 no-op 으로 바꿔 'process() takes no keyword arguments' 회피.
- Windows ROOT/CA 저장소(corporate root CA included) + certifi 공개루트를 corp_ca.pem 으로 병합.
- httpx.Client(verify=corp_ca.pem) 를 anthropic/openai 클라이언트에 직접 주입.
반드시 run_harness/judge import 보다 먼저 neutralize_truststore() 호출.
"""
import os, ssl, base64
from pathlib import Path
HERE = Path(__file__).resolve().parent
CA_PEM = HERE / "corp_ca.pem"

def neutralize_truststore():
    try:
        import truststore
        truststore.inject_into_ssl = lambda *a, **k: None  # 전역 ssl 몽키패치 무력화
        print("[netfix] truststore inject 무력화(httpx 충돌 회피)")
    except Exception as e:
        print("[netfix] truststore 미설치/스킵:", e)

def export_windows_ca(dest: Path = CA_PEM) -> Path:
    if dest.exists() and dest.stat().st_size > 2000:
        print(f"[netfix] 기존 CA 번들 사용: {dest}"); return dest
    blocks = []
    try:
        for store in ("ROOT", "CA"):
            for cert, enc, _ in ssl.enum_certificates(store):   # Windows 전용
                if enc == "x509_asn":
                    b = base64.b64encode(cert).decode()
                    body = "\n".join(b[i:i+64] for i in range(0, len(b), 64))
                    blocks.append(f"-----BEGIN CERTIFICATE-----\n{body}\n-----END CERTIFICATE-----\n")
        print(f"[netfix] Windows 저장소에서 인증서 {len(blocks)}개 추출")
    except Exception as e:
        print("[netfix] Windows 저장소 추출 실패(비Windows?):", e)
    try:
        import certifi
        blocks.append(Path(certifi.where()).read_text(encoding="utf-8"))
    except Exception:
        pass
    dest.write_text("".join(blocks), encoding="utf-8")
    print(f"[netfix] CA 번들 작성: {dest} ({dest.stat().st_size} bytes)")
    return dest

def _mk_httpx(pkg, timeout=600):
    """pkg('httpx2' 또는 'httpx').Client(verify=corp_ca.pem) 생성."""
    mod = __import__(pkg)
    return mod.Client(verify=str(CA_PEM), timeout=timeout)

def patched_anthropic():
    """anthropic SDK는 httpx2 사용 → httpx2 우선, 실패 시 httpx 폴백."""
    import anthropic
    for pkg in ("httpx2", "httpx"):
        try:
            return anthropic.Anthropic(http_client=_mk_httpx(pkg))
        except (TypeError, ImportError) as e:
            last = e
    raise last

def patched_openai():
    """OpenAI SDK는 표준 httpx → httpx 우선, 실패 시 httpx2 폴백."""
    from openai import OpenAI
    for pkg in ("httpx", "httpx2"):
        try:
            return OpenAI(http_client=_mk_httpx(pkg))
        except (TypeError, ImportError) as e:
            last = e
    raise last
