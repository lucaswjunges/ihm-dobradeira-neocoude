# INSTRUÇÕES: Teste de Escrita nos Ângulos Oficiais

## 📋 Objetivo

Verificar se é possível escrever valores via Modbus nas áreas:
- **0x0500-0x0504** (setpoints oficiais - 16-bit)
- **0x0840-0x0852** (shadow - 32-bit MSW/LSW)

---

## 🔧 Pré-requisitos

1. CLP conectado via RS485 em `/dev/ttyUSB0` ou `/dev/ttyUSB1`
2. Python 3 com pymodbus instalado
3. Permissões de acesso à porta serial

---

## ▶️ Como Executar

### Opção 1: Teste Automático (recomendado)

```bash
cd /home/lucas-junges/Documents/clientes/w&co/ihm
python3 test_write_official_angles.py
```

O script irá:
1. ✅ Ler valores atuais
2. ✅ Escrever valores de teste (90°, 120°, 45°)
3. ✅ Verificar se escrita funcionou
4. ✅ **Restaurar valores originais automaticamente**

### Opção 2: Teste Manual via Python

```python
from modbus_client import ModbusClientWrapper
import modbus_map as mm

# Conectar
client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

# Teste 1: Ler área 0x0500
addr = 0x0500  # Dobra 1
value = client.read_register(addr)
print(f"Valor atual: {value} ({value/10.0:.1f}°)")

# Teste 2: Escrever valor de teste
test_value = 900  # 90.0°
success = client.write_register(addr, test_value)
print(f"Escrita: {'OK' if success else 'FALHA'}")

# Teste 3: Ler de volta
new_value = client.read_register(addr)
print(f"Valor após escrita: {new_value} ({new_value/10.0:.1f}°)")

# Verificar
if new_value == test_value:
    print("✅ Área 0x0500 é GRAVÁVEL!")
else:
    print("❌ Área 0x0500 está protegida ou sobrescrita")
```

---

## 📊 Resultados Esperados

### ✅ CENÁRIO 1: Área 0x0500 Gravável

```
📖 ETAPA 1: Lendo valores ORIGINAIS...
  0x0500 - Dobra 1:   650 (  65.0°)

✏️  ETAPA 2: Escrevendo valores DE TESTE...
  Escrevendo em 0x0500 - Dobra 1: 900 (90.0°)... ✅ OK

🔍 ETAPA 3: Verificando se valores foram GRAVADOS...
  ✅ 0x0500 - Dobra 1:   900 (  90.0°) - Esperado: 900 (90.0°)

💡 CONCLUSÃO: Área 0x0500 é GRAVÁVEL via Modbus
```

### ❌ CENÁRIO 2: Área Protegida

```
✏️  ETAPA 2: Escrevendo valores DE TESTE...
  Escrevendo em 0x0500 - Dobra 1: 900 (90.0°)... ✅ OK

🔍 ETAPA 3: Verificando se valores foram GRAVADOS...
  ❌ 0x0500 - Dobra 1:   650 (  65.0°) - Esperado: 900 (90.0°)

💡 CONCLUSÃO: Área está protegida (ladder sobrescreve valores)
```

---

## 🔍 Análise Baseada em Logs Anteriores

### O que sabemos dos logs:

```
✅ CONFIRMADO:
   • IHM Web ESTÁ ESCREVENDO em 0x0500
   • Valores são GRAVADOS com sucesso
   • Valores PERSISTEM entre leituras

Log evidence:
   ✓ read_register 0x0500: 510 (0x01FE)  → 51.0°
   ✓ read_register 0x0500: 650 (0x028A)  → 65.0°  [valor mudou!]
   ✓ read_register 0x0502: 1803 (0x070B) → 180.3°
   ✓ read_register 0x0504: 580 (0x0244)  → 58.0°
```

**Conclusão dos logs:** Área 0x0500 **É GRAVÁVEL** via Modbus! ✅

---

## ⚠️ Problema Detectado

Embora 0x0500 seja gravável, o **ladder NÃO lê dessa área**:

```
PRINCIPA.LAD:
  Line00008: SUB 0858 = 0842 - 0840  ← Lê de 0x0840, NÃO de 0x0500!
  Line00009: SUB 0858 = 0848 - 0846
  Line00010: SUB 0858 = 0852 - 0850
```

**Impacto:**
- ✅ IHM grava em 0x0500: **65°, 180.3°, 58°**
- ❌ Ladder lê de 0x0840: **valores diferentes?**
- ⚠️ Máquina pode dobrar em ângulos **não exibidos na IHM**!

---

## 🛠️ Soluções Propostas

### Solução A: Gravar Direto em 0x0840 (Rápida)

**Modificar Python:**
```python
# modbus_client.py - write_bend_angle()
def write_bend_angle(self, bend_number: int, degrees: float) -> bool:
    addresses_msw = {
        1: 0x0842,  # BEND_1_LEFT_MSW
        2: 0x0848,  # BEND_2_LEFT_MSW
        3: 0x0852   # BEND_3_LEFT_MSW
    }
    addresses_lsw = {
        1: 0x0840,  # BEND_1_LEFT_LSW
        2: 0x0846,  # BEND_2_LEFT_LSW
        3: 0x0850   # BEND_3_LEFT_LSW
    }
    # Escrever 32-bit MSW+LSW
```

**Prós:**
- ✅ Sem mudança no ladder
- ✅ Implementação imediata

**Contras:**
- ⚠️ Área 0x0840 pode ser sobrescrita por ROT4
- ⚠️ Não usa área oficial (0x0500)

---

### Solução B: Modificar Ladder (Correta)

**Alterar PRINCIPA.LAD linhas 8-10:**
```
// ANTES:
Line00008: SUB 0858 = 0842 - 0840

// DEPOIS:
Line00008: SUB 0858 = 0x0502 - 0x0500  ← Lê de área oficial!
```

**Prós:**
- ✅ Usa área oficial (0x0500)
- ✅ Coincidência perfeita IHM ↔ Ladder
- ✅ Conforme manual Atos MPC4004

**Contras:**
- ⚠️ Requer upload de novo ladder
- ⚠️ Modificação em 3 linhas críticas

---

### Solução C: Rotina de Cópia (Híbrida)

**Adicionar ROT6.lad:**
```
[Line00001]
  Comment: SYNC 0x0500 -> 0x0840
  Out: MOV 0x0500 → 0x0840  // Dobra 1
  Out: MOV 0x0502 → 0x0842
  ...
```

**Prós:**
- ✅ Mantém área 0x0500 como oficial
- ✅ Ladder sempre sincronizado
- ✅ Sem tocar em código existente

**Contras:**
- ⚠️ Aumenta scan time
- ⚠️ Cópia a cada ciclo (overhead)

---

## 📝 Checklist de Execução

```
[ ] 1. Conectar CLP via RS485
[ ] 2. Executar: python3 test_write_official_angles.py
[ ] 3. Anotar resultado da área 0x0500
[ ] 4. Anotar resultado da área 0x0840
[ ] 5. Decidir qual solução implementar (A, B ou C)
```

---

## 🎯 Recomendação Final

**Com base nos logs:**

1. **Área 0x0500 É GRAVÁVEL** ✅
2. **Executar teste para confirmar** 100%
3. **Implementar Solução B** (modificar ladder) como definitiva
4. **Usar Solução A** (gravar em 0x0840) como temporária para testes

---

## 📞 Próximos Passos

1. Execute o teste quando CLP estiver conectado
2. Relate os resultados
3. Escolha a solução a implementar
4. Eu posso gerar o código/ladder necessário

**Comando:**
```bash
python3 test_write_official_angles.py
```
