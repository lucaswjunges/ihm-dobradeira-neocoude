# Diagnóstico Completo - Comunicação Modbus ESP32 ↔ CLP

## ✅ Correções Aplicadas

### 1. **STOP BITS Corrigido** ⭐ IMPORTANTE
- **Antes:** `stop_bits=1` (padrão)
- **Depois:** `stop_bits=2` (conforme CLP Atos)
- **Configuração atual:** `57600, 8N2` (57600 baud, 8 data bits, NO parity, 2 stop bits)

### 2. **Código Sem Erros**
- ✅ Erro `SPEED_CONTROL` corrigido
- ✅ Servidor HTTP estável
- ✅ ESP32 respondendo em `192.168.0.106`

### 3. **Testes de Fiação**
- ✅ A/B testado em AMBAS posições
  - Posição 1 (original): `connected: false`
  - Posição 2 (invertido): `connected: false`
  - Posição 1 (volta): `connected: false`

---

## ❌ Resultado Atual

**API continua retornando:**
```json
{
    "connected": false,  // CLP não responde
    "encoder_angle": 11.9,
    "bend_1_angle": 0.4,
    "bend_2_angle": 281.8,
    "bend_3_angle": 1748.9
}
```

**Mesmo após:**
- ✅ Corrigir stop_bits para 2
- ✅ Testar ambas posições A/B
- ✅ Confirmar state 00BE = ON

---

## 🔌 Configuração de Fiação Correta

### ESP32 → MAX485:
```
ESP32          MAX485
GPIO17 (TX) → DI (Data Input)
GPIO16 (RX) → RO (Receiver Output)
GPIO4       → DE + RE (jumpeados juntos)
3.3V        → VCC
GND         → GND
```

### MAX485 → CLP:
```
MAX485      CLP Atos
A      →    RS485-A (positivo)
B      →    RS485-B (negativo)
GND    →    GND comum
```

---

## 🔍 Próximas Verificações Necessárias

### 1. **Alimentação MAX485** ⚠️ CRÍTICO

Medir com multímetro:
- **VCC do MAX485:** Deve ser exatos **3.3V** ou **5.0V**
  - Se 0V → Sem alimentação
  - Se < 2.5V → Insuficiente
  - Se > 5.5V → MAX485 pode estar queimado

**Como testar:**
```bash
# Ponta vermelha: VCC do MAX485
# Ponta preta: GND
# Deve ler: 3.3V ou 5.0V
```

---

### 2. **Continuidade dos Fios** ⚠️ IMPORTANTE

Testar com multímetro (modo continuidade/beep):

**Teste A:**
- Ponta 1: GPIO17 do ESP32
- Ponta 2: Pino DI do MAX485
- **Deve:** Beepar (continuidade OK)

**Teste B:**
- Ponta 1: GPIO16 do ESP32
- Ponta 2: Pino RO do MAX485
- **Deve:** Beepar

**Teste C:**
- Ponta 1: GPIO4 do ESP32
- Ponta 2: Pinos DE+RE do MAX485 (jumpeados)
- **Deve:** Beepar

**Teste D:**
- Ponta 1: GND do ESP32
- Ponta 2: GND do MAX485
- **Deve:** Beepar

**Teste E:**
- Ponta 1: Pino A do MAX485
- Ponta 2: Terminal RS485-A do CLP
- **Deve:** Beepar

**Teste F:**
- Ponta 1: Pino B do MAX485
- Ponta 2: Terminal RS485-B do CLP
- **Deve:** Beepar

---

### 3. **Tensão nos Pinos do ESP32**

Medir com multímetro (modo voltímetro DC):

**GPIO17 (TX) - Idle:**
- **Deve:** ~3.3V (HIGH quando idle)
- Se 0V → Problema no ESP32 ou conexão

**GPIO16 (RX):**
- **Deve:** Variar (recebendo dados)
- Se sempre 0V ou 3.3V fixo → Sem dados do MAX485

**GPIO4 (DE/RE):**
- **Deve:** 0V (modo RX idle)
- Se 3.3V constante → Travado em modo TX

---

### 4. **Barramento RS485 (A/B do CLP)**

Medir diferencial entre A e B:

**Com CLP ligado e idle:**
- Ponta +: Terminal A do CLP
- Ponta -: Terminal B do CLP
- **Deve:** Cerca de +2V a +5V (polarização do barramento)
- Se 0V → CLP não está transmitindo/polarizando o barramento

**Nota:** Essa medida DEVE ser feita com CLP LIGADO!

---

### 5. **Slave ID e Baudrate do CLP**

**Via software Atos:**
- Ler registro `1988H` (6536 decimal) → Slave ID
  - ESP32 está tentando ID=1
  - Se CLP tiver outro ID, não vai responder

- Ler registro `1987H` (6535 decimal) → Baudrate
  - ESP32 está usando 57600
  - Valores possíveis: 9600, 19200, 38400, 57600, 115200

---

## 🧪 Teste Alternativo: mbpoll via PC

Conectar USB-RS485 no notebook e testar diretamente:

```bash
# Instalar mbpoll
sudo apt install mbpoll

# Testar leitura do encoder
mbpoll -a 1 -r 1238 -c 2 -t 4 -b 57600 -P none -s 2 /dev/ttyUSB0
#      ↑    ↑      ↑     ↑    ↑         ↑       ↑
#      |    |      |     |    |         |       +- Stop bits = 2
#   Slave  Reg   Qtd  Tipo Baud    No parity
```

**Resultado esperado:**
```
[1238]:  0
[1239]:  360
```

**Se funcionar do PC:**
- Problema está no ESP32 ou MAX485

**Se não funcionar do PC:**
- Problema no CLP ou cabo RS485

---

## 📊 Checklist de Verificação

### Hardware ESP32:
- [x] GPIO17, 16, 4 configurados
- [x] UART2 inicializado
- [x] Baudrate 57600
- [x] Stop bits 2 ✓ CORRIGIDO
- [x] Parity None
- [ ] **Tensão GPIO17 = 3.3V** (verificar com multímetro)
- [ ] **Tensão GPIO4 = 0V idle** (verificar)

### Hardware MAX485:
- [ ] **VCC = 3.3V ou 5.0V** (MEDIR!)
- [ ] **GND comum** com ESP32
- [ ] DE + RE jumpeados
- [ ] Continuidade DI ← GPIO17
- [ ] Continuidade RO → GPIO16
- [ ] Continuidade DE/RE ← GPIO4

### Hardware CLP:
- [x] State 00BE = ON (confirmado)
- [ ] **Tensão diferencial A-B = +2V a +5V** (MEDIR!)
- [ ] Slave ID = 1 (verificar no software)
- [ ] Baudrate = 57600 (verificar no software)
- [ ] Stop bits = 2 (verificar no software)

### Cabo RS485:
- [ ] Continuidade A do MAX485 → A do CLP
- [ ] Continuidade B do MAX485 → B do CLP
- [ ] Continuidade GND MAX485 → GND CLP
- [ ] Cabo blindado (opcional mas recomendado)
- [ ] Comprimento < 10m (para evitar atenuação)

---

## 🎯 Ação Prioritária

### **MEDIR TENSÃO NO MAX485** ⭐⭐⭐

Essa é a verificação mais importante!

**Com multímetro:**
1. Ponta vermelha: VCC do MAX485
2. Ponta preta: GND do MAX485
3. **Resultado esperado:** 3.3V ou 5.0V

**Se VCC = 0V ou < 2.5V:**
- MAX485 não está alimentado corretamente
- **Solução:** Verificar conexão 3.3V do ESP32 → VCC do MAX485

**Se VCC > 5.5V:**
- MAX485 pode estar queimado
- **Solução:** Substituir MAX485

---

## 📝 Resumo

**Tudo feito no ESP32:**
- ✅ Código correto
- ✅ Configuração UART correta (57600, 8N2)
- ✅ Pinos GPIO corretos (17/16/4)

**Próximo passo:**
- ⚠️ Verificar HARDWARE (tensões, continuidade, MAX485)
- ⚠️ Confirmar configuração do CLP (Slave ID, baudrate)

**Se tudo acima estiver OK e ainda não funcionar:**
- Problema pode ser no cabo RS485 (mau contato, inversão interna)
- Ou problema no transceiver RS485 do próprio CLP

---

**Data:** 17/Novembro/2025
**Versão:** FINAL-DIAGNOSTICO-HARDWARE
