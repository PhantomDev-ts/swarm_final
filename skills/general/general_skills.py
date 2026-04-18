# SKILL.md — Skills Gerais do Swarm
# Acessíveis por TODOS os agentes, independente da equipe.

"""
skills/general/general_skills.py
Skills gerais disponíveis para todos os agentes do swarm.
"""

import os
import json
import datetime
import subprocess
import tempfile
import urllib.request
import urllib.parse
import urllib.error
import re
from pathlib import Path
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
#  WEB SEARCH  (DuckDuckGo Instant Answer — sem chave)
# ══════════════════════════════════════════════════════════════════════════════
def web_search(query: str, max_results: int = 6) -> str:
    """Busca na web via DuckDuckGo. Retorna resumo + links relevantes."""
    try:
        params  = urllib.parse.urlencode({"q": query, "format": "json", "no_html": 1, "skip_disambig": 1})
        req     = urllib.request.Request(
            f"https://api.duckduckgo.com/?{params}",
            headers={"User-Agent": "SwarmAgent/2.0"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())

        results: list[str] = []
        if data.get("AbstractText"):
            src = data.get("AbstractSource", "")
            results.append(f"📌 [{src}] {data['AbstractText'][:600]}")
        for item in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(item, dict) and item.get("Text"):
                url = item.get("FirstURL", "")
                results.append(f"• {item['Text'][:250]}  {url}")
        return "\n".join(results) if results else "Sem resultados diretos. Tente reformular a query."
    except Exception as e:
        return f"[web_search erro] {e}"


# ══════════════════════════════════════════════════════════════════════════════
#  FETCH URL  (extrai texto limpo de qualquer URL)
# ══════════════════════════════════════════════════════════════════════════════
def fetch_url(url: str, max_chars: int = 4000) -> str:
    """Acessa uma URL e retorna o conteúdo em texto limpo."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 SwarmAgent/2.0",
        })
        with urllib.request.urlopen(req, timeout=12) as r:
            raw = r.read().decode("utf-8", errors="ignore")
        clean = re.sub(r"<script[^>]*>.*?</script>", " ", raw, flags=re.S)
        clean = re.sub(r"<style[^>]*>.*?</style>", " ", clean, flags=re.S)
        clean = re.sub(r"<[^>]+>", " ", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean[:max_chars]
    except Exception as e:
        return f"[fetch_url erro] {e}"


# ══════════════════════════════════════════════════════════════════════════════
#  ANALYSE VIDEO  (skill ffmpeg — extrai frames + descreve com IA)
# ══════════════════════════════════════════════════════════════════════════════
def analyse_video(
    video_path: str,
    fps_sample: float = 1.0,
    model_key: str = "qwen_vision",
    question: str = "Descreva o que acontece neste frame, identifique padrões virais, hooks visuais, ritmo de edição e técnicas de engajamento.",
) -> str:
    """
    SKILL: ffmpeg-analyse-video
    Extrai frames de um vídeo com ffmpeg e analisa cada um com modelo de visão.
    Retorna análise timestampada com padrões virais identificados.
    
    Args:
        video_path: caminho para .mp4, .mov, .avi, etc.
        fps_sample: quantos frames por segundo amostrar (1.0 = 1 frame/s)
        model_key:  modelo com visão para análise ("qwen_vision" ou "gemini_flash")
        question:   o que perguntar sobre cada frame
    """
    video_path = Path(video_path)
    if not video_path.exists():
        return f"[analyse_video] Arquivo não encontrado: {video_path}"

    # Verifica ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "[analyse_video] ffmpeg não encontrado. Instale com: apt install ffmpeg"

    with tempfile.TemporaryDirectory() as tmpdir:
        out_pattern = os.path.join(tmpdir, "frame_%04d.jpg")

        # Extrai duração via ffprobe
        try:
            probe = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json",
                 "-show_format", "-show_streams", str(video_path)],
                capture_output=True, text=True, timeout=30
            )
            meta     = json.loads(probe.stdout)
            duration = float(meta.get("format", {}).get("duration", 0))
        except Exception:
            duration = 0

        # Extrai frames
        try:
            subprocess.run(
                ["ffmpeg", "-i", str(video_path),
                 "-vf", f"fps={fps_sample}", "-q:v", "3", out_pattern],
                capture_output=True, timeout=120, check=True,
            )
        except subprocess.CalledProcessError as e:
            return f"[analyse_video] Erro ffmpeg: {e.stderr.decode()[:300]}"

        frames = sorted(Path(tmpdir).glob("frame_*.jpg"))
        if not frames:
            return "[analyse_video] Nenhum frame extraído."

        # Analisa cada frame com modelo de visão
        from llm_engine import call_llm

        analyses: list[str] = []
        if duration and len(frames) > 0:
            interval = duration / len(frames)
        else:
            interval = 1.0 / fps_sample

        for i, frame_path in enumerate(frames[:30]):  # máx 30 frames
            timestamp = f"{interval * i:.1f}s"
            result    = call_llm(
                model_key,
                [{"role": "user", "content": question}],
                image_path=str(frame_path),
                temperature=0.3,
            )
            analyses.append(f"[{timestamp}] {result}")

        # Síntese final
        synthesis_prompt = (
            "Com base nas análises frame-a-frame abaixo, forneça:\n"
            "1. PADRÕES VIRAIS identificados\n"
            "2. HOOKS visuais e de edição\n"
            "3. RITMO e pacing\n"
            "4. FÓRMULA replicável (estrutura do vídeo)\n"
            "5. O que NÃO fazer (evitar AI slop)\n\n"
            "ANÁLISES:\n" + "\n".join(analyses[:15])
        )
        synthesis = call_llm(
            model_key,
            [{"role": "user", "content": synthesis_prompt}],
            temperature=0.4,
        )

        return (
            f"=== ANÁLISE DE VÍDEO: {video_path.name} ===\n"
            f"Duração: {duration:.1f}s | Frames amostrados: {len(frames)}\n\n"
            "── FRAMES ──\n" + "\n".join(analyses) + "\n\n"
            "── SÍNTESE VIRAL ──\n" + synthesis
        )


# ══════════════════════════════════════════════════════════════════════════════
#  UTILIDADES
# ══════════════════════════════════════════════════════════════════════════════
def get_datetime() -> str:
    return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def calculate(expr: str) -> str:
    allowed = set("0123456789+-*/.()%eE ")
    if not all(c in allowed for c in expr):
        return "[calc] Expressão inválida."
    try:
        return str(eval(expr, {"__builtins__": {}}))  # noqa: S307
    except Exception as e:
        return f"[calc erro] {e}"


def summarize_text(text: str, sentences: int = 4) -> str:
    parts    = re.split(r"(?<=[.!?])\s+", text.strip())
    selected = [s for s in parts if len(s) > 40][:sentences]
    return " ".join(selected) if selected else text[:400]


# ══════════════════════════════════════════════════════════════════════════════
#  DESCRIÇÃO INJETADA NOS SYSTEM PROMPTS
# ══════════════════════════════════════════════════════════════════════════════
GENERAL_SKILLS_DESCRIPTION = """
╔══ SKILLS GERAIS (disponíveis para você) ═══════════════════════════════════╗
║  web_search(query)              → Pesquisa na web (DuckDuckGo)             ║
║  fetch_url(url)                 → Extrai conteúdo de qualquer URL          ║
║  analyse_video(path)            → Analisa vídeo frame-a-frame com ffmpeg   ║
║  calculate(expr)                → Calculadora matemática                   ║
║  get_datetime()                 → Data/hora atual                          ║
║  summarize_text(text)           → Resumo de texto longo                    ║
╚════════════════════════════════════════════════════════════════════════════╝
Para usar: mencione a skill no output como [SKILL: nome_da_skill(args)]
"""
