# 🔴 DIAGNÓSTICO: Problema de Escrita Modbus

**Data:** 18 de Novembro de 2025
**Status:** ❌ BLOQUEADO - Escrita via Modbus RTU falhando 100%

---

## 📊 Sintomas

### ✅ O que FUNCIONA:
- Leitura Modbus: `connected: true`, valores retornam
- Comunicação básica RS485: ESP32 ↔ CLP estabelecida
- WiFi e servidor HTTP: operacional
- Interface web: carrega corretamente

### ❌ O que NÃO FUNCIONA:
- **Escrita em registros Modbus:** 100% de falha
- Erro no console: `"Erro gravacao registros"`
- Ocorre no primeiro `write_register()` (MSW ou LSW em 0x0A00/0x0A02)

---

## 🧪 Testes Realizados

### Teste 1: Timeout aumentado
- **Ação:** Timeout 1.0s → 2.0s
- **Resultado:** ❌ Ainda falha 100%

### Teste 2: Delays aumentados
- **Ação:**
  - Estabilização TX: 5ms → 10ms
  - Aguarda TX: 10ms → 20ms
  - Polling RX: 5ms → 10ms, dados: 10ms → 20ms
  - Delay entre comandos: +50ms
  - Delay trigger: 100ms → 150ms
- **Resultado:** ❌ Ainda falha 100%

### Teste 3: Leitura de estado
- **Comando:** `curl http://192.168.0.106/api/state`
- **Resposta:** ✅ Sucesso
```json
{
    "bend_1_angle": 0.0,
    "bend_2_angle": 0.0,
    "bend_3_angle": 0.0,
    "encoder_angle": 0.0,
    "speed_class": 1,
    "connected": true
}
```

### Teste 4: Escrita de ângulo
- **Comando:** `curl http://192.168.0.106/api/write_bend?bend=1&angle=77.5`
- **Console Serial:**
```
Gravando Dobra 1: 77.5° -> 0x0A00/0x0A02 (MSW=0, LSW=775)
Erro gravacao registros
```
- **Resposta:** ❌ `{"success": false, "message": "FAILED"}`

---

## 🔍 Análise

### Falha ocorre em: `write_register(0x0A00, MSW)`
- Função Modbus: **0x06 (Preset Single Register)**
- Endereço: **0x0A00 (Modbus Input Buffer)**
- CLP não responde ou retorna erro

### Possíveis Causas:

#### 1. **Área 0x0A00 protegida contra escrita** (MAIS PROVÁVEL)
- CLP Atos pode ter área "Modbus Input" como **read-only**
- Mesmo com ROT5 lendo de 0x0A00, pode não aceitar escrita externa
- **Solução:** Testar escrita em área alternativa (0x0500, 0x0550)

#### 2. **Hardware RS485 - Pino DE/RE não funciona**
- GPIO4 (DE/RE do MAX485) pode não estar controlando TX/RX
- MAX485 fica travado em modo RX → não transmite
- **Solução:** Medir tensão GPIO4 durante TX (deve ir para HIGH)

#### 3. **Slave ID incorreto**
- Tentando escrever em slave ID errado
- Mas leitura funciona com slave_id=1, então improvável
- **Solução:** Confirmar slave ID no CLP

#### 4. **Stop bits incorreto**
- Configurado: 2 stop bits
- CLP pode esperar 1 stop bit
- Mas leitura funciona, então improvável
- **Solução:** Testar com stop=1

#### 5. **CLP não aceita Function Code 0x06**
- Alguns PLCs só aceitam 0x10 (Write Multiple Registers)
- **Solução:** Modificar código para usar FC 0x10

---

## 🛠️ Ações Necessárias (Próximos Passos)

### URGENTE - Teste 1: Escrever em área alternativa
```bash
# Via mbpoll (se Ubuntu conectado ao CLP):
mbpoll -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0500 /dev/ttyUSB0 100

# OU modificar código ESP32 para testar 0x0500 em vez de 0x0A00
```

**Objetivo:** Confirmar se área 0x0A00 está protegida

---

### URGENTE - Teste 2: Verificar GPIO4 (DE/RE)
```python
# Via REPL ESP32:
from machine import Pin
de_re = Pin(4, Pin.OUT)

# Testar manualmente
de_re.value(1)  # Modo TX - medir tensão (deve ser ~3.3V)
de_re.value(0)  # Modo RX - medir tensão (deve ser ~0V)
```

**Objetivo:** Confirmar pino DE/RE funciona

---

### Teste 3: Usar Function Code 0x10 (Write Multiple)
Modificar `lib/umodbus/serial.py`:
```python
def write_multiple_registers(self, slave_addr, starting_addr, values):
    """Function Code 0x10: Preset Multiple Registers"""
    qty = len(values)
    byte_count = qty * 2
    frame = struct.pack('>BBHHB', slave_addr, 0x10, starting_addr, qty, byte_count)
    for val in values:
        frame += struct.pack('>H', val & 0xFFFF)
    self._send_frame(frame)
    response = self._receive_frame()

    if not response or len(response) < 6:
        return False

    return response[1] == 0x10
```

**Objetivo:** Alguns PLCs só aceitam FC 0x10

---

### Teste 4: Testar com 1 stop bit
```python
# boot.py ou main.py
self.uart = UART(uart_id, baudrate=baudrate, bits=data_bits,
                parity=parity, stop=1, tx=tx_pin, rx=rx_pin)  # stop=1
```

**Objetivo:** Verificar se stop bits está causando problema

---

### Teste 5: Conectar Ubuntu ao CLP via USB-RS485
- Conectar conversor USB-RS485 ao Ubuntu
- Testar escrita via `mbpoll` diretamente
- Comparar comportamento Ubuntu vs ESP32

**Objetivo:** Isolar problema (software vs hardware)

---

## 📦 Arquivos Modificados

### `/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/lib/umodbus/serial.py`
- ✅ Timeout: 2.0s
- ✅ Delays aumentados

### `/home/lucas-junges/Documents/clientes/w&co/ihm_esp32/modbus_client_esp32.py`
- ✅ Delay 50ms entre comandos
- ✅ Trigger delay 150ms

---

## 💡 Hipótese Principal

**Área 0x0A00 é READ-ONLY para Modbus externo.**

### Evidências:
1. ROT5 **lê** de 0x0A00 (interno ao CLP)
2. Leitura Modbus funciona (áreas 0x0840, 0x04D6)
3. Escrita Modbus falha **especificamente em 0x0A00**

### Solução Proposta:
**Usar área 0x0500 (Angle Setpoints) que é comprovadamente gravável:**
- Ladder program Principal.lad **escreve** em 0x0500
- Área documentada como "setpoint" = gravável
- Remover ROT5 e usar 0x0500 diretamente

### Mudança de Código:
```python
# modbus_map.py
BEND_ANGLES_WRITE = {
    'BEND_1_MSW': 0x0500,  # Em vez de 0x0A00
    'BEND_1_LSW': 0x0502,  # Em vez de 0x0A02
    # Sem triggers necessários
}
```

---

## 📞 Perguntas para o Usuário

1. **CLP está ligado e operacional?** ✅ (leitura funciona)
2. **Cabo RS485 A/B está correto?** ⚠️ (verificar)
3. **MAX485 DE/RE está em GPIO4?** ⚠️ (verificar)
4. **Área 0x0A00 é gravável via Modbus?** ❓ (testar)
5. **Posso tentar escrever em 0x0500?** ❓ (requer aprovação)

---

## 📚 Documentação Relacionada

- `RESUMO_IMPLEMENTACAO_FINAL.md` - Implementação 0x0A00 + ROT5
- `DESCOBERTA_CRITICA_0x0A00.md` - Análise ROT5
- `HARDWARE.md` - Pinout ESP32 ↔ MAX485 ↔ CLP

---

**Status:** 🔴 AGUARDANDO DIAGNÓSTICO HARDWARE OU TESTE ÁREA ALTERNATIVA
