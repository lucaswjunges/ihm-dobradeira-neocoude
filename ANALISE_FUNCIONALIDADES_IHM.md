# 🔍 ANÁLISE COMPLETA - FUNCIONALIDADES FALTANTES NA IHM WEB

**Data**: 10/11/2025 06:52
**Situação atual**: Sistema enviando teclas para CLP, mas interação na interface incompleta

---

## ❌ PROBLEMAS IDENTIFICADOS

### **1. EDIÇÃO DE ÂNGULOS - FUNCIONAMENTO INADEQUADO**

**Comportamento Atual**:
- Clicar no valor `AJ=0000` → Abre `prompt()` do navegador
- Usuário digita valor no popup
- Popup tem apenas OK/Cancelar

**Por que é inadequado**:
- ❌ Não usa o teclado virtual da IHM (K0-K9)
- ❌ Botão EDIT não faz nada
- ❌ Botões ENTER/ESC não funcionam na edição
- ❌ Experiência diferente da IHM física
- ❌ Popup pode não aparecer em tablets (alguns navegadores bloqueiam)

**Comportamento Esperado** (IHM física):
1. Navegar para Tela 4/5/6 (usando ↑↓ ou K1/K2/K3)
2. Pressionar **EDIT** → Campo entra em modo de edição
3. Digitar novo valor usando **K0-K9**
4. Pressionar **ENTER** → Salva
5. Ou pressionar **ESC** → Cancela

---

### **2. BOTÃO EDIT - NÃO FAZ NADA NA INTERFACE**

**Código atual**:
```javascript
sendKey(38, event)  // Apenas envia comando ao CLP
```

**Problema**:
- ✅ Envia para o CLP (correto)
- ❌ Não ativa modo de edição na interface web

**Deveria fazer**:
1. Enviar comando ao CLP
2. **E TAMBÉM**: Ativar modo de edição no campo atual (se estiver em tela de ângulo)

---

### **3. TECLADO NUMÉRICO - NÃO DIGITA VALORES**

**Teclas afetadas**: K0, K6, K7, K8, K9

**Comportamento atual**:
- Apenas envia comando ao CLP
- Não digita números na interface

**Deveria fazer**:
- **Se em modo de edição**: Digitar o número no campo
- **Se NÃO em modo de edição**: Apenas enviar ao CLP

---

### **4. ENTER/ESC - NÃO FUNCIONAM NA EDIÇÃO**

**Comportamento atual**:
- ENTER (37): Apenas envia ao CLP
- ESC (188): Apenas envia ao CLP

**Deveria fazer**:
- **ENTER**: Se em modo edição → Salvar valor + sair do modo
- **ESC**: Se em modo edição → Cancelar + sair do modo
- **Ambos**: Também enviar ao CLP

---

### **5. INDICADORES VISUAIS FALTANDO**

**O que não está sendo mostrado**:
- ❌ Estado do modo (Manual/Automático) - **Tela 2 existe mas não atualiza**
- ❌ Classe de velocidade atual (1/2/3) - **Tela 3 existe mas não atualiza**
- ❌ LEDs K1/K2/K3 (qual dobra está ativa) - **Não implementado**
- ❌ LEDs K4/K5 (direção selecionada) - **Não implementado**
- ❌ Estado EDIT ativo - **Não implementado**
- ❌ Estado LOCK ativo - **Não implementado**

**Telas que existem mas não funcionam**:
```javascript
// Tela 2 - Modo AUTO/MAN
line1: "OP.AUTOM/OP.MANUAL",
line2: "                    "  // ← DEVERIA mostrar modo atual

// Tela 3 - Classe de velocidade
line1: "VELOCID. TRABALHANDO",
line2: "                    "  // ← DEVERIA mostrar 1, 2 ou 3

// Tela 7 - Dobra atual
line1: "*SELECAO DA ROTACAO*",
line2: "                    "  // ← DEVERIA mostrar K4 (←) ou K5 (→)

// Tela 8 - Contador
line1: "CARENAGEM DOBRADEIRA",
line2: "                    "  // ← DEVERIA mostrar contador de peças

// Tela 9 - Tempo
line1: "TOTALIZADOR DE TEMPO",
line2: "*****     :  h *****"  // ← DEVERIA mostrar horas de operação
```

---

### **6. ESTADOS DO CLP NÃO ESTÃO SENDO LIDOS**

**Dados que o backend deveria ler mas não está**:

```python
# No ihm_server_final.py, polling lê apenas:
- encoder (✅ OK)
- angle1, angle2, angle3 (✅ OK mas valores errados)
- inputs (❌ desabilitado)
- outputs (❌ desabilitado)
- velocidade_classe (❌ desabilitado - sempre 0)

# Faltam:
- Modo atual (Manual/Auto) → Bit no CLP
- Dobra ativa (K1/K2/K3) → Bits 896, 897, 898
- Direção (K4/K5) → Bits no CLP
- Estado LOCK → Bit 241
- Estado EDIT → Bit 38
- Contador de peças → Registro no CLP
- Tempo de operação → Cálculo ou registro
```

---

## 📋 FUNCIONALIDADES QUE FUNCIONAM

✅ **Envio de teclas para o CLP** (18/18)
✅ **Leitura do encoder** (tempo real)
✅ **Navegação UP/DOWN** (11 telas)
✅ **Atalhos K1/K2/K3** (ir para telas de ângulo)
✅ **WebSocket estável** (reconexão automática)
✅ **Feedback visual** (botões piscam ao clicar)
✅ **Indicador de conexão** (WebSocket e CLP)

---

## 🎯 O QUE PRECISA SER IMPLEMENTADO

### **PRIORIDADE 1: Edição de Ângulos Funcional**

**Substituir `prompt()` por editor inline**:

```javascript
// Novo fluxo de edição
let editMode = false;
let editBuffer = '';
let editField = null;  // 'angle1', 'angle2', ou 'angle3'

function editAngle(tela, currentValue) {
    // Ativar modo de edição
    editMode = true;
    editField = `angle${tela-3}`;
    editBuffer = '';

    // Indicador visual no display
    showFeedback('EDIT: Digite 0-360 + ENTER');
}

function sendKey(code, event) {
    // Se em modo de edição
    if (editMode) {
        // K0-K9: Adicionar dígito
        if (code >= 160 && code <= 169) {
            const digit = (code === 169) ? '0' : String(code - 159);
            editBuffer += digit;
            updateScreen();  // Mostra buffer na tela
            return;  // Não envia ao CLP durante edição
        }

        // ENTER: Confirmar
        if (code === 37) {
            const valor = parseInt(editBuffer);
            if (valor >= 0 && valor <= 360) {
                saveAngle(editField, valor);
                editMode = false;
                editBuffer = '';
            } else {
                showFeedback('Erro: 0-360!', true);
            }
            return;
        }

        // ESC: Cancelar
        if (code === 188) {
            editMode = false;
            editBuffer = '';
            showFeedback('Edição cancelada');
            updateScreen();
            return;
        }
    }

    // Modo normal: enviar ao CLP
    ws.send(JSON.stringify({ action: 'press_key', key_code: code }));
    // ... resto do código
}
```

---

### **PRIORIDADE 2: Botão EDIT Funcional**

```javascript
// EDIT deve ativar edição se estiver em tela de ângulo
if (code === 38) { // EDIT
    if (screen >= 4 && screen <= 6) {
        // Ativar modo de edição
        const currentAngle = data[`angle${screen-3}`];
        editAngle(screen, currentAngle);
    }
    // Também enviar ao CLP
    ws.send(JSON.stringify({ action: 'press_key', key_code: code }));
}
```

---

### **PRIORIDADE 3: Ler Estados do CLP**

**No backend (`ihm_server_final.py`)**:

```python
# Adicionar ao polling
async def poll_clp_data():
    while True:
        try:
            # ... leituras existentes ...

            # Ler estados do sistema
            modo_auto = modbus.read_coil(MODO_AUTO_BIT) or False
            dobra_1_ativa = modbus.read_coil(896) or False  # K1
            dobra_2_ativa = modbus.read_coil(897) or False  # K2
            dobra_3_ativa = modbus.read_coil(898) or False  # K3

            # Adicionar aos dados
            data = {
                'action': 'update',
                'data': {
                    # ... dados existentes ...
                    'modo_auto': modo_auto,
                    'dobra_ativa': 1 if dobra_1_ativa else (2 if dobra_2_ativa else 3),
                    'velocidade_classe': velocidade_classe,  # Re-habilitar leitura
                },
                'timestamp': datetime.now().isoformat()
            }
```

---

### **PRIORIDADE 4: Atualizar Displays das Telas**

**Tela 2 - Modo**:
```javascript
line2: () => data.modo_auto ?
    "   MODO AUTOMATICO   " :
    "     MODO MANUAL     "
```

**Tela 3 - Velocidade**:
```javascript
line2: () => `  CLASSE ${data.velocidade_classe || 1} (${[5,10,15][data.velocidade_classe-1] || 5} RPM)  `
```

**Tela 7 - Dobra Atual**:
```javascript
line2: () => `   DOBRA ${data.dobra_ativa || 1} ATIVA   `
```

---

### **PRIORIDADE 5: LEDs Visuais**

**Adicionar indicadores visuais**:

```html
<div class="led-indicators">
    <div class="led-group">
        <span class="led" id="led-k1">K1</span>
        <span class="led" id="led-k2">K2</span>
        <span class="led" id="led-k3">K3</span>
    </div>
    <div class="led-group">
        <span class="led" id="led-k4">K4←</span>
        <span class="led" id="led-k5">K5→</span>
    </div>
    <div class="led-group">
        <span class="led" id="led-edit">EDIT</span>
        <span class="led" id="led-lock">LOCK</span>
    </div>
</div>

<style>
.led {
    display: inline-block;
    padding: 4px 8px;
    background: #333;
    color: #666;
    border-radius: 3px;
    margin: 2px;
    font-size: 10px;
}

.led.active {
    background: #00ff00;
    color: #000;
    box-shadow: 0 0 10px #00ff00;
}
</style>
```

---

## 📊 RESUMO: O QUE ESTÁ FALTANDO

| Funcionalidade | Status Atual | Status Esperado | Prioridade |
|----------------|--------------|-----------------|------------|
| **Edição de ângulos** | ⚠️ Usa prompt() | ✅ Editor inline com K0-K9 | 🔴 ALTA |
| **Botão EDIT** | ❌ Só envia ao CLP | ✅ Ativa edição na tela | 🔴 ALTA |
| **Teclado K0-K9 em edição** | ❌ Não digita | ✅ Digita valores | 🔴 ALTA |
| **ENTER confirmar edição** | ❌ Só envia ao CLP | ✅ Salva valor editado | 🔴 ALTA |
| **ESC cancelar edição** | ❌ Só envia ao CLP | ✅ Cancela edição | 🔴 ALTA |
| **Tela 2: Modo Auto/Man** | ⚠️ Vazia | ✅ Mostra modo atual | 🟡 MÉDIA |
| **Tela 3: Velocidade** | ⚠️ Vazia | ✅ Mostra classe 1/2/3 | 🟡 MÉDIA |
| **Tela 7: Dobra ativa** | ⚠️ Vazia | ✅ Mostra 1/2/3 | 🟡 MÉDIA |
| **LEDs K1/K2/K3** | ❌ Não existe | ✅ Indicam dobra ativa | 🟡 MÉDIA |
| **LEDs K4/K5** | ❌ Não existe | ✅ Indicam direção | 🟡 MÉDIA |
| **LED EDIT** | ❌ Não existe | ✅ Indica modo edição | 🟢 BAIXA |
| **LED LOCK** | ❌ Não existe | ✅ Indica teclado travado | 🟢 BAIXA |
| **Tela 8: Contador** | ❌ Vazia | ✅ Mostra peças | 🟢 BAIXA |
| **Tela 9: Tempo** | ❌ Vazia | ✅ Mostra horas | 🟢 BAIXA |

---

## 🚨 PROBLEMAS CRÍTICOS (Impedem uso real)

1. **Edição de ângulos não usa teclado virtual**
   - Operador não pode usar a IHM como faria na física
   - Popup pode não funcionar em todos dispositivos

2. **Sem feedback visual de estados**
   - Não sabe qual dobra está ativa
   - Não sabe se está em Manual ou Auto
   - Não sabe qual velocidade está configurada

3. **Teclas com dupla função não implementadas**
   - EDIT deveria ativar edição + enviar ao CLP
   - ENTER deveria confirmar edição + enviar ao CLP
   - ESC deveria cancelar edição + enviar ao CLP

---

## ✅ PLANO DE AÇÃO RECOMENDADO

### **Fase 1: Edição Funcional** (CRÍTICO)
1. Implementar modo de edição inline
2. Fazer K0-K9 digitarem durante edição
3. Fazer ENTER confirmar e ESC cancelar
4. Fazer EDIT ativar modo de edição

**Tempo estimado**: 1-2 horas
**Impacto**: Sistema se torna usável para operação real

### **Fase 2: Indicadores Visuais** (IMPORTANTE)
1. Ler estados do CLP (modo, dobra ativa, velocidade)
2. Atualizar Telas 2, 3, 7 com dados reais
3. Adicionar LEDs visuais (K1/K2/K3, K4/K5)

**Tempo estimado**: 2-3 horas
**Impacto**: Operador tem feedback completo

### **Fase 3: Complementos** (DESEJÁVEL)
1. Contador de peças (Tela 8)
2. Tempo de operação (Tela 9)
3. LED EDIT/LOCK

**Tempo estimado**: 1-2 horas
**Impacto**: Paridade 100% com IHM física

---

## 📝 RECOMENDAÇÃO FINAL

**Para uso imediato** (testes básicos):
- ✅ Sistema atual funciona para **enviar comandos ao CLP**
- ✅ Pode testar teclas e ver encoder
- ❌ **NÃO usar para editar ângulos em produção** (usar IHM física para isso)

**Para uso em produção**:
- 🔴 **OBRIGATÓRIO**: Implementar Fase 1 (edição funcional)
- 🟡 **RECOMENDADO**: Implementar Fase 2 (indicadores)
- 🟢 **OPCIONAL**: Implementar Fase 3 (complementos)

---

**Próximo passo sugerido**: Implementar editor inline de ângulos (Fase 1)?
