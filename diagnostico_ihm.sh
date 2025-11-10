#!/bin/bash
################################################################################
# diagnostico_ihm.sh
#
# Script de diagnóstico rápido do sistema IHM
# Verifica todas as dependências e conectividade
################################################################################

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}${BOLD}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                    DIAGNÓSTICO RÁPIDO - IHM WEB                            ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Função de teste
test_item() {
    local name=$1
    local command=$2
    local error_msg=$3

    echo -n "  $name... "
    
    if eval "$command" &>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        if [ ! -z "$error_msg" ]; then
            echo -e "${RED}✗${NC}"
            echo -e "    ${RED}$error_msg${NC}"
            ((ERRORS++))
        else
            echo -e "${YELLOW}⚠${NC}"
            ((WARNINGS++))
        fi
        return 1
    fi
}

# 1. Sistema Operacional
echo -e "${BOLD}[1] Sistema Operacional${NC}"
test_item "Linux" "uname -s | grep -q Linux" "Sistema não é Linux"
test_item "Ubuntu/Debian" "command -v apt" ""
echo ""

# 2. Python
echo -e "${BOLD}[2] Python e Dependências${NC}"
test_item "Python 3" "command -v python3" "Python 3 não instalado (sudo apt install python3)"
if command -v python3 &>/dev/null; then
    VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "    Versão: $VERSION"
fi
test_item "pip3" "command -v pip3" "pip3 não instalado (sudo apt install python3-pip)"
test_item "websockets" "python3 -c 'import websockets'" "websockets não instalado (pip3 install websockets)"
test_item "pymodbus" "python3 -c 'import pymodbus'" "pymodbus não instalado (pip3 install pymodbus)"
echo ""

# 3. Arquivos do Sistema
echo -e "${BOLD}[3] Arquivos do Sistema IHM${NC}"
test_item "ihm_server_final.py" "test -f ihm_server_final.py" "Arquivo não encontrado"
test_item "modbus_client.py" "test -f modbus_client.py" "Arquivo não encontrado"
test_item "ihm_completa.html" "test -f ihm_completa.html" "Arquivo não encontrado"
test_item "test_ihm_completa.py" "test -f test_ihm_completa.py" ""
echo ""

# 4. Hardware
echo -e "${BOLD}[4] Hardware (Porta Serial)${NC}"
if ls /dev/ttyUSB* &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Portas USB seriais encontradas:"
    for port in /dev/ttyUSB*; do
        if [ -r "$port" ] && [ -w "$port" ]; then
            echo -e "    ${GREEN}✓${NC} $port (leitura/escrita OK)"
        else
            echo -e "    ${YELLOW}⚠${NC} $port (sem permissões - use: sudo chmod 666 $port)"
            ((WARNINGS++))
        fi
    done
else
    echo -e "  ${YELLOW}⚠${NC} Nenhuma porta USB serial encontrada"
    echo -e "    ${YELLOW}Conecte o conversor USB-RS485${NC}"
    ((WARNINGS++))
fi
echo ""

# 5. Network
echo -e "${BOLD}[5] Rede${NC}"
test_item "Interface de rede ativa" "ip link show | grep -q 'state UP'" ""
if ip addr show | grep -q 'inet '; then
    echo -e "  ${GREEN}✓${NC} Endereços IP:"
    ip addr show | grep 'inet ' | awk '{print "    " $2}' | head -3
else
    echo -e "  ${YELLOW}⚠${NC} Nenhum endereço IP configurado"
fi
echo ""

# 6. Porta WebSocket
echo -e "${BOLD}[6] Porta WebSocket (8086)${NC}"
if netstat -tuln 2>/dev/null | grep -q ':8086 '; then
    echo -e "  ${YELLOW}⚠${NC} Porta 8086 já está em uso"
    PID=$(lsof -ti:8086 2>/dev/null)
    if [ ! -z "$PID" ]; then
        CMD=$(ps -p $PID -o comm=)
        echo -e "    Processo: $CMD (PID $PID)"
    fi
    ((WARNINGS++))
else
    echo -e "  ${GREEN}✓${NC} Porta 8086 disponível"
fi
echo ""

# 7. Teste de Conexão Modbus (se porta serial existe)
if ls /dev/ttyUSB0 &>/dev/null 2>&1; then
    echo -e "${BOLD}[7] Teste de Conexão Modbus${NC}"
    echo -n "  Tentando conectar ao CLP em /dev/ttyUSB0... "
    
    TEST_RESULT=$(python3 << 'PYEOF' 2>&1
import sys
sys.path.insert(0, '.')
try:
    from modbus_client import ModbusClient, ModbusConfig
    config = ModbusConfig(port='/dev/ttyUSB0')
    client = ModbusClient(stub_mode=False, config=config)
    if client.connect():
        encoder = client.get_encoder_angle()
        client.disconnect()
        if encoder is not None:
            print(f"OK:{encoder}")
            sys.exit(0)
        else:
            print("FAIL:Encoder retornou None")
            sys.exit(1)
    else:
        print("FAIL:Falha ao conectar")
        sys.exit(1)
except Exception as e:
    print(f"FAIL:{str(e)}")
    sys.exit(1)
PYEOF
)
    
    if echo "$TEST_RESULT" | grep -q "^OK:"; then
        ENCODER=$(echo "$TEST_RESULT" | cut -d: -f2)
        echo -e "${GREEN}✓${NC}"
        echo -e "    ${GREEN}CLP conectado! Encoder = $ENCODER${NC}"
    else
        echo -e "${RED}✗${NC}"
        ERROR_MSG=$(echo "$TEST_RESULT" | cut -d: -f2-)
        echo -e "    ${RED}$ERROR_MSG${NC}"
        ((ERRORS++))
    fi
    echo ""
fi

# 8. Servidor rodando?
echo -e "${BOLD}[8] Servidor IHM${NC}"
if pgrep -f "ihm_server_final.py" > /dev/null; then
    PID=$(pgrep -f "ihm_server_final.py")
    echo -e "  ${GREEN}✓${NC} Servidor rodando (PID $PID)"
    echo -e "    ${BLUE}Logs:${NC} tail -f ihm_server_final.log"
    echo -e "    ${BLUE}Parar:${NC} pkill -f ihm_server_final.py"
else
    echo -e "  ${YELLOW}⚠${NC} Servidor não está rodando"
    echo -e "    ${BLUE}Iniciar:${NC} ./start_ihm.sh"
fi
echo ""

# Resumo
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}${BOLD}✓ SISTEMA OK - Tudo funcionando perfeitamente!${NC}"
    echo ""
    echo "Próximo passo:"
    echo "  ./start_ihm.sh              # Iniciar servidor"
    echo "  ou"
    echo "  ./start_ihm.sh --stub       # Modo simulação (sem CLP)"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}${BOLD}⚠ AVISOS: $WARNINGS${NC}"
    echo ""
    echo "Sistema funcional, mas há alguns avisos acima."
else
    echo -e "${RED}${BOLD}✗ ERROS: $ERRORS | AVISOS: $WARNINGS${NC}"
    echo ""
    echo "Corrija os erros acima antes de prosseguir."
fi
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════════════════${NC}"
