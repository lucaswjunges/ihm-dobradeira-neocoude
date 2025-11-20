# CLAUDE.md - IHM Web Raspberry Pi 3B+

## Visão Geral
Versão embarcada da IHM Web para dobradeira NEOCOUDE-HD-15, rodando em **Raspberry Pi 3B+** com Python 3.

**Origem:** Portado de `/ihm/` (versão Python/Ubuntu) - praticamente código idêntico

---

## 🎯 Arquitetura Raspberry Pi 3B+

```
┌─────────────────────────────────────────────┐
│  Raspberry Pi 3B+ (Raspberry Pi OS)         │
│                                             │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │ systemd      │──┬──→│ WiFi STA+AP     │ │
│  │ (auto-start) │  │   │ (hostapd+       │ │
│  └──────────────┘  │   │  dnsmasq)       │ │
│                    │   └─────────────────┘ │
│  ┌──────────────┐  │   ┌─────────────────┐ │
│  │ main_server  │──┼──→│ Web Server      │ │
│  │ (Python 3)   │  │   │ (aiohttp/Flask) │ │
│  └──────────────┘  │   └─────────────────┘ │
│                    │                        │
│  ┌──────────────┐  │   ┌─────────────────┐ │
│  │ modbus_map   │◄─┘   │ Modbus RTU      │ │
│  │ (constantes) │      │ (pymodbus)      │ │
│  └──────────────┘      └─────────────────┘ │
│                              │              │
└──────────────────────────────┼──────────────┘
                               │ USB
                               │ /dev/ttyUSB0
                               ▼
                        ┌──────────────┐
                        │ USB-RS485    │
                        │ (FTDI/CH340) │
                        └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │  CLP Atos    │
                        │  MPC4004     │
                        └──────────────┘
```

---

## 📁 Estrutura de Arquivos

```
ihm_rpi/
├── CLAUDE.md                    ← Este arquivo
├── README.md                    ← Instruções de uso
├── INSTALL.md                   ← Guia de instalação
│
├── main_server.py               ← Servidor principal (IGUAL Ubuntu)
├── modbus_map.py                ← Registros Modbus (IGUAL Ubuntu)
├── modbus_client.py             ← Cliente Modbus (IGUAL Ubuntu)
├── state_manager.py             ← Gerenciador de estado (IGUAL Ubuntu)
│
├── static/
│   └── index.html               ← Interface web (IGUAL Ubuntu)
│
├── config/
│   ├── ihm.service              ← Systemd service
│   ├── hostapd.conf             ← WiFi AP config
│   ├── dnsmasq.conf             ← DHCP server
│   └── dhcpcd.conf              ← Network config
│
└── scripts/
    ├── install.sh               ← Instalação automática
    ├── setup_wifi.sh            ← Configurar WiFi STA+AP
    └── start_ihm.sh             ← Script de inicialização
```

---

## ⚙️ Hardware Necessário

### Componentes
1. **Raspberry Pi 3B+** (R$ 350-450) - WiFi dual-band built-in
2. **Cartão microSD 16GB+** (R$ 30-50) - Classe 10 ou melhor
3. **Fonte 5V 3A USB-C** (R$ 40-60) - Oficial recomendada
4. **Conversor USB-RS485** (R$ 25-40) - FTDI ou CH340
5. **Cabo USB-A para mini/micro USB** (R$ 10)
6. **Caixa DIN rail** (opcional, R$ 60-100)

### Conexões

**RS485 via USB:**
```
Raspberry Pi         USB-RS485        CLP
USB Port      ─────→ USB plug
                     RS485-A   ────→  RS485-A
                     RS485-B   ────→  RS485-B
                     GND       ────→  GND
```

**Alimentação:**
```
Opção 1 (recomendado):
  Fonte 5V 3A ─→ USB-C (GPIO header)

Opção 2 (painel industrial):
  24V Painel ─→ Buck 24V→5V 5A ─→ GPIO 5V + GND

ATENÇÃO: RPi3B+ consome até 2.5A (picos), use fonte adequada!
```

**LEDs Indicadores (GPIO - opcional):**
```
GPIO17 ─→ LED externo (WiFi STA conectado)
GPIO27 ─→ LED externo (Modbus OK)
GPIO22 ─→ LED externo (Cliente WebSocket conectado)
```

---

## 🔧 Vantagens vs ESP32

| Característica | ESP32 | Raspberry Pi 3B+ |
|----------------|-------|------------------|
| **CPU** | 240 MHz dual-core | 1.4 GHz quad-core |
| **RAM** | 520 KB | 1 GB |
| **Storage** | 4 MB Flash | 16+ GB microSD |
| **SO** | MicroPython | Linux completo |
| **Python** | MicroPython (subset) | CPython 3.11 (completo) |
| **WiFi** | 2.4 GHz only | 2.4 + 5 GHz dual-band |
| **STA+AP** | Difícil | Nativo (hostapd) |
| **Bibliotecas** | Limitadas | PyPI completo |
| **USB** | Não | 4 portas USB 2.0 |
| **Ethernet** | Não | Gigabit Ethernet |
| **Custo** | ~R$ 60 | ~R$ 400 |
| **Boot time** | ~6s | ~30s |
| **Consumo** | 0.5W | 5W (típico) |

**Conclusão:** RPi é melhor para produção industrial (robustez, debugging, atualizações)

---

## 🌐 Configuração WiFi STA+AP Simultâneo

### Modo STA (Station)
Conecta na rede da fábrica para:
- Acesso remoto via SSH
- Atualizações do sistema
- Monitoramento remoto
- Logs para servidor central

```bash
SSID: WiFi_Fabrica
IP: DHCP ou estático (ex: 192.168.0.100)
```

### Modo AP (Access Point)
Cria rede própria para tablet:
- Interface isolada
- DHCP integrado
- Sem dependência da rede da fábrica

```bash
SSID: IHM_NEOCOUDE
Senha: dobradeira123
IP: 192.168.50.1
Range DHCP: 192.168.50.10-50.20
```

### Tablet Acessa
```
1. Conectar WiFi "IHM_NEOCOUDE" (senha: dobradeira123)
2. Abrir navegador
3. Acessar: http://192.168.50.1/
```

---

## 📦 Instalação Rápida

### 1. Preparar microSD (PC/Notebook)
```bash
# Baixar Raspberry Pi OS Lite (64-bit)
wget https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2024-03-15/2024-03-15-raspios-bookworm-arm64-lite.img.xz

# Flash no microSD (Linux)
xzcat 2024-03-15-raspios-bookworm-arm64-lite.img.xz | sudo dd of=/dev/sdX bs=4M status=progress

# Ou usar Raspberry Pi Imager (GUI)
```

### 2. Configurar SSH e WiFi inicial
```bash
# Montar partição boot
cd /media/$USER/boot

# Habilitar SSH
touch ssh

# Configurar WiFi inicial (para primeira conexão)
cat > wpa_supplicant.conf << EOF
country=BR
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="Seu_WiFi_Temporario"
    psk="sua_senha"
}
EOF

# Desmontar e inserir no Raspberry Pi
```

### 3. Primeira conexão SSH
```bash
# Ligar Raspberry Pi (aguardar 1-2 minutos)
# Descobrir IP:
ping raspberrypi.local
# Ou verificar no roteador

# Conectar via SSH
ssh pi@192.168.0.XXX
# Senha padrão: raspberry

# IMPORTANTE: Trocar senha
passwd
```

### 4. Instalação automática
```bash
# Clonar repositório
cd /home/pi
git clone https://github.com/seu-usuario/ihm_neocoude.git
cd ihm_neocoude/ihm_rpi

# Executar script de instalação
sudo bash scripts/install.sh
```

O script `install.sh` faz tudo automaticamente:
- ✅ Atualiza sistema
- ✅ Instala Python 3 + dependências
- ✅ Configura WiFi STA+AP
- ✅ Instala pymodbus + aiohttp
- ✅ Configura systemd service
- ✅ Testa comunicação Modbus
- ✅ Reinicia sistema

Após reiniciar, o sistema estará pronto!

---

## 🔧 Instalação Manual (Detalhada)

### 1. Atualizar Sistema
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git hostapd dnsmasq
```

### 2. Configurar WiFi STA+AP
```bash
# Parar serviços
sudo systemctl stop hostapd dnsmasq

# Configurar interface wlan0 (STA + AP)
sudo tee /etc/dhcpcd.conf > /dev/null << EOF
interface wlan0
    static ip_address=192.168.50.1/24
    nohook wpa_supplicant
EOF

# Configurar hostapd (AP)
sudo tee /etc/hostapd/hostapd.conf > /dev/null << EOF
interface=wlan0
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
EOF

sudo tee /etc/default/hostapd > /dev/null << EOF
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Configurar dnsmasq (DHCP)
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo tee /etc/dnsmasq.conf > /dev/null << EOF
interface=wlan0
dhcp-range=192.168.50.10,192.168.50.20,255.255.255.0,24h
domain=wlan
address=/ihm.local/192.168.50.1
EOF

# Configurar wpa_supplicant (STA)
sudo tee -a /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null << EOF

network={
    ssid="WiFi_Fabrica"
    psk="senha_fabrica"
    priority=1
}
EOF

# Habilitar IP forwarding (opcional - para internet via STA)
sudo sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sudo sysctl -p

# Iniciar serviços
sudo systemctl unmask hostapd
sudo systemctl enable hostapd dnsmasq
sudo systemctl start hostapd dnsmasq
```

### 3. Instalar Aplicação Python
```bash
cd /home/pi
git clone https://github.com/seu-usuario/ihm_neocoude.git
cd ihm_neocoude/ihm_rpi

# Criar virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install pymodbus aiohttp aiohttp-cors websockets gpiozero
```

### 4. Configurar Systemd Service
```bash
sudo tee /etc/systemd/system/ihm.service > /dev/null << EOF
[Unit]
Description=IHM Web Dobradeira Neocoude
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/ihm_neocoude/ihm_rpi
ExecStart=/home/pi/ihm_neocoude/ihm_rpi/venv/bin/python3 main_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable ihm.service
sudo systemctl start ihm.service
```

### 5. Testar
```bash
# Verificar status
sudo systemctl status ihm.service

# Ver logs
sudo journalctl -u ihm.service -f

# Testar conexão
curl http://localhost:8080
```

---

## 🐛 Debug e Monitoramento

### Logs do Sistema
```bash
# Logs da aplicação
sudo journalctl -u ihm.service -f

# Logs do WiFi AP
sudo journalctl -u hostapd -f

# Logs do DHCP
sudo journalctl -u dnsmasq -f

# Logs do kernel (USB-RS485)
dmesg | grep ttyUSB
```

### Verificar WiFi
```bash
# Status AP
sudo systemctl status hostapd

# Clientes conectados
iw dev wlan0 station dump

# IP e interfaces
ip addr show

# Testar conectividade STA
ping 8.8.8.8
```

### Verificar Modbus
```bash
# Listar dispositivos USB
lsusb

# Verificar porta serial
ls -l /dev/ttyUSB*

# Testar comunicação (instalar mbpoll)
sudo apt install -y mbpoll
mbpoll -a 1 -b 57600 -t 3 -r 1238 -c 2 /dev/ttyUSB0
```

### LEDs de Status (via GPIO)
```python
# Adicionar em main_server.py
from gpiozero import LED

led_wifi = LED(17)
led_modbus = LED(27)
led_client = LED(22)

# Piscar LED quando conectar WiFi STA
led_wifi.on()

# Piscar LED quando Modbus OK
if modbus_client.is_connected():
    led_modbus.on()

# Piscar LED quando cliente WebSocket conecta
led_client.on()
```

---

## ⚡ Performance e Consumo

### Boot Time
- **Tempo total:** ~35-40 segundos
  - BIOS/bootloader: ~5s
  - Linux kernel: ~10s
  - Services (WiFi): ~15s
  - Aplicação Python: ~5s

### Latência
- Leitura Modbus: ~30ms (vs 50ms ESP32)
- WebSocket update: ~300ms (vs 500ms ESP32)
- Resposta botão: ~50ms (vs 100ms ESP32)

### Consumo de Energia
| Modo | Corrente | Potência |
|------|----------|----------|
| **Idle** | 400mA | 2W |
| **WiFi ativo** | 600mA | 3W |
| **CPU 100%** | 1200mA | 6W |
| **Típico operação** | 800mA | 4W |

**Fonte recomendada:** 5V 3A (15W) com margem de segurança

### Memória
```bash
# Ver uso de RAM
free -h

# Ver uso de CPU
htop

# Ver uso de disco
df -h
```

---

## 🔒 Segurança em Produção

### 1. Trocar Senhas Padrão
```bash
# Senha do usuário pi
passwd

# Senha WiFi AP
sudo nano /etc/hostapd/hostapd.conf
# Trocar: wpa_passphrase=SuaSenhaForte123!
sudo systemctl restart hostapd
```

### 2. Configurar Firewall
```bash
sudo apt install -y ufw

# Permitir apenas portas necessárias
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 8080/tcp # WebSocket

# Bloquear resto
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
```

### 3. Desabilitar Serviços Desnecessários
```bash
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

### 4. Backup Automático
```bash
# Script de backup
cat > /home/pi/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/pi/backups"
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/ihm_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    /home/pi/ihm_neocoude \
    /etc/hostapd \
    /etc/dnsmasq.conf \
    /etc/systemd/system/ihm.service
EOF

chmod +x /home/pi/backup.sh

# Agendar backup diário (crontab)
(crontab -l 2>/dev/null; echo "0 3 * * * /home/pi/backup.sh") | crontab -
```

---

## 🚀 Deploy em Produção

### Checklist Pré-Deploy
- [ ] Sistema atualizado (`sudo apt update && sudo apt upgrade`)
- [ ] WiFi STA+AP funcionando
- [ ] Comunicação Modbus testada
- [ ] WebSocket testado com tablet
- [ ] LEDs de status instalados
- [ ] Fonte de alimentação adequada (5V 3A)
- [ ] Backup do microSD criado
- [ ] Senha WiFi alterada
- [ ] Senha SSH alterada
- [ ] Firewall configurado
- [ ] Documentação entregue ao cliente

### Instalação Física
```
1. Montar RPi em caixa DIN rail
2. Conectar USB-RS485 ao painel
3. Conectar fonte 5V 3A
4. Conectar LEDs de status (opcional)
5. Fixar antena WiFi (se externa)
6. Testar conectividade WiFi (tablet)
7. Testar comunicação Modbus (CLP)
8. Executar teste de stress 24h
```

### Teste de Stress
```bash
# Executar por 24h
while true; do
    curl http://localhost:8080/api/status
    sleep 1
done

# Monitorar temperatura
watch -n 1 vcgencmd measure_temp

# Monitorar recursos
htop
```

### Manutenção Programada
```bash
# Atualização mensal
sudo apt update && sudo apt upgrade -y

# Limpeza de logs antigos
sudo journalctl --vacuum-time=30d

# Verificar saúde do microSD
sudo badblocks -v /dev/mmcblk0
```

---

## 🆘 Troubleshooting

### RPi não liga
- ✅ Verificar LED vermelho aceso (alimentação OK)
- ✅ Verificar LED verde piscando (leitura microSD)
- ✅ Trocar fonte (mínimo 5V 3A)
- ✅ Testar microSD em outro PC

### WiFi AP não aparece
```bash
# Verificar status hostapd
sudo systemctl status hostapd

# Ver erros
sudo journalctl -u hostapd -n 50

# Reiniciar serviço
sudo systemctl restart hostapd

# Testar manualmente
sudo hostapd -d /etc/hostapd/hostapd.conf
```

### WiFi STA não conecta
```bash
# Verificar wpa_supplicant
sudo wpa_cli status

# Escanear redes
sudo iwlist wlan0 scan | grep SSID

# Reconfigurar
sudo raspi-config
# 1. System Options → Wireless LAN
```

### USB-RS485 não detectado
```bash
# Listar USB
lsusb

# Verificar drivers
dmesg | grep -i ftdi
dmesg | grep -i ch340

# Instalar drivers (se necessário)
sudo apt install -y linux-modules-extra-raspi
```

### Modbus timeout
```bash
# Verificar porta
ls -l /dev/ttyUSB*

# Permissões
sudo usermod -a -G dialout pi
# Logout e login novamente

# Testar com mbpoll
mbpoll -a 1 -b 57600 -P none -t 3 -r 1238 -c 2 /dev/ttyUSB0
```

### Aplicação não inicia
```bash
# Ver logs detalhados
sudo journalctl -u ihm.service -f

# Verificar dependências
cd /home/pi/ihm_neocoude/ihm_rpi
source venv/bin/activate
pip list

# Testar manualmente
python3 main_server.py
```

### Temperatura alta
```bash
# Verificar temperatura
vcgencmd measure_temp

# Se > 70°C:
# 1. Instalar dissipador de calor
# 2. Adicionar cooler 5V
# 3. Melhorar ventilação da caixa
```

---

## 📊 Comparação: RPi3B+ vs Ubuntu Notebook

| Característica | Ubuntu Notebook | RPi 3B+ | Melhor |
|----------------|-----------------|---------|--------|
| **Custo** | R$ 2000-4000 | R$ 400 | RPi |
| **Consumo** | 30-60W | 4W | RPi |
| **Tamanho** | Grande | Mini | RPi |
| **Boot** | 60s | 35s | RPi |
| **Robustez** | Baixa | Alta | RPi |
| **Manutenção** | Complexa | Simples | RPi |
| **CPU** | i5/i7 | 1.4GHz ARM | Notebook |
| **RAM** | 8-16GB | 1GB | Notebook |
| **SSD** | 256GB+ | 16GB SD | Notebook |
| **USB** | 2-4 portas | 4 portas | Empate |
| **WiFi AP** | Difícil | Nativo | RPi |
| **Industrial** | Não | Sim | RPi |

**Conclusão:** RPi3B+ é ideal para ambiente industrial!

---

## 📚 Referências

- **Raspberry Pi OS:** https://www.raspberrypi.com/software/
- **hostapd:** https://w1.fi/hostapd/
- **dnsmasq:** https://thekelleys.org.uk/dnsmasq/doc.html
- **pymodbus:** https://pymodbus.readthedocs.io/
- **aiohttp:** https://docs.aiohttp.org/
- **systemd:** https://systemd.io/

---

## 🎓 Próximas Melhorias

1. **Watchdog hardware:** Auto-reset se travar
2. **Logs remotos:** Enviar para servidor SYSLOG
3. **OTA updates:** Atualização via WiFi
4. **Dashboard Grafana:** Métricas em tempo real
5. **Backup automático:** Para servidor NAS
6. **VPN:** Acesso remoto seguro
7. **Docker:** Containerizar aplicação
8. **Redundância:** Cluster RPi (failover)

---

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** Novembro 2025
**Versão:** 2.0-RPI3B+
**Dispositivo:** Raspberry Pi 3B+ (Quad-core 1.4GHz, 1GB RAM, WiFi dual-band)
