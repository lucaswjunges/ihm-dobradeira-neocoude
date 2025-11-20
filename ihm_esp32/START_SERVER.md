# 🚀 Iniciar Servidor IHM Web - Raspberry Pi 3B+

Guia para iniciar o servidor da IHM Web de diferentes formas.

---

## 🔄 Modo Automático (Systemd) - RECOMENDADO

O servidor inicia automaticamente ao ligar o Raspberry Pi.

### Verificar Status

```bash
sudo systemctl status ihm
```

**Saída esperada:**
```
● ihm.service - IHM Web - Dobradeira NEOCOUDE-HD-15
   Loaded: loaded (/etc/systemd/system/ihm.service; enabled; vendor preset: enabled)
   Active: active (running) since ...
```

### Controlar Serviço

```bash
# Iniciar
sudo systemctl start ihm

# Parar
sudo systemctl stop ihm

# Reiniciar
sudo systemctl restart ihm

# Ver logs em tempo real
sudo journalctl -u ihm -f

# Ver últimas 50 linhas de log
sudo journalctl -u ihm -n 50
```

### Habilitar/Desabilitar Auto-Start

```bash
# Habilitar (inicia com o sistema)
sudo systemctl enable ihm

# Desabilitar (não inicia com o sistema)
sudo systemctl disable ihm
```

---

## 🛠️ Modo Manual (para testes)

Use quando quiser testar sem systemd ou com parâmetros diferentes.

### Opção 1: Script Interativo (Mais Fácil)

```bash
cd /home/pi/ihm_esp32
bash scripts/start_ihm.sh
```

O script pergunta:
- `1` = Modo LIVE (conectar ao CLP)
- `2` = Modo STUB (simulação sem CLP)

### Opção 2: Python Direto

```bash
cd /home/pi/ihm_esp32
source venv/bin/activate

# Modo LIVE (conectar ao CLP via USB)
python3 main_server.py --port /dev/ttyUSB0

# Modo STUB (simulação - sem CLP)
python3 main_server.py --stub
```

**Parar:** Pressionar `Ctrl+C`

---

## 🔍 Verificar se Servidor Está Rodando

### Método 1: Systemd

```bash
sudo systemctl is-active ihm
```

**Saída esperada:** `active`

### Método 2: Processos

```bash
ps aux | grep main_server.py
```

**Saída esperada:** Linha com `/home/pi/ihm_esp32/main_server.py`

### Método 3: Portas de Rede

```bash
sudo netstat -tlnp | grep python3
```

**Saída esperada:**
```
tcp  0  0.0.0.0:8080  0.0.0.0:*  LISTEN  1234/python3
tcp  0  0.0.0.0:8765  0.0.0.0:*  LISTEN  1234/python3
```

- **Porta 8080:** Servidor HTTP (serve `index.html`)
- **Porta 8765:** Servidor WebSocket (comunicação em tempo real)

### Método 4: Testar com curl

```bash
curl http://localhost:8080
```

**Saída esperada:** HTML da página `index.html`

---

## 📱 Acessar do Tablet

### 1. Conectar WiFi

```
SSID: IHM_NEOCOUDE
Senha: dobradeira123
```

### 2. Abrir Navegador

```
http://192.168.50.1
```

ou

```
http://ihm.local
```

### 3. DevTools (Debugging)

No navegador (Chrome/Firefox):
- Pressionar `F12`
- Aba **Console:** Ver erros JavaScript
- Aba **Network > WS:** Ver mensagens WebSocket

---

## 🐛 Problemas Comuns

### Servidor não inicia (systemd)

```bash
# Ver logs de erro
sudo journalctl -u ihm -n 50 --no-pager

# Problemas comuns:
# 1. Virtual environment não existe
cd /home/pi/ihm_esp32
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Permissão negada em /dev/ttyUSB0
sudo usermod -a -G dialout pi
# Logout e login novamente

# 3. Porta USB não existe (modo LIVE)
ls /dev/ttyUSB*
# Se não aparecer, trocar para modo STUB (ver abaixo)
```

### Trocar para Modo STUB (sem CLP)

```bash
# Editar service
sudo nano /etc/systemd/system/ihm.service

# Alterar linha ExecStart:
# DE:
ExecStart=/home/pi/ihm_esp32/venv/bin/python3 /home/pi/ihm_esp32/main_server.py --port /dev/ttyUSB0

# PARA:
ExecStart=/home/pi/ihm_esp32/venv/bin/python3 /home/pi/ihm_esp32/main_server.py --stub

# Salvar (Ctrl+O, Enter, Ctrl+X)

# Recarregar e reiniciar
sudo systemctl daemon-reload
sudo systemctl restart ihm
```

### Página não abre (timeout)

```bash
# Verificar se servidor está rodando
sudo systemctl status ihm

# Verificar se WiFi está funcionando
ip addr show wlan0 | grep 192.168.50.1

# Verificar se hostapd está rodando
sudo systemctl status hostapd

# Reiniciar tudo
sudo systemctl restart ihm
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq
```

### WebSocket desconecta (DESLIGADO em vermelho)

```bash
# Ver logs do servidor
sudo journalctl -u ihm -f

# Problemas comuns:
# 1. Timeout Modbus (se modo LIVE)
#    Solução: Verificar cabo RS485 ou trocar para STUB

# 2. Servidor travou
#    Solução: sudo systemctl restart ihm

# 3. Problema no código Python
#    Solução: Ver logs acima
```

---

## 📊 Monitoramento em Tempo Real

### Logs Combinados (Servidor + WiFi + DHCP)

```bash
# Terminal 1: Logs do servidor
sudo journalctl -u ihm -f

# Terminal 2: Logs do WiFi AP
sudo journalctl -u hostapd -f

# Terminal 3: Clientes conectados
watch -n 2 'iw dev wlan0 station dump | grep Station'
```

### Dashboard de Status (Script Automático)

```bash
bash scripts/check_status.sh
```

Mostra:
- ✅ Status de todos os serviços
- 🌡️ Temperatura da CPU
- 💾 Uso de memória e disco
- 📡 Clientes WiFi conectados
- 🔌 Porta USB detectada
- 🐍 Processos Python rodando

---

## ⚙️ Configurações Avançadas

### Alterar Porta Serial (USB-RS485)

```bash
# Editar service
sudo nano /etc/systemd/system/ihm.service

# Alterar --port:
ExecStart=... --port /dev/ttyUSB1  # ou /dev/ttyAMA0, etc

# Recarregar
sudo systemctl daemon-reload
sudo systemctl restart ihm
```

### Logs Persistentes (Syslog)

```bash
# Habilitar logs persistentes
sudo mkdir -p /var/log/journal
sudo systemctl restart systemd-journald

# Ver logs antigos
sudo journalctl -u ihm --since "2025-01-01"
```

### Limitar Uso de Memória

```bash
# Editar service
sudo nano /etc/systemd/system/ihm.service

# Adicionar em [Service]:
MemoryLimit=256M
CPUQuota=80%

# Recarregar
sudo systemctl daemon-reload
sudo systemctl restart ihm
```

---

## 🔄 Atualizar Servidor

### Atualizar Código (Git Pull)

```bash
cd /home/pi/ihm_esp32
git pull

# Reiniciar servidor
sudo systemctl restart ihm
```

### Atualizar Dependências Python

```bash
cd /home/pi/ihm_esp32
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Reiniciar servidor
sudo systemctl restart ihm
```

### Reinstalar do Zero

```bash
# Parar serviço
sudo systemctl stop ihm
sudo systemctl disable ihm

# Remover instalação antiga
rm -rf /home/pi/ihm_esp32

# Reinstalar (ver QUICK_START.md)
cd /home/pi
git clone https://github.com/seu-usuario/ihm_neocoude.git
cd ihm_neocoude/ihm_esp32
sudo bash scripts/install.sh
sudo reboot
```

---

**Desenvolvido por:** Eng. Lucas William Junges  
**Versão:** 2.0-RPI3B+  
**Data:** Novembro 2025
