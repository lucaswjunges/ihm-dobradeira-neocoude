# Resultado do Teste Modbus ESP32 ↔ CLP

## 🧪 Teste Executado

**Data:** 17/Novembro/2025
**Método:** Script Python via serial (REPL)

---

## ❌ Resultado: COMUNICAÇÃO MODBUS FALHOU

### Testes Realizados:

1. **Teste 1: Leitura Encoder (32-bit)**
   - Endereços: 1238 (MSW) + 1239 (LSW)
   - Resultado: `None` (sem resposta do CLP)
   - ❌ **FALHOU**

2. **Teste 2: Leitura Ângulo Dobra 1**
   - Endereço: 1280
   - Resultado: `None` (sem resposta do CLP)
   - ❌ **FALHOU**

3. **Teste 3: Leitura Entrada Digital E0**
   - Endereço: 256
   - Resultado: `None` (sem resposta do CLP)
   - ❌ **FALHOU**

---

## 🔍 Diagnóstico

### Configuração ESP32 (Confirmada):
✅ UART2 inicializado corretamente
✅ Baudrate: 57600
✅ GPIO17 (TX), GPIO16 (RX), GPIO4 (DE/RE)
✅ Slave ID: 1

### Problema Identificado:

**CLP NÃO ESTÁ RESPONDENDO** às requisições Modbus RTU.

---

## 🛠️ Possíveis Causas

### 1. **State 00BE (190) = OFF no CLP** ⚠️ MAIS PROVÁVEL
   - Este state **DEVE estar ON** para habilitar modo slave Modbus
   - Se estiver OFF, CLP ignora todas as requisições Modbus

   **Como verificar:**
   - Conectar no CLP via software de programação
   - Procurar state `00BE` (hex) ou `190` (decimal)
   - **Forçar ON** manualmente ou via ladder

---

### 2. **Fiação RS485 Invertida**
   - A e B podem estar trocados

   **Como verificar:**
   ```
   CLP lado:       MAX485 lado:
   A (positivo) ─→ A (não B!)
   B (negativo) ─→ B (não A!)
   GND          ─→ GND
   ```

   **Teste:**
   - Inverter A ↔ B e testar novamente

---

### 3. **Slave ID Errado**
   - ESP32 está tentando ID = 1
   - CLP pode estar configurado com outro ID

   **Como verificar:**
   - Ler registro `1988H` (6536 decimal) do CLP
   - Este registro armazena o Slave ID
   - Valores típicos: 1-10

   **Teste:**
   - Editar `main.py` linha 22:
   ```python
   SLAVE_ID = 2  # Testar 2, 3, 4, etc.
   ```

---

### 4. **Baudrate Incorreto**
   - ESP32 está usando 57600
   - CLP pode estar configurado diferente

   **Como verificar:**
   - Ler registro `1987H` (6535 decimal) do CLP
   - Valores possíveis: 9600, 19200, 38400, 57600, 115200

   **Teste:**
   - Editar `modbus_client_esp32.py` linha 32:
   ```python
   self.client = ModbusRTU(uart_id=2, baudrate=19200, ...)
   ```

---

### 5. **MAX485 Sem Alimentação ou Defeituoso**

   **Como verificar:**
   - Medir tensão no pino VCC do MAX485
   - Deve ser exatos 3.3V ou 5.0V (dependendo do módulo)

   **Sinais de problema:**
   - VCC = 0V → Sem alimentação
   - VCC < 2.5V → Tensão insuficiente
   - VCC > 5.5V → Módulo pode estar queimado

---

### 6. **CLP Desligado ou em Modo Master**

   **Como verificar:**
   - LED de RUN do CLP aceso?
   - CLP está executando o ladder?
   - State `03D0` (976 decimal) = OFF? (modo master deve estar desligado)

---

## 📋 Checklist de Verificação

Use este checklist para diagnosticar:

- [ ] **CLP está ligado** (24V alimentação OK)
- [ ] **State 00BE = ON** no ladder (verificar via software de programação)
- [ ] **State 03D0 = OFF** no ladder (modo master desligado)
- [ ] **MAX485 alimentado** (medir VCC = 3.3V ou 5.0V)
- [ ] **Fiação RS485:**
  - [ ] A conectado em A (não invertido)
  - [ ] B conectado em B (não invertido)
  - [ ] GND comum entre ESP32, MAX485 e CLP
- [ ] **GPIO ESP32:**
  - [ ] GPIO17 → MAX485 DI
  - [ ] GPIO16 → MAX485 RO
  - [ ] GPIO4 → MAX485 DE + RE (jumpeados)
- [ ] **Slave ID correto** (ler registro 1988H = 6536 do CLP)
- [ ] **Baudrate correto** (ler registro 1987H = 6535 do CLP)

---

## 🔧 Próximos Passos Recomendados

### **Passo 1: Verificar State 00BE no CLP** ⭐ PRIORITÁRIO

1. Conectar no CLP via software de programação Atos
2. Ir em modo "Monitor" ou "Online"
3. Procurar state `00BE` (hex) ou `190` (decimal)
4. Se estiver OFF → **Forçar ON**
5. Salvar mudança no ladder

**Sem este state ON, NADA vai funcionar!**

---

### **Passo 2: Testar Fiação (se state 00BE já estiver ON)**

1. Desconectar fios A e B do MAX485
2. Inverter: A ↔ B
3. Reconectar
4. Executar teste novamente (usar `COMANDO_TESTE_RAPIDO.txt`)

---

### **Passo 3: Tentar Outros Slave IDs**

Editar `main.py` linha 22 e testar IDs de 1 a 10:

```python
# Testar um por vez
SLAVE_ID = 1  # Teste 1
# Fazer upload
# Testar

SLAVE_ID = 2  # Teste 2
# Fazer upload
# Testar
```

---

### **Passo 4: Tentar Outros Baudrates**

Editar `modbus_client_esp32.py` linha 32:

```python
# Testar um por vez
self.client = ModbusRTU(uart_id=2, baudrate=9600, ...)   # Teste 1
self.client = ModbusRTU(uart_id=2, baudrate=19200, ...)  # Teste 2
self.client = ModbusRTU(uart_id=2, baudrate=38400, ...)  # Teste 3
self.client = ModbusRTU(uart_id=2, baudrate=57600, ...)  # Teste 4 (atual)
```

---

## 🎯 Como Saber se Funcionou

Quando a comunicação Modbus estiver OK, você verá:

**Via Interface Web:**
- `http://192.168.0.106`
- **"CLP ✓"** em VERDE (canto superior direito)
- Encoder atualizando em tempo real
- Ângulos sendo lidos/escritos

**Via Teste Manual (Thonny):**
```python
>>> result = modbus.read_holding_registers(1, 1238, 2)
>>> print(result)
[0, 360]  # ✓ SUCESSO! (em vez de None)
```

**Via Logs ESP32:**
```
✓ Leitura OK:
  MSW: 0, LSW: 360
  Encoder: 36.0°
```

---

## 🆘 Se Nada Funcionar

### Teste com Ferramenta Externa (PC)

Use `mbpoll` no notebook conectado via USB-RS485:

```bash
# Instalar mbpoll
sudo apt install mbpoll

# Testar leitura (holding registers, slave 1, endereço 1238, quantidade 2)
mbpoll -a 1 -r 1238 -c 2 -t 4 -b 57600 /dev/ttyUSB0

# Se retornar valores → CLP OK, problema no ESP32
# Se retornar timeout → Problema no CLP ou fiação
```

---

## 📊 Status Atual

| Componente | Status |
|------------|--------|
| ESP32 Modbus Init | ✅ OK |
| UART2 Config | ✅ OK |
| Baudrate | ✅ 57600 |
| Slave ID | ✅ 1 |
| **Comunicação CLP** | ❌ **FALHOU** |
| Possível causa | ⚠️ State 00BE = OFF |

---

**Desenvolvido por:** Eng. Lucas William Junges
**Data:** 17/Novembro/2025
**Versão:** 1.0-ESP32-MODBUS-DIAGNOSTIC
