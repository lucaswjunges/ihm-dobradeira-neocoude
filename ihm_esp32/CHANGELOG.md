# Changelog - IHM Web Raspberry Pi 3B+

Todas as mudanças notáveis neste projeto serão documentadas aqui.

---

## [2.0-RPI3B+] - 2025-01-19

### ✨ Adicionado

#### 🔧 Configuração Systemd
- **config/ihm.service** - Serviço systemd para auto-start ao ligar
  - Restart automático em caso de falha (RestartSec=10)
  - Logs via journald
  - Suporte a modo LIVE e STUB
  - Nice=-5 (prioridade alta)

#### 📡 Configuração WiFi Access Point
- **config/hostapd.conf** - WiFi AP completo
  - SSID: IHM_NEOCOUDE
  - Senha: dobradeira123
  - Canal 7 (2.4GHz)
  - WPA2-PSK (CCMP)
  - IEEE 802.11n (HT40)
  - Country: BR

#### 🌐 Configuração DHCP
- **config/dnsmasq.conf** - Servidor DHCP integrado
  - Range: 192.168.50.10 - 192.168.50.20
  - Gateway: 192.168.50.1 (o próprio RPi)
  - DNS: 8.8.8.8, 8.8.4.4
  - Resolve ihm.local → 192.168.50.1

#### 🔌 Configuração de Rede
- **config/dhcpcd.conf** - Interface wlan0
  - IP estático: 192.168.50.1/24
  - Desabilita wpa_supplicant na interface AP

#### 🚀 Scripts de Instalação
- **scripts/install.sh** - Instalação 100% automática
  - Atualiza sistema
  - Instala dependências (hostapd, dnsmasq, python3)
  - Configura WiFi AP
  - Instala virtual environment + pacotes Python
  - Habilita serviço systemd
  - Configura permissões USB (grupo dialout)
  - Configura NAT (compartilhar internet via Ethernet)

- **scripts/start_ihm.sh** - Inicialização manual interativa
  - Detecta porta USB automaticamente
  - Menu para escolher modo LIVE ou STUB
  - Ativa virtual environment automaticamente

- **scripts/check_status.sh** - Diagnóstico completo
  - Status de todos os serviços (ihm, hostapd, dnsmasq)
  - Temperatura da CPU
  - Uso de memória e disco
  - Clientes WiFi conectados
  - Porta USB detectada
  - Processos Python rodando
  - Portas de rede (8080, 8765)
  - Últimas linhas de log

- **scripts/setup_wifi_ap_sta.sh** - WiFi STA+AP simultâneo (experimental)
  - Cria interface virtual uap0
  - STA em wlan0 (rede da fábrica)
  - AP em uap0 (IHM)
  - NAT para compartilhar internet

#### 📚 Documentação
- **INSTALL.md** - Guia completo de instalação
  - Pré-requisitos hardware
  - Instalação rápida (3 comandos)
  - Instalação manual detalhada
  - Troubleshooting completo
  - Configurações avançadas
  - Segurança em produção

- **QUICK_START.md** - Início ultra-rápido
  - Checklist hardware
  - 3 comandos para instalar
  - Verificação de funcionamento
  - Comandos úteis (1-liner)

- **START_SERVER.md** - Guia de inicialização
  - Modo automático (systemd)
  - Modo manual (script/python)
  - Verificação de status
  - Troubleshooting
  - Monitoramento em tempo real
  - Configurações avançadas

- **requirements.txt** - Dependências Python
  - pymodbus==3.6.0
  - aiohttp==3.9.1
  - aiohttp-cors==0.7.0
  - websockets==12.0
  - gpiozero==2.0

#### 📦 Estrutura de Diretórios
```
ihm_esp32/
├── config/          # Arquivos de configuração do sistema
│   ├── ihm.service
│   ├── hostapd.conf
│   ├── dnsmasq.conf
│   └── dhcpcd.conf
├── scripts/         # Scripts de automação
│   ├── install.sh
│   ├── start_ihm.sh
│   ├── check_status.sh
│   └── setup_wifi_ap_sta.sh
├── static/          # Interface web
│   └── index.html
├── main_server.py   # Servidor principal
├── modbus_client.py # Cliente Modbus
├── modbus_map.py    # Mapa de registros
├── state_manager.py # Gerenciador de estado
└── requirements.txt # Dependências Python
```

### 🔧 Modificado
- **CLAUDE.md** atualizado com seção Raspberry Pi 3B+
  - Arquitetura detalhada
  - Comparação RPi vs ESP32
  - Configuração WiFi STA+AP
  - Troubleshooting específico do RPi
  - Checklist de deploy em produção

### 🐛 Corrigido
- N/A (versão inicial para Raspberry Pi)

### 🗑️ Removido
- N/A (versão inicial para Raspberry Pi)

---

## [1.0-Ubuntu] - 2025-01-15

### ✨ Versão Original (Ubuntu/Notebook)
- Servidor Python com asyncio + websockets
- Interface web HTML5 pura
- Modbus RTU via pymodbus
- Modo stub para desenvolvimento

---

## 🔮 Planejado (Roadmap)

### v2.1 (Próximo)
- [ ] Watchdog hardware (auto-reset se travar)
- [ ] Logs remotos via syslog
- [ ] OTA updates (atualização via WiFi)
- [ ] Backup automático diário

### v2.2
- [ ] Dashboard Grafana (métricas em tempo real)
- [ ] VPN para acesso remoto seguro
- [ ] Containerização com Docker
- [ ] Cluster RPi (redundância/failover)

### v3.0 (ESP32)
- [ ] Port completo para MicroPython
- [ ] Redução de consumo (<1W)
- [ ] Boot em <10s
- [ ] Custo reduzido (R$ 60 vs R$ 400)

---

**Mantido por:** Eng. Lucas William Junges  
**Repositório:** https://github.com/seu-usuario/ihm_neocoude
