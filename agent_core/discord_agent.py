"""
agent_core/discord_agent.py

Integração do agente autônomo com Discord.
!task  → executa tarefa autônoma, streama progresso no canal
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import discord
from agent_core.autonomous_agent import AutonomousAgent

# ─── Buffer de updates para Discord ──────────────────────────────────────────
class DiscordTaskRunner:
    """
    Roda o agente autônomo numa thread separada e streama
    o progresso para o canal Discord sem bloquear o bot.
    """

    def __init__(self, model_key: str = "qwen_vision"):
        self.model_key = model_key

    async def run_task(
        self,
        task:    str,
        channel: discord.TextChannel,
        workdir: str = "/kaggle/working",
    ):
        agent        = AutonomousAgent(model_key=self.model_key)
        loop         = asyncio.get_event_loop()
        buffer:list[str] = []
        flush_lock   = asyncio.Lock()
        done_event   = asyncio.Event()

        # Status message editável (atualizado a cada N updates)
        status_msg: discord.Message | None = None
        status_msg = await channel.send(
            f"🤖 **Agente iniciando tarefa...**\n```\n{task[:200]}\n```"
        )

        async def flush_buffer():
            """Envia acúmulo de updates como novas mensagens."""
            nonlocal buffer
            async with flush_lock:
                if not buffer:
                    return
                combined = "\n".join(buffer[:15])
                buffer   = buffer[15:]
                # Divide se necessário
                chunks = [combined[i:i+1800] for i in range(0, len(combined), 1800)]
                for chunk in chunks:
                    await channel.send(chunk)

        def on_update(msg: str):
            # Chamado da thread do agente — agenda flush no event loop
            buffer.append(msg)
            if len(buffer) >= 5:
                asyncio.run_coroutine_threadsafe(flush_buffer(), loop)

        # Roda o agente em thread separada para não bloquear o Discord
        async def run_in_thread():
            result = await loop.run_in_executor(
                None,
                lambda: agent.run(task, workdir=workdir, on_update=on_update),
            )
            return result

        try:
            await asyncio.wait_for(run_in_thread(), timeout=3600)  # 1h máx
        except asyncio.TimeoutError:
            await channel.send("⚠️ **Timeout** — tarefa excedeu 1 hora.")
        except Exception as e:
            await channel.send(f"❌ **Erro no agente:** {e}")
        finally:
            # Flush final
            await flush_buffer()
            done_event.set()


runner = DiscordTaskRunner(model_key="qwen_vision")
