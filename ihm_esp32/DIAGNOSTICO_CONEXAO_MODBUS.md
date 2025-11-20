# DIAGNÓSTICO - CONEXÃO MODBUS ESP32 ↔ CLP

**Data:** 18 de Novembro de 2025
**Problema:** IHM Web acessível, mas não consegue mudar ângulos

---

## 🔴 Problema Identificado

```json
{
    "connected": false,
    "encoder_angle": 0.0,
    "bend_1_angle": 0.0,
    ...
}
```

O ESP32 **NÃO** está conseguindo se conectar ao CLP via Modbus RTU.

---

## 🔌 Checklist de Conexão

### 1. Hardware ESP32 ↔ MAX485 ↔ CLP

Verifique as conexões:

```
ESP32 GPIO17 (TX)  ───→  MAX485 DI (pino 1)
ESP32 GPIO16 (RX)  ───→  MAX485 RO (pino 4)
ESP32 GPIO4  (DE)  ───→  MAX485 DE + RE (pinos 2+3 juntos)
ESP32 3.3V         ───→  MAX485 VCC (pino 8)
ESP32 GND          ───→  MAX485 GND (pino 5)

MAX485 A (pino 6)  ───→  CLP RS485-B A
MAX485 B (pino 7)  ───→  CLP RS485-B B
```

**IMPORTANTE:**
- ✅ GPIO4 deve estar em **HIGH** (3.3V) para ativar transmissão
- ✅ A e B do MAX485 **NÃO** podem estar invertidos
- ✅ CLP deve estar ligado

---

### 2. Verificar Estado CLP

O estado `0x00BE` (190) **DEVE** estar ON no ladder para habilitar Modbus slave:

```python
# No REPL do ESP32
import modbus_client_esp32 as mc
client = mc.ModbusClientWrapper(stub_mode=False, slave_id=1)

# Tentar ler um coil simples
result = client.client.read_coils(1, 0x00BE, 1)  # Estado Modbus enabled
print(f"Estado 0x00BE: {result}")
```

Esperado: `[True]` ou `[1]`

---

### 3. Teste Manual Modbus

Execute no REPL do ESP32:

```python
import modbus_client_esp32 as mc
import modbus_map as mm

# Conecta
client = mc.ModbusClientWrapper(stub_mode=False, slave_id=1)
print(f"Conectado: {client.connected}")

# Testa leitura simples
encoder_msw = client.read_register(mm.ENCODER['ANGLE_MSW'])
print(f"Encoder MSW: {encoder_msw}")

# Se None = timeout/erro
if encoder_msw is None:
    print("ERRO: CLP não está respondendo!")
else:
    print("OK: CLP respondendo")
```

---

### 4. Verificar Baudrate e Parity

Padrão configurado: **57600 8N2**

Verifique no CLP (registro `1987H` = 6535 dec):
- 57600 baud
- 8 data bits
- None parity
- 2 stop bits

---

### 5. Teste de Escrita de Ângulo

Após confirmar comunicação OK:

```python
# Escrever 90° na Dobra 1
success = client.write_bend_angle(1, 90.0)
print(f"Escrita: {success}")

# Aguardar 1s
import time
time.sleep(1)

# Ler de volta
angle = client.read_bend_angle(1)
print(f"Ângulo lido: {angle}°")
```

---

## 🛠️ Soluções para Problemas Comuns

### Problema: `connected: false` sempre

**Causa:** UART2 não está funcionando ou MAX485 com defeito

**Solução:**
1. Verificar pinos GPIO17/16/4 com multímetro:
   - GPIO17: deve variar 0-3.3V (TX piscando)
   - GPIO16: deve variar 0-3.3V (RX piscando)
   - GPIO4: deve estar fixo em 3.3V (DE/RE HIGH)

2. Trocar MAX485 por outro (podem queimar fácil)

3. Testar com cabo mais curto (max 1 metro para teste)

---

### Problema: Timeout ao ler registros

**Causa:** Slave ID errado ou estado 0x00BE = OFF

**Solução:**
1. Verificar slave ID no CLP (registro `1988H` = 6536 dec)
2. Forçar estado `0x00BE` = ON no ladder
3. Testar com slave_id diferente (tentar 0-10)

---

### Problema: Escreve mas não lê de volta

**Causa:** Triggers não estão funcionando (ROT5 não está copiando)

**Solução:**
1. Verificar se ROT5.lad está carregado no CLP
2. Confirmar que triggers são COILS (função 0x05)
3. Verificar área SCADA 0x0B00 está sendo atualizada

---

## 🔍 Debug Avançado

### Ver logs do modbus_client_esp32.py

Os prints já estão no código, capture via serial:

```bash
screen /dev/ttyACM0 115200
```

Logs esperados:
```
Conectando Modbus UART2...
✓ Modbus conectado

Gravando Dobra 1: 90.5° -> 0x0A00/0x0A02 (MSW=0, LSW=905)
  Acionando trigger 0x0390 (via coil)...
OK: Dobra 1 = 90.5°
```

Se ver:
```
⚠ Erro Modbus: [timeout]
```

= Problema de comunicação física (hardware)

---

### Teste com mbpoll (via Ubuntu)

Se ESP32 estiver conectado ao Ubuntu via RS485-USB:

```bash
# Leitura (testa comunicação)
mbpoll -a 1 -b 57600 -P none -s 2 -t 3 -r 1238 -c 2 /dev/ttyUSB0

# Escrita em 0x0A00 (teste direto)
mbpoll -a 1 -b 57600 -P none -s 2 -t 4 -r 2560 1 /dev/ttyUSB0
```

---

## ✅ Checklist Final

- [ ] CLP ligado
- [ ] MAX485 alimentado (3.3V ou 5V)
- [ ] GPIO17/16/4 conectados corretamente
- [ ] A/B do RS485 não invertidos
- [ ] Estado 0x00BE = ON
- [ ] Baudrate 57600 configurado
- [ ] Teste manual no REPL funcionando
- [ ] Logs mostrando "Modbus conectado"

---

## 🆘 Se NADA funcionar

**Possíveis causas graves:**

1. **MAX485 queimado** - trocar por novo
2. **GPIO do ESP32 queimado** - testar com outro ESP32
3. **CLP não está em modo Modbus** - reprogramar ladder
4. **Cabo RS485 muito longo** - usar máx 1m para teste

**Solução temporária:**

Use modo STUB para testar interface:

```python
# modbus_client_esp32.py linha ~16
STUB_MODE = True  # Trocar de False para True
```

Reinicie ESP32 - ângulos serão simulados (não gravam no CLP)

---

**Boa sorte!** 🔧
