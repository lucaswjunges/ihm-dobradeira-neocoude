#!/bin/bash
# Teste completo de escrita/leitura com mbpoll
# Data: 16/Nov/2025
# Inclui: ângulos, velocidade, botões, I/O

PORT="/dev/ttyUSB0"
BAUD="57600"
SLAVE="1"
PARITY="none"
STOPBITS="2"

echo "========================================"
echo "TESTE COMPLETO DE GRAVAÇÃO - MBPOLL"
echo "CLP Atos MPC4004 - IHM Dobradeira"
echo "========================================"
echo ""
echo "Porta: $PORT"
echo "Baudrate: $BAUD"
echo "Slave ID: $SLAVE"
echo ""

# Verificar conexão básica
echo "=== TESTE DE CONEXÃO ==="
echo "Lendo estado 0x00BE (190) - Modbus habilitado..."
mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 190 -t 0 -c 1 $PORT

if [ $? -eq 0 ]; then
    echo "✅ Conexão OK"
else
    echo "❌ Falha na conexão - verifique porta e cabos"
    exit 1
fi
echo ""

# Menu interativo
while true; do
    echo ""
    echo "=== MENU DE TESTES ==="
    echo "1) Gravar e ler ângulos de dobra"
    echo "2) Mudar classe de velocidade (K1+K7)"
    echo "3) Testar botão individual (pulso)"
    echo "4) Ler encoder atual"
    echo "5) Ler todas as entradas digitais (E0-E7)"
    echo "6) Ler todas as saídas digitais (S0-S7)"
    echo "7) Testar escrita de ângulo customizado"
    echo "8) Executar teste completo automatizado"
    echo "0) Sair"
    echo ""
    echo -n "Escolha uma opção: "
    read choice

    case $choice in
        1)
            echo ""
            echo "=== GRAVANDO ÂNGULOS DE TESTE ==="
            # Dobra 1: 90°
            echo "Dobra 1 Esquerda: 90.0°"
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2112 -t 4 $PORT 0      # MSW
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2114 -t 4 $PORT 900    # LSW

            # Dobra 2: 120°
            echo "Dobra 2 Esquerda: 120.0°"
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2120 -t 4 $PORT 0      # MSW
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2122 -t 4 $PORT 1200   # LSW

            # Dobra 3: 135°
            echo "Dobra 3 Esquerda: 135.0°"
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2128 -t 4 $PORT 0      # MSW
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2130 -t 4 $PORT 1350   # LSW

            echo ""
            echo "=== LENDO DE VOLTA ==="
            echo "Dobra 1:"
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2112 -t 4 -c 2 $PORT

            echo "Dobra 2:"
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2120 -t 4 -c 2 $PORT

            echo "Dobra 3:"
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2128 -t 4 -c 2 $PORT
            ;;

        2)
            echo ""
            echo "=== MUDANÇA DE VELOCIDADE (K1+K7) ==="
            echo "ATENÇÃO: Só funciona em MODO MANUAL e máquina PARADA"
            echo ""
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 160 -t 0 $PORT 1  # K1 ON
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 166 -t 0 $PORT 1  # K7 ON
            sleep 0.1
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 160 -t 0 $PORT 0  # K1 OFF
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 166 -t 0 $PORT 0  # K7 OFF
            echo "✅ Comando enviado - verificar display físico"
            ;;

        3)
            echo ""
            echo "Botões disponíveis:"
            echo "K0=169, K1=160, K2=161, K3=162, K4=163, K5=164"
            echo "K6=165, K7=166, K8=167, K9=168"
            echo "S1=220, S2=221, ENTER=37, ESC=188, EDIT=38"
            echo ""
            echo -n "Digite o endereço do botão: "
            read btn_addr

            echo "Enviando pulso no botão $btn_addr..."
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $btn_addr -t 0 $PORT 1
            sleep 0.1
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $btn_addr -t 0 $PORT 0
            echo "✅ Pulso enviado"
            ;;

        4)
            echo ""
            echo "=== LENDO ENCODER (0x04D6/0x04D7) ==="
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 1238 -t 4 -c 2 $PORT
            echo ""
            echo "Converter para graus: (MSW << 16 | LSW) / 10"
            ;;

        5)
            echo ""
            echo "=== ENTRADAS DIGITAIS (E0-E7) ==="
            for i in {0..7}; do
                addr=$((256 + i))
                echo -n "E$i (coil $addr): "
                mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $addr -t 0 -c 1 $PORT 2>/dev/null | grep -E "\[0\]|\[1\]"
            done
            ;;

        6)
            echo ""
            echo "=== SAÍDAS DIGITAIS (S0-S7) ==="
            for i in {0..7}; do
                addr=$((384 + i))
                echo -n "S$i (coil $addr): "
                mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $addr -t 0 -c 1 $PORT 2>/dev/null | grep -E "\[0\]|\[1\]"
            done
            ;;

        7)
            echo ""
            echo "=== ÂNGULO CUSTOMIZADO ==="
            echo -n "Digite o ângulo em graus (ex: 45.5): "
            read angle_deg

            # Converter para valor CLP (x10)
            value_clp=$(awk "BEGIN {printf \"%d\", $angle_deg * 10}")
            msw=$((value_clp >> 16))
            lsw=$((value_clp & 0xFFFF))

            echo "Valor CLP: $value_clp (MSW=$msw, LSW=$lsw)"
            echo ""
            echo "Gravar em qual dobra?"
            echo "1) Dobra 1 (2112/2114)"
            echo "2) Dobra 2 (2120/2122)"
            echo "3) Dobra 3 (2128/2130)"
            echo -n "Escolha: "
            read bend_choice

            case $bend_choice in
                1) msw_addr=2112; lsw_addr=2114 ;;
                2) msw_addr=2120; lsw_addr=2122 ;;
                3) msw_addr=2128; lsw_addr=2130 ;;
                *) echo "Opção inválida"; continue ;;
            esac

            echo "Gravando..."
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $msw_addr -t 4 $PORT $msw
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $lsw_addr -t 4 $PORT $lsw

            echo ""
            echo "Lendo de volta:"
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r $msw_addr -t 4 -c 2 $PORT
            ;;

        8)
            echo ""
            echo "=== TESTE AUTOMATIZADO COMPLETO ==="

            echo "1) Lendo encoder..."
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 1238 -t 4 -c 2 $PORT

            echo ""
            echo "2) Gravando ângulos: 90°, 120°, 45°..."
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2112 -t 4 $PORT 0
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2114 -t 4 $PORT 900
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2120 -t 4 $PORT 0
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2122 -t 4 $PORT 1200
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2128 -t 4 $PORT 0
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2130 -t 4 $PORT 450

            echo ""
            echo "3) Verificando gravação..."
            sleep 0.5
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2112 -t 4 -c 2 $PORT
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2120 -t 4 -c 2 $PORT
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 2128 -t 4 -c 2 $PORT

            echo ""
            echo "4) Testando pulso em K1..."
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 160 -t 0 $PORT 1
            sleep 0.1
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 160 -t 0 $PORT 0

            echo ""
            echo "5) Lendo I/O digital..."
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 256 -t 0 -c 8 $PORT
            mbpoll -a $SLAVE -b $BAUD -P $PARITY -s $STOPBITS -r 384 -t 0 -c 8 $PORT

            echo ""
            echo "✅ TESTE COMPLETO FINALIZADO"
            ;;

        0)
            echo "Saindo..."
            exit 0
            ;;

        *)
            echo "Opção inválida"
            ;;
    esac
done
