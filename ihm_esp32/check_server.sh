#!/bin/bash

echo "=============================================="
echo "  STATUS DO SERVIDOR IHM"
echo "=============================================="
echo ""

PID=$(cat ihm.pid 2>/dev/null)
if [ -n "$PID" ]; then
    echo "PID: $PID"
    if ps -p $PID > /dev/null 2>&1; then
        echo "Status: ✅ RODANDO"
    else
        echo "Status: ✗ PARADO"
    fi
else
    echo "PID: N/A"
    echo "Status: ✗ PARADO"
fi

echo ""
IP=$(hostname -I | awk '{print $1}')
echo "IP do Raspberry Pi: $IP"
echo ""

echo "Portas abertas:"
ss -tlnp 2>/dev/null | grep -E ":8080|:8765" || echo "  (WebSocket abre sob demanda)"

echo ""
echo "Logs recentes (últimas 8 linhas):"
tail -8 ihm.log 2>/dev/null || echo "  Nenhum log disponível"

echo ""
echo "=============================================="
echo "  ACESSE DE QUALQUER DISPOSITIVO NA REDE:"
echo "  http://$IP:8080"
echo "=============================================="
