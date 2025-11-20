#!/bin/bash
# Bateria de Testes Modbus - CLP Atos com clp_MODIFICADO_IHM_WEB_COM_ROT5.sup
# Data: 2025-11-18
# Objetivo: Validar escrita de ângulos em diferentes áreas de memória

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações Modbus
PORT="/dev/ttyUSB0"
BAUDRATE=57600
SLAVE_ID=1

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}  BATERIA DE TESTES MODBUS - CLP ATOS${NC}"
echo -e "${BLUE}=========================================${NC}"
echo ""
echo "Configuração:"
echo "  Porta: $PORT"
echo "  Baudrate: $BAUDRATE"
echo "  Slave ID: $SLAVE_ID"
echo ""

# Função para pausar entre testes
pause() {
    echo -e "${YELLOW}Pressione ENTER para continuar...${NC}"
    read
}

# Função para testar escrita e leitura
test_write_read() {
    local area=$1
    local addr=$2
    local value=$3
    local description=$4

    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Teste: $description${NC}"
    echo -e "${BLUE}Área: $area | Endereço: $addr (dec) | Valor: $value${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Escrita
    echo -e "\n${YELLOW}[1/3] Escrevendo valor $value no registrador $addr...${NC}"
    mbpoll -m tcp -a $SLAVE_ID -r $addr -t 4:int -b $BAUDRATE -P none $PORT $value

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Escrita bem-sucedida${NC}"
    else
        echo -e "${RED}✗ Erro na escrita${NC}"
        return 1
    fi

    sleep 0.5

    # Leitura
    echo -e "\n${YELLOW}[2/3] Lendo registrador $addr para validar...${NC}"
    mbpoll -m tcp -a $SLAVE_ID -r $addr -c 1 -t 4:int -b $BAUDRATE -P none $PORT

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Leitura bem-sucedida${NC}"
    else
        echo -e "${RED}✗ Erro na leitura${NC}"
        return 1
    fi

    sleep 0.5

    # Leitura da área completa (contexto)
    echo -e "\n${YELLOW}[3/3] Lendo contexto (6 registradores a partir de $addr)...${NC}"
    mbpoll -m tcp -a $SLAVE_ID -r $addr -c 6 -t 4:int -b $BAUDRATE -P none $PORT

    return 0
}

# Função para testar escrita de coil
test_write_coil() {
    local addr=$1
    local value=$2
    local description=$3

    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Teste Coil: $description${NC}"
    echo -e "${BLUE}Endereço: $addr (dec) | Valor: $value${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    echo -e "\n${YELLOW}Escrevendo coil $addr = $value...${NC}"
    mbpoll -m tcp -a $SLAVE_ID -r $addr -t 0 -b $BAUDRATE -P none $PORT $value

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Escrita de coil bem-sucedida${NC}"
    else
        echo -e "${RED}✗ Erro na escrita de coil${NC}"
        return 1
    fi

    sleep 0.5

    echo -e "\n${YELLOW}Lendo coil $addr...${NC}"
    mbpoll -m tcp -a $SLAVE_ID -r $addr -c 1 -t 0 -b $BAUDRATE -P none $PORT

    return 0
}

echo -e "\n${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  FASE 1: TESTE DE COMUNICAÇÃO BÁSICA${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"

pause

echo -e "\n${YELLOW}Testando leitura de registradores (encoder 0x04D6-0x04D7)...${NC}"
mbpoll -m tcp -a $SLAVE_ID -r 1238 -c 2 -t 4:int -b $BAUDRATE -P none $PORT

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Comunicação OK${NC}"
else
    echo -e "${RED}✗ Falha na comunicação - verifique conexão${NC}"
    exit 1
fi

echo -e "\n${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  FASE 2: TESTES ÁREA 0x0A00 (IHM WEB)${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"

pause

# Teste 1: Ângulo 1 Esquerda em 0x0A00
test_write_read "0x0A00" 2560 900 "Ângulo 1 Esquerda (90.0°)"

pause

# Teste 2: Ângulo 2 Esquerda em 0x0A01
test_write_read "0x0A01" 2561 1200 "Ângulo 2 Esquerda (120.0°)"

pause

# Teste 3: Ângulo 3 Esquerda em 0x0A02
test_write_read "0x0A02" 2562 450 "Ângulo 3 Esquerda (45.0°)"

pause

# Teste 4: Ângulo 1 Direita em 0x0A03
test_write_read "0x0A03" 2563 850 "Ângulo 1 Direita (85.0°)"

pause

# Teste 5: Ângulo 2 Direita em 0x0A04
test_write_read "0x0A04" 2564 1100 "Ângulo 2 Direita (110.0°)"

pause

# Teste 6: Ângulo 3 Direita em 0x0A05
test_write_read "0x0A05" 2565 600 "Ângulo 3 Direita (60.0°)"

echo -e "\n${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  FASE 3: TESTES ÁREA 0x0500 (OFICIAL)${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"

pause

# Teste 7: Ângulo inicial 1 em 0x0500
test_write_read "0x0500" 1280 0 "Ângulo Inicial 1 (0°)"

pause

# Teste 8: Ângulo final 1 em 0x0501
test_write_read "0x0501" 1281 900 "Ângulo Final 1 (90.0°)"

pause

# Teste 9: Ângulo inicial 2 em 0x0502
test_write_read "0x0502" 1282 0 "Ângulo Inicial 2 (0°)"

pause

# Teste 10: Ângulo final 2 em 0x0503
test_write_read "0x0503" 1283 1200 "Ângulo Final 2 (120.0°)"

echo -e "\n${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  FASE 4: TESTES ÁREA 0x0392 (TRIGGER)${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"

pause

# Teste 11: Trigger em 0x0392
test_write_read "0x0392" 914 1 "Trigger Alternativo (bit set)"

pause

# Teste 12: Reset trigger
test_write_read "0x0392" 914 0 "Trigger Alternativo (bit reset)"

echo -e "\n${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  FASE 5: TESTES DE COILS (BITS)${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"

pause

# Teste 13: Testar bit de trigger 0x0392 via coil
test_write_coil 914 1 "Trigger 0x0392 ON via coil"

pause

test_write_coil 914 0 "Trigger 0x0392 OFF via coil"

pause

# Teste 14: Testar bit 0x0A10 (possível trigger IHM)
test_write_coil 2576 1 "Bit 0x0A10 ON (trigger IHM?)"

pause

test_write_coil 2576 0 "Bit 0x0A10 OFF"

echo -e "\n${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  FASE 6: VALIDAÇÃO FINAL${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"

pause

echo -e "\n${YELLOW}Lendo área 0x0A00 completa (10 registradores)...${NC}"
mbpoll -m tcp -a $SLAVE_ID -r 2560 -c 10 -t 4:int -b $BAUDRATE -P none $PORT

pause

echo -e "\n${YELLOW}Lendo área 0x0500 completa (10 registradores)...${NC}"
mbpoll -m tcp -a $SLAVE_ID -r 1280 -c 10 -t 4:int -b $BAUDRATE -P none $PORT

pause

echo -e "\n${YELLOW}Lendo área 0x0392 (trigger)...${NC}"
mbpoll -m tcp -a $SLAVE_ID -r 914 -c 1 -t 4:int -b $BAUDRATE -P none $PORT

echo -e "\n${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}  BATERIA DE TESTES CONCLUÍDA!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "Próximos passos:"
echo "  1. Analisar quais áreas aceitaram escrita"
echo "  2. Verificar se CLP reage aos triggers"
echo "  3. Documentar áreas funcionais"
echo "  4. Atualizar modbus_map.py com áreas validadas"
echo ""
