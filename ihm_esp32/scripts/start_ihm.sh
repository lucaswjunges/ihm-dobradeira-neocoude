#!/bin/bash
###############################################################################
# Script de Inicialização Manual - IHM Web
# Use este script para testar o servidor manualmente (fora do systemd)
###############################################################################

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}IHM Web - Inicialização Manual${NC}"
echo -e "${GREEN}========================================${NC}\n"

# Diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

# Verificar virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment não encontrado!${NC}"
    echo "Execute: python3 -m venv venv && source venv/bin/activate && pip install pymodbus aiohttp websockets"
    exit 1
fi

# Ativar venv
source venv/bin/activate

# Verificar porta USB
if ls /dev/ttyUSB* > /dev/null 2>&1; then
    USB_PORT=$(ls /dev/ttyUSB* | head -1)
    echo -e "${GREEN}✓ Porta USB detectada: $USB_PORT${NC}"
    MODE="live"
else
    echo -e "${YELLOW}⚠️  Porta USB não detectada - modo STUB${NC}"
    MODE="stub"
fi

# Perguntar modo
echo ""
echo "Escolha o modo de operação:"
echo "  1) LIVE - Conectar ao CLP via $USB_PORT"
echo "  2) STUB - Simulação (sem CLP)"
read -p "Opção [1/2]: " choice

case $choice in
    1)
        echo -e "\n${GREEN}▶ Iniciando em modo LIVE...${NC}\n"
        python3 main_server.py --port "$USB_PORT"
        ;;
    2)
        echo -e "\n${GREEN}▶ Iniciando em modo STUB...${NC}\n"
        python3 main_server.py --stub
        ;;
    *)
        echo "Opção inválida!"
        exit 1
        ;;
esac
