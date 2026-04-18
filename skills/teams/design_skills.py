"""
skills/teams/design_skills.py
Skills exclusivas da equipe de Design & UX.
"""


def ux_friction_audit_template(product_type: str = "app") -> str:
    """Template de auditoria de fricção UX."""
    return f"""
UX FRICTION AUDIT — {product_type.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NÍVEL 1 — FRICÇÃO DE PERCEPÇÃO
□ Hierarquia visual clara? (1 foco por tela)
□ CTA principal óbvio sem precisar procurar?
□ Tempo de carregamento percebido aceitável? (<3s regra)
□ Feedback imediato em todas as ações interativas?

NÍVEL 2 — FRICÇÃO COGNITIVA
□ Quantidade de opções por tela (≤7 ± 2 por Miller's Law)?
□ Labels autoexplicativas? (não precisa de tooltip para entender)
□ Formulários: apenas campos essenciais?
□ Mensagens de erro: dizem O QUE fazer, não só O QUE aconteceu?

NÍVEL 3 — FRICÇÃO EMOCIONAL
□ Tom de voz: respeitoso, não condescendente?
□ Estados vazios (empty states): são oportunidades de engajamento?
□ Onboarding: mostra valor ANTES de pedir dados?
□ Micro-interações que causam delight?

NÍVEL 4 — FRICÇÃO TÉCNICA
□ Touch targets: mínimo 44×44px (iOS), 48×48dp (Android)?
□ Contraste: mínimo 4.5:1 para texto normal (WCAG AA)?
□ Comportamento em teclado virtual (mobile)?
□ Funciona com navegação por teclado (desktop)?

PRIORIZAÇÃO DE FIXES (impact × effort):
Alta Impact / Baixo Esforço → FAÇA AGORA
Alta Impact / Alto Esforço  → PLANEJE
Baixo Impact / Baixo Esforço → BACKLOG
Baixo Impact / Alto Esforço → IGNORE
"""


def design_token_generator(
    primary_color: str = "#6366f1",
    brand_name: str = "Brand",
    style: str = "modern",  # modern | minimal | bold | soft
) -> str:
    """Gera design tokens CSS/Tailwind."""
    return f"""
/* Design Tokens — {brand_name} | Estilo: {style} */
/* Gerado pelo Swarm Design Agent */

:root {{
  /* ── Cores ─────────────────────────────────────────── */
  --color-primary:     {primary_color};
  --color-primary-hover: color-mix(in srgb, {primary_color} 85%, black);
  --color-primary-light: color-mix(in srgb, {primary_color} 15%, white);

  --color-surface-0:  #ffffff;
  --color-surface-1:  #f8f9fa;
  --color-surface-2:  #f1f3f5;
  --color-border:     #dee2e6;

  --color-text-primary:   #111827;
  --color-text-secondary: #6b7280;
  --color-text-muted:     #9ca3af;

  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error:   #ef4444;
  --color-info:    #3b82f6;

  /* ── Tipografia ─────────────────────────────────────── */
  --font-display: 'Your Display Font', sans-serif;
  --font-body:    'Your Body Font', sans-serif;
  --font-mono:    'JetBrains Mono', monospace;

  --text-xs:   0.75rem;   /* 12px */
  --text-sm:   0.875rem;  /* 14px */
  --text-base: 1rem;      /* 16px */
  --text-lg:   1.125rem;  /* 18px */
  --text-xl:   1.25rem;   /* 20px */
  --text-2xl:  1.5rem;    /* 24px */
  --text-3xl:  1.875rem;  /* 30px */
  --text-4xl:  2.25rem;   /* 36px */

  /* ── Espaçamento (8pt grid) ─────────────────────────── */
  --space-1:  0.25rem;  /* 4px  */
  --space-2:  0.5rem;   /* 8px  */
  --space-3:  0.75rem;  /* 12px */
  --space-4:  1rem;     /* 16px */
  --space-6:  1.5rem;   /* 24px */
  --space-8:  2rem;     /* 32px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */

  /* ── Bordas e sombras ───────────────────────────────── */
  --radius-sm:  0.25rem;
  --radius-md:  0.5rem;
  --radius-lg:  0.75rem;
  --radius-xl:  1rem;
  --radius-full: 9999px;

  --shadow-sm:  0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md:  0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg:  0 10px 15px -3px rgb(0 0 0 / 0.1);

  /* ── Motion ─────────────────────────────────────────── */
  --transition-fast:   150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow:   400ms ease;
}}

/* Tailwind config equivalente (tailwind.config.js):
   colors.primary: '{primary_color}',
   fontFamily.display: ['Your Display Font'],
   spacing base: 4 (8pt grid / 2)
*/
"""


def visual_hierarchy_checklist(screen_name: str = "tela") -> str:
    """Checklist de hierarquia visual."""
    return f"""
HIERARQUIA VISUAL — {screen_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PERGUNTA-TESTE: "Se eu tirasse todas as cores e ficasse só com tamanhos,
a hierarquia ainda seria clara?"

NÍVEL 1 — O QUE É ISSO? (identidade)
□ Logo/brand visível sem procurar
□ Título da página/seção claramente maior que tudo
□ Máximo 1 elemento dominante por tela

NÍVEL 2 — O QUE POSSO FAZER? (ação)
□ CTA primário: cor + tamanho + posição únicos
□ CTA secundário: claramente subordinado ao primário
□ Ações destrutivas: visualmente distantes dos CTAs principais

NÍVEL 3 — O QUE PRECISO SABER? (contexto)
□ Informações de suporte em tamanho e peso menores
□ Labels e metadados: cor secundária (#6b7280 ou similar)
□ Informação legal/disclaimer: muted, nunca competindo

FLUXO DE LEITURA ESPERADO (marque o padrão):
□ F-pattern (texto denso, leitura linear)
□ Z-pattern (landing pages, páginas de marketing)
□ Gutenberg (quadrante inferior direito = CTA)
□ Livre (galeria, exploração)

AJUSTES NECESSÁRIOS:
"""


DESIGN_SKILLS_DESCRIPTION = """
╔══ SKILLS DA SUA EQUIPE (Design) ════════════════════════════════════════════╗
║  ux_friction_audit_template(product)    → Auditoria completa de fricção UX  ║
║  design_token_generator(color, brand)   → Tokens CSS/Tailwind prontos       ║
║  visual_hierarchy_checklist(screen)     → Checklist de hierarquia visual     ║
║  [+ brand_system_builder, competitor_ux_teardown, accessibility_audit]       ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
