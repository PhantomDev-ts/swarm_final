"""
Orquestrador Central — roteamento por palavras-chave + colaboração entre agentes.
"""

import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from agents.agent_definitions import ALL_AGENTS, AGENT_ALIASES
from agents.agent_engine import engine
from message_bus import send_message

KEYWORDS: dict[str, list[str]] = {
    "neuromarketing": [
        "marketing", "funil", "copy", "persuasão", "cliente", "persona",
        "campanha", "anúncio", "conversão", "neuromarketing", "gatilho",
        "venda", "oferta", "lead", "cta", "headline", "email marketing",
    ],
    "dev": [
        "código", "bug", "api", "segurança", "vulnerabilidade", "script",
        "deploy", "banco", "backend", "frontend", "python", "javascript",
        "docker", "servidor", "endpoint", "função", "classe", "erro",
        "performance", "algoritmo", "database", "query",
    ],
    "design": [
        "design", "layout", "wireframe", "interface", "ui", "ux", "cores",
        "tipografia", "logo", "marca", "visual", "prototipo", "acessibilidade",
        "figma", "grid", "componente", "tela", "botão", "formulário",
    ],
    "research": [
        "pesquisa", "mercado", "concorrente", "tendência", "análise",
        "dados", "relatório", "seo", "keyword", "estudo", "benchmark",
        "swot", "tam", "crescimento", "oportunidade", "estatística",
    ],
    "conteudo": [
        "conteúdo", "viral", "post", "vídeo", "reels", "tiktok",
        "instagram", "youtube", "linkedin", "hashtag", "hook", "legenda",
        "roteiro", "storytelling", "feed", "engajamento", "algoritmo",
        "shorts", "carrossel", "thread", "trend",
    ],
}


class Orchestrator:
    def route(
        self,
        message: str,
        agent_hint: Optional[str] = None,
        user_display: str = "Usuário",
        image_path: Optional[str] = None,
    ) -> tuple[str, str]:
        if agent_hint:
            name = AGENT_ALIASES.get(agent_hint.lower(), agent_hint.lower())
            if name in ALL_AGENTS:
                return name, engine.run(name, message, user_display, image_path)

        name = self._keyword_route(message) or "research"
        return name, engine.run(name, message, user_display, image_path)

    def collaborate(
        self,
        from_agent: str,
        to_agent: str,
        task: str,
        context: str = "",
    ) -> str:
        send_message(from_agent, to_agent, f"Tarefa de {from_agent}", task, "high")
        full_task = f"[Pedido de {from_agent}]: {task}"
        if context:
            full_task += f"\nContexto: {context}"
        return engine.run(to_agent, full_task, f"Agente {from_agent}")

    def broadcast(self, message: str, user_display: str = "Usuário") -> dict[str, str]:
        return {
            name: engine.run(name, message, user_display)
            for name in ALL_AGENTS
        }

    def _keyword_route(self, msg: str) -> Optional[str]:
        lower  = msg.lower()
        scores = {k: sum(1 for w in ws if w in lower) for k, ws in KEYWORDS.items()}
        best   = max(scores, key=lambda k: scores[k])
        return best if scores[best] > 0 else None


orchestrator = Orchestrator()
