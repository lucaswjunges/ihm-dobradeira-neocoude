#!/bin/bash
# Script final para iniciar IHM em modo LIVE

echo "═══════════════════════════════════════════════"
echo " IHM WEB - MODO LIVE - INICIALIZAÇÃO FINAL"
echo "═══════════════════════════════════════════════"

# 1. Matar TUDO
echo
echo "🧹 Limpando processos existentes..."
sudo killall -9 python3 2>/dev/null
sleep 2

# 2. Verificar porta livre
if sudo lsof -i :8080 > /dev/null 2>&1; then
    echo "❌ ERRO: Porta 8080 ainda em uso!"
    sudo lsof -i :8080
    exit 1
fi

echo "✅ Portas liberadas"

# 3. Iniciar servidor LIVE
echo
echo "🚀 Iniciando servidor LIVE..."
echo "   Porta serial: /dev/ttyUSB0"
echo "   Baudrate: 57600"
echo "   Slave ID: 1"
echo

cd /home/lucas-junges/Documents/wco/ihm_esp32
exec python3 main_server.py --port /dev/ttyUSB0
