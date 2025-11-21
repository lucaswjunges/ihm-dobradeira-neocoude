# 📋 CHECKLIST DE DEPLOY - IHM WEB RASPBERRY PI 3B+

**Projeto:** IHM Web para Dobradeira NEOCOUDE-HD-15
**Hardware:** Raspberry Pi 3B+ (Quad-core 1.4GHz, 1GB RAM, WiFi dual-band)
**Data:** 21/Nov/2025
**Autor:** Eng. Lucas William Junges

---

## ⚙️ FASE 1: Preparação Inicial (1-2 horas)

### 1.1. Preparar microSD Card
- [ ] Baixar Raspberry Pi OS Lite (64-bit) - versão **2024-10-22** ou mais recente
- [ ] Flash no microSD (16GB+ Classe 10) usando Raspberry Pi Imager
- [ ] Habilitar SSH (criar arquivo `ssh` na partição boot)
- [ ] Configurar WiFi inicial (criar `wpa_supplicant.conf`)
- [ ] Inserir microSD no RPi e ligar

### 1.2. Primeira Conexão
```bash
# Descobrir IP do RPi
ping raspberrypi.local

# Conectar via SSH
ssh pi@<IP_RPI>
# Senha padrão: raspberry

# TROCAR SENHA IMEDIATAMENTE!
passwd
```

### 1.3. Atualização Inicial (ÚLTIMA VEZ!)
```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt autoremove -y
sudo reboot
```

---

## 🔧 FASE 2: Instalação do Sistema (30 min)

### 2.1. Clonar Repositório
```bash
cd /home/pi
git clone https://github.com/seu-usuario/ihm_neocoude.git
cd ihm_neocoude/ihm_rpi
```

### 2.2. Executar Script de Instalação
```bash
sudo bash scripts/install.sh
```

**O que este script faz:**
- ✅ Instala Python 3 + dependências (pymodbus, aiohttp, websockets)
- ✅ Configura WiFi STA+AP simultâneo (hostapd + dnsmasq)
- ✅ Cria systemd service (auto-start)
- ✅ Testa comunicação Modbus
- ✅ Configura firewall (ufw)

### 2.3. Configurar Headless (RECOMENDADO)
```bash
sudo bash scripts/setup_headless.sh
```

**Benefícios:**
- 🚀 Boot mais rápido (35s → 20s)
- 💾 Menos RAM usada (~300MB economizados)
- 🔋 Menos consumo de energia
- 📈 Mais estável (menos componentes)

---

## 🌐 FASE 3: Configuração WiFi (20 min)

### 3.1. Verificar WiFi STA (Conexão com rede da fábrica)
```bash
# Editar wpa_supplicant
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf

# Adicionar rede da fábrica:
network={
    ssid="WiFi_Fabrica"
    psk="senha_da_fabrica"
    priority=1
}

# Reiniciar WiFi
sudo systemctl restart wpa_supplicant
```

### 3.2. Verificar WiFi AP (Rede para tablet)
```bash
# Verificar status AP
sudo systemctl status hostapd

# Ver clientes conectados
iw dev wlan0 station dump

# Testar DHCP
sudo systemctl status dnsmasq
```

### 3.3. Configurações WiFi AP
- **SSID:** `IHM_NEOCOUDE`
- **Senha:** `dobradeira123` (TROCAR EM PRODUÇÃO!)
- **IP do RPi:** `192.168.50.1`
- **Range DHCP:** `192.168.50.10` - `192.168.50.20`

**Tablet acessa:**
1. Conectar WiFi "IHM_NEOCOUDE"
2. Abrir navegador
3. Acessar: `http://192.168.50.1:8080`

---

## 🔐 FASE 4: Segurança e Bloqueio (15 min)

### 4.1. Executar Script de Bloqueio de Produção
```bash
sudo bash scripts/setup_production_lock.sh
```

**O que este script faz:**
- 🔒 Desabilita atualizações automáticas
- 🔒 Bloqueia pacotes críticos (kernel, Python, systemd)
- ⚙️ Ativa watchdog hardware (auto-reset se travar)
- 📊 Configura rotação de logs (max 100MB)
- 💾 Cria snapshot do sistema atual

### 4.2. Trocar Senhas
```bash
# Senha WiFi AP
sudo nano /etc/hostapd/hostapd.conf
# Trocar: wpa_passphrase=SuaSenhaForte123!
sudo systemctl restart hostapd

# Senha SSH
passwd
```

### 4.3. Configurar Firewall
```bash
# Permitir apenas portas necessárias
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 8080/tcp # HTTP/WebSocket

# Bloquear resto
sudo ufw default deny incoming
sudo ufw enable
```

---

## 🌍 FASE 5: Acesso Remoto (OPCIONAL - 10 min)

### Opção A: Tailscale (RECOMENDADO)
```bash
sudo bash scripts/setup_tailscale.sh
```

**Vantagens:**
- ✅ 100% gratuito
- ✅ Sem necessidade de abrir portas no roteador
- ✅ Funciona atrás de CGNAT
- ✅ Criptografia automática

**Como usar:**
1. Instalar Tailscale no seu PC/celular (casa)
2. Acessar RPi via: `ssh pi@<IP_TAILSCALE>`
3. Acessar IHM via: `http://<IP_TAILSCALE>:8080`

### Opção B: ZeroTier (Alternativa)
Similar ao Tailscale, também gratuito.

### Opção C: Port Forwarding + DynDNS
Requer admin do roteador da fábrica (não recomendado - risco de segurança).

---

## 🚀 FASE 6: Recursos Avançados (OPCIONAL - 30 min)

### 6.1. LEDs de Status no Painel
```bash
sudo bash scripts/setup_advanced_features.sh
# Escolher opção 1: "LED de status no painel (GPIO)"
```

**Conexões:**
- GPIO17 (pino 11) → LED VERDE (WiFi OK)
- GPIO27 (pino 13) → LED AMARELO (Modbus OK)
- GPIO22 (pino 15) → LED AZUL (Cliente conectado)
- GPIO10 (pino 19) → LED VERMELHO (Erro)

### 6.2. Buzzer de Alertas
```bash
sudo bash scripts/setup_advanced_features.sh
# Escolher opção 2: "Buzzer de alerta (GPIO)"
```

**Conexão:**
- GPIO18 (pino 12) → BUZZER (5V ativo)

### 6.3. Alertas via Telegram
```bash
sudo bash scripts/setup_advanced_features.sh
# Escolher opção 4: "Alertas via Telegram"
```

**Configuração:**
1. Abrir Telegram e buscar `@BotFather`
2. Criar bot com `/newbot`
3. Copiar TOKEN
4. Editar `telegram_alerts.py` com TOKEN e CHAT_ID

### 6.4. Backup Automático
```bash
sudo bash scripts/setup_advanced_features.sh
# Escolher opção 7: "Backup automático (cron)"
```

**Execução:** Diário às 03:00
**Local:** `/home/pi/backups/`
**Retenção:** Últimos 7 backups

---

## 🔌 FASE 7: Instalação Física (1 hora)

### 7.1. Hardware Necessário
- [x] Raspberry Pi 3B+ (R$ 350-450)
- [x] MicroSD 16GB+ Classe 10 (R$ 30-50)
- [x] Fonte 5V 3A USB-C (R$ 40-60) - Oficial recomendada
- [x] Conversor USB-RS485 (R$ 25-40) - FTDI ou CH340
- [x] Cabo USB-A para USB do conversor (R$ 10)
- [x] Caixa DIN rail (opcional, R$ 60-100)
- [ ] LEDs 5mm (opcional - 4 unidades: verde, amarelo, azul, vermelho)
- [ ] Buzzer 5V (opcional)
- [ ] UPS/Bateria 5V (opcional - alta disponibilidade)

### 7.2. Conexões Elétricas

**RS485 (CLP):**
```
Raspberry Pi         USB-RS485        CLP Atos MPC4004
USB Port      ─────→ USB plug
                     RS485-A   ────→  RS485-A (Canal B)
                     RS485-B   ────→  RS485-B (Canal B)
                     GND       ────→  GND
```

**Alimentação (Opção 1 - Fonte dedicada):**
```
Fonte 5V 3A ──→ USB-C (Raspberry Pi)
```

**Alimentação (Opção 2 - Painel industrial):**
```
24V Painel ──→ Buck Converter 24V→5V 5A ──→ GPIO 5V + GND (pinos 2 e 6)
```

**⚠️ ATENÇÃO:** RPi3B+ consome até 2.5A em picos! Use fonte adequada!

### 7.3. Montagem no Painel
1. Fixar RPi em caixa DIN rail
2. Conectar USB-RS485 ao painel
3. Conectar fonte de alimentação
4. Conectar LEDs de status (opcional)
5. Conectar buzzer (opcional)
6. Fixar antena WiFi (se externa)
7. Furar caixa para ventilação (3-4 furos 5mm)

---

## ✅ FASE 8: Testes Finais (30 min)

### 8.1. Teste de Comunicação Modbus
```bash
# Listar porta USB
ls -l /dev/ttyUSB*

# Testar leitura encoder
mbpoll -a 1 -b 57600 -P none -t 4 -r 1238 -c 2 /dev/ttyUSB0
```

**Esperado:** Valores hexadecimais do encoder (32-bit MSW+LSW)

### 8.2. Teste de WiFi AP
```bash
# Tablet: Conectar WiFi "IHM_NEOCOUDE"
# Tablet: Abrir navegador
# Tablet: Acessar http://192.168.50.1:8080

# No RPi, verificar cliente conectado:
sudo journalctl -u dnsmasq -f
```

### 8.3. Teste de WebSocket
```bash
# Verificar logs em tempo real
sudo journalctl -u ihm.service -f
```

**Esperado:**
```
🔗 Cliente WebSocket conectado: ('192.168.50.10', 54321)
✅ Estado completo enviado com sucesso!
```

### 8.4. Teste de Botões Virtuais
- [ ] Testar teclado numérico (K0-K9)
- [ ] Testar funções (S1, S2)
- [ ] Testar navegação (setas, ESC, ENTER)
- [ ] Testar controle motor (AVANÇAR, RECUAR, PARAR)

### 8.5. Teste de Stress (24h)
```bash
# Executar loop de comandos
while true; do
    curl http://localhost:8080/
    sleep 1
done &

# Monitorar temperatura
watch -n 5 vcgencmd measure_temp

# Monitorar recursos
htop
```

**Critérios de aceitação:**
- ✅ Temperatura < 65°C (sem dissipador) ou < 55°C (com dissipador)
- ✅ Uso de RAM < 600MB
- ✅ Uso de CPU < 30% (média)
- ✅ Sem reinicializações inesperadas
- ✅ WebSocket sem desconexões

---

## 🆘 FASE 9: Troubleshooting

### Problema: RPi não liga
**Sintomas:** LED vermelho apagado ou LED verde não pisca
**Soluções:**
1. Verificar fonte de alimentação (mínimo 5V 3A)
2. Trocar cabo USB-C
3. Testar microSD em outro RPi
4. Verificar LED vermelho (alimentação OK) e verde (leitura SD)

### Problema: WiFi AP não aparece
**Sintomas:** Tablet não vê rede "IHM_NEOCOUDE"
**Soluções:**
```bash
# Verificar status hostapd
sudo systemctl status hostapd

# Ver erros
sudo journalctl -u hostapd -n 50

# Reiniciar serviço
sudo systemctl restart hostapd

# Testar manualmente (debug)
sudo hostapd -d /etc/hostapd/hostapd.conf
```

### Problema: Modbus timeout
**Sintomas:** Erro ao ler registros do CLP
**Soluções:**
1. Verificar cabo RS485 (A/B não invertidos)
2. Verificar CLP ligado e em RUN
3. Verificar estado `00BE` (190 dec) ativo no ladder
4. Verificar baudrate (deve ser 57600)
5. Verificar permissões do usuário:
```bash
sudo usermod -a -G dialout pi
# Logout e login novamente
```

### Problema: Aplicação não inicia
**Sintomas:** IHM não responde em http://192.168.50.1:8080
**Soluções:**
```bash
# Ver logs detalhados
sudo journalctl -u ihm.service -f

# Verificar dependências Python
cd /home/pi/ihm_neocoude/ihm_rpi
source venv/bin/activate
pip list

# Testar manualmente
python3 main_server.py --stub
```

### Problema: Temperatura alta
**Sintomas:** `vcgencmd measure_temp` > 70°C
**Soluções:**
1. Instalar dissipador de calor (R$ 15)
2. Adicionar cooler 5V (R$ 10)
3. Melhorar ventilação da caixa (furos adicionais)
4. Reduzir overclock (se aplicado)
5. Verificar se caixa está em local com ventilação

---

## 📊 INDICADORES DE SUCESSO

### Boot Time
- ✅ **Headless:** 20-25 segundos (boot completo)
- ✅ **Com GUI:** 35-40 segundos

### Performance
- ✅ **Latência Modbus:** < 30ms (vs 50ms ESP32)
- ✅ **WebSocket update:** < 300ms (vs 500ms ESP32)
- ✅ **Resposta botão:** < 50ms (vs 100ms ESP32)

### Consumo
- ✅ **Idle:** ~2W (400mA @ 5V)
- ✅ **WiFi ativo:** ~3W (600mA @ 5V)
- ✅ **Típico operação:** ~4W (800mA @ 5V)
- ✅ **Pico máximo:** ~6W (1200mA @ 5V)

### Disponibilidade
- ✅ **Uptime esperado:** > 99.5% (< 4h downtime/mês)
- ✅ **MTBF (Mean Time Between Failures):** > 8760h (1 ano)
- ✅ **MTTR (Mean Time To Repair):** < 30 min (troca microSD)

---

## 📝 ENTREGÁVEIS FINAIS

### Documentação
- [x] `CLAUDE.md` - Instruções para futuras manutenções
- [x] `DEPLOY_CHECKLIST.md` - Este documento
- [x] `README.md` - Instruções de uso
- [x] Diagrama de conexões elétricas (desenhar à mão OK)

### Backups
- [x] Imagem completa do microSD (backup.img)
- [x] Snapshot do sistema (`ihm_production_snapshot_YYYYMMDD.tar.gz`)
- [x] Código-fonte no GitHub/GitLab

### Treinamento Cliente
- [ ] Demonstração de operação básica (1 hora)
- [ ] Treinamento troubleshooting (30 min)
- [ ] Entrega de credenciais (SSH, WiFi, Telegram)
- [ ] Contato para suporte remoto

---

## 🎯 CHECKLIST FINAL DE DEPLOY

### Pré-Deploy
- [ ] Sistema atualizado (última vez!)
- [ ] WiFi STA+AP testado
- [ ] Modbus testado com CLP real
- [ ] WebSocket testado com tablet
- [ ] Headless configurado
- [ ] Atualizações bloqueadas
- [ ] Watchdog ativo
- [ ] Firewall configurado
- [ ] Senhas alteradas
- [ ] Backup criado
- [ ] LEDs de status instalados (opcional)
- [ ] Buzzer instalado (opcional)
- [ ] Telegram configurado (opcional)
- [ ] Tailscale configurado (opcional)

### Instalação Física
- [ ] RPi montado em caixa DIN rail
- [ ] USB-RS485 conectado ao CLP
- [ ] Fonte 5V 3A conectada
- [ ] Ventilação adequada (furos na caixa)
- [ ] LEDs de status conectados (opcional)
- [ ] Buzzer conectado (opcional)
- [ ] UPS/bateria conectado (opcional)
- [ ] Etiquetas de identificação coladas

### Testes Finais
- [ ] Boot teste (< 25s)
- [ ] WiFi AP visível no tablet
- [ ] Tablet acessa http://192.168.50.1:8080
- [ ] WebSocket conecta
- [ ] Modbus lê encoder
- [ ] Botões virtuais funcionam
- [ ] Motor gira (AVANÇAR/RECUAR)
- [ ] Parada de emergência funciona
- [ ] Temperatura < 65°C (24h stress test)
- [ ] Sem reinicializações (24h stress test)

### Entrega
- [ ] Cliente treinado
- [ ] Documentação entregue (impressa ou PDF)
- [ ] Credenciais entregues (papel lacrado)
- [ ] Backup entregue (pendrive)
- [ ] Contato suporte fornecido
- [ ] Garantia definida (sugerir 90 dias)

---

## 📞 SUPORTE PÓS-DEPLOY

### Suporte Remoto (via Tailscale)
```bash
# Acesso SSH
ssh pi@<IP_TAILSCALE>

# Ver logs
sudo journalctl -u ihm.service -f

# Reiniciar serviço
sudo systemctl restart ihm.service

# Reiniciar sistema
sudo reboot
```

### Atualizações Futuras
⚠️ **IMPORTANTE:** Sistema está bloqueado para atualizações!

**Se REALMENTE necessário atualizar:**
```bash
# Desbloquear pacotes
sudo apt-mark unhold python3 raspberrypi-kernel systemd

# Atualizar
sudo apt update && sudo apt upgrade -y

# Bloquear novamente
sudo apt-mark hold python3 raspberrypi-kernel systemd

# Criar novo snapshot
sudo bash /home/pi/backup_ihm.sh
```

### Restauração de Backup
**Opção A: Restaurar snapshot (mais rápido)**
```bash
sudo tar -xzf ihm_production_snapshot_YYYYMMDD.tar.gz -C /
sudo reboot
```

**Opção B: Reescrever microSD completo (mais seguro)**
```bash
# No PC/Notebook:
sudo dd if=backup_ihm_rpi.img of=/dev/sdX bs=4M status=progress
```

---

## 🏆 GARANTIA DE QUALIDADE

Este sistema foi desenvolvido seguindo as melhores práticas de:
- ✅ Automação industrial (NR-12)
- ✅ Segurança de software (OWASP)
- ✅ Confiabilidade (MTBF, MTTR)
- ✅ Manutenibilidade (documentação completa)

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** 21/Novembro/2025
**Versão:** 2.0-RPI3B+
**Licença:** MIT (open-source)

---

**FIM DO CHECKLIST**
