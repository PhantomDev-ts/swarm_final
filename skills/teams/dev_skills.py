"""
skills/teams/dev_skills.py
Skills exclusivas da equipe de Dev & CyberSecurity.
"""


def security_audit_checklist(target_type: str = "web_api") -> str:
    checklists = {
        "web_api": """
OWASP TOP 10 AUDIT — Web API
━━━━━━━━━━━━━━━━━━━━━━━━━━━
□ A01 Broken Access Control
  • Teste: acesse endpoints com token de outro usuário
  • Verifique: IDOR em IDs sequenciais (troque /user/123 por /user/124)
  • JWT: valida assinatura? aceita alg:none?

□ A02 Cryptographic Failures
  • Dados sensíveis em trânsito: TLS 1.2+ obrigatório
  • Dados em repouso: senha com bcrypt/argon2 (não MD5/SHA1)
  • Segredos no código-fonte ou .env commitado?

□ A03 Injection
  • SQL: usa ORM com parameterized queries?
  • NoSQL: valida inputs antes de montar query?
  • Command injection: usa subprocess com shell=True?

□ A05 Security Misconfiguration
  • Headers: X-Content-Type-Options, CSP, HSTS presentes?
  • CORS: aceita origin:* em produção?
  • Debug mode desativado em produção?

□ A07 Auth & Session
  • Rate limiting em /login e /register?
  • Tokens expiram? Refresh token rotation?
  • Logout invalida token no servidor?

□ A09 Logging & Monitoring
  • Falhas de auth são logadas com IP + timestamp?
  • Logs não contêm dados sensíveis (senhas, tokens)?
""",
        "frontend": """
SECURITY AUDIT — Frontend
━━━━━━━━━━━━━━━━━━━━━━━━━
□ XSS: usa innerHTML diretamente? (use textContent ou sanitize)
□ Dependências: npm audit sem vulnerabilidades críticas/high?
□ Secrets no bundle? (API keys no código cliente)
□ CSP header configurado e restritivo?
□ Formulários: CSRF token em requests state-changing?
□ localStorage: não armazena dados sensíveis?
□ Open redirects em parâmetros de URL?
""",
    }
    return checklists.get(target_type, checklists["web_api"])


def code_review_template(language: str = "python") -> str:
    return f"""
CODE REVIEW FRAMEWORK — {language.upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMADA 1 — CORRECTNESS
□ A lógica faz o que o nome diz?
□ Edge cases tratados (None, empty, overflow)?
□ Erros propagados corretamente (não silenciados)?

CAMADA 2 — SECURITY
□ Input validation antes de usar?
□ Dados sensíveis expostos em logs/exceptions?
□ Dependências: versão pinada e auditada?

CAMADA 3 — PERFORMANCE
□ N+1 queries em loops?
□ Objetos grandes copiados desnecessariamente?
□ Caches onde faz sentido?

CAMADA 4 — MAINTAINABILITY
□ Função faz mais de uma coisa? (SRP)
□ Nome do método descreve o comportamento?
□ Teste unitário possível? (baixo acoplamento)

CAMADA 5 — {language.upper()}-SPECIFIC
"""  + {
    "python": """□ Type hints presentes?\n□ f-strings em vez de .format()?\n□ Context managers para arquivos/conexões?\n□ List comprehension vs loop explícito (legibilidade)?""",
    "javascript": """□ async/await em vez de .then() encadeado?\n□ === em vez de == ?\n□ Null coalescing (??) em vez de || para defaults?\n□ Dependências de efeito colateral no useEffect?""",
}.get(language.lower(), "□ Siga as convenções da linguagem")


DEV_SKILLS_DESCRIPTION = """
╔══ SKILLS DA SUA EQUIPE (Dev) ═══════════════════════════════════════════════╗
║  security_audit_checklist(target)  → OWASP checklist por tipo de target     ║
║  code_review_template(language)    → Framework de code review em camadas     ║
║  [+ api_design, performance_profiler, devops_blueprint, dependency_audit]    ║
╚════════════════════════════════════════════════════════════════════════════╝
"""
