#!/bin/bash
# Script para iniciar servidor IHM com limpeza completa

echo "🧹 Limpando processos e portas..."

# Matar TODOS os processos Python VÁRIAS VEZES
for i in {1..3}; do
    sudo killall -9 python3 2>/dev/null
    sleep 1
done

# Liberar portas FORÇADAMENTE
for i in {1..3}; do
    sudo fuser -k 8080/tcp 2>/dev/null
    sudo fuser -k 8765/tcp 2>/dev/null
    sleep 1
done

# Aguardar liberação completa
sleep 3

# Verificar se portas estão livres
if sudo lsof -i :8080 > /dev/null 2>&1; then
    echo "❌ ERRO: Porta 8080 ainda está em uso!"
    echo "Processos usando porta 8080:"
    sudo lsof -i :8080
    echo ""
    echo "Matando processos manualmente..."
    sudo lsof -ti :8080 | xargs -r sudo kill -9
    sleep 2
fi

if sudo lsof -i :8765 > /dev/null 2>&1; then
    echo "❌ ERRO: Porta 8765 ainda está em uso!"
    sudo lsof -ti :8765 | xargs -r sudo kill -9
    sleep 2
fi

echo "✓ Limpeza concluída"
echo ""
echo "🚀 Iniciando servidor IHM LIVE..."
echo ""

# Iniciar servidor
cd /home/lucas-junges/Documents/wco/ihm_esp32
python3 main_server.py --port /dev/ttyUSB0

# Se chegou aqui, servidor foi interrompido
echo ""
echo "Servidor encerrado"
