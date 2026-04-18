"""
agent_core/terminal.py

Interface de terminal interativo — tipo Claude Code.
Execute: python -m agent_core.terminal
Ou:      python agent_core/terminal.py
"""

import sys
import os
import threading
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_core.autonomous_agent import AutonomousAgent

# ─── Cores ANSI ───────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CYAN   = "\033[36m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BLUE   = "\033[34m"
MAGENTA= "\033[35m"
RED    = "\033[31m"
WHITE  = "\033[97m"

def c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"


# ─── Spinner ──────────────────────────────────────────────────────────────────
class Spinner:
    FRAMES = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]

    def __init__(self, label: str = "Pensando"):
        self._label   = label
        self._running = False
        self._thread  = None
        self._i       = 0

    def start(self):
        self._running = True
        self._thread  = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self, clear: bool = True):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        if clear:
            sys.stdout.write("\r\033[K")
            sys.stdout.flush()

    def _spin(self):
        import time
        while self._running:
            frame = self.FRAMES[self._i % len(self.FRAMES)]
            sys.stdout.write(f"\r{c(CYAN, frame)} {c(DIM, self._label)}...")
            sys.stdout.flush()
            self._i += 1
            time.sleep(0.1)


# ─── Formatação de output ─────────────────────────────────────────────────────
def fmt_update(msg: str) -> str:
    """Formata mensagens de progresso do agente."""
    if msg.startswith("💭"):
        return c(DIM, msg)
    if msg.startswith("⚡"):
        return c(YELLOW, msg)
    if msg.startswith("🔧"):
        return c(BLUE, msg)
    if msg.startswith("✅"):
        return c(GREEN, BOLD + msg + RESET)
    if msg.startswith("❌") or "ERRO" in msg:
        return c(RED, msg)
    if msg.startswith("🎨"):
        return c(MAGENTA, msg)
    return msg


# ─── Banner ───────────────────────────────────────────────────────────────────
MASCOT = f"""
{c(CYAN, '     ░░░░░░░░░░░░  ')}
{c(CYAN, '   ░░            ░░')}
{c(CYAN, '  ░  ◉◉    ◉◉     ░')}
{c(CYAN, '  ░     ──        ░')}  {c(WHITE, BOLD + 'AI AGENT SWARM')}
{c(CYAN, '   ░░░░   ░░░░░░░ ░')}  {c(DIM, 'powered by g4f.dev')}
{c(CYAN, '       ╠   ╣      ')}
{c(CYAN, '       ║   ║      ')}
{c(CYAN, '      _╝   ╚_     ')}
{c(CYAN, '  ' + BOLD + '     BYTE      ')}
"""

BANNER = f"""
{c(CYAN, BOLD + '╔══════════════════════════════════════════════════════════╗')}
{c(CYAN, BOLD + '║')}  {c(WHITE, BOLD + '🤖  AI Agent Swarm — Agente Autônomo + OpenClaude')}  {c(CYAN, BOLD + '║')}
{c(CYAN, BOLD + '╚══════════════════════════════════════════════════════════╝')}
{MASCOT}
{c(DIM, 'Comandos especiais:')}
  {c(YELLOW, '/model <key>')}      trocar modelo  {c(DIM,'(gemini_flash | qwen_vision | glm | minimax)')}
  {c(YELLOW, '/dir <path>')}       mudar diretório de trabalho
  {c(YELLOW, '/clear')}            limpar histórico da sessão
  {c(YELLOW, '/history')}          ver tarefas desta sessão
  {c(YELLOW, '/tools')}            listar tools disponíveis
  {c(YELLOW, '/openclaude')}       lançar OpenClaude com g4f.dev {c(DIM,'(Claude Code completo)')}
  {c(YELLOW, '/exit')}             sair

{c(DIM, 'Exemplos de tarefas:')}
  {c(DIM, '→')} Crie um jogo Snake em Python com pygame
  {c(DIM, '→')} Analise este vídeo e extraia a fórmula viral: /path/video.mp4
  {c(DIM, '→')} Gere 5 imagens de produto para campanha no Instagram
  {c(DIM, '→')} Scrape os títulos dos top 20 vídeos de produtividade do YouTube
  {c(DIM, '→')} Construa uma API REST em FastAPI com auth JWT em /tmp/api
  {c(DIM, '→')} Instale o Godot headless e crie um jogo de plataforma 2D
"""


# ─── Loop principal ───────────────────────────────────────────────────────────
def main():
    print(BANNER)

    model_key = "qwen_vision"
    workdir   = os.getcwd()
    agent     = AutonomousAgent(model_key=model_key)
    history   = []   # histórico de tarefas da sessão

    print(c(DIM, f"  Modelo: {model_key}  |  Dir: {workdir}"))
    print(c(DIM, "  /openclaude [gemini|qwen|glm]  →  lança OpenClaude completo\n"))

    while True:
        try:
            raw = input(c(CYAN, BOLD + "▶ ") + c(WHITE, "")).strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{c(DIM, 'Saindo...')}")
            break

        if not raw:
            continue

        # ── Comandos especiais ────────────────────────────────────────────────
        if raw.startswith("/"):
            parts = raw.split(maxsplit=1)
            cmd   = parts[0].lower()

            if cmd == "/exit":
                print(c(DIM, "Até mais!"))
                break

            elif cmd == "/clear":
                agent = AutonomousAgent(model_key=model_key)
                print(c(GREEN, "✓ Histórico limpo."))

            elif cmd == "/model" and len(parts) > 1:
                model_key     = parts[1].strip()
                agent         = AutonomousAgent(model_key=model_key)
                print(c(GREEN, f"✓ Modelo: {model_key}"))

            elif cmd == "/dir" and len(parts) > 1:
                new_dir = parts[1].strip()
                if Path(new_dir).is_dir():
                    workdir = new_dir
                    os.chdir(workdir)
                    print(c(GREEN, f"✓ Diretório: {workdir}"))
                else:
                    print(c(RED, f"✗ Diretório não existe: {new_dir}"))

            elif cmd == "/openclaude":
                # Lança o OpenClaude com g4f.dev configurado
                import subprocess as _sp
                launch = Path(__file__).parent.parent / "scripts" / "launch_openclaude.sh"
                if not launch.exists():
                    print(c(RED, "✗ Execute primeiro: bash scripts/install_openclaude.sh"))
                else:
                    model_arg = parts[1] if len(parts) > 1 else "gemini"
                    print(c(GREEN, f"▸ Lançando OpenClaude com modelo: {model_arg}"))
                    print(c(DIM,   "  (OpenClaude tem bash, file edit, grep, glob + as tools do Swarm via MCP)"))
                    print()
                    os.execv("/bin/bash", ["/bin/bash", str(launch), model_arg])

            elif cmd == "/history":
                if not history:
                    print(c(DIM, "(nenhuma tarefa ainda)"))
                for i, t in enumerate(history[-10:], 1):
                    print(f"  {c(DIM, str(i)+'.')} {t[:80]}")

            elif cmd == "/tools":
                from agent_core.autonomous_agent import TOOLS_SCHEMA
                for t in TOOLS_SCHEMA:
                    print(f"  {c(YELLOW, t['name']):<25} {c(DIM, t['description'][:70])}")

            else:
                print(c(RED, f"Comando desconhecido: {cmd}"))

            continue

        # ── Tarefa para o agente ──────────────────────────────────────────────
        history.append(raw)
        spinner = Spinner("Agente trabalhando")
        spinner.start()
        _spinner_active = True

        updates: list[str] = []

        def on_update(msg: str):
            nonlocal _spinner_active
            if _spinner_active:
                spinner.stop()
                _spinner_active = False
                print()
            formatted = fmt_update(msg)
            print(formatted)
            updates.append(msg)

        try:
            result = agent.run(
                task=raw,
                workdir=workdir,
                on_update=on_update,
            )
            if _spinner_active:
                spinner.stop()
                print()

        except KeyboardInterrupt:
            spinner.stop()
            print(c(YELLOW, "\n⚠️  Interrompido pelo usuário."))
        except Exception as e:
            spinner.stop()
            print(c(RED, f"\n❌ Erro inesperado: {e}"))

        print(c(DIM, f"\n{'─'*54}\n"))


if __name__ == "__main__":
    main()
