#!/bin/bash
# Script para habilitar NAT no notebook Linux
# Permite que tablet conectado no ESP32 tenha internet via notebook

echo "🌐 Configurando NAT Bridge no Linux"
echo "===================================="

# Detecta interface WiFi
WIFI_IF=$(ip -o link show | grep -oP 'wl[^:]+' | head -1)
if [ -z "$WIFI_IF" ]; then
    echo "❌ Interface WiFi não encontrada"
    exit 1
fi

echo "✓ Interface WiFi: $WIFI_IF"

# Detecta IP do ESP32 (deve estar conectado via WiFi)
ESP32_NET="192.168.4.0/24"

echo ""
echo "Habilitando IP forwarding..."
sudo sysctl -w net.ipv4.ip_forward=1

echo "Configurando iptables NAT..."
sudo iptables -t nat -A POSTROUTING -s $ESP32_NET -o $WIFI_IF -j MASQUERADE
sudo iptables -A FORWARD -i $WIFI_IF -o $WIFI_IF -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i $WIFI_IF -o $WIFI_IF -s $ESP32_NET -j ACCEPT

echo ""
echo "✅ NAT Bridge configurado!"
echo ""
echo "📱 COMO TESTAR:"
echo "1. Conecte o NOTEBOOK no WiFi: IHM_NEOCOUDE"
echo "2. Conecte o TABLET no WiFi: IHM_NEOCOUDE"
echo "3. No tablet, teste: https://google.com"
echo ""
echo "⚠️ IMPORTANTE:"
echo "   - Notebook precisa estar conectado em NET_2G5F245C via cabo Ethernet"
echo "   - Ou conectado em outra rede WiFi secundária"
echo ""
echo "Para DESFAZER:"
echo "   sudo iptables -t nat -F"
echo "   sudo iptables -F FORWARD"
echo "   sudo sysctl -w net.ipv4.ip_forward=0"
