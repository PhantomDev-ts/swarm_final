"""
LLM Engine — g4f.space/v1 (hosted, com key) + g4f.space/api/ollama (gratuito)

Fluxo de uma requisição:
  call_llm("ollama-glm-5.1", messages)
      → resolve provider = "ollama"
      → url = https://g4f.space/api/ollama/chat/completions
      → model = "glm-5.1"
      → POST sem Authorization header (gratuito)
      → retorna texto

  call_llm("glm-5.1", messages)
      → resolve provider = "hosted"
      → url = https://g4f.space/v1/chat/completions
      → model = "zai-org/GLM-5.1"
      → POST com Authorization: Bearer g4f_xxx
      → retorna texto
"""

import json
import base64
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional
import sys

sys.path.insert(0, str(Path(__file__).parent))
from config import (
    G4F_API_KEY, G4F_HOSTED_URL, G4F_OLLAMA_URL,
    ALL_MODELS, MAX_TOKENS,
)


# ─── Encode imagem ────────────────────────────────────────────────────────────
def _b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _mime(path: str) -> str:
    return {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".png": "image/png",  ".webp": "image/webp"}.get(
        Path(path).suffix.lower(), "image/jpeg"
    )


# ─── Resolve URL e headers por provider ──────────────────────────────────────
def _endpoint(provider: str) -> tuple[str, dict]:
    """Retorna (url, headers) para o provider dado."""
    if provider == "hosted":
        if not G4F_API_KEY:
            raise ValueError(
                "G4F_API_KEY não definida — modelos 'hosted' exigem key.\n"
                "Defina G4F_API_KEY=g4f_xxx no .env ou use modelos 'ollama' (gratuitos)."
            )
        return G4F_HOSTED_URL + "/chat/completions", {
            "Content-Type":  "application/json",
            "Authorization": f"Bearer {G4F_API_KEY}",
        }
    elif provider == "ollama":
        return G4F_OLLAMA_URL + "/chat/completions", {
            "Content-Type": "application/json",
        }
    elif provider == "gemini":
        from config import G4F_GEMINI_URL
        return G4F_GEMINI_URL + "/chat/completions", {
            "Content-Type": "application/json",
        }
    elif provider == "nvidia":
        from config import G4F_NVIDIA_URL
        return G4F_NVIDIA_URL + "/chat/completions", {
            "Content-Type": "application/json",
        }
    else:
        raise ValueError(f"Provider desconhecido: {provider}")


# ─── Chamada principal ────────────────────────────────────────────────────────
def call_llm(
    model_key: str,
    messages: list[dict],
    system: str = "",
    image_path: Optional[str] = None,
    temperature: float = 0.85,
    debug: bool = False,
) -> str:
    """
    Chama qualquer modelo do catálogo via g4f.

    Args:
        model_key:   chave em ALL_MODELS (ex: "glm-5.1", "ollama-kimi-k2.5")
        messages:    histórico de mensagens [{"role": ..., "content": ...}]
        system:      system prompt
        image_path:  caminho de imagem (só modelos com vision=True)
        temperature: criatividade 0.0-1.0
        debug:       imprime request/response completo
    """
    if model_key not in ALL_MODELS:
        return (
            f"[ERRO] Modelo '{model_key}' não existe no catálogo.\n"
            f"Disponíveis: {', '.join(ALL_MODELS.keys())}"
        )

    cfg      = ALL_MODELS[model_key]
    provider = cfg["provider"]

    try:
        url, headers = _endpoint(provider)
    except ValueError as e:
        return f"[ERRO] {e}"

    # Monta mensagens
    all_msgs: list[dict] = []
    if system:
        all_msgs.append({"role": "system", "content": system})

    img_injected = False
    for msg in messages:
        if (image_path and not img_injected
                and msg["role"] == "user"
                and cfg.get("vision")):
            all_msgs.append({
                "role": "user",
                "content": [
                    {"type": "text",      "text": msg["content"]},
                    {"type": "image_url", "image_url": {
                        "url": f"data:{_mime(image_path)};base64,{_b64(image_path)}"
                    }},
                ],
            })
            img_injected = True
        else:
            all_msgs.append(msg)

    payload = {
        "model":       cfg["model"],
        "messages":    all_msgs,
        "max_tokens":  MAX_TOKENS,
        "temperature": temperature,
    }

    if debug:
        print(f"\n[LLM DEBUG] {model_key}")
        print(f"  url:      {url}")
        print(f"  model:    {cfg['model']}")
        print(f"  provider: {provider}")
        print(f"  messages: {len(all_msgs)} msgs")
        print(f"  auth:     {'Bearer ***' if 'Authorization' in headers else 'nenhuma'}")

    # POST
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            raw  = resp.read().decode("utf-8")
            data = json.loads(raw)

        if debug:
            print(f"  status: 200 OK")
            print(f"  tokens: {data.get('usage', {})}")

        return data["choices"][0]["message"]["content"].strip()

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        if debug:
            print(f"  status: {e.code}\n  body: {body[:400]}")
        msgs = {
            400: f"[HTTP 400] Requisição inválida. Model: {cfg['model']}. Body: {body[:200]}",
            401: "[HTTP 401] API key inválida. Verifique G4F_API_KEY.",
            403: "[HTTP 403] Acesso negado. Key sem permissão para este modelo.",
            404: f"[HTTP 404] Modelo não encontrado: {cfg['model']}",
            429: "[HTTP 429] Rate limit. Aguarde e tente de novo.",
            503: "[HTTP 503] Serviço indisponível. Tente outro modelo.",
        }
        return msgs.get(e.code, f"[HTTP {e.code}] {body[:300]}")

    except urllib.error.URLError as e:
        return f"[ERRO REDE] {e.reason} — verifique conexão ou tente modelo 'ollama'."

    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return f"[ERRO PARSE] Resposta inesperada da API: {e}"

    except Exception as e:
        return f"[ERRO] {type(e).__name__}: {e}"


# ─── Probe de modelo ──────────────────────────────────────────────────────────
def probe_model(model_key: str, verbose: bool = False) -> dict:
    """
    Testa um modelo. Retorna:
        {"ok": bool, "latency_ms": int, "response": str, "provider": str, "model_id": str}
    """
    cfg   = ALL_MODELS.get(model_key, {})
    start = time.time()
    resp  = call_llm(
        model_key,
        [{"role": "user", "content": "Responda exatamente: SWARM_OK"}],
        temperature=0.0,
        debug=verbose,
    )
    ms = int((time.time() - start) * 1000)
    ok = "SWARM_OK" in resp or (not resp.startswith("[ERRO") and len(resp) > 3)
    return {
        "ok":         ok,
        "latency_ms": ms,
        "response":   resp[:120],
        "provider":   cfg.get("provider", "?"),
        "model_id":   cfg.get("model",    "?"),
    }


# ─── Probe em lote ────────────────────────────────────────────────────────────
def probe_all(
    tags: list[str] | None = None,
    provider_filter: str | None = None,
    verbose: bool = False,
) -> dict[str, dict]:
    """
    Testa múltiplos modelos em paralelo.

    Args:
        tags:            filtra por tag (ex: ["coding", "vision"])
        provider_filter: "hosted" | "ollama" | None (todos)
        verbose:         mostra detalhes de cada requisição
    """
    import concurrent.futures

    targets = {
        k: v for k, v in ALL_MODELS.items()
        if (not v.get("tts") and not v.get("image"))       # só LLMs de texto
        and (not provider_filter or v["provider"] == provider_filter)
        and (not tags or any(t in v.get("tags", []) for t in tags))
    }

    results: dict[str, dict] = {}

    def _probe(key: str) -> tuple[str, dict]:
        return key, probe_model(key, verbose=verbose)

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(_probe, k): k for k in targets}
        for fut in concurrent.futures.as_completed(futures):
            key, result = fut.result()
            results[key] = result

    return results


# ─── Discovery de modelos disponíveis na API ──────────────────────────────────
def list_available_models(provider: str = "hosted") -> list[str]:
    """
    Consulta GET /models no provider e retorna lista de IDs.
    Útil para confirmar nomes exatos dos modelos após ter a key.
    """
    try:
        url, headers = _endpoint(provider)
        models_url = url.replace("/chat/completions", "/models")
        req = urllib.request.Request(models_url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        return [m["id"] for m in data.get("data", [])]
    except Exception as e:
        return [f"[ERRO] {e}"]
