#!/bin/bash
# Teste completo da funcionalidade ROT5
# Após upload do ladder clp_MODIFICADO_IHM_WEB_COM_ROT5.sup

set -e  # Parar em caso de erro

DEVICE="/dev/ttyUSB1"
BAUDRATE="57600"
SLAVE="1"

echo "============================================"
echo "TESTE COMPLETO ROT5 - MODBUS INTERFACE"
echo "============================================"
echo "Device: $DEVICE"
echo "Baudrate: $BAUDRATE"
echo "Slave ID: $SLAVE"
echo ""

# Função helper para escrita de ângulo
write_angle() {
    local msw_addr=$1
    local lsw_addr=$2
    local angle=$3
    local trigger_addr=$4
    local angle_name=$5

    echo "=== $angle_name: $angle° ==="

    # Escrever MSW (sempre 0 para ângulos até 359°)
    echo "Escrevendo MSW (0x$(printf %04X $msw_addr)) = 0"
    mbpoll -m rtu -a $SLAVE -b $BAUDRATE -P none -s 2 -t 4 -r $msw_addr -1 $DEVICE -- 0

    # Escrever LSW (valor do ângulo)
    echo "Escrevendo LSW (0x$(printf %04X $lsw_addr)) = $angle"
    mbpoll -m rtu -a $SLAVE -b $BAUDRATE -P none -s 2 -t 4 -r $lsw_addr -1 $DEVICE -- $angle

    # Ativar trigger
    echo "Ativando trigger 0x$(printf %04X $trigger_addr)"
    mbpoll -m rtu -a $SLAVE -b $BAUDRATE -P none -s 2 -t 0 -r $trigger_addr -1 $DEVICE -- 1
    sleep 0.1

    # Desativar trigger
    echo "Desativando trigger 0x$(printf %04X $trigger_addr)"
    mbpoll -m rtu -a $SLAVE -b $BAUDRATE -P none -s 2 -t 0 -r $trigger_addr -1 $DEVICE -- 0
    sleep 0.5

    echo ""
}

# Função para ler shadow area
read_shadow() {
    local shadow_addr=$1
    local angle_name=$2

    echo "Lendo shadow area 0x$(printf %04X $shadow_addr) ($angle_name):"
    mbpoll -m rtu -a $SLAVE -b $BAUDRATE -P none -s 2 -t 4 -r $shadow_addr -c 2 -1 $DEVICE
    echo ""
}

# Verificar bit 0x00F7 (condição para ROT5 executar)
echo "=== VERIFICAÇÃO INICIAL ==="
echo "Verificando bit 0x00F7 (deve estar ON para ROT5 executar):"
mbpoll -m rtu -a $SLAVE -b $BAUDRATE -P none -s 2 -t 0 -r 0x00F7 -1 $DEVICE
echo ""

# Teste 1: Ângulo Esquerda 1 (90°)
write_angle 0x0A00 0x0A02 90 0x0390 "Ângulo Esquerda 1"
read_shadow 0x0840 "Ângulo Esquerda 1"

# Teste 2: Ângulo Direita 1 (120°)
write_angle 0x0A04 0x0A06 120 0x0391 "Ângulo Direita 1"
read_shadow 0x0846 "Ângulo Direita 1"

# Teste 3: Ângulo Esquerda 2 (45°)
write_angle 0x0A08 0x0A0A 45 0x0392 "Ângulo Esquerda 2"
read_shadow 0x0850 "Ângulo Esquerda 2"

echo "============================================"
echo "RESUMO DO TESTE"
echo "============================================"
echo "Leitura final de todas as shadow areas:"
echo ""
echo "Shadow 0x0840-0x0842 (Ângulo Esquerda 1 - esperado: 90°):"
mbpoll -m rtu -a $SLAVE -b $BAUDRATE -P none -s 2 -t 4 -r 0x0840 -c 2 -1 $DEVICE
echo ""
echo "Shadow 0x0846-0x0848 (Ângulo Direita 1 - esperado: 120°):"
mbpoll -m rtu -a $SLAVE -b $BAUDRATE -P none -s 2 -t 4 -r 0x0846 -c 2 -1 $DEVICE
echo ""
echo "Shadow 0x0850-0x0852 (Ângulo Esquerda 2 - esperado: 45°):"
mbpoll -m rtu -a $SLAVE -b $BAUDRATE -P none -s 2 -t 4 -r 0x0850 -c 2 -1 $DEVICE
echo ""
echo "IMPORTANTE: Valores podem ser modificados pelo Principal.lad"
echo "após a cópia. Isso é comportamento normal."
echo "============================================"
