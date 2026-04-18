"""
LLM Engine — todas as chamadas via g4f.dev com uma única API key.
Gemini Flash, GLM, MiniMax e Qwen Vision são todos providers internos do g4f.
"""

import json
import base64
import time
import urllib.request
import urllib.error
import sys
from typing import Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import G4F_API_KEY, G4F_BASE_URL, G4F_MODELS, MAX_TOKENS


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def _image_media_type(path: str) -> str:
    ext = Path(path).suffix.lower()
    return {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png",  ".webp": "image/webp"}.get(ext, "image/jpeg")


def call_llm(
    model_key: str,
    messages: list[dict],
    system: str = "",
    image_path: Optional[str] = None,
    temperature: float = 0.85,
) -> str:
    """
    Chama qualquer modelo via g4f.dev usando a API key configurada.
    Todos os modelos (Gemini, GLM, MiniMax, Qwen) passam pelo mesmo endpoint.
    """
    if model_key not in G4F_MODELS:
        return f"[ERRO] Modelo '{model_key}' não encontrado. Disponíveis: {list(G4F_MODELS)}"

    if not G4F_API_KEY:
        return "[ERRO] G4F_API_KEY não configurada. Defina a variável de ambiente."

    cfg = G4F_MODELS[model_key]
    url = G4F_BASE_URL.rstrip("/") + "/chat/completions"

    # Monta lista de mensagens
    all_msgs: list[dict] = []
    if system:
        all_msgs.append({"role": "system", "content": system})

    injected_image = False
    for msg in messages:
        # Injeta imagem na primeira mensagem do user (se modelo suporta visão)
        if (image_path and not injected_image
                and msg["role"] == "user"
                and cfg.get("vision")):
            ext = _image_media_type(image_path)
            b64 = _encode_image(image_path)
            all_msgs.append({
                "role": "user",
                "content": [
                    {"type": "text",      "text": msg["content"]},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{ext};base64,{b64}"
                    }},
                ],
            })
            injected_image = True
        else:
            all_msgs.append(msg)

    payload = {
        "model":       cfg["model"],
        "messages":    all_msgs,
        "max_tokens":  MAX_TOKENS,
        "temperature": temperature,
    }

    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {G4F_API_KEY}",
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        if e.code == 401:
            return "[ERRO 401] API key inválida ou expirada. Verifique G4F_API_KEY."
        if e.code == 429:
            return "[ERRO 429] Rate limit atingido. Aguarde alguns segundos."
        return f"[HTTP {e.code}] {body[:400]}"
    except urllib.error.URLError as e:
        return f"[ERRO de rede] {e.reason} — verifique sua conexão."
    except Exception as e:
        return f"[ERRO LLM] {type(e).__name__}: {e}"


def probe_model(model_key: str) -> dict:
    """Testa se um modelo está respondendo. Retorna status, latência e preview."""
    start = time.time()
    resp  = call_llm(
        model_key,
        [{"role": "user", "content": "Responda exatamente: SWARM_OK"}],
        temperature=0.0,
    )
    ms = int((time.time() - start) * 1000)
    ok = "SWARM_OK" in resp or (len(resp) > 5 and not resp.startswith("[ERRO"))
    return {"ok": ok, "latency_ms": ms, "response_preview": resp[:100]}
