# CLAUDE.md - IHM Web ESP32

## Visão Geral
Versão embarcada da IHM Web para dobradeira NEOCOUDE-HD-15, rodando em **ESP32-WROOM-32** com MicroPython.

**Origem:** Portado de `/ihm/` (versão Python/Ubuntu)

---

## 🎯 Arquitetura ESP32

```
┌─────────────────────────────────────────────┐
│  ESP32-WROOM-32 (MicroPython)               │
│                                             │
│  ┌──────────────┐      ┌─────────────────┐ │
│  │ boot.py      │──┬──→│ WiFi AP Config  │ │
│  └──────────────┘  │   └─────────────────┘ │
│                    │                        │
│  ┌──────────────┐  │   ┌─────────────────┐ │
│  │ main.py      │──┼──→│ Web Server      │ │
│  │ (orquestrador)│ │   │ (Microdot)      │ │
│  └──────────────┘  │   └─────────────────┘ │
│                    │                        │
│  ┌──────────────┐  │   ┌─────────────────┐ │
│  │ modbus_map   │◄─┘   │ Modbus RTU      │ │
│  │ (constantes) │      │ (umodbus)       │ │
│  └──────────────┘      └─────────────────┘ │
│                              │              │
└──────────────────────────────┼──────────────┘
                               │ UART2
                               │ GPIO17/16
                               ▼
                        ┌──────────────┐
                        │   MAX485     │
                        │   (RS485)    │
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
ihm_esp32/
├── CLAUDE.md                    ← Este arquivo
├── README.md                    ← Instruções de uso
├── HARDWARE.md                  ← Esquema de conexões
│
├── boot.py                      ← Inicialização (WiFi)
├── main.py                      ← Servidor principal
├── modbus_map.py                ← Registros Modbus (IGUAL ao Ubuntu)
├── modbus_client_esp32.py       ← Cliente Modbus (MicroPython)
├── state_manager_esp32.py       ← Gerenciador de estado
│
├── static/
│   └── index.html               ← Interface web (IGUAL ao Ubuntu)
│
└── lib/                         ← Bibliotecas externas
    ├── microdot.py              ← Web server
    ├── microdot_websocket.py    ← WebSocket
    └── umodbus/                 ← Modbus RTU
        ├── __init__.py
        ├── serial.py
        └── functions.py
```

---

## ⚙️ Hardware Necessário

### Componentes
1. **ESP32-WROOM-32 DevKit V1** (R$ 40-60)
2. **Módulo MAX485** (R$ 8-15)
3. **Conversor Buck 24V→5V 3A** (R$ 15-25)
4. **Cabos jumper** (R$ 5)

### Conexões (GPIO)

**RS485 via MAX485:**
```
ESP32          MAX485        CLP
GPIO17 (TX) ─→ DI
GPIO16 (RX) ─→ RO
GPIO4  (DE) ─→ DE + RE
3.3V        ─→ VCC
GND         ─→ GND
               A     ────→  RS485-A
               B     ────→  RS485-B
               GND   ────→  GND
```

**Alimentação:**
```
Painel 24V ─→ Buck IN+ (24V)
Painel GND ─→ Buck IN- (GND)
Buck OUT+  ─→ ESP32 VIN (5V)
Buck OUT-  ─→ ESP32 GND
```

**LEDs Indicadores (opcional):**
```
GPIO2  ─→ LED interno (WiFi status)
GPIO5  ─→ LED externo (Modbus OK)
GPIO18 ─→ LED externo (Cliente conectado)
```

---

## 🔧 Diferenças em Relação à Versão Ubuntu

### O que MUDOU:

| Ubuntu (CPython) | ESP32 (MicroPython) | Motivo |
|------------------|---------------------|--------|
| `pymodbus` | `umodbus` | Biblioteca nativa MicroPython |
| `aiohttp` | `microdot` | Web server leve (20KB vs 2MB) |
| `asyncio` | `uasyncio` | Async nativo do MicroPython |
| `/dev/ttyUSB0` | `UART(2)` | Hardware direto (GPIO) |
| Logs verbosos | Logs mínimos | Economia de RAM (520KB) |

### O que NÃO MUDOU:

✅ `modbus_map.py` - **100% idêntico** (apenas constantes)
✅ `static/index.html` - **100% idêntico** (navegador não muda)
✅ Protocolo WebSocket - **100% idêntico** (RFC 6455)
✅ Lógica de negócio - **100% idêntica**

---

## 📦 Instalação no ESP32

### 1. Flash MicroPython (uma vez)
```bash
# Baixar firmware
wget https://micropython.org/resources/firmware/esp32-20231005-v1.21.0.bin

# Flash (Linux)
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-20231005-v1.21.0.bin
```

### 2. Upload de Arquivos
```bash
# Via ampy (ou Thonny IDE)
ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put modbus_map.py
ampy --port /dev/ttyUSB0 put modbus_client_esp32.py
ampy --port /dev/ttyUSB0 put state_manager_esp32.py

# Diretórios
ampy --port /dev/ttyUSB0 put static/
ampy --port /dev/ttyUSB0 put lib/
```

### 3. Configurar WiFi
Editar `boot.py`:
```python
WIFI_SSID = "IHM_NEOCOUDE"     # Nome da rede WiFi
WIFI_PASSWORD = "dobradeira123" # Senha (min 8 caracteres)
```

### 4. Testar
```bash
# Console serial
screen /dev/ttyUSB0 115200

# Ou via Thonny
# Tools → Open Serial Monitor
```

---

## 🌐 Configuração WiFi

### Modo AP (Access Point) - RECOMENDADO
ESP32 cria rede própria:
```
SSID: IHM_NEOCOUDE
Senha: dobradeira123
IP: 192.168.4.1
```

**Vantagens:**
- ✅ Independente da rede da fábrica
- ✅ Tablet conecta direto
- ✅ Sem configuração adicional

**Tablet acessa:**
```
http://192.168.4.1/
```

### Modo STA (Station) - ALTERNATIVO
ESP32 conecta na rede existente:
```python
# boot.py
WIFI_MODE = 'STA'
WIFI_SSID = "WiFi_Fabrica"
WIFI_PASSWORD = "senha_fabrica"
```

**Descobrir IP:**
```python
>>> import network
>>> wlan = network.WLAN(network.STA_IF)
>>> wlan.ifconfig()
('192.168.0.150', '255.255.255.0', '192.168.0.1', '8.8.8.8')
```

---

## 🐛 Debug e Monitoramento

### Console Serial (Thonny)
```python
# Logs aparecem no console
print(f"✓ WiFi conectado: {ip}")
print(f"✓ Modbus lendo encoder: {encoder_raw}")
print(f"⚠ Cliente desconectado")
```

### WebREPL (via browser)
```python
# Habilitar WebREPL
import webrepl_setup
# Seguir prompts

# Acessar via navegador
# http://192.168.4.1:8266
```

### LEDs de Status
```python
# GPIO2 - LED interno
# Piscando rápido: Iniciando
# Piscando lento: WiFi conectado
# Aceso: Cliente WebSocket conectado
```

---

## ⚡ Consumo de Energia

| Modo | Corrente | Potência |
|------|----------|----------|
| **Boot** | 350mA | 1.75W |
| **WiFi idle** | 80mA | 0.4W |
| **WiFi TX** | 180mA | 0.9W |
| **Modbus + WiFi** | 120mA | 0.6W |

**Fonte recomendada:** Buck 24V→5V 3A (sobra 2.8A)

---

## 🔒 Segurança

### Produção
1. ❌ **Desabilitar WebREPL** (acesso remoto ao código)
2. ✅ **Trocar senha WiFi** (padrão é fraca)
3. ✅ **Desabilitar logs verbosos** (economiza RAM)
4. ✅ **Criar backup do firmware** (pendrive)

### Backup
```bash
# Backup completo
esptool.py --port /dev/ttyUSB0 read_flash 0 0x400000 backup_ihm_esp32.bin

# Restore (se necessário)
esptool.py --port /dev/ttyUSB0 write_flash 0 backup_ihm_esp32.bin
```

---

## 📊 Performance

### Tempo de Boot
- ESP32 liga: ~2 segundos
- WiFi conecta: ~3 segundos
- Modbus conecta: ~1 segundo
- **Total: ~6 segundos** (vs 60s notebook)

### Latência
- Leitura Modbus: ~50ms
- WebSocket update: ~500ms
- Resposta botão: ~100ms

### Memória
- Firmware MicroPython: 1.5MB
- Código aplicação: ~150KB
- HTML: ~25KB
- Bibliotecas: ~80KB
- **Total: ~1.8MB** (sobra 2.2MB na Flash)

---

## 🚀 Deploy em Produção

### Checklist
- [ ] Flash MicroPython no ESP32
- [ ] Upload de todos os arquivos
- [ ] Configurar WiFi (SSID/senha)
- [ ] Testar comunicação Modbus com CLP
- [ ] Testar WebSocket com tablet
- [ ] Montar em caixa DIN rail
- [ ] Instalar no painel elétrico
- [ ] Teste de stress 24h
- [ ] Criar backup do firmware
- [ ] Documentar IP/senha para cliente

### Manutenção
```bash
# Verificar versão
>>> import sys
>>> sys.version

# Ver uso de memória
>>> import gc
>>> gc.mem_free()

# Reset
>>> import machine
>>> machine.reset()
```

---

## 🆘 Troubleshooting

### ESP32 não conecta WiFi
```python
# Verificar SSID/senha
>>> import network
>>> wlan = network.WLAN(network.AP_IF)
>>> wlan.active(True)
>>> wlan.config(essid='IHM_NEOCOUDE')
```

### Modbus timeout
```python
# Verificar pinos GPIO
>>> from machine import Pin
>>> Pin(17, Pin.OUT).value(1)  # TX alto?
>>> Pin(16, Pin.IN).value()     # RX lendo?
```

### WebSocket desconecta
- Verificar RAM livre: `gc.mem_free()`
- Se < 50KB: reiniciar ESP32
- Reduzir frequência de polling (500ms → 1s)

### Reset constante
- **Causa:** Alimentação insuficiente
- **Solução:** Verificar Buck 5V está em exatos 5.0V
- Medir corrente: deve ser < 500mA

---

## 📚 Referências

- **MicroPython Docs:** https://docs.micropython.org/en/latest/esp32/
- **Microdot:** https://github.com/miguelgrinberg/microdot
- **uModbus:** https://github.com/pycom/pycom-modbus
- **ESP32 Pinout:** https://randomnerdtutorials.com/esp32-pinout-reference-gpios/

---

## 🎓 Próximas Melhorias

1. **OTA Update:** Upload de firmware via WiFi
2. **Logs persistentes:** Salvar em Flash
3. **Watchdog timer:** Auto-reset se travar
4. **Servidor NTP:** Timestamp correto nos logs
5. **HTTPS:** Criptografia WiFi→Tablet

---

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** Novembro 2025
**Versão:** 1.0-ESP32
