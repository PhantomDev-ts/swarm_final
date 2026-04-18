# OpenClaude × Swarm — Integração

OpenClaude é um fork do código fonte real do Claude Code, com um shim
que redireciona as chamadas de API para qualquer provider OpenAI-compatible.
Você ganha **todas as ferramentas do Claude Code** usando seus modelos g4f.

---

## O que você ganha com OpenClaude

| Feature               | OpenClaude | Terminal Python |
|-----------------------|-----------|-----------------|
| Bash tool             | ✅ nativo  | ✅              |
| File edit/read/write  | ✅ nativo  | ✅              |
| Grep / Glob           | ✅ nativo  | ❌              |
| LSP integration       | ✅ nativo  | ❌              |
| Sub-agents            | ✅ nativo  | ❌              |
| Tasks paralelas       | ✅ nativo  | ❌              |
| MCP servers           | ✅ nativo  | ❌              |
| Slash commands        | ✅ nativo  | ❌              |
| Streaming tokens      | ✅ nativo  | ✅              |
| Generate image/video  | via MCP   | ✅              |
| Analyse video         | via MCP   | ✅              |
| Web search            | via MCP   | ✅              |
| Swarm memory          | via MCP   | ✅              |

**Recomendação:** use OpenClaude para tarefas de código/arquivo e o terminal Python para
tarefas que precisam de geração de mídia, análise de vídeo ou integração com o swarm.

---

## Setup

```bash
# 1. Instalar e configurar
chmod +x scripts/install_openclaude.sh
./scripts/install_openclaude.sh

# 2. Lançar
./scripts/launch_openclaude.sh gemini   # rápido
./scripts/launch_openclaude.sh qwen     # mais capaz, tem visão
./scripts/launch_openclaude.sh glm      # raciocínio estruturado
```

Ou a partir do terminal interativo do swarm:
```
/openclaude gemini
```

---

## Como funciona

```
OpenClaude (Claude Code tools)
        │
        ▼
  openaiShim.ts
        │  traduz Anthropic → OpenAI format
        ▼
  g4f.dev/v1/chat/completions
        │  API key: G4F_API_KEY
        ▼
  Gemini Flash / Qwen Vision / GLM / MiniMax

  + MCP Server (swarm)
        │
        ▼
  generate_image / generate_video / analyse_video / memory
```

---

## Variáveis de ambiente usadas

```bash
CLAUDE_CODE_USE_OPENAI=1          # ativa o shim
OPENAI_API_KEY=$G4F_API_KEY       # sua chave g4f.dev
OPENAI_BASE_URL=https://g4f.dev/v1
OPENAI_MODEL=gemini-2.0-flash     # ou qualquer modelo g4f
```

---

## MCP — Tools do Swarm disponíveis no OpenClaude

Quando lançado via `launch_openclaude.sh`, o MCP server do swarm sobe automaticamente
e disponibiliza estas tools para o OpenClaude usar:

- `generate_image(prompt, ...)` — Z-Image-Turbo
- `generate_video(prompt, ...)` — LTX-2.3 GGUF
- `generate_videos_parallel(prompts)` — 2 GPUs em paralelo
- `analyse_video(path, question)` — ffmpeg + visão
- `web_search(query)` — DuckDuckGo
- `memory_save(agent, key, value)` — memória do swarm
- `memory_get(agent, key)` — recupera memória
- `media_status()` — VRAM atual
