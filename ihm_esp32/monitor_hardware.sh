#!/bin/bash
# Monitor de Hardware - Raspberry Pi 3B+
# Monitora temperatura, throttling e tensão em tempo real

while true; do
    clear
    echo "=========================================="
    echo "  MONITOR DE HARDWARE - Raspberry Pi 3B+"
    echo "=========================================="
    echo ""

    # Temperatura
    TEMP=$(vcgencmd measure_temp | cut -d'=' -f2 | cut -d"'" -f1)
    echo "🌡️  Temperatura: $TEMP°C"

    if (( $(echo "$TEMP > 70" | bc -l) )); then
        echo "   ⚠️  ALTA! Adicione dissipador/cooler"
    elif (( $(echo "$TEMP > 60" | bc -l) )); then
        echo "   ⚠️  Elevada. Melhorar ventilação"
    else
        echo "   ✅ OK"
    fi
    echo ""

    # Throttling
    THROTTLED=$(vcgencmd get_throttled | cut -d'=' -f2)
    echo "⚡ Throttling: $THROTTLED"

    if [ "$THROTTLED" = "0x0" ]; then
        echo "   ✅ OK - Sem problemas"
    elif [ "$THROTTLED" = "0x20000" ]; then
        echo "   ⚠️  Throttling JÁ OCORREU (histórico)"
    elif [ "$THROTTLED" = "0x50000" ]; then
        echo "   ⚠️  Undervoltage JÁ OCORREU (histórico)"
    else
        echo "   ❌ PROBLEMA ATIVO! Verifique fonte/temperatura"
    fi
    echo ""

    # Frequência CPU
    FREQ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq)
    FREQ_MHZ=$((FREQ / 1000))
    echo "💻 CPU: ${FREQ_MHZ} MHz"

    if [ $FREQ_MHZ -lt 1200 ]; then
        echo "   ⚠️  CPU reduzida! (throttling ativo)"
    else
        echo "   ✅ OK"
    fi
    echo ""

    # Tensão
    VOLT=$(vcgencmd measure_volts core | cut -d'=' -f2)
    echo "🔌 Tensão Core: $VOLT"
    echo ""

    # Uptime
    echo "⏱️  Uptime: $(uptime -p)"
    echo ""

    echo "=========================================="
    echo "Atualizando a cada 2 segundos..."
    echo "Pressione Ctrl+C para sair"

    sleep 2
done
