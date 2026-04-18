#!/usr/bin/env bash
# scripts/install_openclaude.sh
#
# Instala OpenClaude e configura para usar g4f.dev como backend.
# OpenClaude = fork do código fonte do Claude Code com shim OpenAI-compatible.
# Você ganha TODAS as ferramentas do Claude Code (bash, file edit, grep, glob,
# MCP, agents, tasks) usando seus modelos g4f.
#
# Uso:
#   chmod +x scripts/install_openclaude.sh
#   ./scripts/install_openclaude.sh
#
# Em ambiente sem root (Kaggle):
#   bash scripts/install_openclaude.sh

set -e

CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
BOLD='\033[1m'
RESET='\033[0m'

info()    { echo -e "${CYAN}▸${RESET} $1"; }
success() { echo -e "${GREEN}✓${RESET} $1"; }
warn()    { echo -e "${YELLOW}⚠${RESET}  $1"; }
error()   { echo -e "${RED}✗${RESET} $1"; exit 1; }

echo -e "\n${CYAN}${BOLD}╔══════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║  Swarm × OpenClaude — Setup                  ║${RESET}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════╝${RESET}\n"

# ─── 1. Verificar Node.js ─────────────────────────────────────────────────────
info "Verificando Node.js..."
if ! command -v node &>/dev/null; then
    warn "Node.js não encontrado. Instalando via nvm..."
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    # shellcheck source=/dev/null
    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
    nvm install --lts
    nvm use --lts
fi
NODE_VER=$(node --version)
success "Node.js $NODE_VER"

# ─── 2. Instalar OpenClaude ───────────────────────────────────────────────────
info "Instalando OpenClaude (@gitlawb/openclaude)..."
npm install -g @gitlawb/openclaude 2>&1 | tail -3
if ! command -v openclaude &>/dev/null; then
    # Tenta via npx se install global falhou (Kaggle sem permissão de root)
    warn "Instalação global falhou — usando npx como fallback"
    echo '#!/usr/bin/env bash' > /usr/local/bin/openclaude 2>/dev/null || true
    echo 'npx @gitlawb/openclaude "$@"' >> /usr/local/bin/openclaude 2>/dev/null || true
    chmod +x /usr/local/bin/openclaude 2>/dev/null || true
fi
success "OpenClaude instalado"

# ─── 3. Verificar ripgrep (necessário para grep/glob tools) ──────────────────
info "Verificando ripgrep..."
if ! command -v rg &>/dev/null; then
    if command -v apt-get &>/dev/null; then
        apt-get install -y -q ripgrep 2>/dev/null || \
        cargo install ripgrep 2>/dev/null || \
        warn "ripgrep não instalado — grep tool limitada"
    fi
else
    success "ripgrep $(rg --version | head -1)"
fi

# ─── 4. Detectar G4F_API_KEY ─────────────────────────────────────────────────
info "Configurando provider g4f.dev..."

if [ -z "$G4F_API_KEY" ]; then
    # Tenta ler do .env
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    ENV_FILE="$SCRIPT_DIR/../.env"
    if [ -f "$ENV_FILE" ]; then
        G4F_API_KEY=$(grep '^G4F_API_KEY=' "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    fi
fi

if [ -z "$G4F_API_KEY" ]; then
    echo -e "\n${YELLOW}G4F_API_KEY não encontrada.${RESET}"
    echo -e "Obtenha em: ${CYAN}https://g4f.dev${RESET} → Login → Dashboard → API Keys\n"
    read -rp "Cole sua G4F_API_KEY aqui: " G4F_API_KEY
    if [ -z "$G4F_API_KEY" ]; then
        error "G4F_API_KEY é obrigatória"
    fi
fi

success "G4F_API_KEY: ${G4F_API_KEY:0:14}..."

# ─── 5. Criar perfis de modelo ────────────────────────────────────────────────
PROFILE_DIR="$HOME/.openclaude"
mkdir -p "$PROFILE_DIR"

# Perfil padrão — Gemini Flash (rápido, tasks gerais)
cat > "$PROFILE_DIR/profile-gemini.json" <<EOF
{
  "provider": "openai",
  "apiKey": "$G4F_API_KEY",
  "baseUrl": "https://g4f.dev/v1",
  "model": "gemini-2.0-flash",
  "name": "g4f-gemini-flash"
}
EOF

# Perfil Qwen Vision (mais capaz, tem visão)
cat > "$PROFILE_DIR/profile-qwen.json" <<EOF
{
  "provider": "openai",
  "apiKey": "$G4F_API_KEY",
  "baseUrl": "https://g4f.dev/v1",
  "model": "Qwen/Qwen3.5-397B",
  "name": "g4f-qwen-vision"
}
EOF

# Perfil GLM
cat > "$PROFILE_DIR/profile-glm.json" <<EOF
{
  "provider": "openai",
  "apiKey": "$G4F_API_KEY",
  "baseUrl": "https://g4f.dev/v1",
  "model": "glm-4-plus",
  "name": "g4f-glm"
}
EOF

success "Perfis criados em $PROFILE_DIR"

# ─── 6. Gerar script de launch ────────────────────────────────────────────────
LAUNCH_SCRIPT="$(dirname "$0")/launch_openclaude.sh"
cat > "$LAUNCH_SCRIPT" <<'LAUNCH'
#!/usr/bin/env bash
# launch_openclaude.sh — Inicia OpenClaude com g4f.dev
# Uso: ./scripts/launch_openclaude.sh [gemini|qwen|glm]

CYAN='\033[36m'; RESET='\033[0m'

MODEL="${1:-gemini}"

case "$MODEL" in
  gemini) MODEL_NAME="gemini-2.0-flash" ;;
  qwen)   MODEL_NAME="Qwen/Qwen3.5-397B" ;;
  glm)    MODEL_NAME="glm-4-plus" ;;
  mini)   MODEL_NAME="minimax-2.7" ;;
  *)      MODEL_NAME="$MODEL" ;;
esac

# Carrega .env se existir
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -f "$SCRIPT_DIR/../.env" ] && source "$SCRIPT_DIR/../.env"

if [ -z "$G4F_API_KEY" ]; then
  echo "❌ G4F_API_KEY não definida. Execute install_openclaude.sh primeiro."
  exit 1
fi

export CLAUDE_CODE_USE_OPENAI=1
export OPENAI_API_KEY="$G4F_API_KEY"
export OPENAI_BASE_URL="https://g4f.dev/v1"
export OPENAI_MODEL="$MODEL_NAME"

echo -e "\n${CYAN}🤖 OpenClaude × g4f.dev${RESET}"
echo -e "   Modelo: ${CYAN}$MODEL_NAME${RESET}"
echo -e "   Provider: https://g4f.dev/v1\n"

# Inicia o MCP server do swarm em background
python3 "$SCRIPT_DIR/../agent_core/mcp_server.py" &
MCP_PID=$!
echo "   MCP Swarm Server: PID $MCP_PID"
echo ""

# Inicia OpenClaude
openclaude --mcp-config "$SCRIPT_DIR/../agent_core/mcp_config.json"

# Cleanup
kill $MCP_PID 2>/dev/null || true
LAUNCH
chmod +x "$LAUNCH_SCRIPT"
success "Script de launch: $LAUNCH_SCRIPT"

# ─── 7. Resumo ────────────────────────────────────────────────────────────────
echo -e "\n${GREEN}${BOLD}━━━ Instalação concluída ━━━${RESET}"
echo -e ""
echo -e "  ${CYAN}Iniciar com Gemini Flash:${RESET}  ./scripts/launch_openclaude.sh gemini"
echo -e "  ${CYAN}Iniciar com Qwen Vision:${RESET}   ./scripts/launch_openclaude.sh qwen"
echo -e "  ${CYAN}Iniciar com GLM:${RESET}           ./scripts/launch_openclaude.sh glm"
echo -e ""
echo -e "  Ou configure manualmente:"
echo -e "  ${CYAN}export CLAUDE_CODE_USE_OPENAI=1${RESET}"
echo -e "  ${CYAN}export OPENAI_API_KEY=\$G4F_API_KEY${RESET}"
echo -e "  ${CYAN}export OPENAI_BASE_URL=https://g4f.dev/v1${RESET}"
echo -e "  ${CYAN}export OPENAI_MODEL=gemini-2.0-flash${RESET}"
echo -e "  ${CYAN}openclaude${RESET}"
echo ""
