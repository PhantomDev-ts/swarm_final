"""
Sistema de Mensagens Inter-Agentes
Fila persistida por JSON. Suporta prioridade, leitura e broadcast.
"""

import json, uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import MESSAGES_DIR

MESSAGES_DIR.mkdir(parents=True, exist_ok=True)


def _path(agent: str) -> Path:
    return MESSAGES_DIR / f"{agent}_inbox.json"


def _load(agent: str) -> list[dict]:
    p = _path(agent)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def _write(agent: str, inbox: list[dict]) -> None:
    if len(inbox) > 300:
        inbox = inbox[-300:]
    _path(agent).write_text(
        json.dumps(inbox, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def send_message(
    from_agent: str,
    to_agent: str,
    subject: str,
    body: str,
    priority: str = "normal",  # low | normal | high | urgent
) -> str:
    msg_id = str(uuid.uuid4())[:8]
    inbox  = _load(to_agent)
    inbox.append({
        "id":        msg_id,
        "from":      from_agent,
        "to":        to_agent,
        "subject":   subject,
        "body":      body,
        "priority":  priority,
        "timestamp": datetime.now().isoformat(),
        "read":      False,
    })
    _write(to_agent, inbox)
    return msg_id


def get_unread(agent: str) -> list[dict]:
    return [m for m in _load(agent) if not m.get("read")]


def mark_read(agent: str, msg_id: str) -> None:
    inbox = _load(agent)
    for m in inbox:
        if m.get("id") == msg_id:
            m["read"] = True
    _write(agent, inbox)


def mark_all_read(agent: str) -> None:
    inbox = _load(agent)
    for m in inbox:
        m["read"] = True
    _write(agent, inbox)


def format_for_prompt(agent: str) -> str:
    msgs = get_unread(agent)
    if not msgs:
        return ""
    lines = ["\n╔══ MENSAGENS NÃO LIDAS ══════════════════════════════╗"]
    for m in msgs[-5:]:
        pri = "🔴" if m["priority"] == "urgent" else "🟡" if m["priority"] == "high" else "⚪"
        lines.append(f"║  {pri} [{m['id']}] De {m['from']}: {m['subject']}")
        lines.append(f"║     {m['body'][:150]}")
    lines.append("╚══════════════════════════════════════════════════════╝\n")
    return "\n".join(lines)
