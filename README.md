# 🤖 AI Agent Swarm V2 — com Agente Autônomo

Sistema completo: swarm de agentes especializados + **agente autônomo** que executa qualquer tarefa do início ao fim sozinho, com interface Discord e terminal.

---

## 🆕 O que há de novo nesta versão

### Agente Autônomo (`agent_core/`)
- **Agentic loop** completo com tool use real: bash, arquivos, web, mídia, análise de vídeo
- **Instala o que precisar** — pip, apt, npm, cargo, Godot, ffmpeg, qualquer coisa
- **Itera em erros** — lê o output, pensa, tenta de novo sem parar
- **Reporta em tempo real** — você vê o que está acontecendo enquanto executa
- Interface **Discord** (`!task`) e **terminal interativo** (tipo Claude Code)

### LTX-2.3 GGUF
- Versão Q4 quantizada: **~6GB VRAM** (antes precisava de ~20GB)
- **2 instâncias em paralelo** nas duas GPUs T4 → geração simultânea de vídeos
- Z-Image-Turbo + 2× LTX-2.3 rodam ao mesmo tempo nos 32GB disponíveis

---

## 🗺️ Estrutura

```
swarm_v2/
├── agent_core/
│   ├── autonomous_agent.py   ← agentic loop + todas as tools
│   ├── terminal.py           ← interface CLI (tipo Claude Code)
│   ├── discord_agent.py      ← integração Discord com streaming
│   └── __main__.py           ← entry point: python -m agent_core
│
├── config.py
├── llm_engine.py             ← g4f.dev, API key única
├── media_engine.py           ← Z-Image + LTX-2.3 GGUF + paralelo
├── orchestrator.py
├── memory_system.py
├── message_bus.py
├── agents/
├── skills/
├── discord/bot.py            ← !task, !parallel_video, !gpu + todos os comandos
└── kaggle_setup.ipynb
```

---

## 🔑 Passo 1 — Obter a API key do g4f.dev

1. Acesse **https://g4f.dev**
2. **Login** (Google ou GitHub)
3. **Dashboard → API Keys → Create new key**
4. Copie a chave — começa com `g4f_`

---

## 🤖 Passo 2 — Criar o bot Discord

1. **https://discord.com/developers/applications** → New Application
2. **Bot → Add Bot** → copie o token
3. **Privileged Gateway Intents:** ative `MESSAGE CONTENT INTENT`
4. **OAuth2 → URL Generator:**
   - Scopes: `bot`
   - Permissions: `Send Messages`, `Read Message History`, `Attach Files`, `Embed Links`
5. Adicione o bot ao servidor com o link gerado
6. **Modo Desenvolvedor** no Discord → botão direito no servidor → **Copiar ID**

---

## 📺 Passo 3 — Canais Discord

```
swarm-geral    swarm-marketing    swarm-dev       swarm-design
swarm-research swarm-conteudo     swarm-midia     swarm-logs
```

---

## 🐙 Passo 4 — Push para o GitHub

```bash
unzip ai_swarm_v2_final.zip && cd swarm_v2
git init && git add .
git commit -m "AI Agent Swarm V2"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```

---

## 🖥️ Passo 5 — Terminal local (tipo Claude Code)

```bash
# Instalar dependências mínimas
pip install python-dotenv

# Preencher variáveis
cp .env.example .env   # edite com seus tokens

# Iniciar o terminal interativo
python -m agent_core

# Ou direto:
python agent_core/terminal.py
```

Você verá:
```
╔══════════════════════════════════════════════════════╗
║  🤖  AI Agent Swarm — Modo Autônomo                  ║
╚══════════════════════════════════════════════════════╝

▶ _
```

Digite qualquer tarefa. O agente planeja, executa e reporta em tempo real.

**Comandos do terminal:**
```
/model qwen_vision    trocar modelo
/dir /tmp/projeto     mudar diretório de trabalho
/clear                limpar histórico
/history              ver tarefas desta sessão
/tools                listar todas as tools
/exit                 sair
```

---

## 🟠 Passo 6 — Deploy no Kaggle

### 6.1 — GPU T4 × 2
**⚙️ Settings → Accelerator → GPU T4 × 2**

### 6.2 — Secrets
**⚙️ Settings → Add-ons → Secrets**

| Secret             | Valor                    | Obrigatório |
|--------------------|--------------------------|-------------|
| `G4F_API_KEY`      | `g4f_sua_chave`          | ✅           |
| `DISCORD_TOKEN`    | token do bot             | ✅           |
| `DISCORD_GUILD_ID` | ID do servidor           | ✅           |
| `HF_TOKEN`         | token HuggingFace        | Para mídia  |

HuggingFace: **https://huggingface.co/settings/tokens** → New token (Read)

### 6.3 — Executar `kaggle_setup.ipynb`

Células em ordem: **1** (GPU check) → **2** (instalar deps) → **3** (secrets) → **4** (clone) → **5** (probe modelos) → **6** (opcional: pré-carregar mídia) → **7** (bot rodando)

---

## 💬 Comandos Discord

### 🔥 Agente Autônomo (principal)
```
!task <descrição da tarefa>

Exemplos:
!task Crie um jogo Snake em Python com pygame, salve em /tmp/snake
!task Gere 3 thumbnails 1280x720 para vídeos de produtividade
!task Pesquise os 10 hooks virais mais usados no TikTok hoje
!task Instale o Godot headless e crie um projeto de plataforma 2D
!task Construa uma API REST em FastAPI com auth JWT em /tmp/api
!task Baixe este vídeo, analise a fórmula viral e replique em 3 variações

Flags:
--model qwen_vision   modelo LLM a usar
--dir /caminho        diretório de trabalho
```

### Geração de vídeo paralela (2 GPUs)
```
!parallel_video cena 1: praia ao pôr do sol | cena 2: cidade neon | cena 3: floresta
!gpu   → status de VRAM e modelos carregados
```

### Equipes especializadas
```
!marketing <msg>    🧠 Neuromarketing
!dev <msg>          💻 Dev & CyberSecurity
!design <msg>       🎨 Design & UX
!research <msg>     🔍 Research
!conteudo <msg>     🚀 Conteúdo Viral
```

### Geração individual
```
!imagine <prompt> [--steps 8] [--size 1024x1024] [--seed 42]
!video   <prompt> [--frames 97] [--fps 24] [--seed 42]
!analyse <url ou anexo> [pergunta]
```

### Skills inline
```
!marketing !search neuromarketing 2025   Analise o mercado
!dev       !url https://docs.api.com     Implemente um cliente
```

### Memória e mensagens
```
!memory <ag> list/set/get/del/search
!inbox <ag>
!msg <de> <para> <assunto>|<corpo>
!probe   → testa todos os modelos LLM
```

---

## 🛠️ Tools do Agente Autônomo

| Tool            | O que faz                                              |
|-----------------|--------------------------------------------------------|
| `bash`          | Executa qualquer comando shell (sudo disponível)       |
| `write_file`    | Cria/edita arquivos                                    |
| `read_file`     | Lê arquivos                                            |
| `list_dir`      | Lista diretórios                                       |
| `web_search`    | Pesquisa na web                                        |
| `fetch_url`     | Baixa conteúdo de URLs                                 |
| `generate_image`| Gera imagem com Z-Image-Turbo                          |
| `generate_video`| Gera vídeo com LTX-2.3                                 |
| `analyse_video` | Analisa vídeo frame-a-frame com visão                  |
| `think`         | Raciocínio interno (visível para o usuário)            |
| `report`        | Atualização de progresso em tempo real                 |
| `task_complete` | Finaliza a tarefa com resumo                           |

O agente pode encadear quantas tools precisar, em qualquer ordem, sem pedir aprovação.

---

## 🖥️ Mapa de VRAM (T4 × 2, 32GB total)

```
GPU 0 (16GB):  LTX-2.3 GGUF Q4 (~6GB) + Z-Image-Turbo (~10GB) = ~16GB
GPU 1 (16GB):  LTX-2.3 GGUF Q4 (~6GB)                         =  ~6GB
Buffer livre:  ~10GB para codecs, geração paralela, etc.
```

Com `!parallel_video`, GPU 0 e GPU 1 geram vídeos simultaneamente.

---

## 📋 Variáveis de ambiente

| Variável           | Onde obter                                |
|--------------------|-------------------------------------------|
| `G4F_API_KEY`      | https://g4f.dev → Dashboard → API Keys    |
| `DISCORD_TOKEN`    | discord.com/developers/applications       |
| `DISCORD_GUILD_ID` | Modo Dev ativo → botão direito no servidor|
| `HF_TOKEN`         | huggingface.co/settings/tokens            |
