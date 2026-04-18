"""
skills/teams/research_skills.py
Skills exclusivas da equipe de Research & Inteligência.
"""


def market_sizing_template(market: str, geography: str = "Brasil") -> str:
    return f"""
MARKET SIZING — {market} | {geography}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
METODOLOGIA TOP-DOWN:
1. Mercado global total → filtrar por país/região
2. Aplicar taxa de penetração local
3. Segmentar pelo perfil do produto

METODOLOGIA BOTTOM-UP (mais confiável):
1. N° de clientes potenciais × ticket médio × frequência de compra
2. Fontes: IBGE, relatórios setoriais, associações, CAGED

TAM (Total Addressable Market):
→ Mercado total se 100% dos potenciais clientes comprassem
→ Estimativa: [preencher]

SAM (Serviceable Addressable Market):
→ Subconjunto que você pode atingir com seu modelo atual
→ Estimativa: [preencher]

SOM (Serviceable Obtainable Market):
→ Parcela realista nos primeiros 3 anos
→ Estimativa: [preencher]

CONFIANÇA DOS DADOS: [1-5]
FONTES USADAS: [listar]
O QUE NÃO SABEMOS: [listar gaps]
"""


def competitor_deep_dive_template(competitor: str) -> str:
    return f"""
COMPETITOR DEEP DIVE — {competitor}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. POSICIONAMENTO
   • Promessa central (tagline / hero copy):
   • Para quem se posiciona:
   • O que evita falar (ponto cego):

2. PRODUTO / OFERTA
   • Features principais:
   • Preço e modelo de monetização:
   • O que está faltando (gap de mercado):

3. MARKETING
   • Canais principais:
   • Tipo de conteúdo que produz:
   • Keywords que ranqueia (SEO):
   • Anúncios pagos (ad copy / criativo):

4. REVIEWS / VOZ DO CLIENTE
   • O que clientes AMAM (verbatim):
   • O que clientes ODEIAM (verbatim):
   • Reclamações recorrentes (oportunidade):

5. VULNERABILIDADES
   • Onde você pode ganhar:
   • Onde você NÃO deve competir diretamente:

CONFIANÇA: [1-5] | DATA DA ANÁLISE: [data]
"""


RESEARCH_SKILLS_DESCRIPTION = """
╔══ SKILLS DA SUA EQUIPE (Research) ══════════════════════════════════════════╗
║  market_sizing_template(market, geo)    → TAM/SAM/SOM estruturado           ║
║  competitor_deep_dive_template(name)    → Análise competitiva profunda       ║
║  [+ trend_signal_detection, seo_keyword_intelligence, hypothesis_validation] ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
