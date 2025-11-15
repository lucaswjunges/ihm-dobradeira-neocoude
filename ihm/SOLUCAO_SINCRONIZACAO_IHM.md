# SOLUÇÃO: SINCRONIZAÇÃO IHM Web ↔ IHM Física ↔ CLP

**Data**: 15/Nov/2025 03:48 BRT  
**Status**: ✅ PROBLEMA IDENTIFICADO E SOLUÇÃO DEFINIDA

---

## 🔍 PROBLEMA IDENTIFICADO

### Área de Supervisão (0x0940-0x094E) está VAZIA

Leitura dos registros mostrou **VALORES INVÁLIDOS**:

```
SCREEN_NUM (0x0940):   (sem resposta)
MODE_STATE (0x0946):   22016  ← LIXO (deveria ser 0 ou 1)
BEND_CURRENT (0x0948): 0      ← pode estar correto
DIRECTION (0x094A):    0      ← pode estar correto  
SPEED_CLASS (0x094C):  0      ← ERRADO (deveria ser 5, 10 ou 15)
CYCLE_ACTIVE (0x094E): 1280   ← LIXO (deveria ser 0 ou 1)
```

**Root Cause**: A área 0x0940-0x094E **NÃO é populada pelo ladder**.  
Estes registros foram reservados para comunicação Python→IHM Web, mas o ladder ATOS original NÃO os atualiza.

---

## ✅ SOLUÇÃO: Ler Bits/Registros REAIS do Ladder

A IHM Web deve abandonar a área de supervisão e ler **diretamente os mesmos bits/registros que a IHM física lê**:

### 1. Modo MANUAL/AUTO
```
❌ ERRADO: Ler MODE_STATE (0x0946) - contém lixo
✅ CORRETO: Ler bit 0x02FF (767) - Coil
   - 0 = MANUAL
   - 1 = AUTO
```

**Teste**:
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -t 0 -r 767 -c 1 -1 /dev/ttyUSB0
# Resultado: [767]: 0  → MANUAL
```

---

### 2. Dobra Ativa (1, 2 ou 3)
```
❌ ERRADO: Ler BEND_CURRENT (0x0948)
✅ CORRETO: Ler LEDs K1, K2, K3 (Coils)
   - LED K1 (0x00C0 = 192): Dobra 1 ativa
   - LED K2 (0x00C1 = 193): Dobra 2 ativa
   - LED K3 (0x00C2 = 194): Dobra 3 ativa
```

**Teste**:
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -t 0 -r 192 -c 3 -1 /dev/ttyUSB0
# Resultado: 
# [192]: 0  (LED K1 OFF)
# [193]: 0  (LED K2 OFF)  
# [194]: 0  (LED K3 OFF)
```

---

### 3. Velocidade (5, 10 ou 15 RPM)
```
❌ ERRADO: Ler SPEED_CLASS (0x094C) - retorna 0
✅ CORRETO: Ler registro do inversor 0x0900 (2304)
   - Setpoint de velocidade em unidades internas do CLP
```

**Teste**:
```bash
mbpoll -a 1 -b 57600 -P none -s 2 -t 4 -r 2304 -c 1 -1 /dev/ttyUSB0
# Resultado: [2304]: 3072
```

**Conversão**: Precisa mapear unidades internas → RPM  
(Ver manual NEOCOUDE página 30 para fórmula)

---

### 4. Ângulos Programados
```
✅ JÁ CORRETO: Ler registros 32-bit (MSW+LSW)
   - Dobra 1 Esquerda: 0x0840 (MSW), 0x0842 (LSW)
   - Dobra 2 Esquerda: 0x0848 (MSW), 0x084A (LSW)
   - Dobra 3 Esquerda: 0x0850 (MSW), 0x0852 (LSW)
   (e assim por diante para direita)
```

**Fórmula**:
```python
value_32bit = (MSW << 16) | LSW
angle_degrees = value_32bit / 10.0
```

---

## 📝 MUDANÇAS NECESSÁRIAS

### `state_manager.py` - Polling Loop

**ANTES** (lendo área de supervisão):
```python
state['mode'] = self.modbus_client.read_register(0x0946)  # MODE_STATE
state['bend_current'] = self.modbus_client.read_register(0x0948)
state['speed'] = self.modbus_client.read_register(0x094C)
```

**DEPOIS** (lendo bits/registros reais):
```python
# Modo: bit real 0x02FF
state['mode'] = self.modbus_client.read_coil(0x02FF)  # 0=MANUAL, 1=AUTO

# Dobra: LEDs K1, K2, K3
led1 = self.modbus_client.read_coil(0x00C0)  # LED K1
led2 = self.modbus_client.read_coil(0x00C1)  # LED K2
led3 = self.modbus_client.read_coil(0x00C2)  # LED K3
state['bend_current'] = 1 if led1 else (2 if led2 else (3 if led3 else 0))

# Velocidade: registro do inversor
speed_raw = self.modbus_client.read_register(0x0900)
state['speed'] = self._convert_speed(speed_raw)  # Converter unidades → RPM
```

---

## 🎯 RESULTADO ESPERADO

Após as correções, a IHM Web estará **100% sincronizada** com a IHM física:

| Informação      | IHM Física lê       | IHM Web lerá (corrigido) |
|-----------------|---------------------|--------------------------|
| Modo AUTO/MANUAL| Bit interno 02FF    | ✅ Bit 0x02FF (via Modbus)|
| Dobra ativa     | LEDs K1/K2/K3       | ✅ Coils 0x00C0-0x00C2   |
| Velocidade      | Inversor (registro) | ✅ Registro 0x0900       |
| Ângulos         | Registros 32-bit    | ✅ JÁ CORRETO            |

---

## ⚠️ AÇÕES IMEDIATAS

1. **Modificar `state_manager.py`**:
   - Remover leituras da área 0x0940-0x094E
   - Implementar leituras dos bits/registros reais listados acima

2. **Atualizar `modbus_map.py`**:
   - Marcar `SUPERVISION_AREA` como DEPRECADO/NÃO USAR
   - Adicionar comentários apontando para os registros corretos

3. **Testar sincronização**:
   - Mudar modo via IHM física (se funcionar S1) ou via Python
   - Verificar se IHM Web reflete a mudança corretamente
   - Acionar LEDs K1/K2/K3 via ladder e verificar leitura

---

## 📚 REFERÊNCIAS

- **Bit de Modo**: Descoberto durante análise do ladder (bit 0x02FF)
- **LEDs**: Mapeados em `modbus_map.py` (0x00C0-0x00C4)
- **Inversor**: Manual NEOCOUDE página 30 (conversão velocidade)

---

**Conclusão**: A área de supervisão foi uma **FALSA PREMISSA**. A sincronização correta exige ler os mesmos bits/registros que a IHM física usa, que já estão documentados no ladder e manuais.
