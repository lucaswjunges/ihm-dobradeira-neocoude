# Teste de Comunicação Modbus ESP32 ↔ CLP

## 🎯 Objetivo

Verificar se o ESP32 está conseguindo se comunicar com o CLP Atos MPC4004 via Modbus RTU.

---

## 📋 Checklist Pré-Teste

### Hardware

- [ ] **CLP ligado** (24V alimentação)
- [ ] **MAX485 alimentado** (3.3V ou 5V)
- [ ] **Cabos RS485 conectados:**
  - MAX485 A → CLP RS485-A
  - MAX485 B → CLP RS485-B
  - MAX485 GND → CLP GND
- [ ] **ESP32 conectado ao MAX485:**
  - GPIO17 → MAX485 DI (TX)
  - GPIO16 → MAX485 RO (RX)
  - GPIO4 → MAX485 DE + RE
  - 3.3V → MAX485 VCC
  - GND → MAX485 GND

### Software (CLP)

- [ ] **State 00BE (190 dec) = ON** no ladder
  - Este state **HABILITA** o modo slave Modbus
  - Se estiver OFF, CLP não responde Modbus
- [ ] **Baudrate = 57600** (registro 1987H = 6535 dec)
- [ ] **Slave ID conhecido** (registro 1988H = 6536 dec)
  - Padrão: ID=1
  - Verificar no ladder se foi alterado

---

## 🔧 Método 1: Teste via Thonny (RECOMENDADO)

### Passo 1: Abrir Thonny

```bash
thonny &
```

### Passo 2: Conectar no ESP32

1. `Tools → Options → Interpreter`
2. Selecionar: `MicroPython (ESP32)`
3. Porta: `/dev/ttyACM0`
4. Clicar `OK`

### Passo 3: Fazer Upload do Script de Teste

1. Abrir arquivo:
   ```
   /home/lucas-junges/Documents/clientes/w&co/ihm_esp32/test_modbus_esp32.py
   ```

2. `File → Save As → MicroPython device`
3. Salvar como: `test_modbus_esp32.py`

### Passo 4: Executar Teste

**No console do Thonny:**

```python
>>> import test_modbus_esp32
```

### Passo 5: Analisar Resultado

**Cenário A: Todos os testes OK ✅**

```
==================================================
TESTE MODBUS ESP32 - DIAGNÓSTICO CLP
==================================================

[1/4] Inicializando Modbus...
✓ Modbus inicializado

[2/4] Teste 1: Lendo encoder (32-bit)...
✓ Leitura OK:
  MSW (reg 1238): 0x0000 (0)
  LSW (reg 1239): 0x0168 (360)
  Valor 32-bit: 360
  Ângulo: 36.0°

[3/4] Teste 2: Lendo ângulo dobra 1...
✓ Leitura OK:
  Valor bruto: 900
  Ângulo: 90.0°

[4/4] Teste 3: Lendo entrada digital E0...
✓ Leitura OK:
  Valor bruto: 0x0001 (1)
  E0 status: ON

==================================================
DIAGNÓSTICO COMPLETO
==================================================

✓ Comunicação Modbus OK!
```

**Significado:**
- ✅ Modbus RTU funcionando
- ✅ CLP respondendo
- ✅ Registros sendo lidos corretamente
- **Solução:** Nenhum problema! Sistema funcionando!

---

**Cenário B: Todos os testes falharam ✗**

```
[1/4] Inicializando Modbus...
✓ Modbus inicializado

[2/4] Teste 1: Lendo encoder (32-bit)...
✗ Sem resposta do CLP

[3/4] Teste 2: Lendo ângulo dobra 1...
✗ Sem resposta do CLP

[4/4] Teste 3: Lendo entrada digital E0...
✗ Sem resposta do CLP
```

**Possíveis causas:**

1. **CLP não está em modo slave Modbus**
   - Verificar: State 00BE (190) = ON no ladder
   - Verificar: State 03D0 (976) = OFF (modo master deve estar desligado)

2. **Fiação RS485 invertida**
   - Trocar A ↔ B
   - Tentar novamente

3. **Slave ID errado**
   - Editar `test_modbus_esp32.py` linha 15:
   ```python
   SLAVE_ID = 2  # Testar IDs de 1 a 10
   ```

4. **Baudrate errado**
   - Verificar registro 1987H (6535 dec) no CLP
   - Valores possíveis: 9600, 19200, 38400, 57600, 115200
   - Alterar linha 16 do script:
   ```python
   BAUDRATE = 19200  # Testar outros valores
   ```

5. **MAX485 sem alimentação ou defeituoso**
   - Medir tensão no pino VCC do MAX485 (deve ser 3.3V ou 5V)
   - Verificar LED de TX/RX (se existir)

---

**Cenário C: Valores estranhos (lixo) 🤔**

```
[2/4] Teste 1: Lendo encoder (32-bit)...
✓ Leitura OK:
  MSW (reg 1238): 0xFFFF (65535)
  LSW (reg 1239): 0xAB12 (43794)
  Ângulo: 429496735.4°  ← Absurdo!
```

**Possíveis causas:**

1. **Endereços de registro errados**
   - Encoder pode não estar em 04D6/04D7
   - Analisar ladder `clp.sup` para encontrar endereços corretos

2. **CLP em modo master (não slave)**
   - Forçar state 00BE = ON
   - Forçar state 03D0 = OFF

3. **Interferência RS485**
   - Adicionar resistores terminadores (120Ω) nas pontas do cabo
   - Reduzir comprimento do cabo

---

## 🔧 Método 2: Teste Manual (REPL)

### Passo 1: Abrir Console Serial

```bash
screen /dev/ttyACM0 115200
# Ou via Thonny: View → Shell
```

### Passo 2: Testar Manualmente

```python
>>> from machine import Pin, UART
>>> from lib.umodbus.serial import ModbusRTU

# Inicializar Modbus
>>> modbus = ModbusRTU(uart_id=2, baudrate=57600, tx_pin=17, rx_pin=16, ctrl_pin=4)

# Ler encoder (registros 1238-1239)
>>> result = modbus.read_holding_registers(1, 1238, 2)
>>> print(result)
[0, 360]  # ✓ OK - Encoder em 36.0°

# Se retornar None:
>>> print(result)
None  # ✗ CLP não respondeu
```

---

## 🐛 Troubleshooting Avançado

### Verificar Sinais UART

```python
>>> from machine import Pin

# Verificar TX (deve estar em HIGH quando idle)
>>> tx_pin = Pin(17, Pin.OUT)
>>> tx_pin.value()
1  # ✓ OK

# Verificar RX (deve variar)
>>> rx_pin = Pin(16, Pin.IN)
>>> rx_pin.value()
0 ou 1  # OK se alternar
```

### Verificar DE/RE (controle de direção)

```python
>>> de_pin = Pin(4, Pin.OUT)

# LOW = recepção (padrão)
>>> de_pin.value(0)

# HIGH = transmissão
>>> de_pin.value(1)
```

### Monitorar Tráfego UART (Raw)

```python
>>> from machine import UART
>>> uart = UART(2, baudrate=57600, tx=17, rx=16)

# Enviar comando Modbus manualmente (hex)
# Exemplo: Read Holding Reg, Slave=1, Addr=1238, Qty=2
>>> cmd = bytes([0x01, 0x03, 0x04, 0xD6, 0x00, 0x02])  # Sem CRC
>>> uart.write(cmd)

# Aguardar resposta
>>> import time
>>> time.sleep(0.5)
>>> resp = uart.read()
>>> print(resp)
```

---

## 📊 Tabela de Diagnóstico Rápido

| Sintoma | Causa Provável | Solução |
|---------|----------------|---------|
| **Timeout em todas leituras** | State 00BE = OFF | Forçar ON no ladder |
| **CRC Error** | Baudrate errado | Testar 9600/19200/57600 |
| **Valores aleatórios** | A/B invertidos | Trocar fios RS485 |
| **Funciona 1x depois para** | Problema DE/RE | Verificar GPIO4 |
| **Registros sempre 0** | Endereços errados | Analisar ladder |

---

## ✅ Resultado Esperado

**Após diagnóstico bem-sucedido:**

1. ✅ Todos os 3 testes passam
2. ✅ Valores fazem sentido:
   - Encoder: 0-360° (ou múltiplos)
   - Ângulos: 0-180° (típico)
   - Entradas digitais: 0 ou 1
3. ✅ `connected: true` no `/api/state`
4. ✅ Interface web mostra **"CLP ✓"** em verde

---

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** 17/Novembro/2025
**Versão:** 1.0-ESP32-MODBUS-DIAG
