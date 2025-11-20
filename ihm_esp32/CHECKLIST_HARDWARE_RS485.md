# CHECKLIST HARDWARE - RS485 ESP32 ↔ CLP

**Problema:** ESP32 transmite mas CLP não responde (timeout em todas as leituras)

---

## 🔴 Verificações CRÍTICAS

### 1. **Fios A/B - INVERTER!**

**Tente inverter A e B** entre MAX485 e CLP:

```
TESTE 1 (atual):
MAX485 A → CLP A
MAX485 B → CLP B

TESTE 2 (inverter):
MAX485 A → CLP B  ← TROCAR!
MAX485 B → CLP A  ← TROCAR!
```

**IMPORTANTE:** Algumas conexões RS485 precisam A↔B e B↔A invertidos.

---

### 2. **Tensão GPIO4 (DE/RE)**

Com multímetro, medir GPIO4 do ESP32:

```
Esperado: 3.3V (HIGH fixo)
```

Se estiver 0V: MAX485 ficará em modo recepção e não transmitirá.

**Solução:** Verificar conexão GPIO4 → DE + RE (pinos 2 e 3 do MAX485 juntos)

---

### 3. **Alimentação MAX485**

Medir tensão VCC do MAX485:

```
Esperado: 3.3V ou 5V (conforme modelo)
```

**IMPORTANTE:** Alguns MAX485 precisam 5V, não funcionam com 3.3V.

**Teste:** Alimentar MAX485 com 5V externo (não do ESP32):
```
5V externo → MAX485 VCC
GND externo → MAX485 GND
```

---

### 4. **Continuidade dos fios**

Com multímetro em modo continuidade:

```
ESP32 GPIO17 ←→ MAX485 pino DI (deve haver continuidade)
ESP32 GPIO16 ←→ MAX485 pino RO (deve haver continuidade)
ESP32 GPIO4  ←→ MAX485 pino DE (deve haver continuidade)
ESP32 GPIO4  ←→ MAX485 pino RE (deve haver continuidade)

MAX485 A ←→ CLP RS485-B A (deve haver continuidade)
MAX485 B ←→ CLP RS485-B B (deve haver continuidade)
```

---

### 5. **GND comum**

**CRÍTICO:** ESP32 e CLP **DEVEM** ter GND comum:

```
ESP32 GND ←→ MAX485 GND ←→ CLP GND
```

Se não houver GND comum, comunicação não funciona.

---

### 6. **Baudrate CLP**

Verificar registro `1987H` (6535 dec) no CLP:

```
Valor esperado para 57600 baud: 0x0007
```

Se estiver diferente, CLP está em outro baudrate.

**Teste com outros baudrates:**

Edite `lib/umodbus/serial.py` linha ~32:

```python
# Teste 1: 9600 baud
baudrate=9600

# Teste 2: 19200 baud
baudrate=19200

# Teste 3: 38400 baud
baudrate=38400
```

---

### 7. **Parity e Stop Bits**

CLP pode estar configurado diferente:

**Teste 1:** 8N1 (None, 1 stop)
```python
ModbusRTU(..., parity=None, stop_bits=1)
```

**Teste 2:** 8E1 (Even, 1 stop)
```python
ModbusRTU(..., parity=0, stop_bits=1)  # 0=Even parity
```

**Teste 3:** 8O1 (Odd, 1 stop)
```python
ModbusRTU(..., parity=1, stop_bits=1)  # 1=Odd parity
```

---

### 8. **Estado 0x00BE no Ladder**

O bit `0x00BE` (190) **DEVE** estar forçado ON no ladder para habilitar Modbus slave.

**Como verificar:**
- Abra WinSUP
- Carregue `clp_MODIFICADO_IHM_WEB_COM_ROT5.sup`
- Procure por instrução `SET 0x00BE` ou `LD 1; OUT 0x00BE`
- Deve estar sempre ON (incondicional)

---

### 9. **Canal RS485 correto**

CLP Atos tem **2 canais RS485**:
- RS485-A (canal A)
- RS485-B (canal B) ← **Deve usar este!**

Verifique se está conectado no **RS485-B** (canal B), não no A.

---

### 10. **Resistor de terminação**

Para cabos > 1 metro, pode precisar resistor de terminação 120Ω:

```
         ESP32             CLP
           |               |
MAX485 ----+               +---- RS485-B
    A -----+----- 120Ω ----+---- A
    B -----+---------------+---- B
```

**Teste SEM resistor primeiro.** Só adicione se cabo for longo.

---

## 🔧 Teste Simplificado

### Loopback MAX485

**Teste se MAX485 está funcionando:**

1. Desconecte CLP
2. Curto-circuite A e B do MAX485:
   ```
   MAX485 A ←→ MAX485 B (juntar com jumper)
   ```
3. Execute teste:
   ```bash
   ampy --port /dev/ttyACM0 run test_modbus_debug.py
   ```

**Esperado:** Ainda vai dar timeout (não há slave respondendo)

**MAS:** Se aparecer dados lidos = problema está no lado CLP, não ESP32

---

## 📸 Foto da Conexão

**Tire uma foto clara mostrando:**
1. Pinos ESP32 (GPIO17/16/4)
2. MAX485 completo (todos os pinos)
3. Conexão até o CLP

Isso ajudará a identificar erro de fiação.

---

## ✅ Checklist Final

- [ ] Tentei inverter A/B
- [ ] GPIO4 está em 3.3V (medido com multímetro)
- [ ] MAX485 alimentado corretamente
- [ ] Continuidade OK em todos os fios
- [ ] GND comum ESP32/CLP
- [ ] Estado 0x00BE = ON verificado no ladder
- [ ] Conectado no RS485-B (canal B) do CLP
- [ ] CLP está ligado e rodando

Se **TUDO** estiver OK e ainda não funcionar:
- ❌ MAX485 pode estar queimado → trocar
- ❌ GPIO do ESP32 pode estar queimado → trocar ESP32
- ❌ Porta RS485 do CLP pode estar com defeito

---

**Próximo passo:** INVERTER A/B é o mais provável! 🔄
