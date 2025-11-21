#!/bin/bash
# setup_tailscale.sh - Configura VPN Tailscale para acesso remoto
# ================================================================
# Autor: Lucas William Junges
# Data: 21/Nov/2025
# Descrição: Acesso seguro ao RPi de qualquer lugar (100% gratuito)
#
# Vantagens:
#  ✅ Gratuito para uso pessoal
#  ✅ Sem necessidade de abrir portas no roteador
#  ✅ Funciona atrás de CGNAT
#  ✅ Criptografia end-to-end automática
#  ✅ IP fixo virtual (ex: 100.64.0.5)
#  ✅ Suporte a múltiplos dispositivos (PC casa, celular, etc.)

set -e

echo "═══════════════════════════════════════════════════════════"
echo "INSTALANDO TAILSCALE VPN - ACESSO REMOTO SEGURO"
echo "═══════════════════════════════════════════════════════════"
echo

# 1. Instalar Tailscale
echo "1️⃣  Instalando Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh

# 2. Iniciar Tailscale
echo
echo "2️⃣  Iniciando Tailscale..."
sudo tailscale up

echo
echo "═══════════════════════════════════════════════════════════"
echo "✅ TAILSCALE INSTALADO COM SUCESSO"
echo "═══════════════════════════════════════════════════════════"
echo
echo "📋 PRÓXIMOS PASSOS:"
echo
echo "1. No SEU PC/CELULAR (casa):"
echo "   • Baixe Tailscale: https://tailscale.com/download"
echo "   • Faça login com a MESMA conta Google/Microsoft"
echo
echo "2. Para ver o IP do Raspberry Pi:"
echo "   tailscale ip -4"
echo
echo "3. Para acessar remotamente:"
echo "   ssh pi@<IP_TAILSCALE>"
echo "   Exemplo: ssh pi@100.64.0.5"
echo
echo "4. Para acessar a IHM Web remotamente:"
echo "   http://<IP_TAILSCALE>:8080"
echo "   Exemplo: http://100.64.0.5:8080"
echo
echo "🔒 SEGURANÇA:"
echo "  • Todo tráfego é criptografado (WireGuard)"
echo "  • Sem necessidade de senha (usa chave pública)"
echo "  • Nenhuma porta aberta no roteador da fábrica"
echo
