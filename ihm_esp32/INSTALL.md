# 📦 Guia de Instalação - IHM Web Raspberry Pi 3B+

Guia completo para instalação da IHM Web no Raspberry Pi 3B+ para a dobradeira NEOCOUDE-HD-15.

---

## 📋 Pré-requisitos

### Hardware Necessário

1. **Raspberry Pi 3B+** (R$ 350-450)
   - CPU: Quad-core 1.4GHz ARM Cortex-A53
   - RAM: 1GB LPDDR2
   - WiFi: 2.4GHz + 5GHz dual-band
   - 4x USB 2.0
   
2. **Cartão microSD 16GB+** (R$ 30-50)
   - Classe 10 ou superior (recomendado: UHS-I U3)
   
3. **Fonte 5V 3A** (R$ 40-60)
   - USB-C (oficial recomendada)
   - Consumo típico: 4W (~800mA), pico: 6W (~1200mA)
   
4. **Conversor USB-RS485** (R$ 25-40)
   - FTDI ou CH340
   - Para comunicação com CLP Atos MPC4004
   
5. **Cabo USB** (R$ 10)
   - USB-A para mini/micro USB (conforme conversor)

### Software Necessário

- **Raspberry Pi OS Lite** (64-bit) - versão Bookworm ou superior
- Acesso à internet para instalação de pacotes

---

## 🚀 Instalação Rápida (Recomendado)

### Passo 1: Preparar microSD

**Opção A: Raspberry Pi Imager (mais fácil)**

```bash
# No seu PC/notebook, baixe:
# https://www.raspberrypi.com/software/

# No Imager:
1. Escolher OS: Raspberry Pi OS Lite (64-bit)
2. Escolher Storage: Seu cartão microSD
3. Configurações avançadas (ícone engrenagem):
   - Hostname: ihm-neocoude
   - Habilitar SSH: ✓
   - Usuário: pi / Senha: (sua senha)
   - WiFi (opcional): Conectar em rede temporária
4. Gravar
```

**Opção B: Download manual + dd**

```bash
# Baixar imagem
wget https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2024-03-15/2024-03-15-raspios-bookworm-arm64-lite.img.xz

# Gravar no microSD (substitua /dev/sdX pelo device correto!)
# CUIDADO: Comando destrutivo!
xzcat 2024-03-15-raspios-bookworm-arm64-lite.img.xz | sudo dd of=/dev/sdX bs=4M status=progress && sync
```

### Passo 2: Primeira Conexão SSH

```bash
# Inserir microSD no Raspberry Pi e ligar

# Aguardar 1-2 minutos para boot

# Descobrir IP (método 1 - mDNS)
ping raspberrypi.local

# Ou descobrir IP (método 2 - router/nmap)
nmap -sn 192.168.0.0/24

# Conectar via SSH
ssh pi@192.168.0.XXX
# Senha: a que você configurou no Imager
```

### Passo 3: Clonar Repositório

```bash
# No Raspberry Pi via SSH:
cd /home/pi

# Clonar repositório
git clone https://github.com/seu-usuario/ihm_neocoude.git

# Entrar no diretório
cd ihm_neocoude/ihm_esp32
```

### Passo 4: Executar Instalação Automática

```bash
# Executar script de instalação (requer sudo)
sudo bash scripts/install.sh
```

O script fará automaticamente:
- ✅ Atualizar sistema operacional
- ✅ Instalar Python 3 + dependências (pymodbus, aiohttp, websockets)
- ✅ Configurar WiFi Access Point (hostapd)
- ✅ Configurar servidor DHCP (dnsmasq)
- ✅ Configurar interface wlan0 (IP estático 192.168.50.1)
- ✅ Instalar serviço systemd (auto-start)
- ✅ Configurar permissões USB (grupo dialout)

**Tempo estimado: 5-10 minutos** (dependendo da velocidade da internet)

### Passo 5: Reiniciar

```bash
sudo reboot
```

Após ~40 segundos, o sistema estará pronto!

---

## 📱 Conectar Tablet

### 1. Procurar WiFi

No tablet, procurar rede WiFi:

```
SSID: IHM_NEOCOUDE
Senha: dobradeira123
```

### 2. Acessar Interface Web

Abrir navegador (Chrome/Firefox/Safari):

```
http://192.168.50.1
```

ou

```
http://ihm.local
```

✅ **Pronto!** A interface web deve aparecer.

---

## 🔧 Instalação Manual (Detalhada)

<details>
<summary>Clique aqui para expandir</summary>

### 1. Atualizar Sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Instalar Pacotes do Sistema

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    hostapd \
    dnsmasq \
    net-tools \
    wireless-tools \
    rfkill
```

### 3. Desbloquear WiFi

```bash
sudo rfkill unblock wlan
```

### 4. Criar Virtual Environment

```bash
cd /home/pi/ihm_neocoude/ihm_esp32

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install pymodbus aiohttp aiohttp-cors websockets gpiozero
```

### 5. Configurar hostapd

```bash
# Copiar configuração
sudo cp config/hostapd.conf /etc/hostapd/hostapd.conf

# Configurar daemon
sudo tee /etc/default/hostapd > /dev/null << 'HOSTAPD_EOF'
DAEMON_CONF="/etc/hostapd/hostapd.conf"
HOSTAPD_EOF

# Habilitar serviço
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
```

### 6. Configurar dnsmasq

```bash
# Backup configuração original
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig

# Copiar nova configuração
sudo cp config/dnsmasq.conf /etc/dnsmasq.conf

# Habilitar serviço
sudo systemctl enable dnsmasq
```

### 7. Configurar Interface wlan0

```bash
# Editar dhcpcd.conf
sudo nano /etc/dhcpcd.conf

# Adicionar no final:
interface wlan0
    static ip_address=192.168.50.1/24
    nohook wpa_supplicant
```

### 8. Instalar Serviço systemd

```bash
# Copiar service file
sudo cp config/ihm.service /etc/systemd/system/ihm.service

# Reload daemon
sudo systemctl daemon-reload

# Habilitar auto-start
sudo systemctl enable ihm.service
```

### 9. Configurar Permissões USB

```bash
sudo usermod -a -G dialout pi

# Logout e login novamente para aplicar
```

### 10. Reiniciar Serviços

```bash
sudo systemctl restart dhcpcd
sudo systemctl start hostapd
sudo systemctl start dnsmasq
sudo systemctl start ihm
```

### 11. Verificar Status

```bash
# Status do servidor IHM
sudo systemctl status ihm

# Status do WiFi AP
sudo systemctl status hostapd

# Status do DHCP
sudo systemctl status dnsmasq

# Clientes conectados no WiFi
iw dev wlan0 station dump
```

</details>

---

## 🐛 Troubleshooting

### WiFi "IHM_NEOCOUDE" não aparece

```bash
# Verificar status hostapd
sudo systemctl status hostapd

# Ver erros detalhados
sudo journalctl -u hostapd -n 50

# Testar configuração manualmente
sudo hostapd -d /etc/hostapd/hostapd.conf

# Reiniciar serviço
sudo systemctl restart hostapd
```

### Servidor não inicia

```bash
# Ver logs do servidor
sudo journalctl -u ihm -f

# Verificar se porta USB existe
ls -l /dev/ttyUSB*

# Testar servidor manualmente (modo STUB)
cd /home/pi/ihm_esp32
source venv/bin/activate
python3 main_server.py --stub
```

### USB-RS485 não detectado

```bash
# Listar dispositivos USB
lsusb

# Ver logs do kernel
dmesg | grep -i ftdi
dmesg | grep -i ch340

# Verificar permissões
groups pi  # Deve conter "dialout"

# Se não tiver, adicionar:
sudo usermod -a -G dialout pi
# Logout e login novamente
```

### Tablet conecta mas não acessa http://192.168.50.1

```bash
# Verificar se interface wlan0 está UP
ip addr show wlan0

# Verificar DHCP
sudo systemctl status dnsmasq

# Verificar firewall
sudo iptables -L

# Verificar se servidor está escutando
sudo netstat -tlnp | grep 8080
```

### Modbus timeout

```bash
# Instalar mbpoll para teste
sudo apt install -y mbpoll

# Testar comunicação (exemplo: ler encoder)
mbpoll -a 1 -b 57600 -P none -t 3 -r 1238 -c 2 /dev/ttyUSB0

# Se funcionar: problema é no código Python
# Se não funcionar: problema é no hardware/CLP
```

---

## ⚙️ Configurações Avançadas

### Trocar Senha do WiFi

```bash
# Editar configuração
sudo nano /etc/hostapd/hostapd.conf

# Alterar linha:
wpa_passphrase=SUA_NOVA_SENHA_FORTE

# Salvar (Ctrl+O, Enter, Ctrl+X)

# Reiniciar serviço
sudo systemctl restart hostapd
```

### Trocar SSID (Nome do WiFi)

```bash
# Editar configuração
sudo nano /etc/hostapd/hostapd.conf

# Alterar linha:
ssid=NOME_DA_SUA_REDE

# Reiniciar serviço
sudo systemctl restart hostapd
```

### Modo STUB (Simulação sem CLP)

```bash
# Editar service
sudo nano /etc/systemd/system/ihm.service

# Alterar linha ExecStart para:
ExecStart=/home/pi/ihm_esp32/venv/bin/python3 /home/pi/ihm_esp32/main_server.py --stub

# Reload e reiniciar
sudo systemctl daemon-reload
sudo systemctl restart ihm
```

### Logs em Tempo Real

```bash
# Servidor IHM
sudo journalctl -u ihm -f

# WiFi AP
sudo journalctl -u hostapd -f

# DHCP
sudo journalctl -u dnsmasq -f

# Kernel (USB)
dmesg -w
```

### Backup do Sistema

```bash
# Criar diretório de backups
mkdir -p /home/pi/backups

# Backup completo (executar manualmente)
tar -czf /home/pi/backups/ihm_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    /home/pi/ihm_esp32 \
    /etc/hostapd \
    /etc/dnsmasq.conf \
    /etc/dhcpcd.conf \
    /etc/systemd/system/ihm.service

# Listar backups
ls -lh /home/pi/backups/
```

### Atualização do Sistema

```bash
# Atualizar repositório Git
cd /home/pi/ihm_esp32
git pull

# Reinstalar dependências Python (se houver mudanças)
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar servidor
sudo systemctl restart ihm
```

---

## 📊 Monitoramento

### Temperatura

```bash
# Ver temperatura da CPU
vcgencmd measure_temp

# Se > 70°C:
# - Instalar dissipador de calor
# - Adicionar ventilador (5V GPIO)
# - Melhorar ventilação da caixa
```

### Uso de Recursos

```bash
# CPU e RAM
htop

# Memória
free -h

# Disco
df -h

# Processos Python
ps aux | grep python3
```

### Clientes Conectados WiFi

```bash
# Ver clientes ativos
iw dev wlan0 station dump

# Ou com endereço MAC:
cat /var/lib/misc/dnsmasq.leases
```

---

## 🔒 Segurança (Produção)

### 1. Trocar Senha do Usuário pi

```bash
passwd
# Digite nova senha forte
```

### 2. Configurar Firewall

```bash
sudo apt install -y ufw

# Permitir apenas portas necessárias
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (futuro)
sudo ufw allow 8080/tcp # WebSocket

# Ativar
sudo ufw enable
```

### 3. Desabilitar Serviços Desnecessários

```bash
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

### 4. Atualizar Regularmente

```bash
# Executar mensalmente
sudo apt update && sudo apt upgrade -y
sudo reboot
```

---

## 📚 Próximos Passos

Após instalação bem-sucedida:

1. ✅ **Testar conectividade WiFi** (tablet conecta?)
2. ✅ **Testar interface web** (http://192.168.50.1 abre?)
3. ✅ **Conectar USB-RS485** (CLP Atos)
4. ✅ **Testar comunicação Modbus** (leitura encoder funciona?)
5. ✅ **Testar botões virtuais** (K1-K9, S1-S2)
6. ✅ **Validar em produção** (teste 24h)

---

## 🆘 Suporte

- **GitHub Issues:** https://github.com/seu-usuario/ihm_neocoude/issues
- **Documentação:** `CLAUDE.md`, `README.md`
- **Email:** lucas@exemplo.com

---

**Desenvolvido por:** Eng. Lucas William Junges  
**Data:** Novembro 2025  
**Versão:** 2.0-RPI3B+  
**Dispositivo:** Raspberry Pi 3B+ (Quad-core 1.4GHz, 1GB RAM, WiFi dual-band)
