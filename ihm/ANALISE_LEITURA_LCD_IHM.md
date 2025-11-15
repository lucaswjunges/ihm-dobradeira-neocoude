# Análise: Leitura do Estado da Tela LCD da IHM Física

**Data:** 2025-11-11
**Teste realizado:** `test_ihm_lcd_read.py`
**Objetivo:** Descobrir se a IHM web pode ler o estado do visor LCD da IHM física via Modbus RTU

---

## 🔍 Descobertas do Teste Empírico

### ✅ Registro 0FEC (4076) - SCREEN_NUM

**Resultado:** O registro É LEGÍVEL via Modbus, mas NÃO reflete o estado da tela atual.

```
Valor lido: 0 (0x0000)
Após simulação de K1: 0 (0x0000) - SEM MUDANÇA
```

**Interpretação:**
- O registro **existe** e pode ser lido
- O valor permanece **estático em 0**
- Não muda quando simulamos tecla K1 (que deveria navegar para tela 4)
- Confirma a documentação: é um registro de **comando** (Ladder → IHM), não de **status**

### 📊 Registros Relacionados

Todos os coils testados estão **desligados** (OFF):
- `00D7` (215) - LOAD_TRIGGER: OFF
- `00DB` (219) - DISPLAY_OFF: OFF
- `00D8` (216) - KEY_LOCKED: OFF
- `00DA` (218) - VALUE_CHANGED: OFF
- `00D2` (210) - COUNT_BLOCK: OFF

### 🗺️ Exploração da Área de Memória

**Registros 4070-4089 (ao redor de 0FEC):**

| Endereço | Hex    | Valor | Hex Valor | Observação |
|----------|--------|-------|-----------|------------|
| 4070     | 0x0FE6 | 32329 | 0x7E49    | Dados não identificados |
| 4071     | 0x0FE7 | 18943 | 0x49FF    | Dados não identificados |
| 4072     | 0x0FE8 | 65535 | 0xFFFF    | Provavelmente não usado |
| 4073     | 0x0FE9 | 65280 | 0xFF00    | Possível flag |
| 4074     | 0x0FEA | 76    | 0x004C    | **Interessante - valor baixo** |
| 4075     | 0x0FEB | 19456 | 0x4C00    | Possível configuração |
| **4076** | **0x0FEC** | **0** | **0x0000** | **SCREEN_NUM - sempre zero** |
| 4079     | 0x0FEF | 255   | 0x00FF    | Possível máscara |
| 4080-4088| 0x0FF0-0xFF8 | 65535 | 0xFFFF | Área não utilizada |

**Conclusão da exploração:**
Não há registro alternativo óbvio que armazene o número da tela atual. Os valores 0xFFFF sugerem área não inicializada/não utilizada.

---

## 🚫 Por Que Não Conseguimos Ler a Tela Atual?

### Arquitetura do Protocolo IHM-CLP Original

```
┌──────────────┐                           ┌──────────────┐
│   LADDER     │      Escreve 0FEC         │  IHM Física  │
│   (CLP)      │ ────────────────────────► │  (4004.95C)  │
│              │                           │              │
│              │   ◄─── SEM RETORNO ───    │              │
│              │   (não escreve estado)    │              │
└──────────────┘                           └──────────────┘
```

**Fluxo de Funcionamento:**
1. Usuário pressiona tecla na IHM física
2. IHM processa localmente e muda de tela
3. IHM escreve coil correspondente (K1=160, K2=161, etc.)
4. Ladder detecta coil e executa lógica
5. **Ladder pode escrever 0FEC para forçar mudança de tela**
6. **IHM NÃO escreve de volta qual tela está exibindo**

**Razão técnica:**
A IHM física Atos Expert Series tem **firmware proprietário** que gerencia:
- LCD de 2 linhas × 20 caracteres
- 11 telas configuradas (0-10)
- Navegação interna entre telas
- **Estado da tela é interno ao firmware, não exposto via Modbus**

---

## 💡 Estratégia Recomendada para IHM Web

### ❌ Abordagem INVIÁVEL: Sincronização de Telas

```python
# NÃO FUNCIONA - tentativa de ler tela atual
current_screen = modbus_client.read_register(0x0FEC)  # Sempre retorna 0
# Impossível saber se IHM física está na tela 1, 4, 7, etc.
```

### ✅ Abordagem VIÁVEL: Replicação de Lógica

A IHM web deve **replicar o comportamento funcional**, não o estado literal:

#### 1️⃣ Manter Estado Local de Navegação

```python
class WebHMIState:
    def __init__(self):
        self.current_screen = 0  # Estado local independente
        self.modo = "MANUAL"      # AUTO ou MANUAL
        self.dobra_atual = 1      # 1, 2 ou 3
        self.velocidade = 5       # 5, 10 ou 15 rpm

    def press_key(self, key):
        # Lógica de navegação replicada da IHM física
        if key == "K1":
            self.current_screen = 4  # Tela de ângulos dobra 1
            self.dobra_atual = 1
        elif key == "K2":
            self.current_screen = 5  # Tela de ângulos dobra 2
            self.dobra_atual = 2
        # etc...

        # Envia comando ao CLP
        modbus_client.press_key(key_address)
```

#### 2️⃣ Sincronização via Dados, Não Telas

```python
# Ler dados reais do CLP
encoder_angle = modbus_client.read_32bit(0x04D6, 0x04D7)
bend_1_angle = modbus_client.read_32bit(BEND_1_LEFT_MSW, BEND_1_LEFT_LSW)
led1_active = modbus_client.read_coil(LED1_ADDRESS)

# Atualizar UI com base nos DADOS
if led1_active:
    highlight_bend_1()  # LED1 aceso = Dobra 1 ativa
update_angle_display(encoder_angle)
update_setpoint_display(bend_1_angle)
```

#### 3️⃣ Replicar Regras de Negócio da IHM Física

```python
def validate_mode_change(self):
    """S1 só troca modo se máquina parada e na dobra 1"""
    if self.cycle_active:
        return False, "Ciclo em andamento - aguarde finalizar"
    if self.dobra_atual != 1:
        return False, "Retorne à dobra 1 para trocar modo"
    return True, "OK"

def validate_speed_change(self):
    """K1+K7 só em modo MANUAL"""
    if self.modo != "MANUAL":
        return False, "Mudança de velocidade só em MANUAL"
    return True, "OK"
```

---

## 📋 Mapeamento: Telas Físicas → Componentes Web

### Tela 0: Inicial / Standby
**IHM Física:** Exibe logo ou mensagem de aguardo
**IHM Web:**
- Componente: `<div id="screen-standby">`
- Exibe: Status de conexão, encoder atual
- Transição: Qualquer tecla → tela correspondente

### Tela 4: Ângulos Dobra 1 (K1)
**IHM Física:**
```
DOBRA 1 - ESQ
ANG: 090.0°
```

**IHM Web:**
```jsx
<div class="bend-screen active" data-bend="1">
  <h2>DOBRA 1</h2>
  <div class="angle-display">
    <label>ÂNGULO ESQUERDA:</label>
    <input type="number" id="bend-1-left" value="90.0">°
  </div>
  <div class="angle-display">
    <label>ÂNGULO DIREITA:</label>
    <input type="number" id="bend-1-right" value="90.0">°
  </div>
</div>
```

### Tela 5: Ângulos Dobra 2 (K2)
**Idêntico à tela 4, mas para `bend-2-left` e `bend-2-right`**

### Tela 6: Ângulos Dobra 3 (K3)
**Idêntico à tela 4, mas para `bend-3-left` e `bend-3-right`**

### Telas 7-9: Diagnóstico (S1 + K7/K8/K9)
**IHM Web:**
- Aba "Diagnóstico" com gêmeo digital (E0-E7, S0-S7)
- Não precisa replicar estrutura de telas - usar abas

---

## 🛠️ Implementação Prática

### Estrutura de Componentes Web

```html
<!-- index.html -->
<div id="ihm-container">
  <!-- Sempre visível: Encoder e Status -->
  <header class="ihm-header">
    <div class="encoder-display">
      <span id="angle-current">45.7°</span>
    </div>
    <div class="status-indicators">
      <span class="led" data-led="1"></span>
      <span class="led" data-led="2"></span>
      <span class="led" data-led="3"></span>
    </div>
  </header>

  <!-- Área de conteúdo dinâmico (muda com navegação) -->
  <main class="ihm-content">
    <div class="screen" data-screen="standby">...</div>
    <div class="screen" data-screen="bend-1">...</div>
    <div class="screen" data-screen="bend-2">...</div>
    <div class="screen" data-screen="bend-3">...</div>
  </main>

  <!-- Teclado virtual (sempre visível) -->
  <nav class="ihm-keyboard">
    <button data-key="K1">1</button>
    <button data-key="K2">2</button>
    <!-- ... -->
  </nav>
</div>
```

### Lógica de Navegação JavaScript

```javascript
class IHMNavigator {
  constructor() {
    this.currentScreen = 'standby';
    this.screens = {
      'standby': { element: document.querySelector('[data-screen="standby"]') },
      'bend-1': { element: document.querySelector('[data-screen="bend-1"]') },
      'bend-2': { element: document.querySelector('[data-screen="bend-2"]') },
      'bend-3': { element: document.querySelector('[data-screen="bend-3"]') }
    };
  }

  navigate(screenId) {
    // Ocultar tela atual
    this.screens[this.currentScreen].element.classList.remove('active');

    // Mostrar nova tela
    this.screens[screenId].element.classList.add('active');
    this.currentScreen = screenId;
  }

  handleKeyPress(key) {
    // Replicar lógica da IHM física
    switch(key) {
      case 'K1':
        this.navigate('bend-1');
        break;
      case 'K2':
        this.navigate('bend-2');
        break;
      case 'K3':
        this.navigate('bend-3');
        break;
      case 'ESC':
        this.navigate('standby');
        break;
    }

    // Enviar comando ao CLP via WebSocket
    ws.send(JSON.stringify({ action: 'press_key', key: key }));
  }
}
```

---

## ⚙️ Modificação do Ladder (Opcional)

### Possibilidade: Adicionar Registro de Estado

Se no futuro for necessário **sincronizar** IHM web com IHM física:

```ladder
; Adicionar no início do programa PRINCIPA
; Escrever número da tela atual em registro dedicado

[K1 Pressed]
  MOV #4, REG_TELA_ATUAL   ; Tela 4 (ângulos dobra 1)

[K2 Pressed]
  MOV #5, REG_TELA_ATUAL   ; Tela 5 (ângulos dobra 2)

[K3 Pressed]
  MOV #6, REG_TELA_ATUAL   ; Tela 6 (ângulos dobra 3)

; etc...
```

**Vantagens:**
- IHM web pode ler `REG_TELA_ATUAL` via Modbus
- Sincronização exata com IHM física

**Desvantagens:**
- Requer modificação e teste do ladder
- Aumenta complexidade de manutenção
- **NÃO É NECESSÁRIO** para funcionamento da IHM web

**Recomendação:** ❌ **NÃO MODIFICAR** o ladder neste momento. A abordagem de estado local independente é mais robusta e simples.

---

## ✅ Conclusões e Próximos Passos

### ✅ Resposta à Pergunta Original

**"É possível ler o conteúdo do visor LCD da IHM física?"**
❌ **NÃO** - O firmware da IHM física não expõe o estado da tela via Modbus.

**"É possível saber em que tela está?"**
❌ **NÃO** - O registro 0FEC é de comando (escrita), não de status (leitura).

**"Seria possível modificar o ladder para salvar o visor na memória?"**
✅ **SIM** - Tecnicamente possível, mas **NÃO RECOMENDADO**. A solução de estado local é superior.

### 🎯 Estratégia de Implementação

1. **IHM Web Independente:**
   - Manter estado local de navegação
   - Replicar lógica das 11 telas físicas
   - Sincronizar via dados (encoder, ângulos, LEDs)

2. **Vantagens da Abordagem:**
   - ✅ Funciona sem IHM física conectada
   - ✅ Não depende de firmware proprietário
   - ✅ Mais simples de implementar e manter
   - ✅ Permite melhorias na UX (abas ao invés de telas)

3. **Interface Moderna vs. Emulação Literal:**
   - Em vez de 11 telas sequenciais → **3 abas** (Operação, Diagnóstico, Configuração)
   - Todas as informações relevantes sempre visíveis
   - Navegação mais intuitiva para tablet

### 📝 Tarefas Pendentes

- [ ] Implementar classe `IHMNavigator` em JavaScript
- [ ] Criar componentes para cada "tela" (agora como divs tabuladas)
- [ ] Mapear teclas físicas → ações na IHM web
- [ ] Testar leitura contínua de LEDs (0x00C0-0x00C4) para sincronização
- [ ] Validar regras de negócio (modo MANUAL/AUTO, sequência de dobras)

---

## 📚 Referências

- **Teste executado:** `test_ihm_lcd_read.py`
- **Documentação estudada:**
  - `PROTOCOLO_IHM_CLP_COMPLETO.md`
  - `ANALISE_COMPLETA_REGISTROS_PRINCIPA.md`
  - `MAPEAMENTO_IHM_EXPERT.md`
- **Manuais:**
  - `manual_MPC4004.txt` (páginas 133-134: Modbus)
  - `neocoude_manual.txt` (operação da máquina)

---

**Conclusão Final:**
A IHM web deve funcionar como **substituto funcional** (não emulador literal) da IHM física, mantendo estado independente e sincronizando via leitura de dados reais do CLP (encoder, setpoints, I/O, LEDs). Esta abordagem é mais robusta, testável e futura-compatível com ESP32.
