# 🔴 DIAGNÓSTICO FINAL - Problema de Escrita Modbus

**Data:** 18 de Novembro de 2025
**Status:** 🔴 BLOQUEADO - CLP não responde a comandos de escrita

---

## ✅ O QUE FUNCIONA

### Hardware RS485
- ✅ MAX485 alimentado (3.3V conectado)
- ✅ Fios A/B verificados e reconectados
- ✅ ESP32 transmitindo corretamente (logs confirmam TX)
- ✅ GPIO4 (DE/RE) controlando modo TX/RX

### Comunicação Modbus - LEITURA
```json
{
    "connected": true,
    "encoder_angle": 0.0,
    "bend_1_angle": 0.0,
    "bend_2_angle": 0.0,
    "bend_3_angle": 0.0,
    "speed_class": 1
}
```
- ✅ Function Code 0x03 (Read Holding Registers): **FUNCIONA**
- ✅ CLP responde a leituras de 0x04D6, 0x0840, 0x0B00, etc.
- ✅ Valores lidos corretamente (0.0 = sem movimento)

---

## ❌ O QUE NÃO FUNCIONA

### Comunicação Modbus - ESCRITA

**Logs do console:**
```
[MODBUS TX] Slave=1, Func=0x06, Addr=0x0500, Val=0
[MODBUS RX] TIMEOUT - sem resposta

[MODBUS TX] Slave=1, Func=0x06, Addr=0x0500, Val=775
[MODBUS RX] TIMEOUT - sem resposta
```

**Comportamento:**
- ❌ Function Code 0x06 (Write Single Register): **NÃO RECEBE RESPOSTA**
- ❌ CLP não responde a comandos de escrita
- ❌ Timeout após 2 segundos de espera
- ❌ Testado em múltiplas áreas: 0x0A00, 0x0500, 0x0502

---

## 🔍 ANÁLISE TÉCNICA

### Evidências Coletadas

1. **Leitura e Escrita usam o mesmo canal RS485**
   - Leitura funciona → Hardware RS485 OK
   - Escrita falha → Problema específico de escrita

2. **ESP32 transmite corretamente**
   - Logs confirmam: `[MODBUS TX] Slave=1, Func=0x06`
   - Frame Modbus enviado (estrutura correta)
   - CRC calculado automaticamente

3. **CLP não responde**
   - Nenhuma resposta recebida (TIMEOUT)
   - OU resposta incompleta (5 bytes em vez de 6)

### Conclusão
**O CLP Atos MPC4004 está configurado como SOMENTE LEITURA ou bloqueando Function Code 0x06.**

---

## 🎯 CAUSA RAIZ PROVÁVEL

### Hipótese 1: CLP em Modo Somente Leitura (MAIS PROVÁVEL)
**Evidência:**
- Leitura (FC 0x03) funciona perfeitamente
- Escrita (FC 0x06) não recebe resposta
- Comportamento consistente em todos os endereços testados

**Verificação necessária:**
1. Estado **0x00BE (190 dec)** no ladder deve estar **ON**
   - Habilita Modbus slave mode
2. Verificar se há **proteção contra escrita** no programa ladder
3. Verificar **parâmetros RS485** do CLP:
   - Baudrate: 57600
   - Stop bits: 2
   - Parity: None
   - **Modo:** Deve ser R/W (não apenas R)

---

### Hipótese 2: CLP não suporta Function Code 0x06

Alguns PLCs antigos só aceitam **0x10 (Write Multiple Registers)**.

**Solução:** Modificar biblioteca uModbus para usar FC 0x10.

```python
def write_single_register(self, slave_addr, register_addr, value):
    """Usar 0x10 em vez de 0x06"""
    qty = 1
    byte_count = 2
    frame = struct.pack('>BBHHB', slave_addr, 0x10, register_addr, qty, byte_count)
    frame += struct.pack('>H', value & 0xFFFF)
    self._send_frame(frame)
    response = self._receive_frame()
    return response and response[1] == 0x10
```

---

### Hipótese 3: Área 0x0500 protegida

Mesmo sendo área de "setpoints", pode ter proteção no ladder.

**Solução:** Testar escrita em área **0x0940 (SUPERVISION_AREA)** que sabemos ser gravável.

---

## 📋 PLANO DE AÇÃO

### URGENTE 1: Verificar configuração CLP

Via WinSUP2 ou painel do CLP:

1. **Estado 0x00BE (Modbus Slave Enable):**
   ```
   Deve estar: ON (TRUE)
   Se estiver OFF: Forçar ON
   ```

2. **Parâmetros RS485-B:**
   ```
   Registrador 0x1987 (6535 dec): Baudrate
   Registrador 0x1988 (6536 dec): Slave Address
   Verificar: 57600 bps, Slave ID = 1
   ```

3. **Proteção contra escrita:**
   - Ver ladder se há condições bloqueando escrita
   - Verificar se há "Write Enable" bit

---

### URGENTE 2: Testar com Function Code 0x10

Modificar código para usar Write Multiple Registers:

**Arquivo:** `lib/umodbus/serial.py`

Adicionar método:
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

Modificar `modbus_client_esp32.py`:
```python
def write_register(self, address, value):
    # Tentar FC 0x10 em vez de FC 0x06
    return self.client.write_multiple_registers(self.slave_id, address, [value])
```

---

### ALTERNATIVA 3: Testar área 0x0940

Área validada como gravável pelo Python:

```python
# modbus_map.py já tem:
SUPERVISION_AREA = {
    'SPEED_CLASS': 0x094C,  # 2380 - Testado R/W ✅
}
```

**Teste:**
```python
# Via REPL ESP32
from lib.umodbus.serial import ModbusRTU
client = ModbusRTU(uart_id=2, baudrate=57600, data_bits=8, stop_bits=2, tx_pin=17, rx_pin=16, ctrl_pin=4)

# Testar escrita em 0x094C (área validada)
result = client.write_single_register(1, 0x094C, 5)
print("Resultado:", result)
```

---

## 🔧 TESTES VIA UBUNTU (Recomendado)

Conectar USB-RS485 do Ubuntu ao CLP para comparar comportamento:

### Teste 1: Leitura via mbpoll
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0500 -c 1 /dev/ttyUSB0
```

**Esperado:** Retorna valor atual do registro

---

### Teste 2: Escrita via mbpoll
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -t 4 -r 0x0500 /dev/ttyUSB0 100
```

**Se falhar:** Confirma que CLP está em modo somente leitura
**Se funcionar:** Problema é específico do ESP32/uModbus

---

### Teste 3: Escrita via pymodbus (Python Ubuntu)
```python
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    stopbits=2,
    bytesize=8,
    parity='N',
    timeout=2
)

if client.connect():
    # FC 0x06
    result = client.write_register(0x0500, 100, slave=1)
    print("FC 0x06:", result)

    # FC 0x10
    result = client.write_registers(0x0500, [100], slave=1)
    print("FC 0x10:", result)

    client.close()
```

---

## 📊 MATRIZ DE DIAGNÓSTICO

| Teste | Ubuntu mbpoll | Ubuntu pymodbus | ESP32 uModbus | Diagnóstico |
|-------|---------------|-----------------|---------------|-------------|
| **Leitura (FC 0x03)** | ✅ | ✅ | ✅ | Hardware OK |
| **Escrita FC 0x06** | ❌ | ❌ | ❌ | CLP não suporta FC 0x06 |
| **Escrita FC 0x06** | ✅ | ✅ | ❌ | Problema no uModbus |
| **Escrita FC 0x10** | ✅ | ✅ | ? | Testar FC 0x10 no ESP32 |

---

## 💡 RECOMENDAÇÃO FINAL

### Caminho 1: Habilitar escrita no CLP (IDEAL)
1. Verificar estado 0x00BE
2. Verificar proteção no ladder
3. Configurar RS485 modo R/W

### Caminho 2: Usar FC 0x10 (WORKAROUND)
1. Modificar uModbus para FC 0x10
2. Testar escrita
3. Se funcionar, implementar permanentemente

### Caminho 3: Escrever via Python (TEMPORÁRIO)
1. Manter Python rodando no Ubuntu
2. Python recebe comandos da IHM Web
3. Python escreve no CLP via pymodbus
4. ESP32 só faz leitura

---

## 📞 PERGUNTAS PARA O CLIENTE

1. **O CLP estava funcionando antes com escrita via Modbus?**
   - Se sim: O que mudou?
   - Se não: Nunca foi configurado para escrita

2. **Existe documentação da configuração atual do CLP?**
   - Backup do ladder
   - Parâmetros RS485

3. **É possível acessar o CLP via WinSUP2?**
   - Para verificar estado 0x00BE
   - Para modificar parâmetros RS485

4. **Há possibilidade de testar com outro CLP?**
   - Para isolar problema hardware vs software

---

**Status:** 🔴 AGUARDANDO VERIFICAÇÃO DA CONFIGURAÇÃO DO CLP
**Próximo Passo:** Verificar estado 0x00BE e parâmetros RS485 no CLP

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** 18/Nov/2025
