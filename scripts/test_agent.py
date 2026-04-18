"""
scripts/test_agent.py
Testa um agente diretamente no terminal, sem precisar do Discord.

Uso:
    python scripts/test_agent.py conteudo "Crie 3 hooks para TikTok sobre produtividade"
    python scripts/test_agent.py research !search tendências IA 2025
    python scripts/test_agent.py dev "Revise este código: def login(user, pw): return user==pw"
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_engine import engine
from agents.agent_definitions import ALL_AGENTS, AGENT_ALIASES


def main():
    if len(sys.argv) < 3:
        print("Uso: python test_agent.py <agente> <mensagem>")
        print(f"Agentes disponíveis: {', '.join(ALL_AGENTS.keys())}")
        sys.exit(1)

    agent_raw = sys.argv[1].lower()
    message   = " ".join(sys.argv[2:])
    agent     = AGENT_ALIASES.get(agent_raw, agent_raw)

    if agent not in ALL_AGENTS:
        print(f"❌ Agente '{agent_raw}' inválido. Disponíveis: {', '.join(ALL_AGENTS.keys())}")
        sys.exit(1)

    ag = ALL_AGENTS[agent]
    print(f"\n{ag.emoji} [{ag.team}] recebendo tarefa...")
    print(f"Mensagem: {message}\n")
    print("─" * 60)

    reply = engine.run(agent, message, "CLI")

    print(reply)
    print("─" * 60)


if __name__ == "__main__":
    main()
