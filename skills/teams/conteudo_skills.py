"""
skills/teams/conteudo_skills.py
Skills exclusivas da equipe de Conteúdo & Viral.
"""


# ─── Biblioteca de hooks testados ────────────────────────────────────────────
HOOK_ARSENAL = {
    "curiosidade": [
        "Ninguém te contou isso sobre {tema} porque {razão_surpreendente}",
        "O motivo pelo qual {resultado_desejado} ainda não aconteceu pra você",
        "Eu estudei {N} {referências} sobre {tema}. O que aprendi vai te chocar",
        "{profissional} passa {tempo} por dia fazendo isso. Você provavelmente não sabe o que é",
    ],
    "contrario": [
        "{conselho_comum} está te sabotando. Aqui o porquê",
        "Para de {ação_popular}. Faça {ação_contraintuitiva} em vez disso",
        "Todo mundo faz {X}. Os 1% fazem {Y}",
    ],
    "especificidade": [
        "Em {N} dias, {resultado_específico_com_número}. Método completo:",
        "Exatamente {N} passos que me fizeram {resultado_específico}",
        "De {ponto_A_específico} para {ponto_B_específico} em {tempo_específico}",
    ],
    "urgência": [
        "{tendência} vai desaparecer em {tempo}. Aproveite agora:",
        "Se você tem menos de {X}, preste atenção nisso",
        "Isso só funciona enquanto {condição_que_vai_mudar}",
    ],
    "identidade": [
        "Se você é {identidade_do_público}, este vídeo foi feito pra você",
        "O que {grupo_desejado} faz diferente de {grupo_atual}",
        "Você trabalha duro mas não chega lá? Pode ser isso:",
    ],
}


def hook_generator(tema: str, plataforma: str = "tiktok", estilo: str = "curiosidade") -> str:
    """Gera hooks para diferentes plataformas e estilos."""
    hooks = HOOK_ARSENAL.get(estilo, HOOK_ARSENAL["curiosidade"])
    formatted = [h.replace("{tema}", tema) for h in hooks]

    platform_specs = {
        "tiktok":    "0-3s críticos | voz alta, energia, pattern interrupt visual",
        "instagram": "primeira linha visível sem expandir | save-worthy | carousel tension",
        "youtube":   "thumbnail + title = promessa | primeiros 30s retêm ou perdem",
        "linkedin":  "primeira linha antes do 'ver mais' | profissional mas humano",
        "twitter":   "thread: 1ª mensagem = tudo | tensão que force o próximo tweet",
    }

    return f"""
HOOK ARSENAL — Tema: {tema} | Plataforma: {plataforma.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Spec da plataforma: {platform_specs.get(plataforma, 'universal')}
Estilo: {estilo}

HOOKS GERADOS:
""" + "\n".join(f"  {i+1}. {h}" for i, h in enumerate(formatted)) + """

ANTI-SLOP CHECK:
✗ Não use: "Você PRECISA saber disso!" (batido)
✗ Não use: "Isso vai mudar sua vida" (vago)
✗ Não use: "Siga para mais dicas!" (morto)
✓ Use especificidade + tensão + identidade
"""


def viral_formula_extractor(
    views: str,
    platform: str,
    content_type: str,
    description: str,
) -> str:
    """Template para desconstrução de conteúdo viral de referência."""
    return f"""
DESCONSTRUÇÃO VIRAL
━━━━━━━━━━━━━━━━━━
Referência: {views} views | {platform} | {content_type}
Descrição: {description}

ANÁLISE ESTRUTURAL:
┌─ HOOK (0-3s)
│  • Elemento visual de abertura:
│  • Primeira fala/texto:
│  • Por que para o scroll?
│
├─ DESENVOLVIMENTO
│  • Ritmo de cortes (lento/médio/rápido):
│  • Padrão de revelação (informação liberada gradualmente?):
│  • Momento de maior tensão:
│  • Uso de som/música:
│
├─ CLÍMAX / PAYOFF
│  • O que o espectador recebe:
│  • Surpresa ou confirmação de expectativa?
│
└─ CTA / LOOP
   • Chama ação? Qual?
   • Cria vontade de assistir de novo?
   • Faz a pessoa querer compartilhar para parecer o quê?

GATILHO EMOCIONAL PRIMÁRIO:
□ Surpresa  □ Inveja  □ Inspiração  □ Humor  □ Raiva  □ Nostalgia

FÓRMULA REPLICÁVEL (preencher após análise):
[Tema diferente] + [mesmo mecanismo de hook] + [mesmo ritmo] = [resultado esperado]

O QUE NÃO COPIAR (evitar AI slop):
• Não replique o visual se parecer template
• Não use a mesma trilha saturada
• Traga especificidade do SEU nicho
"""


def platform_algorithm_brief(platform: str) -> str:
    """Briefing atualizado de como o algoritmo de cada plataforma funciona."""
    briefs = {
        "tiktok": """
TIKTOK ALGORITHM BRIEF (2025)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SINAL MAIS FORTE: completion rate (% que assiste até o fim)
SEGUNDO: replays (loop automático = ouro)
TERCEIRO: shares > saves > comments > likes
QUARTO: tempo médio assistido vs. duração do vídeo

DISTRIBUIÇÃO:
• Começa com ~200 pessoas (seed audience)
• Se completion >50%: distribui para +2k
• Se mantém: +20k, +200k, viral
• Conta nova tem BOOST nas primeiras semanas

O QUE MATA ALCANCE:
• Watermarks de outras plataformas (shadow reduce)
• Cortes abruptos nos primeiros 0.5s
• Baixa qualidade de áudio
• Voz-off genérica de IA detectável

FORMATOS COM MAIS ALCANCE AGORA:
• Vertical nativo (9:16)
• 15-60s para alcance, 3-5min para monetização
• Text-on-screen com narração (acessibilidade = ranking)
""",
        "instagram": """
INSTAGRAM ALGORITHM BRIEF (2025)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SINAL MAIS FORTE: saves (indica conteúdo de valor)
SEGUNDO: shares para stories/DMs
TERCEIRO: comments (longos > curtos > emojis)
QUARTO: watch time em Reels

REELS vs FEED:
• Reels: descoberta (alcança não-seguidores)
• Carrossel: maior tempo por post = mais alcance orgânico
• Stories: engajamento com seguidores existentes

CAROUSEL HACK:
• Slide 1: tensão/promessa irresistível
• Slides 2-N: desenvolvimento (cada um deve criar curiosidade pelo próximo)
• Último slide: resolução SURPREENDENTE que faz salvar

O QUE FUNCIONA AGORA:
• Face + emotion nos primeiros frames de Reels
• Cover frame customizado (não o primeiro frame)
• Legenda com quebras de linha (pára o scroll visual)
""",
        "youtube": """
YOUTUBE ALGORITHM BRIEF (2025)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SINAL MAIS FORTE: CTR do thumbnail × watch time
SEGUNDO: average view duration (% do vídeo assistido)
TERCEIRO: clicks em cards/end screens
QUARTO: likes, comments, saves

SHORTS vs LONG FORM:
• Shorts: swipe-away rate nos primeiros 1-2s é decisivo
• Long: retenção acima de 50% em vídeos de 10min+ = push forte

THUMBNAIL SCIENCE:
• Rosto com emoção clara > sem rosto
• Contraste alto + texto ≤5 palavras
• Curiosity gap (imagem + texto = pergunta não respondida)
• Teste A/B após 48h

TITLE FORMULA:
[Número OU Palavra forte] + [Benefício específico] + [Elemento curiosidade]
Ex: "7 erros que sabotam seu crescimento (o #4 vai te chocar)"
""",
    }
    return briefs.get(platform.lower(), f"Plataforma '{platform}' não mapeada. Use: tiktok, instagram, youtube")


# ─── Descrição para injeção no system prompt ─────────────────────────────────
CONTEUDO_SKILLS_DESCRIPTION = """
╔══ SKILLS DA SUA EQUIPE (Conteúdo) ═════════════════════════════════════════╗
║  hook_generator(tema, plataforma, estilo)  → Biblioteca de hooks testados  ║
║  viral_formula_extractor(views, ...)       → Desconstrução de viral         ║
║  platform_algorithm_brief(platform)        → Briefing do algoritmo atual    ║
║  [+ content_calendar, hashtag_strategy, engagement_loop_design]             ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
