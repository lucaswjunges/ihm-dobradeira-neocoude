# IHM Web ESP32 - NEOCOUDE-HD-15

Versão embarcada da IHM Web para ESP32-WROOM-32 com MicroPython.

## 🚀 Quick Start

### 1. Instalar MicroPython no ESP32

```bash
# Baixar firmware
wget https://micropython.org/resources/firmware/esp32-20231005-v1.21.0.bin

# Flash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-20231005-v1.21.0.bin
```

### 2. Configurar WiFi

Editar `boot.py`:
```python
WIFI_SSID = 'IHM_NEOCOUDE'
WIFI_PASSWORD = 'dobradeira123'
```

### 3. Upload de Arquivos

**Opção A: Thonny IDE (recomendado para iniciantes)**
1. Abrir Thonny
2. Tools → Options → Interpreter → MicroPython (ESP32)
3. Arrastar arquivos para o ESP32

**Opção B: ampy (linha de comando)**
```bash
# Instalar ampy
pip install adafruit-ampy

# Upload arquivos
ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put modbus_map.py
ampy --port /dev/ttyUSB0 put modbus_client_esp32.py
ampy --port /dev/ttyUSB0 put state_manager_esp32.py

# Upload diretórios
ampy --port /dev/ttyUSB0 put static/
ampy --port /dev/ttyUSB0 put lib/
```

### 4. Testar

```bash
# Console serial
screen /dev/ttyUSB0 115200

# Deverá aparecer:
# IHM WEB - DOBRADEIRA NEOCOUDE-HD-15 (ESP32)
# ✓ WiFi AP ativo
# SSID: IHM_NEOCOUDE
# IP: 192.168.4.1
```

### 5. Acessar Interface

**No tablet/notebook:**
1. Conectar no WiFi "IHM_NEOCOUDE" (senha: dobradeira123)
2. Abrir navegador
3. Acessar: **http://192.168.4.1**

---

## 📁 Arquivos Necessários

### Obrigatórios (criar/baixar)
- [x] `boot.py` - Configuração WiFi ✓ CRIADO
- [x] `main.py` - Servidor principal (PRECISA CRIAR)
- [x] `modbus_map.py` - Mapa Modbus ✓ COPIADO
- [x] `modbus_client_esp32.py` - Cliente Modbus (PRECISA CRIAR)
- [ ] `state_manager_esp32.py` - Gerenciador de estado (PRECISA CRIAR)
- [x] `static/index.html` - Interface web ✓ COPIADO

### Bibliotecas Externas (baixar)
- [ ] `lib/microdot.py` - Web server
- [ ] `lib/microdot_websocket.py` - WebSocket
- [ ] `lib/umodbus/` - Modbus RTU

---

## 🔗 Download de Bibliotecas

### Microdot (Web Server)
```bash
# Download direto
wget https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot/microdot.py -O lib/microdot.py
wget https://raw.githubusercontent.com/miguelgrinberg/microdot/main/src/microdot/microdot_websocket.py -O lib/microdot_websocket.py
```

### uModbus (Modbus RTU)
```bash
# Clone repo
git clone https://github.com/pycom/pycom-modbus.git
cp -r pycom-modbus/umodbus lib/
```

---

## 🛠️ Hardware

### Conexões

**RS485 (MAX485):**
```
ESP32 GPIO17 (TX) → MAX485 DI
ESP32 GPIO16 (RX) → MAX485 RO
ESP32 GPIO4 (DE)  → MAX485 DE + RE
ESP32 3.3V        → MAX485 VCC
ESP32 GND         → MAX485 GND
MAX485 A          → CLP RS485-A
MAX485 B          → CLP RS485-B
```

**Alimentação:**
```
Painel 24V → Buck 24V→5V IN+
Painel GND → Buck IN-
Buck OUT+  → ESP32 VIN
Buck OUT-  → ESP32 GND
```

---

## 📊 Status da Migração

| Arquivo | Status | Complexidade |
|---------|--------|--------------|
| `boot.py` | ✅ PRONTO | Simples |
| `modbus_map.py` | ✅ PRONTO | Nenhuma (copiado) |
| `static/index.html` | ✅ PRONTO | Nenhuma (copiado) |
| `main.py` | ⏳ TODO | Média |
| `modbus_client_esp32.py` | ⏳ TODO | Média |
| `state_manager_esp32.py` | ⏳ TODO | Baixa |
| Bibliotecas | ⏳ TODO | Simples (download) |

**Progresso:** 3/7 arquivos (43%)
**Tempo estimado restante:** 2-3 horas

---

## 🆘 Troubleshooting

### ESP32 não aparece em /dev/ttyUSB0
```bash
# Verificar conexão USB
dmesg | tail

# Instalar driver CH340/CP2102 se necessário
sudo apt install -y ch341-driver
```

### Erro ao fazer upload
```bash
# Reiniciar ESP32 segurando botão BOOT
# Soltar BOOT após começar upload
```

### WebSocket não conecta
- Verificar IP correto no navegador
- Tablet deve estar na mesma rede WiFi
- Abrir console do navegador (F12) para ver erros

---

## 📞 Suporte

**Desenvolvedor:** Eng. Lucas William Junges
**Projeto:** IHM Web Dobradeira NEOCOUDE-HD-15
**Data:** Novembro 2025

**Documentação completa:** Ver `CLAUDE.md`
