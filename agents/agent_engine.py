"""
Agent Engine — executa agentes, parseia skill calls, gerencia histórico.
"""

import re, json, sys, os
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import TEAM_DEFAULT_MODEL, MAX_HISTORY, LOGS_DIR
from llm_engine import call_llm
from memory_system import format_for_prompt, auto_extract_memories
from message_bus import format_for_prompt as inbox_prompt, mark_all_read
from agents.agent_definitions import ALL_AGENTS, AgentDef
from skills.general.general_skills import (
    web_search, fetch_url, analyse_video,
    get_datetime, calculate, summarize_text,
    GENERAL_SKILLS_DESCRIPTION,
)

LOGS_DIR.mkdir(parents=True, exist_ok=True)


class AgentEngine:
    def __init__(self):
        self._histories: dict[str, list] = {}

    def run(
        self,
        agent_name: str,
        user_message: str,
        user_display: str = "Usuário",
        image_path: Optional[str] = None,
        extra_context: str = "",
    ) -> str:
        if agent_name not in ALL_AGENTS:
            return f"❌ Agente '{agent_name}' inválido. Disponíveis: {list(ALL_AGENTS.keys())}"

        agent: AgentDef = ALL_AGENTS[agent_name]

        # Pré-processa skill calls inline (!search, !url, !calc, !date, !analyse)
        user_message, pre_skill_result = self._execute_inline_skills(user_message)

        # Monta system prompt
        memory_block = format_for_prompt(agent_name)
        inbox_block  = inbox_prompt(agent_name)
        system       = agent.system_prompt.format(
            memory=memory_block or "Nenhuma memória ainda.",
            inbox=inbox_block  or "Nenhuma mensagem.",
        )
        system += GENERAL_SKILLS_DESCRIPTION
        if extra_context:
            system += f"\n\nCONTEXTO ADICIONAL:\n{extra_context}"
        if pre_skill_result:
            system += f"\n\n📊 RESULTADO DE SKILL PRÉ-EXECUTADA:\n{pre_skill_result}"

        # Histórico de conversa
        hist = self._histories.setdefault(agent_name, [])
        hist.append({"role": "user", "content": f"[{user_display}]: {user_message}"})
        if len(hist) > MAX_HISTORY * 2:
            self._histories[agent_name] = hist[-(MAX_HISTORY * 2):]
            hist = self._histories[agent_name]

        # Chamada LLM
        model_key = TEAM_DEFAULT_MODEL.get(agent_name, "gemini_flash")
        reply     = call_llm(
            model_key,
            hist,
            system=system,
            image_path=image_path,
            temperature=0.88,
        )

        hist.append({"role": "assistant", "content": reply})

        # Pós-processamento: executa skill calls no reply
        reply = self._execute_reply_skills(agent_name, reply)

        # Salva memórias automáticas
        saved = auto_extract_memories(agent_name, reply)

        # Limpa inbox
        mark_all_read(agent_name)

        # Log
        self._log(agent_name, user_display, user_message, reply, saved)

        return reply

    # ─── Inline skills (!comando no texto do usuário) ─────────────────────────
    def _execute_inline_skills(self, message: str) -> tuple[str, str]:
        results: list[str] = []

        # !search <query>
        for m in re.finditer(r"!search\s+(.+?)(?=\s*!|\s*$)", message, re.IGNORECASE):
            q = m.group(1).strip()
            results.append(f"🔍 web_search('{q}'):\n{web_search(q)}")
            message = message.replace(m.group(0), "").strip()

        # !url <link>
        for m in re.finditer(r"!url\s+(https?://\S+)", message, re.IGNORECASE):
            url = m.group(1)
            results.append(f"🌐 fetch_url('{url}'):\n{fetch_url(url)}")
            message = message.replace(m.group(0), "").strip()

        # !calc <expr>
        for m in re.finditer(r"!calc\s+([0-9+\-*/.()%\s]+)", message, re.IGNORECASE):
            expr = m.group(1).strip()
            results.append(f"🔢 calculate('{expr}') = {calculate(expr)}")
            message = message.replace(m.group(0), "").strip()

        # !date
        if "!date" in message.lower():
            results.append(f"📅 {get_datetime()}")
            message = re.sub(r"!date", "", message, flags=re.IGNORECASE).strip()

        # !analyse <path>
        for m in re.finditer(r"!analyse\s+(\S+\.(?:mp4|mov|avi|mkv|webm))", message, re.IGNORECASE):
            path = m.group(1)
            results.append(f"🎬 analyse_video('{path}'):\n{analyse_video(path)}")
            message = message.replace(m.group(0), "").strip()

        return message, "\n\n".join(results)

    # ─── Skill calls no reply do agente [SKILL: nome(args)] ──────────────────
    def _execute_reply_skills(self, agent_name: str, reply: str) -> str:
        skill_pattern = re.compile(
            r"\[SKILL:\s*(\w+)\(([^)]*)\)\]", re.IGNORECASE
        )
        for match in skill_pattern.finditer(reply):
            skill_name = match.group(1).lower()
            args_raw   = match.group(2).strip().strip("'\"")

            result = ""
            if skill_name == "web_search":
                result = web_search(args_raw)
            elif skill_name == "fetch_url":
                result = fetch_url(args_raw)
            elif skill_name == "calculate":
                result = calculate(args_raw)
            elif skill_name == "get_datetime":
                result = get_datetime()
            elif skill_name == "summarize_text":
                result = summarize_text(args_raw)
            elif skill_name == "analyse_video":
                result = analyse_video(args_raw)

            if result:
                reply = reply.replace(
                    match.group(0),
                    f"\n\n📊 **Resultado de {skill_name}:**\n{result}\n",
                )

        return reply

    def _log(self, agent, user, message, reply, memories_saved=0):
        log_path = LOGS_DIR / f"{agent}_log.jsonl"
        entry = {
            "ts":       datetime.now().isoformat(),
            "agent":    agent,
            "user":     user,
            "msg":      message[:400],
            "reply":    reply[:800],
            "mem_saved": memories_saved,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


engine = AgentEngine()
