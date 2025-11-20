#!/bin/bash

###############################################################################
# IHM NEOCOUDE - Script de Configuração WiFi STA
#
# Permite adicionar ou modificar credenciais de rede WiFi externa
# após a instalação inicial.
#
# Uso: sudo bash setup_wifi.sh
###############################################################################

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar root
if [ "$EUID" -ne 0 ]; then
    log_error "Execute como root: sudo bash setup_wifi.sh"
    exit 1
fi

echo "=========================================="
echo "  IHM NEOCOUDE - Configuração WiFi STA"
echo "=========================================="
echo ""

# Escanear redes disponíveis
log_info "Escaneando redes WiFi disponíveis..."
echo ""

# Garantir que wlan0 está up
ip link set wlan0 up 2>/dev/null || true
sleep 2

# Scan
iwlist wlan0 scan 2>/dev/null | grep -E "ESSID|Quality|Encryption" | sed 's/^[ \t]*//' || log_error "Falha ao escanear redes"

echo ""
echo "=========================================="

# Pedir credenciais
read -p "SSID da rede WiFi: " WIFI_SSID
read -s -p "Senha da rede WiFi: " WIFI_PASSWORD
echo ""
echo ""

# Validar entrada
if [ -z "$WIFI_SSID" ]; then
    log_error "SSID não pode estar vazio"
    exit 1
fi

# Adicionar ao wpa_supplicant
log_info "Adicionando credenciais ao wpa_supplicant..."

# Gerar hash da senha
PSK=$(wpa_passphrase "$WIFI_SSID" "$WIFI_PASSWORD" | grep -E "^\s*psk=" | sed 's/^[ \t]*psk=//')

# Adicionar configuração
cat >> /etc/wpa_supplicant/wpa_supplicant.conf << EOF

network={
    ssid="$WIFI_SSID"
    psk=$PSK
    priority=10
}
EOF

log_success "Credenciais adicionadas"

# Reiniciar wpa_supplicant
log_info "Reiniciando wpa_supplicant..."
wpa_cli -i wlan0 reconfigure > /dev/null 2>&1 || true

# Aguardar conexão
log_info "Aguardando conexão (até 30 segundos)..."
sleep 5

# Verificar se conectou
CONNECTED=0
for i in {1..25}; do
    if wpa_cli -i wlan0 status | grep -q "wpa_state=COMPLETED"; then
        CONNECTED=1
        break
    fi
    sleep 1
done

echo ""
if [ $CONNECTED -eq 1 ]; then
    IP=$(ip -4 addr show wlan0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
    log_success "Conectado com sucesso!"
    log_info "IP obtido: $IP"
    log_info "Teste de internet:"
    if ping -c 2 8.8.8.8 > /dev/null 2>&1; then
        log_success "Internet funcionando!"
    else
        log_error "Sem acesso à internet (verifique roteador)"
    fi
else
    log_error "Não foi possível conectar"
    log_info "Verifique SSID e senha e tente novamente"
    exit 1
fi

echo ""
log_success "Configuração concluída!"
