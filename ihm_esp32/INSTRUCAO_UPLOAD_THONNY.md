# Instruções para Upload via Thonny

## O Problema

O ESP32 está rodando código antigo com erro `'module' object has no attribute 'SPEED_CONTROL'`.
O comando `ampy` não está conseguindo fazer upload.

## Solução: Upload via Thonny (5 minutos)

### Passo 1: Abrir Thonny

```bash
thonny &
```

### Passo 2: Conectar no ESP32

1. `Tools → Options → Interpreter`
2. Selecionar: `MicroPython (ESP32)`
3. Porta: `/dev/ttyACM0`
4. Clicar `OK`

### Passo 3: Fazer Upload do main.py

1. `File → Open...`
2. Navegar para:
   ```
   /home/lucas-junges/Documents/clientes/w&co/ihm_esp32/main.py
   ```
3. Abrir o arquivo

4. `File → Save As...`
5. Selecionar: `MicroPython device`
6. Salvar como: `main.py` (substituir)

### Passo 4: Resetar ESP32

No console do Thonny (parte inferior):

```python
>>> import machine
>>> machine.reset()
```

Ou pressionar: **CTRL+D**

### Passo 5: Verificar

Aguardar 5 segundos e verificar logs no console. Deve aparecer:

```
========================================
IHM WEB - SERVIDOR ESP32
========================================

Modo: LIVE (CLP real)
✓ Sistema inicializado
✓ Servidor HTTP iniciado em :80
```

**SEM** erros de `SPEED_CONTROL`!

### Passo 6: Testar Modbus

No console do Thonny, colar comandos:

```python
from lib.umodbus.serial import ModbusRTU
modbus = ModbusRTU(uart_id=2, baudrate=57600, tx_pin=17, rx_pin=16, ctrl_pin=4)

# Testar leitura
result = modbus.read_holding_registers(1, 1238, 2)
print(f"Encoder: {result}")

# Se result != None → FUNCIONOU!
# Se result == None → CLP não está respondendo
```

---

## Resultado Esperado

### Se Modbus Funcionar:

```python
>>> result = modbus.read_holding_registers(1, 1238, 2)
>>> print(f"Encoder: {result}")
Encoder: [0, 360]  # ✓ SUCESSO!
```

### Se Modbus Continuar Falhando:

```python
>>> result = modbus.read_holding_registers(1, 1238, 2)
>>> print(f"Encoder: {result}")
Encoder: None  # ✗ CLP não respondeu
```

**Causa:** State 00BE = OFF no CLP (precisa forçar ON)

---

Por favor, execute esses passos no Thonny!
