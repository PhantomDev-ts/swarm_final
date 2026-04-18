"""
AI Agent Swarm V2 — Configuração Central
Todos os modelos via g4f.dev (API key única)
Geração local via LTX-2.3 + Z-Image no Kaggle T4 x2
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

# ─── Canais Discord ───────────────────────────────────────────────────────────
CHANNELS = {
    "geral":      "swarm-geral",
    "marketing":  "swarm-marketing",
    "dev":        "swarm-dev",
    "design":     "swarm-design",
    "research":   "swarm-research",
    "conteudo":   "swarm-conteudo",
    "midia":      "swarm-midia",
    "logs":       "swarm-logs",
}

# ─── g4f API Key (única para todos os modelos) ────────────────────────────────
# Obtenha em: https://g4f.dev → Dashboard → API Keys
# No Kaggle: Settings > Secrets > G4F_API_KEY
G4F_API_KEY = os.getenv("G4F_API_KEY", "")

# Endpoint base do g4f.dev (todos os modelos passam por aqui)
G4F_BASE_URL = "https://g4f.dev/v1"

# ─── Modelos via g4f.dev ──────────────────────────────────────────────────────
# Ollama e DeepInfra são acessados PELO g4f como providers internos
# Você não precisa de chaves separadas para eles
G4F_MODELS = {
    "gemini_flash": {
        "model":       "gemini-2.0-flash",
        "vision":      True,
        "description": "Gemini 2.0 Flash — rápido, tasks gerais e análise de imagem",
    },
    "glm": {
        "model":       "glm-4-plus",
        "vision":      False,
        "description": "GLM 5.1 — raciocínio estruturado",
    },
    "minimax": {
        "model":       "minimax-2.7",
        "vision":      False,
        "description": "MiniMax 2.7 — via g4f → Ollama provider",
    },
    "qwen_vision": {
        "model":       "Qwen/Qwen3.5-397B",
        "vision":      True,
        "description": "Qwen 3.5 397B com visão — via g4f → DeepInfra provider",
    },
}

# Modelo padrão por equipe
TEAM_DEFAULT_MODEL = {
    "neuromarketing": "gemini_flash",
    "dev":            "qwen_vision",   # visão para analisar código/screenshots
    "design":         "qwen_vision",   # visão para analisar wireframes/imagens
    "research":       "gemini_flash",
    "conteudo":       "gemini_flash",
}

# ─── Geração de mídia (local no Kaggle) ───────────────────────────────────────
HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN", "")

LTXV_MODEL_ID    = "Lightricks/LTX-Video"
ZIMAGE_MODEL_ID  = "Tongyi-MAI/Z-Image-Turbo"

# Resolução padrão (T4 x2 = 32GB VRAM total)
LTXV_RESOLUTION   = (704, 480)
LTXV_NUM_FRAMES   = 97          # (12×8)+1 = ~4s a 24fps
ZIMAGE_RESOLUTION = (1024, 1024)

# ─── LLM Engine ───────────────────────────────────────────────────────────────
MAX_TOKENS  = 3000
MAX_HISTORY = 8

# ─── Agentes ──────────────────────────────────────────────────────────────────
AGENT_NAMES = ["neuromarketing", "dev", "design", "research", "conteudo"]
