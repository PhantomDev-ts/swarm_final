"""
Discord Bot — Interface principal do AI Agent Swarm V2
Comandos de texto + geração de imagem (Z-Image) e vídeo (LTX-2.3)
"""

import os, sys, asyncio, io, tempfile
from pathlib import Path

import discord
from discord.ext import commands

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DISCORD_TOKEN, DISCORD_PREFIX
from orchestrator import orchestrator
from agents.agent_definitions import ALL_AGENTS, AGENT_ALIASES
from agents.agent_engine import engine
from memory_system import save_memory, get_memory, list_memories, delete_memory, search_memory
from message_bus import send_message, get_unread, mark_all_read

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=DISCORD_PREFIX, intents=intents, help_command=None)


# ─── Helpers ─────────────────────────────────────────────────────────────────
def chunks(text: str, limit: int = 1900) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts = []
    while text:
        cut = text.rfind("\n", 0, limit) if len(text) > limit else len(text)
        if cut <= 0:
            cut = limit
        parts.append(text[:cut])
        text = text[cut:].lstrip()
    return parts


async def send_reply(ctx, text: str, agent_name: str = ""):
    ag     = ALL_AGENTS.get(agent_name)
    prefix = f"{ag.emoji} **[{ag.team}]**\n" if ag else ""
    for i, chunk in enumerate(chunks(text)):
        await ctx.send((prefix if i == 0 else "") + chunk)


def resolve_agent(name: str) -> str:
    return AGENT_ALIASES.get(name.lower(), name.lower())


def get_attachment_path(ctx) -> str | None:
    """Salva primeiro attachment de imagem/vídeo e retorna o path."""
    if ctx.message.attachments:
        att = ctx.message.attachments[0]
        ext = Path(att.filename).suffix.lower()
        if ext in (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".avi", ".mkv"):
            return att.url  # URL direta; analyse_video aceita URL via ffmpeg
    return None


# ─── Eventos ─────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Swarm V2 online: {bot.user}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="o swarm trabalhar 🤖"
    ))


@bot.event
async def on_command_error(ctx, error):
    if not isinstance(error, commands.CommandNotFound):
        await ctx.send(f"❌ {error}")


# ─── Equipes ─────────────────────────────────────────────────────────────────
@bot.command(name="marketing", aliases=["nm", "neuromarketing"])
async def cmd_marketing(ctx, *, message: str):
    img = get_attachment_path(ctx)
    async with ctx.typing():
        _, reply = orchestrator.route(message, "neuromarketing", ctx.author.display_name, img)
    await send_reply(ctx, reply, "neuromarketing")


@bot.command(name="dev", aliases=["cyber", "codigo", "programar"])
async def cmd_dev(ctx, *, message: str):
    img = get_attachment_path(ctx)
    async with ctx.typing():
        _, reply = orchestrator.route(message, "dev", ctx.author.display_name, img)
    await send_reply(ctx, reply, "dev")


@bot.command(name="design", aliases=["ux", "ui"])
async def cmd_design(ctx, *, message: str):
    img = get_attachment_path(ctx)
    async with ctx.typing():
        _, reply = orchestrator.route(message, "design", ctx.author.display_name, img)
    await send_reply(ctx, reply, "design")


@bot.command(name="research", aliases=["pesquisa", "intel"])
async def cmd_research(ctx, *, message: str):
    async with ctx.typing():
        _, reply = orchestrator.route(message, "research", ctx.author.display_name)
    await send_reply(ctx, reply, "research")


@bot.command(name="conteudo", aliases=["viral", "content", "tiktok"])
async def cmd_conteudo(ctx, *, message: str):
    img = get_attachment_path(ctx)
    async with ctx.typing():
        _, reply = orchestrator.route(message, "conteudo", ctx.author.display_name, img)
    await send_reply(ctx, reply, "conteudo")


# ─── Roteamento automático ────────────────────────────────────────────────────
@bot.command(name="swarm")
async def cmd_swarm(ctx, *, message: str):
    """Orquestrador decide qual equipe responde."""
    img = get_attachment_path(ctx)
    async with ctx.typing():
        agent, reply = orchestrator.route(message, user_display=ctx.author.display_name, image_path=img)
    await send_reply(ctx, reply, agent)


# ─── Colaboração ─────────────────────────────────────────────────────────────
@bot.command(name="collab")
async def cmd_collab(ctx, from_ag: str, to_ag: str, *, task: str):
    """!collab design dev Implemente este wireframe em React"""
    fa = resolve_agent(from_ag)
    ta = resolve_agent(to_ag)
    if fa not in ALL_AGENTS or ta not in ALL_AGENTS:
        await ctx.send(f"❌ Agentes inválidos. Use: {', '.join(ALL_AGENTS)}")
        return
    async with ctx.typing():
        reply = orchestrator.collaborate(fa, ta, task)
    await send_reply(ctx, f"🔀 **{fa} → {ta}**\n{reply}", ta)


@bot.command(name="broadcast")
async def cmd_broadcast(ctx, *, message: str):
    """Envia para todas as equipes e coleta respostas."""
    await ctx.send("📡 **Broadcast iniciado...**")
    async with ctx.typing():
        results = orchestrator.broadcast(message, ctx.author.display_name)
    for ag_name, reply in results.items():
        ag = ALL_AGENTS[ag_name]
        preview = reply[:350] + ("..." if len(reply) > 350 else "")
        await ctx.send(f"{ag.emoji} **[{ag.team}]**\n{preview}")


# ─── Geração de imagem ────────────────────────────────────────────────────────
@bot.command(name="imagine", aliases=["img", "image"])
async def cmd_imagine(ctx, *, prompt: str):
    """
    Gera imagem com Z-Image-Turbo.
    !imagine retrato fotorrealista de mulher em cenário urbano noturno, neon lights
    
    Flags opcionais no final do prompt:
    --steps 8  --size 1024x1024  --seed 42
    """
    import re

    steps  = 8
    w, h   = 1024, 1024
    seed   = -1

    for m in re.finditer(r"--steps\s+(\d+)", prompt):
        steps  = int(m.group(1))
        prompt = prompt.replace(m.group(0), "").strip()

    for m in re.finditer(r"--size\s+(\d+)x(\d+)", prompt):
        w, h   = int(m.group(1)), int(m.group(2))
        prompt = prompt.replace(m.group(0), "").strip()

    for m in re.finditer(r"--seed\s+(\d+)", prompt):
        seed   = int(m.group(1))
        prompt = prompt.replace(m.group(0), "").strip()

    await ctx.send(f"🖼️ Gerando imagem... `{prompt[:80]}`")
    async with ctx.typing():
        try:
            from media_engine import generate_image
            path = await asyncio.get_event_loop().run_in_executor(
                None, lambda: generate_image(prompt, width=w, height=h, steps=steps, seed=seed)
            )
            await ctx.send(file=discord.File(path))
        except Exception as e:
            await ctx.send(f"❌ Erro na geração: {e}")


# ─── Geração de vídeo ─────────────────────────────────────────────────────────
@bot.command(name="video", aliases=["vid", "ltxv"])
async def cmd_video(ctx, *, prompt: str):
    """
    Gera vídeo com LTX-2.3.
    !video pessoa caminhando numa praia ao pôr do sol, câmera lenta, golden hour
    
    Flags: --frames 97  --fps 24  --seed 42
    """
    import re

    frames = 97
    fps    = 24
    seed   = -1

    for m in re.finditer(r"--frames\s+(\d+)", prompt):
        frames = int(m.group(1))
        prompt = prompt.replace(m.group(0), "").strip()

    for m in re.finditer(r"--fps\s+(\d+)", prompt):
        fps    = int(m.group(1))
        prompt = prompt.replace(m.group(0), "").strip()

    for m in re.finditer(r"--seed\s+(\d+)", prompt):
        seed   = int(m.group(1))
        prompt = prompt.replace(m.group(0), "").strip()

    await ctx.send(f"🎬 Gerando vídeo ({frames} frames, {fps}fps)... isso pode levar alguns minutos no Kaggle T4.")
    async with ctx.typing():
        try:
            from media_engine import generate_video
            path = await asyncio.get_event_loop().run_in_executor(
                None, lambda: generate_video(prompt, num_frames=frames, fps=fps, seed=seed)
            )
            size_mb = Path(path).stat().st_size / 1_000_000
            if size_mb < 8:
                await ctx.send(file=discord.File(path))
            else:
                await ctx.send(f"✅ Vídeo gerado: `{path}` ({size_mb:.1f}MB — grande demais para Discord, salvo localmente)")
        except Exception as e:
            await ctx.send(f"❌ Erro: {e}")


# ─── Análise de vídeo ─────────────────────────────────────────────────────────
@bot.command(name="analyse", aliases=["analisar", "av"])
async def cmd_analyse(ctx, video_url: str = "", *, question: str = ""):
    """
    Analisa vídeo com ffmpeg + IA de visão.
    Anexe um vídeo OU passe uma URL:
    !analyse https://... Como posso replicar os padrões virais deste vídeo?
    """
    url = video_url or (ctx.message.attachments[0].url if ctx.message.attachments else "")
    if not url:
        await ctx.send("❌ Forneça uma URL de vídeo ou anexe um arquivo.")
        return

    q = question or "Identifique padrões virais, hooks visuais, ritmo de edição e fórmula replicável."
    await ctx.send(f"🔍 Analisando vídeo... aguarde.")
    async with ctx.typing():
        from skills.general.general_skills import analyse_video
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: analyse_video(url, question=q)
        )
    await send_reply(ctx, result, "conteudo")


# ─── Probe de modelos ─────────────────────────────────────────────────────────
@bot.command(name="probe", aliases=["testmodelos", "status"])
async def cmd_probe(ctx):
    """Testa todos os modelos LLM configurados."""
    from llm_engine import probe_model
    from config import G4F_MODELS

    await ctx.send("🔬 Testando modelos...")
    lines = []
    for key in G4F_MODELS:
        result = await asyncio.get_event_loop().run_in_executor(None, lambda k=key: probe_model(k))
        icon   = "✅" if result["ok"] else "❌"
        lines.append(f"{icon} `{key}` — {result['latency_ms']}ms — `{result['response_preview']}`")
    await ctx.send("\n".join(lines))


# ─── Memória ──────────────────────────────────────────────────────────────────
@bot.command(name="memory", aliases=["mem"])
async def cmd_memory(ctx, agent_name: str, action: str = "list", key: str = "", *, value: str = ""):
    """
    !memory dev list
    !memory dev set projeto MeuSaaS
    !memory dev get projeto
    !memory dev del projeto
    !memory dev search python
    """
    name = resolve_agent(agent_name)
    if name not in ALL_AGENTS:
        await ctx.send(f"❌ Agente inválido.")
        return

    ag = ALL_AGENTS[name]

    if action == "list":
        entries = list_memories(name)
        if not entries:
            await ctx.send(f"{ag.emoji} Memória de **{name}** vazia.")
            return
        lines = [f"{ag.emoji} **Memória de {name}** ({len(entries)} entradas):"]
        for e in entries[-20:]:
            tags = f" `{','.join(e.get('tags',[]))}`" if e.get("tags") else ""
            lines.append(f"• `{e['key']}` → {e['value'][:100]}{tags}")
        await ctx.send("\n".join(lines))

    elif action == "set":
        save_memory(name, key, value)
        await ctx.send(f"✅ `{key}` salvo em **{name}**")

    elif action == "get":
        v = get_memory(name, key)
        await ctx.send(f"`{key}` = {v}" if v else f"❌ `{key}` não encontrado.")

    elif action == "del":
        ok = delete_memory(name, key)
        await ctx.send(f"🗑️ Deletado." if ok else f"❌ `{key}` não encontrado.")

    elif action == "search":
        results = search_memory(name, key)
        if not results:
            await ctx.send(f"Nenhuma memória encontrada para '{key}'")
        else:
            lines = [f"🔍 {len(results)} resultados em **{name}**:"]
            for e in results[:10]:
                lines.append(f"• `{e['key']}` → {e['value'][:100]}")
            await ctx.send("\n".join(lines))


# ─── Mensagens ────────────────────────────────────────────────────────────────
@bot.command(name="inbox")
async def cmd_inbox(ctx, agent_name: str):
    """!inbox design"""
    name = resolve_agent(agent_name)
    msgs = get_unread(name)
    if not msgs:
        await ctx.send(f"📭 **{name}** — sem mensagens.")
        return
    lines = [f"📬 **Inbox de {name}** ({len(msgs)} não lidas):"]
    for m in msgs:
        pri = {"urgent": "🔴", "high": "🟡"}.get(m["priority"], "⚪")
        lines.append(f"{pri} `[{m['id']}]` De **{m['from']}** | {m['subject']}\n  {m['body'][:120]}")
    await ctx.send("\n".join(lines))


@bot.command(name="msg")
async def cmd_msg(ctx, from_ag: str, to_ag: str, *, content: str):
    """!msg design dev Wireframe pronto|Acesse /drive/wire.fig"""
    fa, ta = resolve_agent(from_ag), resolve_agent(to_ag)
    if fa not in ALL_AGENTS or ta not in ALL_AGENTS:
        await ctx.send("❌ Agentes inválidos.")
        return
    parts   = content.split("|", 1)
    subject = parts[0].strip()
    body    = parts[1].strip() if len(parts) > 1 else subject
    mid     = send_message(fa, ta, subject, body)
    await ctx.send(f"✉️ `{mid}` enviado: **{fa}** → **{ta}** | {subject}")


# ─── Ajuda ────────────────────────────────────────────────────────────────────
@bot.command(name="help")
async def cmd_help(ctx):
    await ctx.send("""
🤖 **AI Agent Swarm V2**

**🔥 Agente Autônomo (novo):**
`!task <tarefa>` — executa qualquer coisa do início ao fim, sozinho
`!parallel_video p1 | p2 | p3` — gera vídeos nas 2 GPUs em paralelo
`!gpu` — status de VRAM e modelos carregados

Exemplos de `!task`:
→ `!task Crie um jogo Snake em Python com pygame`
→ `!task Gere 5 thumbnails para o canal de produtividade`
→ `!task Pesquise os hooks virais do TikTok hoje e monte relatório`
→ `!task Instale o Godot e crie um jogo simples em /tmp/game`

**Equipes:**
`!marketing` `!dev` `!design` `!research` `!conteudo`
Aliases: `!nm` `!cyber` `!ux` `!pesquisa` `!viral`

**Orquestrador:**
`!swarm <msg>` — roteamento automático
`!collab <de> <para>` — colaboração entre equipes
`!broadcast <msg>` — todos respondem

**Geração de mídia:**
`!imagine <prompt>` — imagem (Z-Image-Turbo)
`!video <prompt>` — vídeo (LTX-2.3)
`!analyse <url>` — analisa vídeo frame-a-frame

**Skills inline:**
`!search` `!url` `!calc` `!date` `!analyse`

**Memória:**
`!memory <ag> list/set/get/del/search`

**Mensagens:**
`!inbox <ag>` `!msg <de> <para> <assunto>|<corpo>`

**Flags de geração:**
`--steps 8` `--size 1024x1024` `--seed 42` `--frames 97` `--fps 24`
`--model qwen_vision` `--dir /caminho` (para !task)
""")


# ─── Agente Autônomo ─────────────────────────────────────────────────────────
@bot.command(name="task", aliases=["do", "agent", "auto"])
async def cmd_task(ctx, *, task: str):
    """
    Agente autônomo — executa qualquer tarefa do início ao fim.
    Streama o progresso em tempo real no canal.

    Exemplos:
      !task Crie um jogo Snake em Python com pygame e salve em /tmp/snake
      !task Gere 3 vídeos curtos de produtos com LTX e crie thumbnails com Z-Image
      !task Pesquise os top 10 hooks virais do TikTok hoje e monte um relatório
      !task Instale o Godot headless e exporte este projeto: /tmp/meu_jogo

    Flags:
      --model qwen_vision   escolhe o modelo (padrão: qwen_vision)
      --dir /caminho        diretório de trabalho
    """
    import re as _re

    model_key = "qwen_vision"
    workdir   = "/kaggle/working"

    for m in _re.finditer(r"--model\s+(\S+)", task):
        model_key = m.group(1)
        task = task.replace(m.group(0), "").strip()

    for m in _re.finditer(r"--dir\s+(\S+)", task):
        workdir = m.group(1)
        task = task.replace(m.group(0), "").strip()

    from agent_core.discord_agent import DiscordTaskRunner
    runner = DiscordTaskRunner(model_key=model_key)
    await runner.run_task(task, channel=ctx.channel, workdir=workdir)


@bot.command(name="media_status", aliases=["vram", "gpu"])
async def cmd_media_status(ctx):
    """Mostra uso de VRAM e modelos de mídia carregados."""
    from media_engine import system_status
    await ctx.send(system_status())


@bot.command(name="parallel_video", aliases=["pvid"])
async def cmd_parallel_video(ctx, *, prompts_raw: str):
    """
    Gera múltiplos vídeos em paralelo nas duas GPUs T4.
    Separe os prompts com | (pipe).

    Exemplo:
      !parallel_video praia ao pôr do sol | cidade neon à noite | floresta com névoa
    """
    prompts = [p.strip() for p in prompts_raw.split("|") if p.strip()]
    if not prompts:
        await ctx.send("❌ Forneça ao menos um prompt.")
        return

    await ctx.send(f"🎬 Gerando **{len(prompts)}** vídeos em paralelo (GPU 0 + GPU 1)...")
    async with ctx.typing():
        from media_engine import generate_videos_parallel
        paths = await asyncio.get_event_loop().run_in_executor(
            None, lambda: generate_videos_parallel(prompts)
        )
    for i, path in enumerate(paths):
        size_mb = Path(path).stat().st_size / 1_000_000
        if size_mb < 8:
            await ctx.send(
                content=f"🎬 Vídeo {i+1}/{len(paths)}: `{Path(path).name}`",
                file=discord.File(path),
            )
        else:
            await ctx.send(f"🎬 Vídeo {i+1}: `{path}` ({size_mb:.1f}MB — salvo localmente)")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN não definido.")
        sys.exit(1)
    bot.run(DISCORD_TOKEN)
