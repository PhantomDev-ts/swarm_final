"""
AI Agent Swarm — Configuração Central
Todos os LLMs via g4f.space/v1 (URL correta — g4f.dev é só o site)
Providers: DeepInfra e Ollama roteados pelo g4f
"""

import os
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).parent
MEMORY_DIR   = BASE_DIR / "memory"
MESSAGES_DIR = BASE_DIR / "messages"
LOGS_DIR     = BASE_DIR / "logs"
MEDIA_DIR    = BASE_DIR / "media"

# ─── Discord ──────────────────────────────────────────────────────────────────
DISCORD_TOKEN    = os.getenv("DISCORD_TOKEN", "")
DISCORD_PREFIX   = "!"
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))

CHANNELS = {
    "geral":     "swarm-geral",
    "marketing": "swarm-marketing",
    "dev":       "swarm-dev",
    "design":    "swarm-design",
    "research":  "swarm-research",
    "conteudo":  "swarm-conteudo",
    "midia":     "swarm-midia",
    "logs":      "swarm-logs",
}

# ─── g4f — URLs ───────────────────────────────────────────────────────────────
# g4f.dev  = site de documentação (não é endpoint de API!)
# g4f.space/v1  = endpoint real com API key, roteia para DeepInfra/Ollama/etc.
# g4f.space/api/<provider>  = endpoints gratuitos sem key

G4F_API_KEY = os.getenv("G4F_API_KEY", "")

# Endpoints
G4F_HOSTED_URL  = "https://g4f.space/v1"          # Requer G4F_API_KEY
G4F_OLLAMA_URL  = "https://g4f.space/api/ollama"  # Gratuito, sem key
G4F_GEMINI_URL  = "https://g4f.space/api/gemini"  # Gratuito, sem key
G4F_NVIDIA_URL  = "https://g4f.space/api/nvidia"  # Gratuito, sem key
G4F_AUTO_URL    = "https://g4f.space/api/auto"    # Gratuito, auto-seleciona

# ─── Catálogo completo de modelos ─────────────────────────────────────────────
# provider: "hosted" → g4f.space/v1 (key obrigatória)
#           "ollama" → g4f.space/api/ollama (gratuito)
#           "gemini" → g4f.space/api/gemini (gratuito)
#           "nvidia" → g4f.space/api/nvidia (gratuito)

ALL_MODELS: dict[str, dict] = {

    # ── DeepInfra via g4f.space/v1 (requer G4F_API_KEY) ──────────────────────
    "qwen3.5-397b": {
        "model":    "Qwen/Qwen3.5-397B-A17B",
        "provider": "hosted",
        "vision":   True,
        "tts":      False,
        "desc":     "Qwen 3.5 397B — flagship, tem visão",
    },
    "glm-5.1": {
        "model":    "zai-org/GLM-5.1",
        "provider": "hosted",
        "vision":   False,
        "tts":      False,
        "desc":     "GLM-5.1 — 94% do Claude Opus em coding",
    },
    "kimi-k2.5": {
        "model":    "moonshotai/Kimi-K2.5",
        "provider": "hosted",
        "vision":   False,
        "tts":      False,
        "desc":     "Kimi K2.5 — forte em agentic coding",
    },
    "inworld-tts": {
        "model":    "inworld-ai/inworld-tts-1.5-max",
        "provider": "hosted",
        "vision":   False,
        "tts":      True,
        "desc":     "Inworld TTS 1.5 Max — síntese de voz",
    },

    # ── Ollama via g4f.space/api/ollama (GRATUITO, sem key) ───────────────────
    "gemini-3-flash": {
        "model":    "gemini-3-flash-preview",
        "provider": "ollama",
        "vision":   True,
        "tts":      False,
        "desc":     "Gemini 3 Flash Preview — gratuito, rápido, tem visão",
    },
}

# ─── Modelos padrão por equipe ────────────────────────────────────────────────
# Escolha baseada em: capability + se tem key disponível
# hosted = requer G4F_API_KEY | ollama = gratuito

TEAM_DEFAULT_MODEL: dict[str, str] = {
    "neuromarketing": "gemini-3-flash",   # gratuito, rápido, visão
    "dev":            "glm-5.1",          # hosted, coding especializado
    "design":         "qwen3.5-397b",     # hosted, visão (analisa screenshots)
    "research":       "kimi-k2.5",        # hosted, reasoning analítico
    "conteudo":       "gemini-3-flash",   # gratuito, criativo e rápido
}

# Fallback gratuito quando não há G4F_API_KEY
TEAM_FREE_MODEL: dict[str, str] = {
    "neuromarketing": "gemini-3-flash",
    "dev":            "gemini-3-flash",
    "design":         "gemini-3-flash",
    "research":       "gemini-3-flash",
    "conteudo":       "gemini-3-flash",
}

# Agente autônomo — melhor disponível
AUTONOMOUS_MODEL         = "gemini-3-flash"    # gratuito
AUTONOMOUS_MODEL_PREMIUM = "qwen3.5-397b"      # hosted (com visão)

# ─── Geração de mídia (local no Kaggle) ───────────────────────────────────────
HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN", "")
LTXV_MODEL_ID     = "Lightricks/LTX-Video"
ZIMAGE_MODEL_ID   = "Tongyi-MAI/Z-Image-Turbo"
LTXV_RESOLUTION   = (704, 480)
LTXV_NUM_FRAMES   = 97
ZIMAGE_RESOLUTION = (1024, 1024)

# ─── LLM Engine ───────────────────────────────────────────────────────────────
MAX_TOKENS  = 4000
MAX_HISTORY = 10

AGENT_NAMES = ["neuromarketing", "dev", "design", "research", "conteudo"]
