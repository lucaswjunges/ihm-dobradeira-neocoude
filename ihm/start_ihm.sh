#!/bin/bash
# Script de inicialização da IHM Web - NEOCOUDE-HD-15
# Data: 12 de Novembro de 2025

cd "$(dirname "$0")"

echo "=============================================="
echo "IHM WEB - NEOCOUDE-HD-15"
echo "=============================================="
echo ""

# Verifica dependências
if ! command -v python3 &> /dev/null; then
    echo "✗ ERRO: Python 3 não encontrado!"
    echo "  Instale com: sudo apt install python3"
    exit 1
fi

if ! python3 -c "import pymodbus" 2>/dev/null; then
    echo "⚠️  AVISO: pymodbus não encontrado"
    echo "  Instalando dependências..."
    pip3 install pymodbus websockets aiohttp
fi

echo ""
echo "Escolha o modo de operação:"
echo ""
echo "  1) STUB MODE (simulação - SEM CLP)"
echo "  2) LIVE MODE (produção - COM CLP)"
echo ""
read -p "Opção (1 ou 2): " opcao

case $opcao in
    1)
        echo ""
        echo "✓ Iniciando em STUB MODE (simulação)"
        echo ""
        python3 main_server.py --stub
        ;;
    2)
        echo ""
        echo "Portas seriais disponíveis:"
        ls -1 /dev/ttyUSB* 2>/dev/null || echo "  Nenhuma porta USB encontrada"
        echo ""
        read -p "Porta serial (padrão: /dev/ttyUSB0): " porta
        porta=${porta:-/dev/ttyUSB0}

        if [ ! -e "$porta" ]; then
            echo "✗ ERRO: Porta $porta não encontrada!"
            exit 1
        fi

        echo ""
        echo "✓ Iniciando em LIVE MODE (CLP em $porta)"
        echo ""
        python3 main_server.py --port "$porta"
        ;;
    *)
        echo "✗ Opção inválida!"
        exit 1
        ;;
esac
