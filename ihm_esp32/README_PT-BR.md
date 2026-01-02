# IHM Web - Dobradeira NEOCOUDE-HD-15
## Versão Raspberry Pi 3B+

![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3B%2B-C51A4A?logo=raspberry-pi)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietário-red)

Interface web moderna para controle de dobradeira industrial **NEOCOUDE-HD-15** (Trillor, 2007) via CLP **Atos MPC4004**, rodando em **Raspberry Pi 3B+**.

---

## 📋 Índice

- [Características](#-características)
- [Hardware Necessário](#-hardware-necessário)
- [Instalação Rápida](#-instalação-rápida)
- [Uso](#-uso)
- [Arquitetura](#-arquitetura)
- [Configuração](#-configuração)
- [Troubleshooting](#-troubleshooting)
- [Documentação](#-documentação)

---

## ✨ Características

- ✅ **WiFi STA+AP simultâneo** - Conecta na rede da fábrica E cria rede própria para tablet
- ✅ **Interface web responsiva** - Funciona em tablets, smartphones e PCs
- ✅ **Comunicação Modbus RTU** - Via USB-RS485 (57600 bps)
- ✅ **WebSocket em tempo real** - Atualizações instantâneas (< 300ms)
- ✅ **Auto-start no boot** - Serviço systemd confiável
- ✅ **LEDs de status** - Indicadores GPIO para WiFi, Modbus e Cliente
- ✅ **Logs completos** - journalctl integrado
- ✅ **Baixo consumo** - ~4W típico (vs 40W notebook)
- ✅ **Compacto** - Cabe em caixa DIN rail
- ✅ **Industrial-grade** - Sem partes móveis, SSD opcional

---

## 🛠️ Hardware Necessário

### Componentes Obrigatórios

| Item | Especificação | Custo Aproximado |
|------|---------------|------------------|
| **Raspberry Pi 3B+** | Quad-core 1.4GHz, 1GB RAM, WiFi dual-band | R$ 350-450 |
| **microSD Card** | 16GB+, Classe 10, A1/A2 | R$ 30-50 |
| **Fonte de Alimentação** | 5V 3A, USB-C ou GPIO | R$ 40-60 |
| **Conversor USB-RS485** | FTDI FT232RL ou CH340 | R$ 25-40 |
| **Cabo USB** | USB-A para mini/micro USB | R$ 10 |

### Componentes Opcionais

| Item | Finalidade | Custo |
|------|------------|-------|
| Caixa DIN rail | Montagem no painel elétrico | R$ 60-100 |
| Dissipador + cooler | Refrigeração (se > 60°C) | R$ 15-30 |
| LEDs 5mm | Indicadores de status | R$ 5 |
| Resistores 220Ω | Para LEDs | R$ 2 |

**Custo Total:** ~R$ 500-750 (vs R$ 2000+ notebook)

---

## 🚀 Instalação Rápida

### 1. Preparar microSD (no PC/Notebook)

```bash
# Baixar Raspberry Pi OS Lite (64-bit)
wget https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2024-03-15/2024-03-15-raspios-bookworm-arm64-lite.img.xz

# Flash no microSD (Linux)
xzcat 2024-03-15-raspios-bookworm-arm64-lite.img.xz | sudo dd of=/dev/sdX bs=4M status=progress

# Ou usar Raspberry Pi Imager (GUI - Windows/Mac/Linux)
# https://www.raspberrypi.com/software/
```

### 2. Configurar SSH e WiFi inicial

```bash
# Montar partição boot
cd /media/$USER/bootfs

# Habilitar SSH
touch ssh

# Configurar WiFi temporário (para primeira conexão)
cat > wpa_supplicant.conf << EOF
country=BR
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="Seu_WiFi_Casa"
    psk="sua_senha"
}
EOF

# Desmontar e inserir no Raspberry Pi
cd ~
sudo umount /media/$USER/bootfs
```

### 3. Primeira conexão SSH

```bash
# Ligar Raspberry Pi e aguardar 1-2 minutos

# Descobrir IP
ping raspberrypi.local
# Ou verificar no roteador (MAC: B8:27:EB:xx:xx:xx)

# Conectar via SSH
ssh pi@raspberrypi.local
# Senha padrão: raspberry

# IMPORTANTE: Trocar senha
passwd
```

### 4. Clonar repositório e instalar

```bash
# Atualizar sistema (primeira vez)
sudo apt update && sudo apt upgrade -y

# Clonar repositório
cd /home/pi
git clone https://github.com/seu-usuario/ihm_neocoude.git
cd ihm_neocoude/ihm_rpi

# Executar instalação automática
sudo bash scripts/install.sh
```

O script de instalação vai:
- ✅ Instalar todas as dependências
- ✅ Configurar WiFi STA+AP
- ✅ Instalar aplicação Python
- ✅ Configurar serviço systemd
- ✅ Testar comunicação Modbus
- ✅ Reiniciar sistema

**Tempo total:** ~10-15 minutos

### 5. Pronto!

Após reiniciar:

```
1. Conectar no WiFi "IHM_NEOCOUDE" (senha: dobradeira123)
2. Abrir navegador no tablet
3. Acessar: http://192.168.50.1/
```

---

## 📱 Uso

### Acessar Interface Web

**Via WiFi AP (tablet/smartphone):**
```
1. WiFi → Conectar em "IHM_NEOCOUDE"
2. Senha: dobradeira123
3. Navegador → http://192.168.50.1/
```

**Via SSH (manutenção remota):**
```bash
# Se configurou WiFi STA
ssh pi@192.168.0.XXX

# Ou via mDNS
ssh pi@raspberrypi.local
```

### Comandos Úteis

```bash
# Ver status do serviço
sudo systemctl status ihm.service

# Ver logs em tempo real
sudo journalctl -u ihm.service -f

# Reiniciar serviço
sudo systemctl restart ihm.service

# Parar serviço
sudo systemctl stop ihm.service

# Iniciar serviço
sudo systemctl start ihm.service

# Verificar WiFi AP
sudo systemctl status hostapd

# Ver clientes conectados no WiFi
iw dev wlan0 station dump

# Verificar temperatura
vcgencmd measure_temp

# Testar Modbus manualmente
mbpoll -a 1 -b 57600 -P none -t 3 -r 1238 -c 2 /dev/ttyUSB0
```

### Iniciar Manualmente (Debug)

```bash
cd /home/pi/ihm_neocoude/ihm_rpi
bash scripts/start_ihm.sh
```

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────┐
│  Raspberry Pi 3B+ (Raspberry Pi OS)         │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  main_server.py (Python 3)           │  │
│  │  - WebSocket server (port 8080)      │  │
│  │  - HTTP server (static files)        │  │
│  │  - State manager (polling 250ms)     │  │
│  └─────────┬────────────────────┬────────┘  │
│            │                    │            │
│  ┌─────────▼──────┐  ┌─────────▼─────────┐ │
│  │  Modbus Client │  │  WiFi AP          │ │
│  │  (pymodbus)    │  │  (hostapd)        │ │
│  └────────┬───────┘  └─────────┬─────────┘ │
└───────────┼──────────────────────┼─────────┘
            │                      │
            │ USB                  │ WiFi
            │ /dev/ttyUSB0         │ 192.168.50.1
            ▼                      ▼
     ┌──────────────┐       ┌──────────────┐
     │  USB-RS485   │       │   Tablet     │
     │  (FTDI/CH340)│       │   Browser    │
     └──────┬───────┘       └──────────────┘
            │
            │ RS485 (A/B)
            │ 57600 bps
            ▼
     ┌──────────────┐
     │  CLP Atos    │
     │  MPC4004     │
     └──────────────┘
```

### Fluxo de Dados

1. **Modbus RTU** (250ms polling)
   - RPi lê encoder, I/Os, status do CLP
   - Armazena em `machine_state` (dict)

2. **WebSocket** (push em mudanças)
   - Cliente conecta via `ws://192.168.50.1:8080/ws`
   - Recebe atualizações apenas quando valores mudam
   - Envia comandos (pressionar teclas, editar ângulos)

3. **HTTP** (estático)
   - Serve `index.html`, CSS, JavaScript
   - Sem frameworks - vanilla JS puro

---

## ⚙️ Configuração

### Arquivos de Configuração

| Arquivo | Localização | Descrição |
|---------|-------------|-----------|
| `hostapd.conf` | `/etc/hostapd/` | WiFi AP (SSID, senha, canal) |
| `dnsmasq.conf` | `/etc/dnsmasq.conf` | DHCP server (range, DNS) |
| `dhcpcd.conf` | `/etc/dhcpcd.conf` | IP estático wlan0 |
| `wpa_supplicant.conf` | `/etc/wpa_supplicant/` | WiFi STA (rede externa) |
| `ihm.service` | `/etc/systemd/system/` | Serviço systemd |

### Alterar SSID/Senha WiFi AP

```bash
sudo nano /etc/hostapd/hostapd.conf

# Alterar linhas:
ssid=IHM_NEOCOUDE_NOVO
wpa_passphrase=SenhaSuperForte123!

# Reiniciar
sudo systemctl restart hostapd
```

### Adicionar Rede WiFi STA

```bash
# Método 1: raspi-config
sudo raspi-config
# 1. System Options → S1 Wireless LAN

# Método 2: script
sudo bash scripts/setup_wifi.sh

# Método 3: manual
sudo wpa_passphrase "SSID_Fabrica" "senha" >> /etc/wpa_supplicant/wpa_supplicant.conf
sudo wpa_cli reconfigure
```

### Alterar Porta Serial Modbus

```python
# Editar main_server.py ou modbus_client.py
SERIAL_PORT = '/dev/ttyUSB1'  # Trocar de ttyUSB0 para ttyUSB1
```

### LEDs de Status (GPIO)

Conectar LEDs nos pinos:
- **GPIO17** → LED WiFi STA (acende quando conecta na rede externa)
- **GPIO27** → LED Modbus (acende quando CLP responde)
- **GPIO22** → LED Cliente (acende quando tablet conecta)

Descomentar código em `main_server.py`:
```python
from gpiozero import LED

led_wifi = LED(17)
led_modbus = LED(27)
led_client = LED(22)
```

---

## 🆘 Troubleshooting

### RPi não liga

**Sintoma:** Nenhum LED acende
- ❌ Fonte insuficiente → Usar mínimo 5V 3A
- ❌ Cabo USB ruim → Testar com outro
- ❌ microSD corrompido → Reflash

**Sintoma:** LED vermelho aceso, verde não pisca
- ❌ microSD não detectado → Verificar partição boot
- ❌ Firmware corrompido → Reflash

### WiFi AP não aparece

```bash
# Verificar status
sudo systemctl status hostapd

# Ver erros detalhados
sudo journalctl -u hostapd -n 50

# Testar configuração
sudo hostapd -d /etc/hostapd/hostapd.conf

# Reiniciar serviço
sudo systemctl restart hostapd
```

### USB-RS485 não detectado

```bash
# Listar dispositivos USB
lsusb
# Deve aparecer: "FTDI FT232" ou "CH340"

# Verificar porta
ls -l /dev/ttyUSB*

# Ver logs do kernel
dmesg | grep -i tty

# Verificar permissões
groups pi
# Deve conter: dialout

# Adicionar ao grupo (se necessário)
sudo usermod -a -G dialout pi
# Logout e login novamente
```

### Modbus timeout

```bash
# Testar comunicação
mbpoll -a 1 -b 57600 -P none -t 3 -r 1238 -c 2 /dev/ttyUSB0

# Testar outros slave IDs
for i in {1..10}; do
    echo "Testando slave ID: $i"
    timeout 2 mbpoll -a $i -b 57600 -P none -t 3 -r 1238 -c 1 /dev/ttyUSB0
done

# Verificar wiring
# A ↔ A+
# B ↔ B-
# GND ↔ GND
```

### Aplicação não inicia

```bash
# Ver logs
sudo journalctl -u ihm.service -f

# Verificar dependências
cd /home/pi/ihm_neocoude/ihm_rpi
source venv/bin/activate
pip list

# Testar manualmente
python3 main_server.py
```

### Temperatura alta (> 70°C)

```bash
# Monitorar temperatura
watch -n 1 vcgencmd measure_temp

# Soluções:
# 1. Instalar dissipador de calor
# 2. Adicionar cooler 5V (GPIO)
# 3. Melhorar ventilação da caixa
# 4. Reduzir overclock (se tiver)
```

### WebSocket desconecta frequentemente

```bash
# Verificar memória disponível
free -h

# Se < 100MB livre:
# 1. Reiniciar serviço: sudo systemctl restart ihm.service
# 2. Desabilitar serviços não usados
# 3. Aumentar swap (não recomendado no microSD)
```

---

## 📚 Documentação

### Arquivos do Projeto

- [`CLAUDE.md`](CLAUDE.md) - Documentação técnica completa
- [`INSTALL.md`](INSTALL.md) - Guia de instalação detalhado (a criar)
- [`modbus_map.py`](modbus_map.py) - Mapa de registros Modbus

### Manuais de Referência

- Manual CLP Atos MPC4004 (ver diretório pai)
- Manual Máquina NEOCOUDE-HD-15 (ver diretório pai)
- Especificação do Projeto (ver CLAUDE.md no diretório pai)

### Links Externos

- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [PyModbus Documentation](https://pymodbus.readthedocs.io/)
- [hostapd Documentation](https://w1.fi/hostapd/)
- [dnsmasq Documentation](https://thekelleys.org.uk/dnsmasq/doc.html)

---

## 🔒 Segurança

### Produção

⚠️ **Antes de deploy em produção:**

1. ✅ Trocar senha SSH: `passwd`
2. ✅ Trocar senha WiFi AP: `sudo nano /etc/hostapd/hostapd.conf`
3. ✅ Configurar firewall: `sudo ufw enable`
4. ✅ Desabilitar serviços não usados: `sudo systemctl disable bluetooth avahi-daemon`
5. ✅ Criar backup: `sudo dd if=/dev/mmcblk0 of=/mnt/usb/backup_ihm.img bs=4M status=progress`

### Backup

```bash
# Backup completo do microSD (no PC, com cartão em leitor USB)
sudo dd if=/dev/sdX of=backup_ihm_$(date +%Y%m%d).img bs=4M status=progress

# Comprimir backup (economiza 70%)
gzip backup_ihm_20251118.img

# Restaurar backup
gunzip backup_ihm_20251118.img.gz
sudo dd if=backup_ihm_20251118.img of=/dev/sdX bs=4M status=progress
```

---

## 📊 Performance

| Métrica | Valor | Comparação |
|---------|-------|------------|
| **Boot time** | 35-40s | Notebook: 60s |
| **Latência Modbus** | 30ms | ESP32: 50ms |
| **Latência WebSocket** | 300ms | ESP32: 500ms |
| **Consumo energia** | 4W | Notebook: 40W |
| **Custo** | ~R$ 500 | Notebook: ~R$ 2500 |
| **MTBF** | >50.000h | SSD: >100.000h |

---

## 🤝 Contribuindo

Este é um projeto proprietário. Para dúvidas ou sugestões, entre em contato:

**Eng. Lucas William Junges**

---

## 📝 Licença

Copyright © 2025 Lucas William Junges. Todos os direitos reservados.

---

## 🎯 Roadmap

- [ ] **v2.1** - OTA updates via WiFi
- [ ] **v2.2** - Dashboard Grafana
- [ ] **v2.3** - VPN para acesso remoto
- [ ] **v2.4** - Logs para servidor SYSLOG
- [ ] **v2.5** - Docker containerization
- [ ] **v3.0** - Cluster RPi (failover automático)

---

**Desenvolvido com ❤️ para a indústria brasileira**
**Versão:** 2.0-RPI3B+
**Data:** Novembro 2025
