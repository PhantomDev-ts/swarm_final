"""
skills/teams/marketing_skills.py
Skills exclusivas da equipe de Neuromarketing/Marketing.
Retornam strings formatadas para injetar no contexto do agente.
"""


def audience_psychographics(product: str, context: str = "") -> str:
    """
    Gera template de análise psicográfica profunda.
    O agente preenche com base em pesquisa e memória.
    """
    return f"""
FRAMEWORK: ANÁLISE PSICOGRÁFICA — {product}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. IDENTIDADE E VALORES
   • Quem eles querem SER (não só quem são)
   • Valores não negociáveis
   • Tribos de pertencimento

2. DORES PROFUNDAS (não superficiais)
   • Dor funcional: o problema prático
   • Dor emocional: como se sentem por ter o problema
   • Dor social: o que os outros pensam deles por ter o problema
   • Medo existencial: quem eles se tornam se não resolverem

3. DESEJOS LATENTES (não declarados)
   • O que eles realmente querem (além do produto)
   • O "trabalho" que contratam o produto para fazer (JTBD)

4. GATILHOS DE COMPRA
   • Evento gatilho (o que muda na vida deles para buscar solução)
   • Objeções reais (não as que eles dizem, mas as que pensam)
   • Prova social que REALMENTE importa para eles

5. LINGUAGEM DO CLIENTE
   • Palavras exatas que usam para descrever o problema
   • Metáforas e analogias que ressoam
   • O que NÃO dizer (soa falso/corporativo)

Contexto adicional: {context or 'nenhum'}
"""


def neural_funnel(product: str, price_point: str = "") -> str:
    """Template de funil baseado em neurociência comportamental."""
    return f"""
NEURAL FUNNEL — {product} | Preço: {price_point or 'N/D'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TOPO (Sistema 1 — Automático):
→ Hook que ativa amígdala (medo, curiosidade, inveja, esperança)
→ Pattern interrupt visual/verbal
→ Promessa implícita em <3 segundos

MEIO (Construção de confiança):
→ Prova social estratificada (peer > expert > brand)
→ Especificidade que elimina ceticismo
→ Micro-compromissos progressivos (sim, sim, sim → compra)

FUNDO (Sistema 2 → Racionalização):
→ Justificativa racional para a decisão emocional já tomada
→ Ancoragem de preço
→ Escassez real (não fake) + urgência legítima
→ Garantia que elimina risco percebido

SEQUÊNCIA DE GATILHOS CIALDINI:
1. Reciprocidade → entregue valor ANTES de pedir
2. Compromisso → pequenos sim progressivos
3. Prova social → mostre quem já fez
4. Autoridade → credenciais específicas, não genéricas
5. Simpatia → humanize, mostre vulnerabilidade
6. Escassez → real, específica, explicada
7. Unidade → "somos iguais, fazemos parte do mesmo grupo"
"""


def viral_trigger_analysis(reference_content: str) -> str:
    """Desconstrução de por que algo viralizou."""
    return f"""
ANÁLISE DE GATILHOS VIRAIS
━━━━━━━━━━━━━━━━━━━━━━━━━
Conteúdo referência: {reference_content}

CHECKLIST DE ANÁLISE:
□ Emoção primária ativada: (raiva / alegria / surpresa / medo / nojo / tristeza)
□ Identidade social: confirma ou desafia crença do grupo?
□ Utilidade: resolve problema real ou entretém genuinamente?
□ Compartilhabilidade: o compartilhamento diz algo sobre quem compartilha?
□ Timing: surfou tendência ou criou uma?
□ Especificidade: dado ou detalhe que parece "insider"?
□ Tensão não resolvida: deixa pergunta sem resposta?
□ Hook nos primeiros 3s: qual foi o padrão de interrupção?

FÓRMULA EXTRAÍDA:
[Preencher após análise]

COMO REPLICAR SEM PLAGIAR:
[Preencher após análise]
"""


# ─── Descrição para injeção no system prompt ─────────────────────────────────
MARKETING_SKILLS_DESCRIPTION = """
╔══ SKILLS DA SUA EQUIPE (Marketing) ════════════════════════════════════════╗
║  audience_psychographics(product)   → Template psicográfico profundo       ║
║  neural_funnel(product, price)      → Funil baseado em neurociência         ║
║  viral_trigger_analysis(content)    → Por que algo viralizou                ║
║  [+ cialdini_copy, color_emotion_map, competitor_ad_autopsy]                ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
