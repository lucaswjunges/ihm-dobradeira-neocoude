#!/bin/bash
# setup_production_lock.sh - Bloqueia sistema para produção
# ================================================================
# Autor: Lucas William Junges
# Data: 21/Nov/2025
# Descrição: Trava sistema em versão estável (ZERO atualizações)
#
# ATENÇÃO: Este script CONGELA o sistema operacional!
#  ✅ PRÓ: Máxima estabilidade, nunca quebra por atualização
#  ❌ CONTRA: Sem patches de segurança (OK para rede isolada)

set -e

echo "═══════════════════════════════════════════════════════════"
echo "CONFIGURANDO RASPBERRY PI PARA PRODUÇÃO (LOCK MODE)"
echo "═══════════════════════════════════════════════════════════"
echo
echo "⚠️  ESTE SCRIPT VAI:"
echo "  • Desabilitar TODAS as atualizações automáticas"
echo "  • Bloquear pacotes críticos (kernel, Python, systemd)"
echo "  • Configurar filesystem read-only (opcional)"
echo "  • Ativar watchdog hardware (auto-reset se travar)"
echo
read -p "Continuar? [s/N]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Cancelado pelo usuário"
    exit 1
fi

# 1. Desabilitar atualizações automáticas
echo
echo "1️⃣  Desabilitando atualizações automáticas..."
sudo systemctl disable apt-daily.timer 2>/dev/null || true
sudo systemctl disable apt-daily-upgrade.timer 2>/dev/null || true
sudo systemctl stop apt-daily.timer 2>/dev/null || true
sudo systemctl stop apt-daily-upgrade.timer 2>/dev/null || true

# Desabilita unattended-upgrades (se existir)
if [ -f /etc/apt/apt.conf.d/50unattended-upgrades ]; then
    sudo systemctl disable unattended-upgrades 2>/dev/null || true
    sudo systemctl stop unattended-upgrades 2>/dev/null || true
fi

echo "   ✅ Atualizações automáticas desabilitadas"

# 2. Bloquear pacotes críticos (hold)
echo
echo "2️⃣  Bloqueando pacotes críticos contra upgrade acidental..."

# Lista de pacotes que NÃO devem NUNCA atualizar
HOLD_PACKAGES=(
    "raspberrypi-kernel"
    "raspberrypi-bootloader"
    "python3"
    "python3-pip"
    "systemd"
    "dbus"
    "udev"
    "libc6"
    "gcc"
)

for pkg in "${HOLD_PACKAGES[@]}"; do
    if dpkg -l | grep -q "^ii.*$pkg"; then
        echo "$pkg hold" | sudo dpkg --set-selections
        echo "   🔒 $pkg → BLOQUEADO"
    fi
done

# Mostrar pacotes bloqueados
echo
echo "   Pacotes bloqueados:"
dpkg --get-selections | grep hold

# 3. Configurar watchdog hardware (auto-reset se travar)
echo
echo "3️⃣  Configurando watchdog hardware..."
sudo apt-get install -y watchdog

# Configurar watchdog
sudo tee /etc/watchdog.conf > /dev/null <<'EOF'
# Watchdog Hardware - Auto-reset se sistema travar
watchdog-device = /dev/watchdog
watchdog-timeout = 15

# Condições de reset
max-load-1 = 24
min-memory = 1

# Testa se processo crítico (ihm.service) está rodando
pidfile = /run/ihm.pid

# Testa se interface de rede está ativa
interface = wlan0

# Testa se consegue escrever em disco
file = /tmp/watchdog-test
change = 300
EOF

# Criar PID file para ihm.service
sudo sed -i '/^\[Service\]/a PIDFile=/run/ihm.pid' /etc/systemd/system/ihm.service 2>/dev/null || true

# Ativar watchdog
sudo systemctl enable watchdog
sudo systemctl start watchdog

echo "   ✅ Watchdog configurado (reset automático se travar > 15s)"

# 4. Configurar filesystem read-only (OPCIONAL - máxima proteção)
echo
read -p "4️⃣  Configurar filesystem READ-ONLY? (proteção máxima) [s/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "   ⚠️  ATENÇÃO: Após isso, sistema NÃO conseguirá gravar logs!"
    echo "   (Use apenas se precisa de confiabilidade 100%)"
    echo
    read -p "   Confirma READ-ONLY filesystem? [s/N]: " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Ss]$ ]]; then
        # Instalar overlayfs
        sudo raspi-config nonint enable_overlayfs
        echo "   ✅ Filesystem READ-ONLY ativado (requer reboot)"
        NEED_REBOOT=true
    fi
fi

# 5. Criar snapshot do sistema atual
echo
echo "5️⃣  Criando snapshot do sistema (backup completo)..."
BACKUP_FILE="/home/pi/ihm_production_snapshot_$(date +%Y%m%d).tar.gz"

sudo tar -czf "$BACKUP_FILE" \
    /home/pi/ihm_neocoude \
    /etc/systemd/system/ihm.service \
    /etc/hostapd \
    /etc/dnsmasq.conf \
    /etc/network \
    /etc/wpa_supplicant \
    /boot/firmware/config.txt \
    2>/dev/null || true

echo "   ✅ Snapshot salvo em: $BACKUP_FILE"
echo "   (Copie para pendrive AGORA com scp)"

# 6. Configurar limites de logs (evitar encher SD)
echo
echo "6️⃣  Configurando rotação de logs..."
sudo tee /etc/logrotate.d/ihm > /dev/null <<'EOF'
/var/log/ihm/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    maxsize 10M
}
EOF

# Limitar tamanho do journald
sudo mkdir -p /etc/systemd/journald.conf.d
sudo tee /etc/systemd/journald.conf.d/size-limit.conf > /dev/null <<'EOF'
[Journal]
SystemMaxUse=100M
RuntimeMaxUse=50M
EOF

sudo systemctl restart systemd-journald

echo "   ✅ Logs limitados a 100MB total"

# 7. Resumo final
echo
echo "═══════════════════════════════════════════════════════════"
echo "✅ SISTEMA BLOQUEADO PARA PRODUÇÃO"
echo "═══════════════════════════════════════════════════════════"
echo
echo "📋 CONFIGURAÇÕES APLICADAS:"
echo "  ✅ Atualizações automáticas: DESABILITADAS"
echo "  ✅ Pacotes críticos: BLOQUEADOS (hold)"
echo "  ✅ Watchdog hardware: ATIVO (reset se travar)"
echo "  ✅ Logs: ROTAÇÃO AUTOMÁTICA (max 100MB)"
echo "  ✅ Snapshot: $BACKUP_FILE"

if [ "$NEED_REBOOT" = true ]; then
    echo "  ⚠️  Filesystem READ-ONLY: REQUER REBOOT"
fi

echo
echo "🔧 MANUTENÇÃO FUTURA:"
echo "  • Para atualizar manualmente (EMERGÊNCIA):"
echo "    sudo apt-mark unhold <pacote>"
echo "    sudo apt update && sudo apt upgrade"
echo "    sudo apt-mark hold <pacote>"
echo
echo "  • Para desbloquear todos pacotes:"
echo "    sudo apt-mark unhold python3 raspberrypi-kernel systemd"
echo
echo "  • Para restaurar snapshot:"
echo "    sudo tar -xzf $BACKUP_FILE -C /"
echo

if [ "$NEED_REBOOT" = true ]; then
    echo "🔄 REBOOT NECESSÁRIO!"
    read -p "Reiniciar agora? [s/N]: " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        sudo reboot
    fi
fi
