"""
scripts/probe_models.py

Testa modelos do catálogo e mostra status, latência e provider.

Uso:
    python scripts/probe_models.py                  # testa todos os ollama (gratuitos)
    python scripts/probe_models.py --hosted         # testa hosted (precisa de key)
    python scripts/probe_models.py --all            # testa tudo
    python scripts/probe_models.py --tags coding    # filtra por tag
    python scripts/probe_models.py --discover       # lista modelos via GET /models
    python scripts/probe_models.py -v               # verbose (mostra raw request)
"""

import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import ALL_MODELS, G4F_API_KEY
from llm_engine import probe_model, probe_all, list_available_models

C = {
    "cyan":   "\033[36m", "green":  "\033[32m", "yellow": "\033[33m",
    "red":    "\033[31m", "dim":    "\033[2m",  "bold":   "\033[1m",
    "reset":  "\033[0m",
}
def c(color: str, text: str) -> str:
    return f"{C[color]}{text}{C['reset']}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hosted",   action="store_true", help="Testa só modelos hosted (key obrigatória)")
    p.add_argument("--ollama",   action="store_true", help="Testa só modelos Ollama (gratuito)")
    p.add_argument("--all",      action="store_true", help="Testa todos")
    p.add_argument("--tags",     nargs="+",           help="Filtra por tags (ex: coding vision)")
    p.add_argument("--discover", action="store_true", help="Lista modelos via GET /models da API")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    print(f"\n{c('cyan', c('bold', '══ AI Agent Swarm — Probe de Modelos ══'))}")

    if G4F_API_KEY:
        print(c("green", f"✓ G4F_API_KEY detectada ({G4F_API_KEY[:14]}...)"))
    else:
        print(c("yellow", "⚠  G4F_API_KEY não definida — só modelos 'ollama' funcionarão"))

    # Discovery
    if args.discover:
        print(f"\n{c('cyan', '▸ Listando modelos disponíveis via GET /models...')}")
        for prov in (["hosted"] if G4F_API_KEY else []) + ["ollama"]:
            print(f"\n  {c('dim', prov + ':')} ")
            ids = list_available_models(prov)
            for mid in ids[:50]:
                print(f"    {mid}")
            if len(ids) > 50:
                print(f"    ... e mais {len(ids)-50}")
        return

    # Determina filtro de provider
    if args.hosted:
        pf = "hosted"
    elif args.ollama or not (args.hosted or args.all):
        pf = "ollama"   # padrão: testar ollama (gratuito)
    else:
        pf = None

    tags = args.tags or None

    print(f"\n  Provider: {c('cyan', pf or 'todos')}  |  Tags: {c('cyan', str(tags) or 'todas')}")
    print(f"  {c('dim', 'Testando em paralelo (6 threads)...')}\n")

    results = probe_all(tags=tags, provider_filter=pf, verbose=args.verbose)

    online, offline = [], []
    rows = sorted(results.items(), key=lambda x: (not x[1]["ok"], x[1]["latency_ms"]))

    hdr = f"{'Modelo':<28} {'Status':<8} {'ms':>6}  {'Provider':<8}  {'Model ID'}"
    print(c("dim", hdr))
    print(c("dim", "─" * 85))

    for key, r in rows:
        icon  = c("green", "✅ OK  ") if r["ok"] else c("red",   "❌ FAIL")
        ms    = f"{r['latency_ms']:>5}ms"
        prov  = c("cyan", r["provider"])
        mid   = c("dim", r["model_id"][:40])
        print(f"{key:<28} {icon} {ms}  {prov:<18}  {mid}")
        (online if r["ok"] else offline).append(key)

    print(c("dim", "\n─" * 85))
    print(f"{c('green', f'✅ Online:  {len(online)}')}  |  {c('red', f'❌ Offline: {len(offline)}')}")

    if online:
        print(f"\n{c('cyan', 'Modelos online:')}")
        for k in online:
            cfg = ALL_MODELS[k]
            print(f"  {k:<28} {c('dim', cfg['desc'])}")

    if offline and args.hosted:
        print(f"\n{c('yellow', 'Dica:')} modelos offline podem ter nome diferente na API.")
        print(f"  Rode: {c('cyan', 'python scripts/probe_models.py --discover')} para ver os IDs reais.")


if __name__ == "__main__":
    main()
