#!/bin/bash
# Script para reiniciar servidor IHM com código atualizado
# Data: 06/Jan/2026

echo "=========================================="
echo "  REINICIANDO SERVIDOR IHM"
echo "=========================================="
echo ""

# 1. Parar processos antigos
echo "🔴 Parando processos antigos..."
pkill -9 -f "python3 main_server.py"
pkill -9 -f "python main_server.py"
sleep 1

# 2. Verificar se parou
RUNNING=$(ps aux | grep "main_server.py" | grep -v grep)
if [ -n "$RUNNING" ]; then
    echo "⚠️  Ainda há processos rodando:"
    echo "$RUNNING"
    echo ""
    echo "Tente matar manualmente:"
    echo "  ps aux | grep main_server"
    echo "  kill -9 <PID>"
    exit 1
fi

echo "✅ Processos antigos parados"
echo ""

# 3. Verificar arquivos atualizados
echo "🔍 Verificando código atualizado..."
if grep -q "HEARTBEAT_INTERVAL = 20" main_server.py; then
    echo "✅ main_server.py: Heartbeat 3s configurado"
else
    echo "❌ main_server.py: Código antigo ainda presente!"
    exit 1
fi

if grep -q "timeout=0.5" modbus_client.py; then
    echo "✅ modbus_client.py: Timeout 500ms configurado"
else
    echo "❌ modbus_client.py: Código antigo ainda presente!"
    exit 1
fi

if grep -q "timeSinceLastMessage > 10000" static/index.html; then
    echo "✅ index.html: Watchdog 10s configurado"
else
    echo "❌ index.html: Código antigo ainda presente!"
    exit 1
fi

echo ""
echo "✅ Todas as atualizações verificadas!"
echo ""

# 4. Iniciar servidor novo
echo "🚀 Iniciando servidor com código atualizado..."
echo ""
python3 main_server.py
