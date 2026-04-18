"""
Sistema de Memória de Longo Prazo
Cada agente tem um <nome>_memory.txt persistido em JSON.
Suporta: save, get, list, delete, search.
"""

import os, json, uuid
from datetime import datetime
from typing import Optional
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from config import MEMORY_DIR

MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _path(agent: str) -> Path:
    return MEMORY_DIR / f"{agent}_memory.txt"


def _load(agent: str) -> list[dict]:
    p = _path(agent)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_all(agent: str, entries: list[dict]) -> None:
    if len(entries) > 500:
        entries = entries[-500:]
    _path(agent).write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def save_memory(agent: str, key: str, value: str, tags: list[str] = []) -> None:
    entries = _load(agent)
    now     = datetime.now().isoformat()
    for e in entries:
        if e.get("key") == key:
            e["value"]   = value
            e["updated"] = now
            e["tags"]    = tags or e.get("tags", [])
            _save_all(agent, entries)
            return
    entries.append({
        "id":      str(uuid.uuid4())[:8],
        "key":     key,
        "value":   value,
        "tags":    tags,
        "agent":   agent,
        "created": now,
        "updated": now,
    })
    _save_all(agent, entries)


def get_memory(agent: str, key: str) -> Optional[str]:
    for e in _load(agent):
        if e.get("key") == key:
            return e.get("value")
    return None


def search_memory(agent: str, query: str) -> list[dict]:
    q = query.lower()
    return [
        e for e in _load(agent)
        if q in e.get("key", "").lower() or q in e.get("value", "").lower()
        or any(q in t.lower() for t in e.get("tags", []))
    ]


def delete_memory(agent: str, key: str) -> bool:
    entries = _load(agent)
    new     = [e for e in entries if e.get("key") != key]
    if len(new) < len(entries):
        _save_all(agent, new)
        return True
    return False


def list_memories(agent: str) -> list[dict]:
    return _load(agent)


def format_for_prompt(agent: str, max_entries: int = 25) -> str:
    entries = _load(agent)[-max_entries:]
    if not entries:
        return ""
    lines = ["\n╔══ MEMÓRIA DE LONGO PRAZO ═══════════════════════════╗"]
    for e in entries:
        lines.append(f"║  [{e['key']}] {e['value'][:120]}")
    lines.append("╚══════════════════════════════════════════════════════╝\n")
    return "\n".join(lines)


def auto_extract_memories(agent: str, reply: str) -> int:
    """
    Extrai e salva automaticamente memórias do formato:
    [MEMORY: chave = valor]
    [MEMORY: chave = valor | tag1,tag2]
    Retorna o número de memórias salvas.
    """
    import re
    pattern = r"\[MEMORY:\s*(.+?)\s*=\s*(.+?)(?:\s*\|\s*([^\]]+))?\]"
    found   = re.findall(pattern, reply)
    for key, value, tags_str in found:
        tags = [t.strip() for t in tags_str.split(",")] if tags_str else []
        save_memory(agent, key.strip(), value.strip(), tags)
    return len(found)
