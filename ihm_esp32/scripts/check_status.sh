#!/bin/bash
###############################################################################
# Script de Diagnóstico - IHM Web Raspberry Pi
###############################################################################

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}\n"
}

print_check() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

print_header "DIAGNÓSTICO IHM WEB - RASPBERRY PI 3B+"

# 1. Sistema operacional
echo -e "${YELLOW}▶ Sistema Operacional${NC}"
cat /etc/os-release | grep PRETTY_NAME
uname -a
echo ""

# 2. Temperatura
echo -e "${YELLOW}▶ Temperatura CPU${NC}"
TEMP=$(vcgencmd measure_temp | cut -d'=' -f2)
echo "Temperatura: $TEMP"
if [[ "${TEMP%\'*}" > "70" ]]; then
    echo -e "${RED}⚠️  ALTA! Considere adicionar dissipador/cooler${NC}"
fi
echo ""

# 3. Memória
echo -e "${YELLOW}▶ Uso de Memória${NC}"
free -h
echo ""

# 4. Disco
echo -e "${YELLOW}▶ Uso de Disco${NC}"
df -h | grep -E "Filesystem|/dev/root"
echo ""

# 5. Serviços systemd
echo -e "${YELLOW}▶ Status dos Serviços${NC}"

systemctl is-active ihm.service > /dev/null 2>&1
print_check $? "Servidor IHM (ihm.service)"

systemctl is-active hostapd.service > /dev/null 2>&1
print_check $? "WiFi Access Point (hostapd)"

systemctl is-active dnsmasq.service > /dev/null 2>&1
print_check $? "Servidor DHCP (dnsmasq)"

echo ""

# 6. Interface WiFi
echo -e "${YELLOW}▶ Interface wlan0${NC}"
ip addr show wlan0 | grep -E "inet |UP"

if ip addr show wlan0 | grep -q "192.168.50.1"; then
    echo -e "${GREEN}✓ IP estático configurado corretamente${NC}"
else
    echo -e "${RED}✗ IP 192.168.50.1 não encontrado!${NC}"
fi
echo ""

# 7. Clientes WiFi conectados
echo -e "${YELLOW}▶ Clientes WiFi Conectados${NC}"
CLIENTS=$(iw dev wlan0 station dump | grep Station | wc -l)
echo "Total de clientes: $CLIENTS"

if [ $CLIENTS -gt 0 ]; then
    iw dev wlan0 station dump | grep -E "Station|signal"
fi
echo ""

# 8. Porta USB-RS485
echo -e "${YELLOW}▶ Porta USB-RS485${NC}"
if ls /dev/ttyUSB* > /dev/null 2>&1; then
    USB_PORT=$(ls /dev/ttyUSB* | head -1)
    echo -e "${GREEN}✓ Porta detectada: $USB_PORT${NC}"
    ls -l /dev/ttyUSB*
    
    # Verificar permissões
    if groups pi | grep -q dialout; then
        echo -e "${GREEN}✓ Usuário 'pi' tem permissão (grupo dialout)${NC}"
    else
        echo -e "${RED}✗ Usuário 'pi' não está no grupo dialout!${NC}"
        echo "Execute: sudo usermod -a -G dialout pi"
    fi
else
    echo -e "${RED}✗ Porta USB não detectada${NC}"
    echo "Conecte o conversor USB-RS485 e execute novamente"
fi
echo ""

# 9. Processos Python
echo -e "${YELLOW}▶ Processos Python (IHM)${NC}"
PYTHON_PROCS=$(ps aux | grep main_server.py | grep -v grep | wc -l)

if [ $PYTHON_PROCS -gt 0 ]; then
    echo -e "${GREEN}✓ Servidor rodando ($PYTHON_PROCS processo)${NC}"
    ps aux | grep main_server.py | grep -v grep
else
    echo -e "${RED}✗ Servidor não está rodando${NC}"
    echo "Execute: sudo systemctl start ihm"
fi
echo ""

# 10. Portas de rede
echo -e "${YELLOW}▶ Portas de Rede (WebSocket/HTTP)${NC}"

if netstat -tlnp 2>/dev/null | grep -q ":8765"; then
    echo -e "${GREEN}✓ WebSocket escutando na porta 8765${NC}"
else
    echo -e "${RED}✗ WebSocket não está escutando (porta 8765)${NC}"
fi

if netstat -tlnp 2>/dev/null | grep -q ":8080"; then
    echo -e "${GREEN}✓ HTTP escutando na porta 8080${NC}"
else
    echo -e "${RED}✗ HTTP não está escutando (porta 8080)${NC}"
fi
echo ""

# 11. Últimas linhas de log
echo -e "${YELLOW}▶ Últimas 10 linhas de log (servidor IHM)${NC}"
journalctl -u ihm.service -n 10 --no-pager
echo ""

# 12. Resumo final
print_header "RESUMO"

ALL_OK=0

systemctl is-active ihm.service > /dev/null 2>&1 || ALL_OK=1
systemctl is-active hostapd.service > /dev/null 2>&1 || ALL_OK=1
systemctl is-active dnsmasq.service > /dev/null 2>&1 || ALL_OK=1
ip addr show wlan0 | grep -q "192.168.50.1" || ALL_OK=1

if [ $ALL_OK -eq 0 ]; then
    echo -e "${GREEN}✓ SISTEMA FUNCIONANDO NORMALMENTE${NC}"
    echo ""
    echo "Conecte-se ao WiFi:"
    echo "  SSID: IHM_NEOCOUDE"
    echo "  Senha: dobradeira123"
    echo "  URL: http://192.168.50.1"
else
    echo -e "${RED}✗ SISTEMA COM PROBLEMAS${NC}"
    echo "Verifique os itens marcados com ✗ acima"
    echo ""
    echo "Comandos úteis:"
    echo "  sudo systemctl restart ihm"
    echo "  sudo systemctl restart hostapd"
    echo "  sudo journalctl -u ihm -f"
fi

echo ""
