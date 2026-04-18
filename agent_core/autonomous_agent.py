"""
agent_core/autonomous_agent.py

Agente autônomo com agentic loop completo.
- Planeja, executa, observa, itera — sem pedir aprovação
- Instala dependências por conta própria quando precisa
- Reporta progresso em tempo real via callback (Discord ou terminal)
- Cada tool call é real: bash, arquivos, web, mídia, análise de vídeo
"""

import os
import sys
import json
import re
import subprocess
import tempfile
import shutil
import textwrap
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_engine import call_llm
from config import TEAM_DEFAULT_MODEL, LOGS_DIR

LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ─── Definição das tools disponíveis ─────────────────────────────────────────

TOOLS_SCHEMA = [
    {
        "name": "bash",
        "description": (
            "Executa qualquer comando bash/shell. Use para: instalar pacotes, "
            "rodar scripts, compilar, chamar CLIs (ffmpeg, git, godot, blender...), "
            "criar processos, verificar o sistema. Sudo disponível no Kaggle."
        ),
        "parameters": {
            "command": "string — o comando bash completo a executar",
            "timeout": "int — segundos máximos (padrão 120, máx 600)",
            "workdir": "string — diretório de trabalho (opcional)",
        },
    },
    {
        "name": "write_file",
        "description": "Cria ou sobrescreve um arquivo com conteúdo fornecido.",
        "parameters": {
            "path":    "string — caminho completo do arquivo",
            "content": "string — conteúdo a escrever",
        },
    },
    {
        "name": "read_file",
        "description": "Lê o conteúdo de um arquivo.",
        "parameters": {
            "path":      "string — caminho do arquivo",
            "max_chars": "int — máximo de caracteres (padrão 8000)",
        },
    },
    {
        "name": "list_dir",
        "description": "Lista arquivos e diretórios em um caminho.",
        "parameters": {
            "path":      "string — diretório a listar",
            "recursive": "bool — listar recursivamente (padrão false)",
        },
    },
    {
        "name": "web_search",
        "description": "Pesquisa na web. Use para documentação, exemplos, tutoriais, versões de pacotes.",
        "parameters": {
            "query": "string — query de busca",
        },
    },
    {
        "name": "fetch_url",
        "description": "Baixa e extrai texto de uma URL. Use para ler documentação, READMEs, APIs.",
        "parameters": {
            "url":       "string — URL completa",
            "max_chars": "int — máximo de caracteres (padrão 6000)",
        },
    },
    {
        "name": "generate_image",
        "description": "Gera uma imagem com Z-Image-Turbo. Retorna o caminho do arquivo.",
        "parameters": {
            "prompt":   "string — descrição da imagem",
            "width":    "int — largura (padrão 1024)",
            "height":   "int — altura (padrão 1024)",
            "steps":    "int — passos de inferência (padrão 8)",
        },
    },
    {
        "name": "generate_video",
        "description": "Gera um vídeo com LTX-2.3. Retorna o caminho do arquivo.",
        "parameters": {
            "prompt":     "string — descrição do vídeo com movimento",
            "num_frames": "int — frames: 49/65/97/121/161 (padrão 97 ≈ 4s)",
            "fps":        "int — frames por segundo (padrão 24)",
        },
    },
    {
        "name": "analyse_video",
        "description": "Analisa vídeo frame-a-frame com IA de visão. Identifica padrões, hooks, fórmulas virais.",
        "parameters": {
            "video_path": "string — caminho ou URL do vídeo",
            "question":   "string — o que analisar (opcional)",
        },
    },
    {
        "name": "think",
        "description": (
            "Raciocínio interno — use para planejar próximos passos, "
            "analisar um resultado, decidir a melhor abordagem. "
            "O conteúdo é exibido ao usuário como raciocínio transparente."
        ),
        "parameters": {
            "thought": "string — seu raciocínio",
        },
    },
    {
        "name": "report",
        "description": "Envia mensagem de progresso ao usuário sem pausar a execução.",
        "parameters": {
            "message": "string — atualização para o usuário",
        },
    },
    {
        "name": "task_complete",
        "description": "Marca a tarefa como concluída com um resumo final.",
        "parameters": {
            "summary": "string — o que foi feito e onde estão os arquivos/resultados",
        },
    },
]

TOOLS_DESCRIPTION = "\n".join(
    f"- **{t['name']}**: {t['description']}"
    for t in TOOLS_SCHEMA
)

# ─── System prompt do agente autônomo ────────────────────────────────────────

AUTONOMOUS_SYSTEM_PROMPT = """Você é um AGENTE AUTÔNOMO de alto nível operando num ambiente Linux com GPU.

IDENTIDADE:
- Você executa tarefas complexas do início ao fim, sozinho
- Você NUNCA pede permissão para continuar — você age e reporta
- Você instala o que precisar (pip, apt, npm, cargo, etc.)
- Você pesquisa documentação quando não sabe algo
- Você itera quando algo falha: lê o erro, pensa, tenta de novo
- Você explica o que está fazendo em tempo real via `report` e `think`

MENTALIDADE:
- Se precisar do Godot: instala o Godot
- Se precisar do FFmpeg: instala o FFmpeg
- Se precisar de uma lib obscura: busca no PyPI ou GitHub e instala
- Você não diz "não posso" — você encontra um caminho
- Erros são informação, não motivo para parar

FORMATO DE RESPOSTA — USE SEMPRE ESTE JSON:
Responda APENAS com um objeto JSON com esta estrutura:

{
  "tool": "nome_da_tool",
  "args": { ... argumentos da tool ... }
}

OU, quando quiser chamar múltiplas tools em sequência, responda com uma lista:
[
  {"tool": "think", "args": {"thought": "Vou primeiro instalar..."}},
  {"tool": "bash",  "args": {"command": "pip install ..."}},
  {"tool": "report","args": {"message": "Instalando dependências..."}}
]

TOOLS DISPONÍVEIS:
""" + TOOLS_DESCRIPTION + """

REGRAS:
1. Sempre comece com `think` para planejar
2. Use `report` para atualizar o usuário a cada etapa significativa
3. Quando algo falha, use `think` para diagnosticar antes de tentar de novo
4. Termine SEMPRE com `task_complete` quando a tarefa estiver pronta
5. Nunca invente resultados de tools — você receberá os resultados reais
6. Se um comando demora muito, divida em etapas menores

AMBIENTE:
- Sistema: Linux (Kaggle/Ubuntu)
- GPU: NVIDIA T4 × 2 disponíveis
- Python: 3.11+
- Diretório de trabalho: /kaggle/working/ (ou o informado)
- Sudo: disponível
"""


# ─── Executor de tools ────────────────────────────────────────────────────────

class ToolExecutor:
    def execute(self, tool_name: str, args: dict) -> str:
        fn = getattr(self, f"_tool_{tool_name}", None)
        if fn is None:
            return f"[ERRO] Tool '{tool_name}' não existe."
        try:
            return fn(**args)
        except TypeError as e:
            return f"[ERRO] Argumentos inválidos para {tool_name}: {e}"
        except Exception as e:
            return f"[ERRO] {tool_name} falhou: {type(e).__name__}: {e}"

    def _tool_bash(self, command: str, timeout: int = 120, workdir: str = "") -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=min(int(timeout), 600),
                cwd=workdir or None,
            )
            out  = result.stdout.strip()[-4000:] if result.stdout else ""
            err  = result.stderr.strip()[-2000:] if result.stderr else ""
            code = result.returncode

            parts = []
            if out:
                parts.append(f"STDOUT:\n{out}")
            if err:
                parts.append(f"STDERR:\n{err}")
            parts.append(f"EXIT CODE: {code}")
            return "\n".join(parts) or "(sem output)"

        except subprocess.TimeoutExpired:
            return f"[TIMEOUT] Comando excedeu {timeout}s"

    def _tool_write_file(self, path: str, content: str) -> str:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"✅ Arquivo escrito: {path} ({len(content)} chars)"

    def _tool_read_file(self, path: str, max_chars: int = 8000) -> str:
        p = Path(path)
        if not p.exists():
            return f"[ERRO] Arquivo não encontrado: {path}"
        content = p.read_text(encoding="utf-8", errors="ignore")
        if len(content) > max_chars:
            return content[:max_chars] + f"\n... [truncado em {max_chars} chars]"
        return content

    def _tool_list_dir(self, path: str, recursive: bool = False) -> str:
        p = Path(path)
        if not p.exists():
            return f"[ERRO] Diretório não encontrado: {path}"
        if recursive:
            items = sorted(p.rglob("*"))
        else:
            items = sorted(p.iterdir())
        lines = []
        for item in items[:200]:
            size = ""
            if item.is_file():
                try:
                    size = f" ({item.stat().st_size:,} bytes)"
                except Exception:
                    pass
            lines.append(f"{'📁' if item.is_dir() else '📄'} {item}{size}")
        if not lines:
            return "(diretório vazio)"
        result = "\n".join(lines)
        if len(items) > 200:
            result += f"\n... e mais {len(items)-200} itens"
        return result

    def _tool_web_search(self, query: str) -> str:
        from skills.general.general_skills import web_search
        return web_search(query)

    def _tool_fetch_url(self, url: str, max_chars: int = 6000) -> str:
        from skills.general.general_skills import fetch_url
        return fetch_url(url, max_chars=max_chars)

    def _tool_generate_image(
        self, prompt: str, width: int = 1024, height: int = 1024, steps: int = 8
    ) -> str:
        from media_engine import generate_image
        return generate_image(prompt, width=width, height=height, steps=steps)

    def _tool_generate_video(
        self, prompt: str, num_frames: int = 97, fps: int = 24
    ) -> str:
        from media_engine import generate_video
        return generate_video(prompt, num_frames=num_frames, fps=fps)

    def _tool_analyse_video(self, video_path: str, question: str = "") -> str:
        from skills.general.general_skills import analyse_video
        return analyse_video(
            video_path,
            question=question or "Identifique padrões virais, hooks e fórmula replicável.",
        )

    def _tool_think(self, thought: str) -> str:
        return f"💭 {thought}"

    def _tool_report(self, message: str) -> str:
        return f"📢 {message}"

    def _tool_task_complete(self, summary: str) -> str:
        return f"✅ TAREFA CONCLUÍDA\n{summary}"


# ─── Agentic Loop ─────────────────────────────────────────────────────────────

class AutonomousAgent:
    MAX_STEPS = 40  # limite de segurança por tarefa

    def __init__(self, model_key: str = "qwen_vision"):
        self.model_key = model_key
        self.executor  = ToolExecutor()
        self._history: list[dict] = []

    def run(
        self,
        task: str,
        workdir: str = "/kaggle/working",
        on_update: Optional[Callable[[str], None]] = None,
    ) -> str:
        """
        Executa uma tarefa autonomamente.

        Args:
            task:      descrição da tarefa
            workdir:   diretório de trabalho
            on_update: callback chamado a cada etapa (para Discord/terminal)
        """
        def emit(msg: str):
            if on_update:
                on_update(msg)
            else:
                print(msg)

        system = AUTONOMOUS_SYSTEM_PROMPT + f"\n\nDIRETÓRIO DE TRABALHO: {workdir}"

        # Inicializa histórico
        self._history = [{"role": "user", "content": task}]

        emit(f"🤖 **Agente autônomo iniciado**\n📋 Tarefa: {task[:200]}")

        for step in range(self.MAX_STEPS):
            # Chama o LLM
            raw = call_llm(
                self.model_key,
                self._history,
                system=system,
                temperature=0.3,
            )

            # Parse do JSON de tool call
            tool_calls = self._parse_tool_calls(raw)
            if not tool_calls:
                # LLM respondeu texto puro — trata como report final
                emit(f"💬 {raw[:1000]}")
                self._history.append({"role": "assistant", "content": raw})
                break

            # Executa cada tool call
            all_results: list[str] = []
            finished = False

            for call in tool_calls:
                tool_name = call.get("tool", "")
                args      = call.get("args", {})

                # Injeta workdir no bash se não especificado
                if tool_name == "bash" and "workdir" not in args:
                    args["workdir"] = workdir

                result = self.executor.execute(tool_name, args)
                all_results.append(f"[{tool_name}] → {result}")

                # Emite para o usuário
                if tool_name == "think":
                    emit(f"💭 _{args.get('thought', '')}_ ")
                elif tool_name == "report":
                    emit(f"⚡ {args.get('message', '')}")
                elif tool_name == "task_complete":
                    emit(f"✅ **Concluído!**\n{args.get('summary', '')}")
                    finished = True
                elif tool_name in ("generate_image", "generate_video"):
                    emit(f"🎨 Gerando `{tool_name}`...")
                else:
                    # Mostra preview do resultado
                    preview = result[:300].replace("\n", " ")
                    emit(f"🔧 `{tool_name}` → {preview}")

            # Adiciona ao histórico
            assistant_content = json.dumps(tool_calls, ensure_ascii=False)
            self._history.append({"role": "assistant", "content": assistant_content})

            results_msg = "\n".join(all_results)
            self._history.append({"role": "user", "content": f"RESULTADOS:\n{results_msg}"})

            # Log
            self._log(task, step, tool_calls, all_results)

            if finished:
                return results_msg

        return "⚠️ Limite de passos atingido. Tarefa pode estar incompleta."

    def _parse_tool_calls(self, raw: str) -> list[dict]:
        """Extrai tool calls do JSON retornado pelo LLM."""
        # Remove markdown code fences se presentes
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*",     "", raw)
        raw = raw.strip()

        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return [parsed]
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            # Tenta extrair JSON do meio de texto
            match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(1))
                    if isinstance(parsed, dict):
                        return [parsed]
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
        return []

    def _log(self, task: str, step: int, calls: list, results: list) -> None:
        log_path = LOGS_DIR / "autonomous_agent.jsonl"
        entry = {
            "ts":    datetime.now().isoformat(),
            "task":  task[:200],
            "step":  step,
            "calls": [c.get("tool") for c in calls],
            "ok":    not any("ERRO" in r for r in results),
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─── Singleton ────────────────────────────────────────────────────────────────
autonomous = AutonomousAgent(model_key="qwen_vision")
