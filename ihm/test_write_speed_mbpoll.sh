#!/bin/bash
# Teste de mudança de classe de velocidade via mbpoll
# Data: 16/Nov/2025
# Método: K1+K7 simultâneo (pulso 100ms)

PORT="/dev/ttyUSB0"
BAUD="57600"
SLAVE="1"
PARITY="none"
STOPBITS="2"

echo "========================================"
echo "TESTE DE MUDANÇA DE VELOCIDADE - MBPOLL"
echo "========================================"
echo ""

# Endereços dos botões
K1_ADDR=160  # 0x00A0
K7_ADDR=166  # 0x00A6

echo "IMPORTANTE: A mudança de velocidade só funciona em MODO MANUAL e máquina PARADA"
echo ""
echo "Ciclo de velocidades: 5 rpm → 10 rpm → 15 rpm → 5 rpm"
echo ""

# Função para pressionar K1+K7 simultaneamente
press_k1_k7() {
    echo ">>> Pressionando K1+K7 simultaneamente..."

    # Liga K1
    echo "    K1 ON (coil $K1_ADDR)..."
    mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $K1_ADDR -t 0 $PORT 1 > /dev/null 2>&1

    # Liga K7
    echo "    K7 ON (coil $K7_ADDR)..."
    mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $K7_ADDR -t 0 $PORT 1 > /dev/null 2>&1

    # Aguarda 100ms
    echo "    Aguardando 100ms..."
    sleep 0.1

    # Desliga K1
    echo "    K1 OFF..."
    mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $K1_ADDR -t 0 $PORT 0 > /dev/null 2>&1

    # Desliga K7
    echo "    K7 OFF..."
    mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $K7_ADDR -t 0 $PORT 0 > /dev/null 2>&1

    echo "    ✅ Comando enviado"
    echo ""
}

# Função para ler estado de velocidade (se houver registro específico)
# NOTA: Pode não existir registro direto - verificar no display físico
read_speed_state() {
    echo ">>> Tentando ler indicadores de velocidade..."

    # Tentar ler LEDs K1/K2/K3 (podem indicar classe)
    echo "    LED1 (192):"
    mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 192 -t 0 -c 1 $PORT 2>/dev/null | grep -E "\[0\]|\[1\]"

    echo "    LED2 (193):"
    mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 193 -t 0 -c 1 $PORT 2>/dev/null | grep -E "\[0\]|\[1\]"

    echo "    LED3 (194):"
    mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 194 -t 0 -c 1 $PORT 2>/dev/null | grep -E "\[0\]|\[1\]"

    echo ""
    echo "    NOTA: Verificar display físico para confirmar velocidade"
    echo ""
}

echo "=== TESTE 1: Mudança de Velocidade ==="
echo ""

for i in {1..3}; do
    echo "--- Tentativa $i ---"
    press_k1_k7
    read_speed_state
    echo "Verificar no display físico se a velocidade mudou"
    echo ""

    if [ $i -lt 3 ]; then
        echo "Pressione ENTER para próxima mudança (ou Ctrl+C para sair)..."
        read
    fi
done

echo ""
echo "=== RESULTADO ESPERADO ==="
echo "- Após cada K1+K7, a velocidade deve ciclar: 5→10→15→5 rpm"
echo "- Verificar no display físico da IHM"
echo "- LEDs podem indicar classe de velocidade (confirmar no ladder)"
echo ""
echo "✅ Se o display mudou: SUCESSO"
echo "❌ Se não mudou: Verificar se está em MODO MANUAL e PARADA"
