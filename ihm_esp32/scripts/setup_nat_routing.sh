#!/bin/bash
# Script para configurar NAT e roteamento para compartilhamento de internet
# Interface STA (WiFi dongle): wlan1
# Interface AP (WiFi interno): wlan0
# Rede AP: 192.168.50.0/24

set -e

echo "[$(date)] Configurando NAT e roteamento para IHM_NEOCOUDE..."

# 1. Habilitar IP forwarding (se ainda não estiver)
echo 1 > /proc/sys/net/ipv4/ip_forward
echo "[OK] IP forwarding habilitado"

# 2. Configurar policy routing para rede AP
# Criar tabela de roteamento 100 se não existir
if ! ip route show table 100 | grep -q "default"; then
    ip route add default via 192.168.0.1 dev wlan1 table 100
    echo "[OK] Rota padrão adicionada na tabela 100"
fi

if ! ip route show table 100 | grep -q "192.168.50.0"; then
    ip route add 192.168.50.0/24 dev wlan0 scope link table 100
    echo "[OK] Rota local adicionada na tabela 100"
fi

# 3. Criar regra de policy routing se não existir
if ! ip rule list | grep -q "from 192.168.50.0/24"; then
    ip rule add from 192.168.50.0/24 table 100 priority 100
    echo "[OK] Regra de policy routing criada"
fi

# 4. Configurar iptables/nftables para FORWARD
# Aceitar tráfego entre wlan0 (AP) e wlan1 (STA)
iptables -C FORWARD -i wlan0 -o wlan1 -j ACCEPT 2>/dev/null || \
    iptables -I FORWARD 1 -i wlan0 -o wlan1 -j ACCEPT
echo "[OK] Regra FORWARD wlan0→wlan1 configurada"

iptables -C FORWARD -i wlan1 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT 2>/dev/null || \
    iptables -I FORWARD 2 -i wlan1 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
echo "[OK] Regra FORWARD wlan1→wlan0 configurada"

# 5. Configurar NAT/MASQUERADE
iptables -t nat -C POSTROUTING -o wlan1 -j MASQUERADE 2>/dev/null || \
    iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE
echo "[OK] NAT/MASQUERADE configurado"

# 6. Aceitar tráfego de entrada/saída em wlan0
iptables -C INPUT -i wlan0 -j ACCEPT 2>/dev/null || \
    iptables -I INPUT -i wlan0 -j ACCEPT
echo "[OK] INPUT wlan0 configurado"

iptables -C OUTPUT -o wlan0 -j ACCEPT 2>/dev/null || \
    iptables -I OUTPUT -o wlan0 -j ACCEPT
echo "[OK] OUTPUT wlan0 configurado"

echo "[$(date)] Configuração concluída com sucesso!"
echo ""
echo "=== Estatísticas ==="
echo "Regras FORWARD:"
iptables -L FORWARD -v -n --line-numbers | head -8
echo ""
echo "Regras NAT:"
iptables -t nat -L POSTROUTING -v -n
echo ""
echo "Policy Routing:"
ip rule list | grep "192.168.50"
ip route show table 100
