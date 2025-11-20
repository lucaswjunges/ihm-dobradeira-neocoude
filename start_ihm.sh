#!/bin/bash
################################################################################
# start_ihm.sh
#
# Script de inicialização automática do servidor IHM Web
#
# Uso:
#   ./start_ihm.sh                    # Inicia em modo LIVE (porta padrão)
#   ./start_ihm.sh --stub             # Inicia em modo STUB (simulação)
#   ./start_ihm.sh --port /dev/ttyUSB1  # Porta serial alternativa
################################################################################

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configurações padrão
PORT="/dev/ttyUSB0"
WS_PORT=8086
STUB_MODE=false

# Banner
echo -e "${BLUE}${BOLD}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                    IHM WEB - NEOCOUDE-HD-15                                ║
║                    Servidor WebSocket + Modbus RTU                         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Parse argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --stub)
            STUB_MODE=true
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --ws-port)
            WS_PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Uso: $0 [opções]"
            echo ""
            echo "Opções:"
            echo "  --stub              Inicia em modo STUB (simulação, sem CLP)"
            echo "  --port <porta>      Porta serial (padrão: /dev/ttyUSB0)"
            echo "  --ws-port <porta>   Porta WebSocket (padrão: 8086)"
            echo "  -h, --help          Mostra esta ajuda"
            echo ""
            echo "Exemplos:"
            echo "  $0                           # Modo normal"
            echo "  $0 --stub                    # Modo simulação"
            echo "  $0 --port /dev/ttyUSB1       # Porta alternativa"
            exit 0
            ;;
        *)
            echo -e "${RED}Opção desconhecida: $1${NC}"
            echo "Use --help para ver opções disponíveis"
            exit 1
            ;;
    esac
done

# Função para verificar dependências
check_dependencies() {
    echo -e "${BOLD}[1/5] Verificando dependências...${NC}"

    # Verificar Python 3
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}✗ Python 3 não encontrado!${NC}"
        echo "  Instale com: sudo apt install python3"
        exit 1
    fi
    echo -e "${GREEN}  ✓ Python 3 instalado${NC}"

    # Verificar pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${YELLOW}  ⚠ pip3 não encontrado (opcional)${NC}"
    else
        echo -e "${GREEN}  ✓ pip3 instalado${NC}"
    fi

    # Verificar bibliotecas Python
    python3 -c "import websockets" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Biblioteca 'websockets' não encontrada!${NC}"
        echo "  Instale com: pip3 install websockets"
        exit 1
    fi
    echo -e "${GREEN}  ✓ websockets instalado${NC}"

    python3 -c "import pymodbus" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Biblioteca 'pymodbus' não encontrada!${NC}"
        echo "  Instale com: pip3 install pymodbus"
        exit 1
    fi
    echo -e "${GREEN}  ✓ pymodbus instalado${NC}"
}

# Função para verificar arquivos
check_files() {
    echo -e "${BOLD}[2/5] Verificando arquivos do sistema...${NC}"

    FILES=("ihm_server_final.py" "modbus_client.py" "ihm_completa.html")

    for file in "${FILES[@]}"; do
        if [ ! -f "$file" ]; then
            echo -e "${RED}✗ Arquivo não encontrado: $file${NC}"
            exit 1
        fi
        echo -e "${GREEN}  ✓ $file${NC}"
    done
}

# Função para verificar porta serial (modo LIVE)
check_serial_port() {
    if [ "$STUB_MODE" = false ]; then
        echo -e "${BOLD}[3/5] Verificando porta serial...${NC}"

        # Verificar se porta existe
        if [ ! -e "$PORT" ]; then
            echo -e "${RED}✗ Porta $PORT não encontrada!${NC}"
            echo ""
            echo "Portas disponíveis:"
            ls -l /dev/ttyUSB* 2>/dev/null || echo "  Nenhuma porta USB serial encontrada"
            echo ""
            echo "Sugestões:"
            echo "  - Conecte o conversor USB-RS485"
            echo "  - Verifique com: ls -l /dev/ttyUSB*"
            echo "  - Use --port para especificar porta diferente"
            exit 1
        fi
        echo -e "${GREEN}  ✓ Porta $PORT existe${NC}"

        # Verificar permissões
        if [ ! -r "$PORT" ] || [ ! -w "$PORT" ]; then
            echo -e "${YELLOW}  ⚠ Sem permissões de leitura/escrita em $PORT${NC}"
            echo "  Ajustando permissões..."
            sudo chmod 666 "$PORT"
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}  ✓ Permissões ajustadas${NC}"
            else
                echo -e "${RED}  ✗ Falha ao ajustar permissões${NC}"
                exit 1
            fi
        else
            echo -e "${GREEN}  ✓ Permissões OK${NC}"
        fi

        # Verificar se porta está em uso
        if lsof "$PORT" &> /dev/null; then
            echo -e "${YELLOW}  ⚠ Porta $PORT está em uso por outro processo${NC}"
            echo ""
            lsof "$PORT"
            echo ""
            read -p "Continuar mesmo assim? [s/N] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Ss]$ ]]; then
                exit 1
            fi
        else
            echo -e "${GREEN}  ✓ Porta $PORT disponível${NC}"
        fi
    else
        echo -e "${BOLD}[3/5] Modo STUB - pulando verificação de porta serial${NC}"
        echo -e "${YELLOW}  ⚠ Rodando em modo SIMULAÇÃO (sem CLP)${NC}"
    fi
}

# Função para verificar porta WebSocket
check_ws_port() {
    echo -e "${BOLD}[4/5] Verificando porta WebSocket...${NC}"

    # Verificar se porta está em uso
    if netstat -tuln 2>/dev/null | grep -q ":$WS_PORT "; then
        echo -e "${YELLOW}  ⚠ Porta $WS_PORT já está em uso${NC}"

        # Tentar encontrar processo
        PID=$(lsof -ti:$WS_PORT 2>/dev/null)
        if [ ! -z "$PID" ]; then
            echo "  Processo usando porta: PID $PID"
            ps -p $PID -o comm=

            read -p "  Deseja matar o processo? [s/N] " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Ss]$ ]]; then
                kill $PID
                sleep 1
                echo -e "${GREEN}  ✓ Processo finalizado${NC}"
            else
                echo -e "${RED}  Abortando...${NC}"
                exit 1
            fi
        fi
    else
        echo -e "${GREEN}  ✓ Porta $WS_PORT disponível${NC}"
    fi
}

# Função para iniciar servidor
start_server() {
    echo -e "${BOLD}[5/5] Iniciando servidor...${NC}"
    echo ""

    # Montar comando
    CMD="python3 ihm_server_final.py --ws-port $WS_PORT"

    if [ "$STUB_MODE" = true ]; then
        CMD="$CMD --stub"
    else
        CMD="$CMD --port $PORT"
    fi

    # Mostrar informações
    echo -e "${BLUE}${BOLD}Configuração:${NC}"
    echo -e "  Modo: ${BOLD}$([ "$STUB_MODE" = true ] && echo "STUB (Simulação)" || echo "LIVE (CLP em $PORT)")${NC}"
    echo -e "  WebSocket: ${BOLD}ws://localhost:$WS_PORT${NC}"
    echo -e "  Interface: ${BOLD}ihm_completa.html${NC}"
    echo ""
    echo -e "${YELLOW}Para parar o servidor: pressione CTRL+C${NC}"
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""

    # Executar comando
    exec $CMD
}

# Função principal
main() {
    check_dependencies
    check_files
    check_serial_port
    check_ws_port
    start_server
}

# Executar
main
