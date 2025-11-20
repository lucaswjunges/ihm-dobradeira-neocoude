#!/bin/bash
# Script de inicialização da IHM Web em modo LIVE (com CLP conectado)
# Uso: ./run_ihm_live.sh [porta_serial]
# Exemplo: ./run_ihm_live.sh /dev/ttyUSB0

set -e  # Para na primeira falha

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Banner
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  IHM WEB - MODO LIVE (CLP Conectado)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Porta serial (padrão: /dev/ttyUSB0)
SERIAL_PORT=${1:-/dev/ttyUSB0}

# Verificar se a porta serial existe
if [ ! -e "$SERIAL_PORT" ]; then
    echo -e "${RED}✗ ERRO: Porta serial $SERIAL_PORT não encontrada!${NC}"
    echo ""
    echo "Portas seriais disponíveis:"
    ls -l /dev/ttyUSB* 2>/dev/null || echo "  Nenhuma porta USB serial encontrada"
    echo ""
    echo "Verifique:"
    echo "  1. Cabo USB-RS485 conectado"
    echo "  2. Drivers FTDI/CH340 instalados"
    echo "  3. Permissões de acesso (sudo usermod -a -G dialout \$USER)"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Porta serial encontrada: $SERIAL_PORT${NC}"

# Verificar permissões
if [ ! -r "$SERIAL_PORT" ] || [ ! -w "$SERIAL_PORT" ]; then
    echo -e "${YELLOW}⚠️  Aviso: Você pode não ter permissões para acessar $SERIAL_PORT${NC}"
    echo -e "${YELLOW}   Execute: sudo usermod -a -G dialout \$USER${NC}"
    echo -e "${YELLOW}   Depois faça logout e login novamente${NC}"
    echo ""
fi

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ ERRO: Python 3 não encontrado!${NC}"
    echo "  Execute: sudo apt install python3 python3-pip"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 encontrado: $(python3 --version)${NC}"

# Verificar dependências Python
echo ""
echo "Verificando dependências Python..."
python3 -c "import pymodbus, websockets, aiohttp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Dependências não encontradas. Instalando...${NC}"
    pip3 install pymodbus websockets aiohttp aiohttp-cors
else
    echo -e "${GREEN}✓ Dependências instaladas${NC}"
fi

# Mostrar configuração
echo ""
echo -e "${YELLOW}Configuração:${NC}"
echo "  Porta serial: $SERIAL_PORT"
echo "  Baudrate: 57600"
echo "  Slave ID: 1"
echo "  WebSocket: ws://0.0.0.0:8765"
echo "  HTTP: http://0.0.0.0:8080"
echo ""

# Perguntar confirmação
echo -e "${YELLOW}Pressione ENTER para iniciar ou Ctrl+C para cancelar...${NC}"
read

# Iniciar servidor
echo ""
echo -e "${GREEN}🚀 Iniciando servidor IHM Web...${NC}"
echo ""

# Executar main_server.py em modo LIVE (sem --stub)
python3 main_server.py --port "$SERIAL_PORT"
