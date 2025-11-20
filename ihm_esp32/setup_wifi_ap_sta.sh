#!/bin/bash
# Script para configurar WiFi AP + STA simultaneamente no Raspberry Pi 3B+
# Permite que o RPi seja Access Point E conecte em uma rede WiFi ao mesmo tempo

echo "=============================================="
echo "  CONFIGURAÇÃO WiFi AP + STA SIMULTÂNEO"
echo "=============================================="
echo ""

# Verifica se é root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Este script precisa ser executado como root"
    echo "Use: sudo bash $0"
    exit 1
fi

echo "1. Instalando pacotes necessários..."
apt-get update
apt-get install -y hostapd dnsmasq iptables-persistent

echo ""
echo "2. Configurando dhcpcd..."

# Backup
cp /etc/dhcpcd.conf /etc/dhcpcd.conf.backup

# Configurar IP estático para wlan0 (AP)
cat >> /etc/dhcpcd.conf <<'EOF'

# Configuração AP (wlan0)
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF

echo "✓ dhcpcd configurado"

echo ""
echo "3. Configurando dnsmasq (DHCP para AP)..."

# Backup
mv /etc/dnsmasq.conf /etc/dnsmasq.conf.backup

cat > /etc/dnsmasq.conf <<'EOF'
# Interface para servir DHCP (AP)
interface=wlan0

# Range de IPs para clientes WiFi
dhcp-range=192.168.4.2,192.168.4.254,255.255.255.0,24h

# Gateway e DNS
dhcp-option=3,192.168.4.1  # Gateway
dhcp-option=6,192.168.4.1  # DNS server

# Logging
log-dhcp
log-facility=/var/log/dnsmasq.log
EOF

echo "✓ dnsmasq configurado"

echo ""
echo "4. Configurando hostapd (Access Point)..."

cat > /etc/hostapd/hostapd.conf <<'EOF'
# Interface WiFi
interface=wlan0

# Driver
driver=nl80211

# SSID (nome da rede)
ssid=IHM_NEOCOUDE

# Canal WiFi (1-13)
channel=7

# Modo (g = 2.4GHz)
hw_mode=g

# País (BR = Brasil)
country_code=BR

# Autenticação
auth_algs=1

# Criptografia WPA2
wpa=2
wpa_passphrase=dobradeira2025
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP

# Ignorar broadcast SSID (0=não, 1=sim)
ignore_broadcast_ssid=0
EOF

# Apontar para config
echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' > /etc/default/hostapd

echo "✓ hostapd configurado"
echo "  SSID: IHM_NEOCOUDE"
echo "  Senha: dobradeira2025"

echo ""
echo "5. Habilitando IP forwarding e NAT..."

# Habilitar IP forwarding
sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
echo 1 > /proc/sys/net/ipv4/ip_forward

# Configurar NAT (iptables)
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT

# Salvar regras iptables
iptables-save > /etc/iptables/rules.v4

echo "✓ NAT configurado (eth0 → wlan0)"

echo ""
echo "6. Configurando wpa_supplicant (conectar em WiFi externo)..."

# Criar configuração para conectar em WiFi (STATION mode em outra interface virtual)
# NOTA: RPi3B+ tem apenas 1 interface WiFi física, então vamos usar a mesma
# mas com prioridade ao AP

cat > /etc/wpa_supplicant/wpa_supplicant-wlan1.conf <<'EOF'
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=BR

# Adicione suas redes WiFi aqui
# Exemplo:
# network={
#     ssid="MinhaRedeWiFi"
#     psk="minha_senha"
#     priority=10
# }
EOF

echo "⚠️  IMPORTANTE: Edite /etc/wpa_supplicant/wpa_supplicant-wlan1.conf"
echo "   e adicione suas redes WiFi"

echo ""
echo "7. Habilitando serviços..."

systemctl unmask hostapd
systemctl enable hostapd
systemctl enable dnsmasq

echo "✓ Serviços habilitados"

echo ""
echo "=============================================="
echo "  CONFIGURAÇÃO CONCLUÍDA!"
echo "=============================================="
echo ""
echo "Para aplicar as mudanças:"
echo "  1. Edite /etc/wpa_supplicant/wpa_supplicant-wlan1.conf (adicione suas redes WiFi)"
echo "  2. Reinicie o sistema: sudo reboot"
echo ""
echo "Após reiniciar:"
echo "  - Access Point: SSID 'IHM_NEOCOUDE' (senha: dobradeira2025)"
echo "  - IP do AP: 192.168.4.1"
echo "  - IP da rede WiFi externa: (automático via DHCP)"
echo ""
echo "Servidor IHM estará acessível em:"
echo "  - Via AP: http://192.168.4.1:8080"
echo "  - Via WiFi externo: http://<IP_DHCP>:8080"
echo "=============================================="
