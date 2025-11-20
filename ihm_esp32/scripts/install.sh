#!/bin/bash
###############################################################################
# Script de Instalação - IHM Web Raspberry Pi 3B+
# Dobradeira NEOCOUDE-HD-15
###############################################################################

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funções auxiliares
print_header() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}\n"
}

print_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    print_error "Execute com sudo: sudo bash scripts/install.sh"
    exit 1
fi

# Variáveis
USER_HOME="/home/pi"
INSTALL_DIR="$USER_HOME/ihm_esp32"
VENV_DIR="$INSTALL_DIR/venv"

print_header "INSTALAÇÃO IHM WEB - RASPBERRY PI 3B+"

# 1. Atualizar sistema
print_step "Atualizando sistema..."
apt update
apt upgrade -y
print_success "Sistema atualizado"

# 2. Instalar dependências do sistema
print_step "Instalando dependências do sistema..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    hostapd \
    dnsmasq \
    net-tools \
    wireless-tools \
    rfkill

print_success "Dependências instaladas"

# 3. Desbloquear WiFi (se bloqueado)
print_step "Desbloqueando WiFi..."
rfkill unblock wlan
print_success "WiFi desbloqueado"

# 4. Criar diretório de instalação
print_step "Preparando diretório de instalação..."
if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
    chown -R pi:pi "$INSTALL_DIR"
fi

# Copiar arquivos do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cp -r "$SCRIPT_DIR"/* "$INSTALL_DIR/"
chown -R pi:pi "$INSTALL_DIR"

print_success "Diretório preparado: $INSTALL_DIR"

# 5. Criar virtual environment e instalar dependências Python
print_step "Criando virtual environment..."
sudo -u pi python3 -m venv "$VENV_DIR"
print_success "Virtual environment criado"

print_step "Instalando dependências Python..."
sudo -u pi "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u pi "$VENV_DIR/bin/pip" install \
    pymodbus \
    aiohttp \
    aiohttp-cors \
    websockets \
    gpiozero

print_success "Dependências Python instaladas"

# 6. Configurar WiFi AP (hostapd)
print_step "Configurando WiFi Access Point..."

# Parar serviços
systemctl stop hostapd || true
systemctl stop dnsmasq || true

# Copiar configuração hostapd
cp "$INSTALL_DIR/config/hostapd.conf" /etc/hostapd/hostapd.conf

# Configurar daemon
cat > /etc/default/hostapd << 'HOSTAPD_EOF'
DAEMON_CONF="/etc/hostapd/hostapd.conf"
HOSTAPD_EOF

print_success "hostapd configurado"

# 7. Configurar DHCP (dnsmasq)
print_step "Configurando servidor DHCP..."

# Backup da configuração original
if [ -f /etc/dnsmasq.conf ] && [ ! -f /etc/dnsmasq.conf.orig ]; then
    mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
fi

# Copiar nova configuração
cp "$INSTALL_DIR/config/dnsmasq.conf" /etc/dnsmasq.conf

print_success "dnsmasq configurado"

# 8. Configurar interface de rede
print_step "Configurando interface wlan0..."

# Backup dhcpcd.conf
if [ -f /etc/dhcpcd.conf ] && [ ! -f /etc/dhcpcd.conf.orig ]; then
    cp /etc/dhcpcd.conf /etc/dhcpcd.conf.orig
fi

# Adicionar configuração wlan0 (se não existir)
if ! grep -q "interface wlan0" /etc/dhcpcd.conf; then
    cat >> /etc/dhcpcd.conf << 'DHCPCD_EOF'

# IHM Web - WiFi Access Point
interface wlan0
    static ip_address=192.168.50.1/24
    nohook wpa_supplicant
DHCPCD_EOF
fi

print_success "Interface wlan0 configurada"

# 9. Habilitar IP forwarding (opcional - para internet via Ethernet)
print_step "Habilitando IP forwarding..."
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sysctl -p > /dev/null 2>&1

print_success "IP forwarding habilitado"

# 10. Configurar iptables NAT (opcional - compartilhar internet)
print_step "Configurando NAT (para compartilhar internet via Ethernet)..."
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Adicionar ao boot
if ! grep -q "iptables-restore" /etc/rc.local; then
    sed -i 's/^exit 0/iptables-restore < \/etc\/iptables.ipv4.nat\nexit 0/' /etc/rc.local
fi

print_success "NAT configurado"

# 11. Instalar serviço systemd
print_step "Instalando serviço systemd..."

# Copiar service file
cp "$INSTALL_DIR/config/ihm.service" /etc/systemd/system/ihm.service

# Reload daemon
systemctl daemon-reload

# Habilitar serviços
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq
systemctl enable ihm.service

print_success "Serviço systemd instalado e habilitado"

# 12. Verificar permissões USB (dialout group)
print_step "Configurando permissões USB..."
usermod -a -G dialout pi
print_success "Usuário 'pi' adicionado ao grupo 'dialout'"

# 13. Reiniciar serviços de rede
print_step "Reiniciando serviços de rede..."
systemctl restart dhcpcd
sleep 2
systemctl start hostapd
systemctl start dnsmasq

print_success "Serviços de rede reiniciados"

# 14. Teste de conectividade Modbus (opcional)
print_step "Verificando porta USB-RS485..."
if ls /dev/ttyUSB* > /dev/null 2>&1; then
    print_success "Porta USB detectada: $(ls /dev/ttyUSB*)"
else
    print_error "Porta USB não detectada - conecte o conversor USB-RS485"
fi

# 15. Resumo final
print_header "INSTALAÇÃO CONCLUÍDA!"

echo -e "${GREEN}Próximos passos:${NC}"
echo "1. Reinicie o Raspberry Pi: sudo reboot"
echo "2. Após reiniciar, o WiFi 'IHM_NEOCOUDE' estará disponível"
echo "3. Conecte seu tablet ao WiFi (senha: dobradeira123)"
echo "4. Abra o navegador e acesse: http://192.168.50.1"
echo ""
echo -e "${YELLOW}Comandos úteis:${NC}"
echo "  sudo systemctl status ihm          # Ver status do servidor"
echo "  sudo systemctl status hostapd      # Ver status do WiFi AP"
echo "  sudo journalctl -u ihm -f          # Ver logs em tempo real"
echo "  iw dev wlan0 station dump          # Ver clientes conectados"
echo ""
echo -e "${YELLOW}Para trocar senha do WiFi:${NC}"
echo "  sudo nano /etc/hostapd/hostapd.conf  # Editar wpa_passphrase"
echo "  sudo systemctl restart hostapd       # Reiniciar serviço"
echo ""
echo -e "${GREEN}Desenvolvido por: Eng. Lucas William Junges${NC}"
echo -e "${GREEN}Data: Novembro 2025${NC}"
echo ""
