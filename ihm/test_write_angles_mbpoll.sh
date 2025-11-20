#!/bin/bash
# Teste de gravação de ângulos de dobra via mbpoll
# Data: 16/Nov/2025
# CLP: Atos MPC4004, Slave ID=1, 57600 bps, 8N2

PORT="/dev/ttyUSB0"
BAUD="57600"
SLAVE="1"
PARITY="none"
STOPBITS="2"

echo "========================================"
echo "TESTE DE GRAVAÇÃO DE ÂNGULOS - MBPOLL"
echo "========================================"
echo ""

# Função para converter graus para valor CLP (graus * 10)
# e escrever nos registros MSW+LSW
write_angle() {
    local name=$1
    local degrees=$2
    local msw_addr=$3
    local lsw_addr=$4

    # Converter para valor CLP (graus * 10)
    local value_clp=$((degrees * 10))

    # Separar em MSW e LSW
    local msw=$((value_clp >> 16))
    local lsw=$((value_clp & 0xFFFF))

    echo ">>> Gravando $name: ${degrees}°"
    echo "    Valor CLP: $value_clp (MSW=$msw, LSW=$lsw)"

    # Escrever MSW
    echo "    Escrevendo MSW no registro $msw_addr..."
    mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $msw_addr -t 4 $PORT $msw

    # Escrever LSW
    echo "    Escrevendo LSW no registro $lsw_addr..."
    mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $lsw_addr -t 4 $PORT $lsw

    echo ""
}

# Função para ler ângulo (32-bit MSW+LSW)
read_angle() {
    local name=$1
    local msw_addr=$2
    local lsw_addr=$3

    echo ">>> Lendo $name:"
    echo "    MSW (registro $msw_addr):"
    msw_val=$(mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $msw_addr -t 4 -c 1 $PORT 2>/dev/null | grep "\[" | awk '{print $2}' | tr -d '[]')

    echo "    LSW (registro $lsw_addr):"
    lsw_val=$(mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $lsw_addr -t 4 -c 1 $PORT 2>/dev/null | grep "\[" | awk '{print $2}' | tr -d '[]')

    # Calcular valor 32-bit
    if [ -n "$msw_val" ] && [ -n "$lsw_val" ]; then
        value_clp=$(( (msw_val << 16) + lsw_val ))
        degrees=$(awk "BEGIN {printf \"%.1f\", $value_clp / 10}")
        echo "    Valor lido: $value_clp → ${degrees}°"
    else
        echo "    ERRO: Não foi possível ler os registros"
    fi
    echo ""
}

echo "=== FASE 1: GRAVAÇÃO DE ÂNGULOS ==="
echo ""

# Gravar ângulos de teste
# Dobra 1 Esquerda: 90.0°
write_angle "Dobra 1 Esquerda" 90 2112 2114

# Dobra 2 Esquerda: 120.0°
write_angle "Dobra 2 Esquerda" 120 2120 2122

# Dobra 3 Esquerda: 135.5°
write_angle "Dobra 3 Esquerda" 135 2128 2130

echo ""
echo "=== FASE 2: VERIFICAÇÃO DOS VALORES GRAVADOS ==="
echo ""
sleep 1

# Ler de volta para confirmar
read_angle "Dobra 1 Esquerda" 2112 2114
read_angle "Dobra 2 Esquerda" 2120 2122
read_angle "Dobra 3 Esquerda" 2128 2130

echo ""
echo "=== FASE 3: TESTE COM ÂNGULOS FRACIONÁRIOS ==="
echo ""

# Testar ângulos com decimais (45.5°, 67.3°, 88.9°)
write_angle "Dobra 1 (teste)" 45 2112 2114
sleep 0.5
read_angle "Dobra 1 (verificação)" 2112 2114

write_angle "Dobra 2 (teste)" 67 2120 2122
sleep 0.5
read_angle "Dobra 2 (verificação)" 2120 2122

write_angle "Dobra 3 (teste)" 89 2128 2130
sleep 0.5
read_angle "Dobra 3 (verificação)" 2128 2130

echo ""
echo "=== TESTE COMPLETO ==="
echo ""
echo "✅ Verificar se os valores gravados correspondem aos lidos"
echo "✅ Confirmar conversão graus ↔ valor_clp (x10 / ÷10)"
echo "✅ Testar na IHM física se os ângulos aparecem corretamente"
