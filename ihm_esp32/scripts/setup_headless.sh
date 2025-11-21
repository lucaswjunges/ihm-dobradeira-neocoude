#!/bin/bash
# setup_headless.sh - Configura RPi3B+ como headless (CLI only)
# ================================================================
# Autor: Lucas William Junges
# Data: 21/Nov/2025
# Descrição: Remove interface gráfica e otimiza para servidor IHM

set -e

echo "═══════════════════════════════════════════════════════════"
echo "CONFIGURANDO RASPBERRY PI 3B+ COMO HEADLESS (CLI ONLY)"
echo "═══════════════════════════════════════════════════════════"
echo

# 1. Desabilitar boot gráfico
echo "1️⃣  Desabilitando boot gráfico..."
sudo systemctl set-default multi-user.target

# 2. Remover pacotes gráficos (OPCIONAL - libera ~1GB no SD)
read -p "   Remover pacotes desktop? (libera ~1GB) [s/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "   Removendo pacotes desktop (pode demorar)..."
    sudo apt-get remove -y --purge \
        xserver-xorg \
        lightdm \
        raspberrypi-ui-mods \
        lxde-* \
        desktop-* \
        gnome-* \
        x11-* \
        gtk-* \
        2>/dev/null || true

    sudo apt-get autoremove -y
    sudo apt-get clean
    echo "   ✅ Pacotes removidos!"
else
    echo "   ⏭️  Pacotes mantidos (pode remover depois)"
fi

# 3. Desabilitar serviços gráficos desnecessários
echo
echo "2️⃣  Desabilitando serviços gráficos..."
sudo systemctl disable lightdm 2>/dev/null || true
sudo systemctl disable bluetooth 2>/dev/null || true
sudo systemctl disable avahi-daemon 2>/dev/null || true
sudo systemctl disable triggerhappy 2>/dev/null || true

# 4. Otimizar GPU memory (mínimo)
echo
echo "3️⃣  Otimizando memória GPU..."
if ! grep -q "gpu_mem=" /boot/firmware/config.txt 2>/dev/null; then
    echo "gpu_mem=16" | sudo tee -a /boot/firmware/config.txt
else
    sudo sed -i 's/gpu_mem=.*/gpu_mem=16/' /boot/firmware/config.txt
fi
echo "   ✅ GPU memory reduzida para 16MB (deixa mais RAM para Python)"

# 5. Configurar console autologin (opcional)
echo
read -p "4️⃣  Habilitar autologin no console? [s/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    sudo systemctl enable getty@tty1.service
    sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
    cat <<EOF | sudo tee /etc/systemd/system/getty@tty1.service.d/autologin.conf
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin pi --noclear %I \$TERM
EOF
    echo "   ✅ Autologin configurado (boot direto como usuário 'pi')"
fi

# 6. Resumo
echo
echo "═══════════════════════════════════════════════════════════"
echo "✅ CONFIGURAÇÃO HEADLESS CONCLUÍDA"
echo "═══════════════════════════════════════════════════════════"
echo
echo "📊 Resumo das alterações:"
echo "  • Boot padrão: multi-user.target (CLI only)"
echo "  • GPU memory: 16MB (mais RAM disponível)"
echo "  • Serviços desabilitados: lightdm, bluetooth, avahi"
echo
echo "🔄 PRÓXIMO PASSO: Reiniciar o sistema"
echo "   sudo reboot"
echo
echo "⚠️  IMPORTANTE: Após reiniciar, acesse APENAS via SSH!"
echo "   ssh pi@<IP_DO_RPI>"
echo
