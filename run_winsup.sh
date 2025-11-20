#!/bin/bash
# Script para rodar WinSUP 2 com Wine otimizado

export WINEPREFIX="$HOME/.wine-winsup"
export WINEARCH=win32
export WINEDEBUG=-all  # Desabilita mensagens de debug

# Verificar se porta está disponível
if ! ls /dev/ttyUSB0 &>/dev/null; then
    echo "❌ ERRO: /dev/ttyUSB0 não encontrado!"
    echo "   Verifique se o adaptador USB-RS485 está conectado"
    exit 1
fi

# Verificar permissões
if ! [ -r /dev/ttyUSB0 ] || ! [ -w /dev/ttyUSB0 ]; then
    echo "⚠ AVISO: Sem permissão para acessar /dev/ttyUSB0"
    echo "   Execute: sudo chmod 666 /dev/ttyUSB0"
    echo "   Ou adicione seu usuário ao grupo dialout"
    exit 1
fi

echo "Iniciando WinSUP 2..."
echo "Wine prefix: $WINEPREFIX"
echo "Porta COM1 -> /dev/ttyUSB0"
echo ""

# Localizar WinSUP (ajuste o caminho se necessário)
WINSUP_PATH=$(find "$WINEPREFIX/drive_c" -name "WinSUP*.exe" 2>/dev/null | head -1)

if [ -z "$WINSUP_PATH" ]; then
    echo "❌ WinSUP não encontrado!"
    echo "   Instale o WinSUP primeiro:"
    echo "   WINEPREFIX=$WINEPREFIX wine /caminho/para/setup_winsup.exe"
    exit 1
fi

echo "Executando: $WINSUP_PATH"
wine "$WINSUP_PATH"
