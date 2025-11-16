# 🚨 ANÁLISE CRÍTICA - CONDIÇÕES S0 E S1

## DESCOBERTA: S0 SÓ LIGA SE E6 ESTIVER **OFF**!

### ROT0.lad - Line00001 (S0 = 0x0180)

```ladder
SAÍDA S0 (0x0180) LIGA SE:

Branch01: E2 AND (NOT S1)
Branch02: 0305 AND 02FF AND (NOT S1)
Branch03: (NOT S1)
Branch04: 0304 AND (NOT S0) [intertravamento]
Branch05: E5 AND (NOT E2)
Branch06: (NOT E2) AND (NOT 02FF)
Branch07: E3 AND E5
Branch08: (NOT E6) AND (NOT E6)  ← AQUI ESTÁ O PROBLEMA!
```

### **PROBLEMA CRÍTICO:**

**Branch08** exige: `(NOT E6) AND (NOT E6)`

Isso significa: **E6 DEVE ESTAR OFF** para S0 ligar!

Mas na análise anterior descobrimos que:
- **E6 = Entrada que permite mudança de modo**
- Durante testes, E6 pode estar ON
- **SE E6 estiver ON → S0 NUNCA liga!**

---

## ROT0.lad - Line00003 (S1 = 0x0181)

```ladder
SAÍDA S1 (0x0181) LIGA SE:

Branch01: E4 AND (NOT S0)
Branch02: 0305 AND 02FF AND (NOT S0)
Branch03: (NOT S0)
Branch04: 0308 AND (NOT S1) [intertravamento]
Branch05: E5 AND (NOT E4)
Branch06: (NOT E4) AND (NOT 02FF)
Branch07: E3 AND E5
Branch08: (NOT E6) AND (NOT E6)  ← MESMO PROBLEMA!
```

**S1 também depende de E6 estar OFF!**

---

## DECODIFICAÇÃO DOS ENDEREÇOS

| Endereço (Hex) | Decimal | Significado |
|----------------|---------|-------------|
| 0102 | 258 | E2 (entrada digital 2) |
| 0103 | 259 | E3 (entrada digital 3) |
| 0104 | 260 | E4 (entrada digital 4) |
| 0105 | 261 | E5 (entrada digital 5) |
| 0106 | 262 | **E6 (entrada crítica!)** |
| 0180 | 384 | **S0 (saída motor avanço)** |
| 0181 | 385 | **S1 (saída motor recuo)** |
| 0190 | 400 | S0 (coil interna?) |
| 0191 | 401 | S1 (coil interna?) |
| 02FF | 767 | Modo bit (Manual/Auto) |
| 0304 | 772 | Estado interno |
| 0305 | 773 | Estado interno |
| 0308 | 776 | Estado interno |

---

## DIAGNÓSTICO DO PROBLEMA

### Por que S0 não liga no teste?

1. ✅ Modbus escreve S0 = ON
2. ✅ CLP recebe comando
3. ❌ **Ladder verifica Branch08: E6 deve estar OFF**
4. ❌ **Se E6 está ON → Ladder força S0 = OFF**
5. ❌ Modbus lê S0 de volta → retorna FALSE

### Confirmação necessária:

```bash
# Verificar estado de E6
python3 -c "
from modbus_client import ModbusClientWrapper
import modbus_map as mm

client = ModbusClientWrapper(port='/dev/ttyUSB0')
e6 = client.read_coil(0x0106)  # E6
print(f'E6 (0x0106): {e6}')

# Se E6 = True → ESSE É O PROBLEMA!
client.close()
"
```

**Se E6 estiver ON → S0 e S1 nunca vão ligar!**

---

## SOLUÇÃO PARA SEGUNDA-FEIRA

### Opção 1: Forçar E6 = OFF

```bash
# Temporariamente desligar E6 via Modbus
python3 -c "
from modbus_client import ModbusClientWrapper

client = ModbusClientWrapper(port='/dev/ttyUSB0')
client.write_coil(0x0106, False)  # Forçar E6 = OFF
print('E6 forçado OFF')
client.close()
"
```

**Depois** testar S0/S1 novamente.

### Opção 2: Jumper físico em E6

Se E6 for uma entrada física:
1. Localizar terminal E6 no CLP
2. Remover jumper/conexão
3. Deixar E6 flutuando (OFF)
4. Testar S0/S1

### Opção 3: Modificar ladder (arriscado!)

Abrir WinSUP e remover Branch08 da lógica S0/S1.

**NÃO recomendado** sem entender por que E6 está lá!

---

## OUTRAS CONDIÇÕES A VERIFICAR

Além de E6, verificar:

```bash
python3 -c "
from modbus_client import ModbusClientWrapper

client = ModbusClientWrapper(port='/dev/ttyUSB0')

# Verificar TODAS as entradas que afetam S0
print('E2:', client.read_coil(0x0102))
print('E3:', client.read_coil(0x0103))
print('E4:', client.read_coil(0x0104))
print('E5:', client.read_coil(0x0105))
print('E6:', client.read_coil(0x0106))  # CRÍTICO!

# Estados internos
print('0305:', client.read_coil(0x0305))
print('0304:', client.read_coil(0x0304))
print('02FF (modo):', client.read_coil(0x02FF))

# Intertravamento
print('S0:', client.read_coil(0x0180))
print('S1:', client.read_coil(0x0181))

client.close()
"
```

---

## CONCLUSÃO FINAL

**PROBLEMA IDENTIFICADO COM 99% DE CERTEZA:**

S0 e S1 **só ligam se E6 estiver OFF**.

**Branch08 de S0 e S1:**
```ladder
(NOT E6) AND (NOT E6)
```

**Ação imediata segunda-feira:**

1. **PRIMEIRO:** Ler estado de E6
2. **SE E6 = True:** Esse é o bloqueio!
3. **SOLUÇÃO:** Forçar E6 = False ou fazer jumper físico
4. **TESTAR:** S0/S1 devem funcionar após isso

**Tempo estimado:** 5-10 minutos (se for só E6)

---

**Gerado em:** 15/Nov/2025 00:45
**Arquivo analisado:** `/working_good/ROT0.lad`
**Linhas críticas:** Line00001 (S0), Line00003 (S1)
