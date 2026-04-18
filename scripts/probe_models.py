"""
scripts/probe_models.py
Testa todos os modelos LLM configurados e exibe latência + status.
Execute antes de iniciar o bot para confirmar quais modelos estão online.

Uso:
    python scripts/probe_models.py
    python scripts/probe_models.py --verbose
"""

import sys, os, argparse, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import G4F_MODELS
from llm_engine import probe_model, call_llm


def main():
    parser = argparse.ArgumentParser(description="Testa modelos LLM do swarm")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mostra resposta completa")
    parser.add_argument("--model",   "-m", default="",          help="Testa apenas um modelo específico")
    args = parser.parse_args()

    targets = [args.model] if args.model and args.model in G4F_MODELS else list(G4F_MODELS.keys())

    print("\n" + "═" * 70)
    print("  AI Agent Swarm V2 — Probe de Modelos LLM")
    print("═" * 70)

    results = {}
    for key in targets:
        cfg = G4F_MODELS[key]
        print(f"\n🔬 Testando: {key}")
        print(f"   Provider: {cfg['provider']}")
        print(f"   Model:    {cfg['model']}")
        print(f"   Vision:   {'sim' if cfg.get('vision') else 'não'}")
        print(f"   Desc:     {cfg['description']}")

        start  = time.time()
        result = probe_model(key)
        ms     = int((time.time() - start) * 1000)

        icon = "✅" if result["ok"] else "❌"
        print(f"   Status:   {icon} {'ONLINE' if result['ok'] else 'OFFLINE'} ({ms}ms)")

        if args.verbose or not result["ok"]:
            print(f"   Resposta: {result['response_preview']}")

        results[key] = result

    # Resumo
    print("\n" + "═" * 70)
    online  = [k for k, r in results.items() if r["ok"]]
    offline = [k for k, r in results.items() if not r["ok"]]
    print(f"✅ Online  ({len(online)}): {', '.join(online) or 'nenhum'}")
    print(f"❌ Offline ({len(offline)}): {', '.join(offline) or 'nenhum'}")
    print("═" * 70 + "\n")

    # Recomendação de modelos para usar
    if online:
        print("💡 Sugestão: edite TEAM_DEFAULT_MODEL em config.py para usar apenas modelos online.\n")

    return 0 if len(online) > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
