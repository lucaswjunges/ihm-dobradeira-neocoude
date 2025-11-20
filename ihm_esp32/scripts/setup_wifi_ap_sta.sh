#!/bin/bash
###############################################################################
# Setup WiFi - Modo STA+AP Simultâneo (Experimental)
# 
# ATENÇÃO: Raspberry Pi 3B+ tem apenas 1 interface WiFi (wlan0)
# Para STA+AP simultâneo, usamos interface virtual (uap0)
# 
# Esta configuração é EXPERIMENTAL - para produção use Ethernet para STA
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Execute com sudo${NC}"
    exit 1
fi

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Setup WiFi STA+AP Simultâneo${NC}"
echo -e "${YELLOW}========================================${NC}\n"

echo -e "${YELLOW}⚠️  ATENÇÃO:${NC}"
echo "Este modo é EXPERIMENTAL para RPi3B+ (1 interface WiFi)"
echo "Para produção, recomenda-se:"
echo "  - Opção 1: Ethernet para conectar na rede da fábrica"
echo "  - Opção 2: Apenas AP (sem STA)"
echo ""
read -p "Deseja continuar? [s/N]: " confirm

if [[ ! "$confirm" =~ ^[Ss]$ ]]; then
    echo "Cancelado"
    exit 0
fi

# Pedir credenciais WiFi da fábrica
echo ""
read -p "SSID da rede da fábrica: " FACTORY_SSID
read -sp "Senha da rede da fábrica: " FACTORY_PSK
echo ""

# Instalar dependências
apt install -y dnsmasq hostapd

# Criar interface virtual uap0
cat > /etc/systemd/system/create_ap_interface.service << 'IFACE_EOF'
[Unit]
Description=Create AP interface uap0
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/iw dev wlan0 interface add uap0 type __ap

[Install]
WantedBy=multi-user.target
IFACE_EOF

systemctl enable create_ap_interface.service
systemctl start create_ap_interface.service

# Configurar dhcpcd
cat >> /etc/dhcpcd.conf << 'DHCPCD_EOF'

# wlan0 = STA (cliente WiFi - rede da fábrica)
interface wlan0
    # DHCP automático da rede da fábrica

# uap0 = AP (Access Point - IHM)
interface uap0
    static ip_address=192.168.50.1/24
    nohook wpa_supplicant
DHCPCD_EOF

# Configurar wpa_supplicant (STA)
cat >> /etc/wpa_supplicant/wpa_supplicant.conf << WPA_EOF

network={
    ssid="$FACTORY_SSID"
    psk="$FACTORY_PSK"
    priority=10
}
WPA_EOF

# Configurar hostapd (AP em uap0)
cat > /etc/hostapd/hostapd.conf << 'HOSTAPD_EOF'
interface=uap0
driver=nl80211
ssid=IHM_NEOCOUDE
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=dobradeira123
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
country_code=BR
HOSTAPD_EOF

# Configurar dnsmasq (DHCP em uap0)
cat > /etc/dnsmasq.conf << 'DNSMASQ_EOF'
interface=uap0
bind-interfaces
dhcp-range=192.168.50.10,192.168.50.20,255.255.255.0,24h
dhcp-option=3,192.168.50.1
dhcp-option=6,8.8.8.8,8.8.4.4
domain=ihm.local
address=/ihm.local/192.168.50.1
DNSMASQ_EOF

# Habilitar IP forwarding (compartilhar internet wlan0 -> uap0)
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sysctl -p

# Configurar NAT
iptables -t nat -A POSTROUTING -o wlan0 -j MASQUERADE
iptables -A FORWARD -i wlan0 -o uap0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i uap0 -o wlan0 -j ACCEPT
sh -c "iptables-save > /etc/iptables.ipv4.nat"

# Habilitar serviços
systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Configuração Concluída!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo "Reinicie o sistema: sudo reboot"
echo ""
echo "Após reiniciar:"
echo "  - wlan0 conectará em: $FACTORY_SSID (STA)"
echo "  - uap0 criará rede: IHM_NEOCOUDE (AP)"
echo ""
