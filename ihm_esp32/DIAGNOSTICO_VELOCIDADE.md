# DIAGNÓSTICO: Problema de Controle de Velocidade
**Data:** 05/Janeiro/2026
**Máquina:** NEOCOUDE-HD-15
**Sintoma:** Velocidade fixa em 15 RPM, não muda via IHM Web

---

## 📊 ANÁLISE DO CÓDIGO

### Fluxo de Controle de Velocidade (Conforme Implementado)

```
IHM Web (Tablet)
    ↓ (WebSocket: action='write_speed', speed=X)
main_server.py (linha 242-273)
    ↓ (Converte RPM → valor registro usando mm.rpm_to_register())
    ↓ (Escreve em 0x0A06 via Modbus FC 0x06)
CLP Atos MPC4004
    ↓ (Ladder DEVE copiar 0x0A06 → 0x06E0)
Saída Analógica 0x06E0
    ↓ (Sinal 0-10V proporcional ao RPM)
Inversor WEG CFW08
    ↓ (Converte tensão → frequência do motor)
Motor 15 HP
```

### Valores de Referência (modbus_map.py linhas 287-293)

| RPM | Valor Registro | Hexadecimal | Tensão Analógica (0-10V) |
|-----|----------------|-------------|---------------------------|
| 0   | 0              | 0x0000      | 0.00V                     |
| 5   | 527            | 0x020F      | 2.64V                     |
| 10  | 1055           | 0x041F      | 5.28V                     |
| 15  | 1583           | 0x062F      | 7.92V                     |
| 19  | 2000 (MAX)     | 0x07D0      | 10.00V                    |

**Fórmula:** `Tensão = (Valor / 2000) × 10V`

---

## 🔍 POSSÍVEIS CAUSAS (Em Ordem de Probabilidade)

### ⚠️ CAUSA 1: Ladder Não Implementado (MAIS PROVÁVEL)
**Sintoma:** IHM escreve em 0x0A06, mas valor não chega em 0x06E0

**O que está faltando:**
- O programa ladder (clp.sup) não tem lógica para copiar 0x0A06 → 0x06E0
- Esta cópia deve ser feita continuamente em cada scan do CLP

**Como verificar:**
```python
# Execute este script Python:
python3 -c "
from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

client = ModbusClientWrapper(stub_mode=False)

print('1. Escrevendo 1055 (10 RPM) em 0x0A06...')
client.write_register(0x0A06, 1055)
time.sleep(1)

print('2. Lendo 0x06E0 (saída analógica)...')
valor = client.read_register(0x06E0)
print(f'   Valor lido: {valor}')

if valor == 1055:
    print('   ✅ Ladder está copiando corretamente!')
elif valor == 1583:
    print('   ❌ Valor não mudou (ainda em 15 RPM = 1583)')
    print('   → PROBLEMA: Ladder NÃO está copiando 0x0A06 para 0x06E0')
else:
    print(f'   ⚠️ Valor inesperado: {valor}')

client.close()
"
```

**SOLUÇÃO se ladder não implementado:**
1. Abrir `clp.sup` no software de programação Atos
2. Adicionar rungs no início do programa principal:
   ```
   RUNG 1: MOV [0x0A06] → [0x06E0]
   ```
3. Fazer upload para o CLP
4. Testar novamente

**OU usar workaround no Python:**
Modificar `modbus_client.py` linha 939:
```python
# ANTES (linha atual):
return self.write_register(mm.RPM_REGISTERS['RPM_WRITE'], register_value)

# DEPOIS (escreve direto em 0x06E0):
return self.write_register(0x06E0, register_value)
```

---

### ⚙️ CAUSA 2: Problema na Saída Analógica (Fiação)
**Sintoma:** 0x06E0 muda no CLP, mas sinal não chega no inversor

**Como verificar:**
1. **Medir tensão no terminal analógico do CLP (saída 0x06E0):**
   - Localizar terminal da saída analógica no painel (verificar manual MPC4004 página 85)
   - Com multímetro, medir tensão DC entre terminal e GND
   - Testar 3 velocidades via IHM:
     - 5 RPM → deveria medir ~2.64V
     - 10 RPM → deveria medir ~5.28V
     - 15 RPM → deveria medir ~7.92V

2. **Se tensão NO CLP está correta:**
   → Problema é no cabo entre CLP e inversor!
   - Verificar cabo de sinal analógico (pode estar solto ou rompido)
   - Verificar conexão no inversor WEG (terminal AI1 ou AI2)

3. **Se tensão NO CLP está ERRADA ou não muda:**
   → Problema é no CLP (saída analógica danificada ou mal configurada)
   - Verificar configuração de escala da saída analógica (manual MPC4004 página 93-97)
   - Considerar usar outra saída analógica disponível

**Documentação de referência:**
- NEOCOUDE manual página 30: Parâmetros do inversor WEG
- Manual MPC4004 páginas 93-97: Configuração de saídas analógicas

---

### 🔧 CAUSA 3: Inversor WEG Configurado Errado
**Sintoma:** Sinal analógico chega no inversor, mas ele ignora

**Como verificar:**
1. **Acessar parâmetros do inversor WEG CFW08:**
   - Pressionar `PROG` no inversor
   - Navegar até grupo `P02xx` (parâmetros de entrada analógica)

2. **Verificar parâmetros críticos:**
   ```
   P201 = Seleção Entrada Analógica
          → Deve estar: 0 (AI1) ou 1 (AI2)
          → Se estiver: 2 (Keypad) → PROBLEMA! Está ignorando analógica

   P202 = Ganho Entrada Analógica
          → Deve estar: 100 (ganho 100%)

   P203 = Offset Entrada Analógica
          → Deve estar: 0 (sem offset)

   P204 = Função Entrada Analógica
          → Deve estar: 0 (Referência de velocidade)
   ```

3. **Verificar entrada sendo usada:**
   - Verificar onde o cabo vindo do CLP está conectado no inversor:
     - Terminal **AI1**: Entrada analógica 1 (0-10V)
     - Terminal **AI2**: Entrada analógica 2 (0-10V ou 4-20mA)
   - Garantir que P201 corresponde ao terminal usado

**SOLUÇÃO se inversor configurado errado:**
1. Alterar P201 para usar entrada analógica (AI1 ou AI2)
2. Verificar P202 = 100 (ganho total)
3. Verificar P204 = 0 (referência de velocidade)
4. Pressionar `SAVE` para salvar alterações
5. Testar mudança de velocidade via IHM

**Referência:** NEOCOUDE manual página 30 (parâmetros do inversor)

---

## 🛠️ TESTE RÁPIDO (Execute AGORA na fábrica)

Execute este comando no terminal do Raspberry Pi:

```bash
cd /home/lucas-junges/Documents/wco/ihm_esp32
python3 << 'EOF'
from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

print("\n" + "="*60)
print("TESTE RÁPIDO DE VELOCIDADE")
print("="*60)

client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

if not client.connected:
    print("❌ CLP não conectado!")
    exit(1)

print("\n1️⃣ Tentando mudar para 5 RPM...")
valor_5rpm = mm.rpm_to_register(5)  # 527
print(f"   Escrevendo {valor_5rpm} em 0x0A06...")
client.write_register(0x0A06, valor_5rpm)
time.sleep(2)

print("\n   Lendo 0x06E0 (saída analógica)...")
lido_5rpm = client.read_register(0x06E0)
print(f"   Valor lido: {lido_5rpm} (esperado: ~{valor_5rpm})")

print("\n2️⃣ Tentando mudar para 10 RPM...")
valor_10rpm = mm.rpm_to_register(10)  # 1055
print(f"   Escrevendo {valor_10rpm} em 0x0A06...")
client.write_register(0x0A06, valor_10rpm)
time.sleep(2)

print("\n   Lendo 0x06E0 (saída analógica)...")
lido_10rpm = client.read_register(0x06E0)
print(f"   Valor lido: {lido_10rpm} (esperado: ~{valor_10rpm})")

print("\n" + "="*60)
print("RESULTADO DO DIAGNÓSTICO:")
print("="*60)

if lido_5rpm is None or lido_10rpm is None:
    print("❌ PROBLEMA: Não consegue ler 0x06E0!")
    print("   Possível causa: Registro não existe ou erro de comunicação")
elif lido_5rpm == valor_5rpm and lido_10rpm == valor_10rpm:
    print("✅ Ladder está copiando corretamente!")
    print("   → Problema deve ser na fiação ou inversor")
    print("   → Medir tensão analógica no inversor com multímetro")
elif lido_5rpm == lido_10rpm:
    print(f"❌ PROBLEMA: 0x06E0 não muda (fixo em {lido_5rpm})")
    print("   → Ladder NÃO está copiando 0x0A06 para 0x06E0")
    print("   → SOLUÇÃO: Adicionar lógica de cópia no ladder")
else:
    print(f"⚠️ Comportamento inesperado:")
    print(f"   5 RPM: esperado {valor_5rpm}, lido {lido_5rpm}")
    print(f"   10 RPM: esperado {valor_10rpm}, lido {lido_10rpm}")

client.close()
print("\n✓ Teste concluído!")
EOF
```

---

## 📋 CHECKLIST DE DIAGNÓSTICO

- [ ] **Executar teste rápido acima** → Identificar se 0x06E0 muda
- [ ] **Se 0x06E0 NÃO muda:** Modificar ladder para copiar 0x0A06 → 0x06E0
- [ ] **Se 0x06E0 muda:** Medir tensão analógica com multímetro
  - [ ] Tensão no CLP (saída 0x06E0): ______ V @ 5 RPM, ______ V @ 10 RPM, ______ V @ 15 RPM
  - [ ] Tensão no inversor (AI1 ou AI2): ______ V @ 5 RPM, ______ V @ 10 RPM, ______ V @ 15 RPM
- [ ] **Se tensão OK no CLP mas não chega no inversor:** Verificar cabo
- [ ] **Se tensão OK no inversor mas não muda RPM:** Verificar parâmetros P201, P202, P204

---

## 💡 SOLUÇÃO RÁPIDA (Se ladder não implementado)

**Opção 1: Modificar Python (temporário)**
Editar `modbus_client.py` linha 939:
```python
def write_speed_class(self, rpm: int) -> bool:
    # ...
    register_value = mm.rpm_to_register(rpm)

    # WORKAROUND: Escreve direto em 0x06E0 (bypass 0x0A06)
    return self.write_register(0x06E0, register_value)
```

**Opção 2: Modificar Ladder (correto)**
1. Abrir `clp.sup` no software Atos
2. Adicionar no MAIN (principal):
   ```
   RUNG 10: MOV [0x0A06] → [0x06E0]  // Copia velocidade IHM → Inversor
   ```
3. Upload para CLP
4. Testar

---

## 📞 PRÓXIMOS PASSOS

1. **Execute o teste rápido acima AGORA**
2. **Anote os valores lidos de 0x06E0**
3. **Me avise o resultado** para eu poder ajudar mais!

Se 0x06E0 não mudar → Problema no ladder (solução fácil!)
Se 0x06E0 mudar → Problema na fiação ou inversor (verificar com multímetro)

---

**Gerado automaticamente por Claude Code**
**Eng. Lucas William Junges**
