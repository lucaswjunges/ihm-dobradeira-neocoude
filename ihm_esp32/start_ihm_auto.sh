#!/bin/bash
# Script de inicialização da IHM com detecção automática de porta USB

VENV_PYTHON="/home/lucas-junges/Documents/wco/ihm_esp32/venv/bin/python3"
MAIN_SERVER="/home/lucas-junges/Documents/wco/ihm_esp32/main_server.py"

# Detecta automaticamente a porta USB-RS485
if [ -e /dev/ttyUSB0 ]; then
    PORT="/dev/ttyUSB0"
elif [ -e /dev/ttyUSB1 ]; then
    PORT="/dev/ttyUSB1"
elif [ -e /dev/ttyUSB2 ]; then
    PORT="/dev/ttyUSB2"
else
    echo "⚠️ Nenhuma porta USB detectada (/dev/ttyUSB*)"
    echo "Iniciando em modo STUB (simulação)"
    exec $VENV_PYTHON $MAIN_SERVER --stub
    exit 0
fi

echo "✓ Porta USB detectada: $PORT"
exec $VENV_PYTHON $MAIN_SERVER --port $PORT
