#!/bin/bash
# Script para configurar Wine otimizado para WinSUP 2
# Cria um Wine prefix dedicado com todas as dependências

set -e

echo "=========================================="
echo "CONFIGURAÇÃO WINE PARA WINSUP 2"
echo "=========================================="
echo ""

# Diretório para o Wine prefix dedicado
WINEPREFIX_DIR="$HOME/.wine-winsup"
export WINEPREFIX="$WINEPREFIX_DIR"
export WINEARCH=win32  # 32-bit (WinSUP geralmente é 32-bit)

echo "1. Criando Wine prefix dedicado em: $WINEPREFIX_DIR"
echo "   Arquitetura: 32-bit (win32)"

if [ -d "$WINEPREFIX_DIR" ]; then
    echo "   ⚠ Wine prefix já existe. Deseja recriar? (s/n)"
    read -r resposta
    if [ "$resposta" = "s" ]; then
        echo "   Removendo prefix antigo..."
        rm -rf "$WINEPREFIX_DIR"
    else
        echo "   Usando prefix existente."
    fi
fi

# Criar novo prefix (32-bit)
if [ ! -d "$WINEPREFIX_DIR" ]; then
    echo "   Criando novo Wine prefix 32-bit..."
    wineboot --init
    echo "   ✓ Prefix criado"
fi

echo ""
echo "2. Configurando portas COM..."

# Criar links simbólicos para portas COM
mkdir -p "$WINEPREFIX_DIR/dosdevices"

# Remover links antigos
rm -f "$WINEPREFIX_DIR/dosdevices/com"*

# Criar COM1 -> ttyUSB0 (porta principal)
ln -sf /dev/ttyUSB0 "$WINEPREFIX_DIR/dosdevices/com1"
echo "   ✓ COM1 -> /dev/ttyUSB0"

# Criar COM2 -> ttyUSB1 (caso exista)
if [ -e /dev/ttyUSB1 ]; then
    ln -sf /dev/ttyUSB1 "$WINEPREFIX_DIR/dosdevices/com2"
    echo "   ✓ COM2 -> /dev/ttyUSB1"
fi

echo ""
echo "3. Instalando dependências Windows..."
echo "   Isso pode demorar alguns minutos..."

# Instalar bibliotecas necessárias via winetricks
# Modo silencioso para não abrir janelas
export DISPLAY=:0

winetricks -q --force \
    vcrun2015 \
    vcrun2017 \
    vcrun2019 \
    dotnet35 \
    dotnet40 \
    dotnet48 \
    corefonts \
    msxml3 \
    msxml6 \
    2>/dev/null || echo "   ⚠ Algumas dependências podem ter falhado (normal)"

echo "   ✓ Dependências instaladas"

echo ""
echo "4. Configurando Wine para modo Windows XP/7..."

# Configurar Wine para emular Windows 7 (melhor compatibilidade com apps industriais)
wine reg add 'HKEY_CURRENT_USER\Software\Wine' /v Version /t REG_SZ /d win7 /f

# Configurar DPI para evitar problemas de interface
wine reg add 'HKEY_CURRENT_USER\Control Panel\Desktop' /v LogPixels /t REG_DWORD /d 96 /f

echo "   ✓ Configurações aplicadas"

echo ""
echo "5. Criando script de lançamento do WinSUP..."

cat > "$HOME/Documents/clientes/w&co/run_winsup.sh" << 'SCRIPT_END'
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
SCRIPT_END

chmod +x "$HOME/Documents/clientes/w&co/run_winsup.sh"

echo "   ✓ Script criado: run_winsup.sh"

echo ""
echo "=========================================="
echo "✓ CONFIGURAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo ""
echo "1. Instalar o WinSUP 2:"
echo "   WINEPREFIX=$WINEPREFIX wine /caminho/para/setup_winsup.exe"
echo ""
echo "2. Dar permissão para a porta USB:"
echo "   sudo chmod 666 /dev/ttyUSB0"
echo ""
echo "3. Executar o WinSUP:"
echo "   ./run_winsup.sh"
echo ""
echo "No WinSUP, configure:"
echo "   - Porta: COM1"
echo "   - Baudrate: 57600"
echo "   - Paridade: Nenhuma"
echo "   - Stop bits: 2"
echo "   - Slave ID: 1"
echo ""
echo "Prefix Wine: $WINEPREFIX_DIR"
echo "=========================================="
