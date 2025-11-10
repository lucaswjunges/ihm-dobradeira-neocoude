# Arquitetura IHM Web - Réplica Virtual da IHM Física

## Visão Geral

Esta IHM web é uma réplica fiel da IHM física 4004.95C integrada ao MPC4004 da Trillor NEOCOUDE-HD-15. O objetivo é simular EXATAMENTE o comportamento do display físico e teclado original.

## 1. Componentes da Interface

### 1.1 Display LCD Virtual (Componente Principal)

**Especificação Física Estimada:**
- Display de caracteres (16x2 ou 20x2) típico de CLPs industriais
- Fonte monoespaçada
- Backlight verde/azul
- Caracteres brancos/pretos de alto contraste

**Funcionalidade:**
- Mostrar telas de operação (ângulo atual, setpoints, status)
- Navegação entre telas usando teclas de seta
- Modo de edição com cursor piscante
- Mensagens de status e erro

### 1.2 Teclado Virtual

**Layout Completo (100% fiel ao físico):**

```
┌─────────────────────────────────────────┐
│  [K7] [K8] [K9]          [↑]  [EDIT]    │
│  [K4] [K5] [K6]     [←] [OK] [→]  [ESC] │
│  [K1] [K2] [K3]          [↓]  [ENTER]   │
│  [S1] [K0] [S2]               [LOCK]    │
└─────────────────────────────────────────┘
```

**LEDs Indicadores:**
- LED K1 (verde): 1ª dobra ativa
- LED K2 (verde): 2ª dobra ativa
- LED K3 (verde): 3ª dobra ativa
- LED K4 (amarelo): Sentido anti-horário (esquerda)
- LED K5 (amarelo): Sentido horário (direita)
- LED S1 (azul): Modo automático ativo
- LED S2 (vermelho): Emergência/erro

### 1.3 Painel de Status

**Indicadores em tempo real:**
- Ângulo encoder atual (atualizado a cada 250ms)
- Modo operação (MANUAL / AUTOMÁTICO)
- Classe de velocidade (5 rpm / 10 rpm / 15 rpm)
- Status do ciclo (PARADO / DOBRANDO / RETORNANDO)
- Posição atual (ZERO / EM MOVIMENTO)

## 2. Máquina de Estados do Display

### 2.1 Telas Principais

#### TELA 1: Operação Normal (Tela Principal)
```
┌──────────────────────┐
│ ANG: 000.0°  D1  ESQ │  Linha 1: Ângulo atual, dobra, direção
│ PV:  000.0°  [AUTO] │  Linha 2: PV (posição), modo
└──────────────────────┘
```

**Campos:**
- `ANG`: Ângulo atual do encoder (leitura real-time de 04D6/04D7)
- `D1/D2/D3`: Dobra atual (1, 2 ou 3) - correspondente ao LED K1/K2/K3
- `ESQ/DIR`: Direção selecionada (esquerda/direita) - correspondente ao LED K4/K5
- `PV`: Position Value - valor auto-calculado pelo CLP
- `[MANUAL]` ou `[AUTO]`: Modo atual

#### TELA 2: Edição de Ângulos (Tela 1HM)
```
┌──────────────────────┐
│ EDITAR ANGULOS      │
│ D1E: 090.0°  █      │  █ = cursor piscante
└──────────────────────┘
```

**Navegação:**
- D1E: Dobra 1 Esquerda
- D2E: Dobra 2 Esquerda
- D3E: Dobra 3 Esquerda
- D1D: Dobra 1 Direita
- D2D: Dobra 2 Direita
- D3D: Dobra 3 Direita

**Edição:**
- Teclas K0-K9: Digitar valor
- ENTER: Confirmar
- ESC: Cancelar

#### TELA 3: Seleção de Velocidade
```
┌──────────────────────┐
│ VELOCIDADE          │
│ CLASSE: █2 (10 RPM) │  █ = cursor
└──────────────────────┘
```

**Opções:**
- 1: 5 RPM (classe 1 - sempre disponível)
- 2: 10 RPM (classe 2 - só automático)
- 3: 15 RPM (classe 3 - só automático)

**Acesso:** K1 + K7 simultâneo (só em modo manual)

#### TELA 4: Seleção de Modo
```
┌──────────────────────┐
│ SELECIONAR MODO     │
│ > MANUAL            │
│   AUTOMATICO        │
└──────────────────────┘
```

**Acesso:** Tecla S1 (só com máquina parada e em D1)

#### TELA 5: Erro/Status
```
┌──────────────────────┐
│ ** EMERGENCIA **    │
│ Pressione S2        │
└──────────────────────┘
```

### 2.2 Transições de Tela

```
TELA_PRINCIPAL (default)
  ├─ [EDIT] ──────> TELA_EDICAO_ANGULOS
  ├─ [S1] ────────> TELA_SELECAO_MODO (se parado e D1)
  ├─ [K1+K7] ─────> TELA_SELECAO_VELOCIDADE (se manual)
  └─ [emergência] ─> TELA_ERRO

TELA_EDICAO_ANGULOS
  ├─ [↑/↓] ───────> navega entre D1E, D2E, D3E, D1D, D2D, D3D
  ├─ [K0-K9] ─────> digita valor
  ├─ [ENTER] ─────> confirma e volta TELA_PRINCIPAL
  └─ [ESC] ───────> cancela e volta TELA_PRINCIPAL

TELA_SELECAO_MODO
  ├─ [↑/↓] ───────> alterna entre MANUAL/AUTOMATICO
  ├─ [ENTER] ─────> confirma e volta TELA_PRINCIPAL
  └─ [ESC] ───────> cancela e volta TELA_PRINCIPAL

TELA_SELECAO_VELOCIDADE
  ├─ [↑/↓] ───────> alterna entre 1/2/3
  ├─ [ENTER] ─────> confirma e volta TELA_PRINCIPAL
  └─ [ESC] ───────> cancela e volta TELA_PRINCIPAL

TELA_ERRO
  └─ [S2] ────────> reset e volta TELA_PRINCIPAL
```

## 3. Lógica de Operação

### 3.1 Modo MANUAL

**Características:**
- Velocidade FIXA em 5 RPM (classe 1)
- Botões de avanço/recuo devem ser **mantidos pressionados**
- Prato rotaciona até ângulo programado
- Retorna automaticamente para zero
- Display pode não mostrar zero exato - pressionar S2 para zerar

**Workflow:**
1. Selecionar dobra (K1, K2 ou K3) - LED acende
2. Selecionar direção (K4=esquerda, K5=direita) - LED acende
3. Verificar ângulo no display
4. Pressionar e **manter** AVANÇAR ou RECUAR
5. Prato dobra até ângulo e retorna
6. Se display não mostra 000.0°, pressionar S2
7. Repetir para próximas dobras

### 3.2 Modo AUTOMÁTICO

**Características:**
- Velocidade selecionável (5/10/15 RPM)
- Ciclo automático (não precisa manter botão)
- Sequência de dobras automática (D1 → D2 → D3)
- Não permite voltar para dobra anterior

**Workflow:**
1. Pressionar S1 para mudar modo (só se parado e em D1)
2. Pressionar PARADA para selecionar direção
3. Pressionar K4 (esquerda) ou K5 (direita) - LED acende
4. Verificar ângulo no display
5. Pressionar AVANÇAR ou RECUAR (aperto rápido, não manter)
6. Sistema executa dobra e retorna automaticamente
7. Avança para próxima dobra (D1 → D2 → D3)
8. Para reiniciar sequência: desligar e religar

**Mudança de Velocidade (só modo automático):**
- Pressionar K1 + K7 simultaneamente
- Navegar com ↑/↓
- ENTER para confirmar

## 4. Mapeamento de Estados do CLP

### 4.1 Registradores de Leitura

```python
# Encoder (32-bit MSW/LSW)
ENCODER_MSW = 0x04D6  # 1238 dec
ENCODER_LSW = 0x04D7  # 1239 dec

# Entradas digitais (E0-E7)
INPUT_E0 = 0x0100  # 256 dec - Sensor de posição zero
INPUT_E1 = 0x0101  # 257 dec - Fim de curso avanço
INPUT_E2 = 0x0102  # 258 dec - Fim de curso recuo
INPUT_E3 = 0x0103  # 259 dec - Botão emergência
INPUT_E4 = 0x0104  # 260 dec - Botão AVANÇAR
INPUT_E5 = 0x0105  # 261 dec - Botão RECUAR
INPUT_E6 = 0x0106  # 262 dec - Botão PARADA
INPUT_E7 = 0x0107  # 263 dec - Comando geral

# Saídas digitais (S0-S7)
OUTPUT_S0 = 0x0180  # 384 dec - Motor sentido horário
OUTPUT_S1 = 0x0181  # 385 dec - Motor sentido anti-horário
OUTPUT_S2 = 0x0182  # 386 dec - VFD enable
OUTPUT_S3 = 0x0183  # 387 dec - Velocidade classe 1
OUTPUT_S4 = 0x0184  # 388 dec - Velocidade classe 2
OUTPUT_S5 = 0x0185  # 389 dec - Velocidade classe 3
OUTPUT_S6 = 0x0186  # 390 dec - LED K1 (dobra 1)
OUTPUT_S7 = 0x0187  # 391 dec - LED K2 (dobra 2)

# Estados internos (a mapear do ladder)
STATE_MODO_MANUAL = ???  # 1=manual, 0=auto
STATE_DOBRA_ATUAL = ???  # 1, 2 ou 3
STATE_DIRECAO_ESQ = ???  # 1=esquerda (K4)
STATE_DIRECAO_DIR = ???  # 1=direita (K5)
STATE_CICLO_ATIVO = ???  # 1=dobrando
STATE_EMERGENCIA = ???   # 1=emergência ativa
STATE_POSICAO_ZERO = ??? # 1=em zero

# Ângulos programados (6 registradores de 16-bit)
REG_ANGULO_D1E = ???  # Dobra 1 Esquerda
REG_ANGULO_D2E = ???  # Dobra 2 Esquerda
REG_ANGULO_D3E = ???  # Dobra 3 Esquerda
REG_ANGULO_D1D = ???  # Dobra 1 Direita
REG_ANGULO_D2D = ???  # Dobra 2 Direita
REG_ANGULO_D3D = ???  # Dobra 3 Direita

# Classe de velocidade
REG_VELOCIDADE_CLASSE = ???  # 1, 2 ou 3
```

### 4.2 Botões da IHM (Write Coil - Modbus 0x05)

```python
# Teclado numérico
BTN_K1 = 0x00A0  # 160 dec
BTN_K2 = 0x00A1  # 161 dec
BTN_K3 = 0x00A2  # 162 dec
BTN_K4 = 0x00A3  # 163 dec
BTN_K5 = 0x00A4  # 164 dec
BTN_K6 = 0x00A5  # 165 dec
BTN_K7 = 0x00A6  # 166 dec
BTN_K8 = 0x00A7  # 167 dec
BTN_K9 = 0x00A8  # 168 dec
BTN_K0 = 0x00A9  # 169 dec

# Funções
BTN_S1 = 0x00DC  # 220 dec - Troca modo
BTN_S2 = 0x00DD  # 221 dec - Reset/zerar

# Navegação
BTN_UP = 0x00AC     # 172 dec
BTN_DOWN = 0x00AD   # 173 dec
BTN_ESC = 0x00BC    # 188 dec
BTN_ENTER = 0x0025  # 37 dec
BTN_EDIT = 0x0026   # 38 dec
BTN_LOCK = 0x00F1   # 241 dec
```

## 5. Arquitetura de Software

### 5.1 Backend (Python)

#### Módulos Atuais (manter):
- `modbus_client.py`: Comunicação Modbus RTU
- `state_manager.py`: Polling e gerenciamento de estado
- `main_server.py`: WebSocket server

#### Módulos Novos (criar):

**`display_manager.py`** - Gerenciador do Display Virtual
```python
class DisplayManager:
    def __init__(self):
        self.current_screen = "TELA_PRINCIPAL"
        self.cursor_position = 0
        self.edit_buffer = ""
        self.line1 = ""
        self.line2 = ""

    def update_main_screen(self, state):
        """Atualiza tela principal com dados do CLP"""
        angle = state['encoder_angle']
        dobra = state['dobra_atual']
        direction = "ESQ" if state['direcao_esq'] else "DIR"
        mode = "AUTO" if state['modo_auto'] else "MANUAL"
        pv = state['pv_value']

        self.line1 = f"ANG: {angle:05.1f}°  D{dobra}  {direction}"
        self.line2 = f"PV:  {pv:05.1f}°  [{mode}]"

    def handle_keypress(self, key, machine_state):
        """Processa tecla e retorna nova tela/ação"""
        # Implementar lógica de navegação
        pass

    def get_display_content(self):
        """Retorna conteúdo atual do display"""
        return {"line1": self.line1, "line2": self.line2,
                "screen": self.current_screen, "cursor": self.cursor_position}
```

**`state_machine.py`** - Máquina de Estados da Operação
```python
class OperationStateMachine:
    def __init__(self):
        self.modo = "MANUAL"  # MANUAL ou AUTO
        self.dobra_atual = 1   # 1, 2 ou 3
        self.direcao = None    # "ESQ" ou "DIR"
        self.velocidade_classe = 1  # 1, 2 ou 3
        self.ciclo_ativo = False

    def can_change_mode(self, machine_state):
        """Só pode trocar modo se parado e em D1"""
        return (not machine_state['ciclo_ativo'] and
                self.dobra_atual == 1)

    def can_change_velocity(self):
        """Só pode trocar velocidade em modo manual"""
        return self.modo == "MANUAL"

    def advance_dobra(self):
        """Avança para próxima dobra (D1→D2→D3)"""
        if self.dobra_atual < 3:
            self.dobra_atual += 1
        # Não permite voltar!
```

### 5.2 Frontend (HTML/CSS/JavaScript)

#### Componentes a Implementar:

**`VirtualLCD` (classe JavaScript)**
```javascript
class VirtualLCD {
    constructor(elementId) {
        this.element = document.getElementById(elementId);
        this.line1 = "";
        this.line2 = "";
        this.cursorPos = 0;
        this.cursorBlink = true;
    }

    update(displayData) {
        // Renderizar display com fonte monoespaçada
        // Adicionar cursor piscante se em modo edição
    }

    startCursorBlink() {
        // Piscar cursor a cada 500ms
    }
}
```

**`VirtualKeypad` (classe JavaScript)**
```javascript
class VirtualKeypad {
    constructor(onKeyPress) {
        this.onKeyPress = onKeyPress;
        this.setupButtons();
        this.setupLEDs();
    }

    setupButtons() {
        // Criar botões K0-K9, S1, S2, etc
        // Estilo 3D com efeito de pressionar
    }

    pressButton(button) {
        // Animação visual
        // Enviar comando via WebSocket
        // Simular hold de 100ms
    }

    updateLEDs(state) {
        // Atualizar LEDs K1/K2/K3 (dobra)
        // Atualizar LEDs K4/K5 (direção)
        // Atualizar LED S1 (modo auto)
    }
}
```

#### Layout HTML:

```html
<div id="ihm-virtual">
    <!-- Display LCD -->
    <div id="lcd-display" class="lcd-screen">
        <div class="lcd-line1"></div>
        <div class="lcd-line2"></div>
    </div>

    <!-- Teclado -->
    <div id="keypad">
        <div class="keypad-row">
            <button class="key num" data-key="K7">7</button>
            <button class="key num" data-key="K8">8</button>
            <button class="key num" data-key="K9">9</button>
            <button class="key nav" data-key="UP">↑</button>
            <button class="key func" data-key="EDIT">EDIT</button>
        </div>
        <!-- ... mais linhas ... -->
    </div>

    <!-- LEDs -->
    <div id="leds">
        <span class="led green" id="led-k1">D1</span>
        <span class="led green" id="led-k2">D2</span>
        <span class="led green" id="led-k3">D3</span>
        <span class="led yellow" id="led-k4">←</span>
        <span class="led yellow" id="led-k5">→</span>
        <span class="led blue" id="led-s1">AUTO</span>
    </div>

    <!-- Painel de Status -->
    <div id="status-panel">
        <div>Modo: <span id="status-modo">MANUAL</span></div>
        <div>Velocidade: <span id="status-vel">5 RPM</span></div>
        <div>Ciclo: <span id="status-ciclo">PARADO</span></div>
    </div>
</div>
```

#### Estilo CSS (tema industrial):

```css
#lcd-display {
    background: #2a4a2a;  /* Verde escuro LCD */
    color: #90ff90;        /* Verde claro caracteres */
    font-family: 'Courier New', monospace;
    font-size: 24px;
    padding: 20px;
    border: 3px solid #333;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    text-shadow: 0 0 5px #90ff90;
}

.key {
    background: linear-gradient(180deg, #555 0%, #333 100%);
    border: 2px solid #666;
    border-radius: 5px;
    color: white;
    font-weight: bold;
    padding: 15px 20px;
    margin: 5px;
    cursor: pointer;
    box-shadow: 0 3px 0 #222;
}

.key:active {
    transform: translateY(3px);
    box-shadow: 0 0 0 #222;
}

.led {
    display: inline-block;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border: 2px solid #333;
    background: #222;
    margin: 5px;
}

.led.on {
    box-shadow: 0 0 10px currentColor;
}

.led.green.on { background: #0f0; }
.led.yellow.on { background: #ff0; }
.led.blue.on { background: #00f; }
.led.red.on { background: #f00; }
```

## 6. Fluxo de Dados

```
CLP (Modbus RTU)
    ↓ (polling 250ms)
state_manager.py
    ↓ (atualiza)
display_manager.py
    ↓ (renderiza)
WebSocket (JSON)
    ↓
VirtualLCD.update()
    ↓
Renderização HTML

---

Usuário pressiona botão virtual
    ↓
VirtualKeypad.pressButton()
    ↓
WebSocket (comando)
    ↓
main_server.py
    ↓
display_manager.handle_keypress()
    ↓ (se comando CLP)
modbus_client.press_key()
    ↓
CLP (Modbus Write Coil 0x05)
```

## 7. Protocolo WebSocket

### Mensagens Backend → Frontend:

```json
{
    "type": "display_update",
    "display": {
        "line1": "ANG: 000.0°  D1  ESQ",
        "line2": "PV:  000.0°  [MANUAL]",
        "screen": "TELA_PRINCIPAL",
        "cursor": -1
    },
    "leds": {
        "k1": true,   // dobra 1 ativa
        "k2": false,
        "k3": false,
        "k4": true,   // direção esquerda
        "k5": false,
        "s1": false   // modo manual (AUTO=false)
    },
    "status": {
        "modo": "MANUAL",
        "velocidade": 1,
        "velocidade_rpm": 5,
        "ciclo_ativo": false,
        "emergencia": false,
        "encoder_angle": 0.0
    }
}
```

### Mensagens Frontend → Backend:

```json
{
    "action": "key_press",
    "key": "K1"
}
```

```json
{
    "action": "key_combo",
    "keys": ["K1", "K7"]  // Para trocar velocidade
}
```

## 8. Próximos Passos de Implementação

1. ✅ Estudar manuais e arquitetar sistema
2. ⏳ Mapear registradores faltantes no ladder (clp.sup)
3. ⏳ Implementar `display_manager.py`
4. ⏳ Implementar `state_machine.py`
5. ⏳ Atualizar `main_server.py` com lógica de display
6. ⏳ Reescrever `index.html` com VirtualLCD e VirtualKeypad
7. ⏳ Testar navegação de telas
8. ⏳ Testar edição de ângulos
9. ⏳ Testar ciclo completo de operação
10. ⏳ Ajustes finos e validação com usuário

## 9. Perguntas Pendentes

### Para o Usuário:
1. **FOTO DA IHM FÍSICA**: Poderia tirar foto do display físico mostrando a tela principal? Isso garantiria layout 100% fiel.
2. **TAMANHO DO DISPLAY**: O display físico é 16x2 ou 20x2 caracteres?
3. **COR DO BACKLIGHT**: Verde, azul ou outro?
4. **COMPORTAMENTO ATUAL**: Consegue fazer algum teste na IHM física para ver como funciona a navegação entre telas?

### Para Análise do Ladder:
- Endereços dos registradores de ângulos (D1E, D2E, D3E, D1D, D2D, D3D)
- Estado de modo (manual/auto)
- Estado de dobra atual (1, 2 ou 3)
- Estado de direção (esquerda/direita)
- Estado de ciclo ativo
- Estado de emergência
- Registrador de classe de velocidade

---

**Autor:** Claude Code
**Data:** 2025-11-08
**Versão:** 1.0 - Arquitetura Inicial
