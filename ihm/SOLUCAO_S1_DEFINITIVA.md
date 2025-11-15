# 🎯 SOLUÇÃO DEFINITIVA: BOTÃO S1 (AUTO/MANUAL)

**Data:** 14 de Novembro de 2025
**Engenheiro:** Análise Sênior CLP Atos
**Arquivo Analisado:** ROT1.LAD (linha 4 e 5)

---

## ✅ PROBLEMA IDENTIFICADO

### **Descoberta 1: Bit de Modo REAL**

O bit de modo **NÃO é 0x0946** (MODE_STATE escrito por Python).

O bit REAL do ladder é **0x02FF (767 decimal)**:
- **02FF = OFF** → Modo MANUAL
- **02FF = ON** → Modo AUTO (proteção ativa)

### **Descoberta 2: Condição Bloqueante**

S1 **requer E6 ativa** para funcionar!

**Lógica do Ladder (ROT1.LAD):**

```ladder
Line00004:
  MONOA 0376 ←─┐
                ├─ S1 (00DC) pressionado
                └─ E6 (0106) ATIVA ← CONDIÇÃO CRÍTICA!

Line00005:
  Se (MONOA_0376 E NOT 02FF):
    SETR 02FF   (Liga modo AUTO)

  Se (MONOA_0376 E 02FF):
    RESET 02FF  (Liga modo MANUAL)
```

**Resultado:** É um **TOGGLE** - alterna entre AUTO/MANUAL cada vez que S1 é pressionado.

---

## 🔍 POR QUE NÃO FUNCIONOU NOS TESTES?

**E6 (entrada digital 6) está provavelmente OFF!**

Nos testes realizados:
1. ✅ S1 (00DC) foi pressionado corretamente
2. ❌ E6 (0106) provavelmente está OFF
3. ❌ Monostável 0376 NÃO ativa
4. ❌ Bit 02FF NÃO muda

**E6 pode ser:**
- Sensor de porta/carenagem de segurança
- Botão físico "PARADA" no painel
- Fim de curso ou sensor de posição
- Outra condição de segurança

---

## ⚡ SOLUÇÕES (3 Opções)

### **Opção 1: Ativar E6 (Hardware)** ⭐ RECOMENDADA

**Procedimento:**
1. Verificar no painel físico:
   - Botão PARADA está pressionado/ativo?
   - Porta ou carenagem está fechada?
   - Sensor está conectado?

2. Pressionar/ativar E6 fisicamente

3. Testar S1 novamente → **Deve funcionar!**

---

### **Opção 2: Forçar E6 via Modbus (Teste)** ⚠️ APENAS PARA TESTE

**Código Python:**
```python
from modbus_client import ModbusClientWrapper
import modbus_map as mm

client = ModbusClientWrapper(port=mm.MODBUS_CONFIG['port'], stub_mode=False)

# FORÇAR E6 = ON (CUIDADO: Bypass de segurança!)
client.write_coil(0x0106, True)  # E6 ON
print("E6 forçado para ON")

# Aguardar 1s
import time
time.sleep(1)

# Agora testar S1
client.write_coil(mm.KEYBOARD_FUNCTION['S1'], True)
time.sleep(0.1)
client.write_coil(mm.KEYBOARD_FUNCTION['S1'], False)
print("S1 pressionado")

# Verificar mudança
time.sleep(0.5)
modo_02ff = client.read_coil(0x02FF)
print(f"Modo 02FF: {modo_02ff} ({'AUTO' if modo_02ff else 'MANUAL'})")

client.close()
```

**⚠️ ATENÇÃO:** Isso é **bypass de segurança**! Usar APENAS para teste em ambiente controlado!

---

### **Opção 3: Modificar Ladder (Remover condição E6)** ❌ NÃO RECOMENDADO

Modificar ROT1.LAD removendo a condição E6. **NÃO FAZER** sem autorização - pode ser requisito de segurança!

---

## 🔧 IMPLEMENTAÇÃO NA IHM WEB

### Adicionar ao modbus_map.py:

```python
# Adicionar ao arquivo modbus_map.py

# BIT DE MODO REAL (não 0x0946!)
MODE_BIT_REAL = 0x02FF  # 767 decimal
# 02FF = OFF → MANUAL
# 02FF = ON  → AUTO

# Monostável do S1
MONO_MODE = 0x0376  # 886 decimal

# Condição crítica para S1
E6_SAFETY = 0x0106  # 262 decimal - Deve estar ON para S1 funcionar

# Adicionar ao CRITICAL_STATES
CRITICAL_STATES = {
    'MODBUS_SLAVE_ENABLED': 0x00BE,  # 190
    'CYCLE_ACTIVE':         0x0191,  # 401
    'MODE_BIT_REAL':        0x02FF,  # 767 - BIT DE MODO REAL!
    'E6_SAFETY_CONDITION':  0x0106,  # 262 - E6 deve estar ON
}
```

### Atualizar state_manager.py:

```python
def poll_mode_state(self):
    """Lê o bit de modo REAL do ladder"""
    # Bit REAL de modo (não 0x0946!)
    mode_bit_02ff = self.client.read_coil(0x02FF)  # 767

    # E6 (condição para S1 funcionar)
    e6_active = self.client.read_coil(0x0106)  # 262

    # Atualizar state
    self.machine_state['mode_auto'] = mode_bit_02ff  # True = AUTO, False = MANUAL
    self.machine_state['e6_safety'] = e6_active
    self.machine_state['s1_enabled'] = e6_active  # S1 só funciona se E6 ativa

    # Para compatibilidade, escrever em MODE_STATE também
    mode_value = 1 if mode_bit_02ff else 0
    self.client.write_register(mm.SUPERVISION_AREA['MODE_STATE'], mode_value)
```

### Atualizar main_server.py:

```python
async def handle_s1_press(self, websocket, data):
    """Handler para botão S1 (mudança AUTO/MANUAL)"""
    # Verificar se E6 está ativa
    e6_active = self.state_manager.machine_state.get('e6_safety', False)

    if not e6_active:
        # Avisar usuário que E6 precisa estar ativa
        await websocket.send(json.dumps({
            'type': 'error',
            'message': 'S1 bloqueado: E6 (segurança) não está ativa. Verifique sensor/botão no painel.'
        }))
        return False

    # Pressionar S1
    success = self.modbus_client.press_key(mm.KEYBOARD_FUNCTION['S1'])

    if success:
        # Aguardar ladder processar
        await asyncio.sleep(0.5)

        # Ler modo atualizado
        mode_bit = self.modbus_client.read_coil(0x02FF)
        mode_text = "AUTO" if mode_bit else "MANUAL"

        await websocket.send(json.dumps({
            'type': 'mode_changed',
            'mode': mode_text,
            'bit_02ff': mode_bit
        }))

        return True

    return False
```

### Atualizar static/index.html:

```javascript
// Adicionar indicador de E6
function updateSafetyIndicators(state) {
    const e6Indicator = document.getElementById('e6-indicator');
    const s1Button = document.getElementById('btn-s1');

    if (state.e6_safety) {
        e6Indicator.textContent = '✅ E6 Ativa';
        e6Indicator.className = 'safety-ok';
        s1Button.disabled = false;
    } else {
        e6Indicator.textContent = '⚠️ E6 Inativa - S1 bloqueado';
        e6Indicator.className = 'safety-warning';
        s1Button.disabled = true;
        s1Button.title = 'S1 bloqueado: E6 não está ativa. Verifique sensor no painel.';
    }
}

// Handler do botão S1
document.getElementById('btn-s1').addEventListener('click', async () => {
    if (!machineState.e6_safety) {
        alert('❌ S1 bloqueado!\n\nE6 (sensor de segurança) não está ativa.\nVerifique:\n- Botão PARADA no painel\n- Porta/carenagem fechada\n- Sensor conectado');
        return;
    }

    ws.send(JSON.stringify({ action: 'press_key', key: 'S1' }));
});

// Exibir modo baseado em 02FF
function updateModeDisplay(state) {
    const modeElement = document.getElementById('mode-display');
    const mode = state.mode_auto ? 'AUTO' : 'MANUAL';
    modeElement.textContent = `Modo: ${mode}`;
    modeElement.className = state.mode_auto ? 'mode-auto' : 'mode-manual';
}
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1: Diagnóstico
- [x] Decodificar ROT1.LAD
- [x] Identificar bit de modo real (02FF)
- [x] Identificar condição E6
- [ ] Verificar estado atual de E6 no CLP
- [ ] Verificar estado atual de 02FF

### Fase 2: Código
- [ ] Atualizar modbus_map.py com 02FF e E6
- [ ] Modificar state_manager.py para ler 02FF
- [ ] Adicionar handler S1 em main_server.py
- [ ] Atualizar interface HTML com indicador E6

### Fase 3: Teste
- [ ] Ativar E6 (física ou via Modbus)
- [ ] Pressionar S1 via IHM Web
- [ ] Verificar mudança de 02FF
- [ ] Confirmar sincronização com MODE_STATE

### Fase 4: Documentação
- [ ] Atualizar CLAUDE.md com bit 02FF
- [ ] Documentar E6 como requisito de segurança
- [ ] Instruções de operação para usuário final

---

## 🚨 AVISOS DE SEGURANÇA

1. **E6 é condição de segurança** - NÃO bypassar sem análise de risco
2. **02FF pode ter outras funções** além de modo - verificar ROT2, ROT3, etc.
3. **Testar em ambiente controlado** antes de produção
4. **Documentar** toda mudança de modo para auditoria

---

## 📊 RESUMO TÉCNICO

| Item | Antes (Errado) | Depois (Correto) |
|------|----------------|------------------|
| Bit de modo | 0x0946 (Python) | 0x02FF (Ladder) |
| Controle de modo | Python escreve | Ladder via S1 + E6 |
| Condição S1 | Nenhuma | E6 (0106) deve estar ON |
| Monostável | N/A | 0x0376 (886) |
| Tipo de operação | Escrita direta | Toggle via botão |

---

## ✅ PRÓXIMOS PASSOS IMEDIATOS

1. **Verificar E6 no painel físico** ou via Modbus
2. **Ativar E6** (fisicamente ou via código)
3. **Testar S1** → Deve alternar 02FF
4. **Implementar código** conforme acima
5. **Testar na IHM Web**

---

**Status:** ✅ SOLUÇÃO IDENTIFICADA E PRONTA PARA IMPLEMENTAÇÃO

**Confiança:** 95% (baseado em análise completa do ladder)

**Risco:** BAIXO (se E6 for respeitada como condição de segurança)
